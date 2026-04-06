from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from music.models import Song
from music.serializers import AlbumSerializer, ArtistSerializer
from .models import Follow, PlayHistory  
from rest_framework import status
from django.utils import timezone
from .models import Song, PlayHistory
from .serializers import SongSerializer
from django.db.models import Count
from datetime import timedelta
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Q
from .models import Song, Artist
from music.models import Album
from streaming.serializers import PlayHistorySerializer
from django.core.cache import cache






class StreamSongView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, song_id):
        try:
            song = Song.objects.get(id=song_id)
        except Song.DoesNotExist:
            return Response({'error': 'Song not found'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        subscription = getattr(user, 'subscription', None)
        is_premium = subscription and subscription.plan == 'premium' and subscription.is_active

        if not is_premium:
            one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
            skip_count = PlayHistory.objects.filter(
                user=user,
                played_at__gte=one_hour_ago,
                skipped=True
            ).count()

            if skip_count >= 5:
                return Response({
                    'error': 'Skip limit reached',
                    'message': 'Free users can only skip 5 times per hour.',
                    'upgrade': True
                }, status=status.HTTP_403_FORBIDDEN)

            recent_streams = PlayHistory.objects.filter(
                user=user,
                played_at__gte=one_hour_ago
            ).count()

            show_ad = recent_streams > 0 and recent_streams % 5 == 0
        else:
            show_ad = False

        song.stream_count += 1
        song.save(update_fields=['stream_count'])

        skipped = request.data.get('skipped', False)
        PlayHistory.objects.create(user=user, song=song, skipped=skipped)

        return Response({
            'song_id':      song.id,
            'title':        song.title,
            'artist':       song.artist.name,
            'audio_url':    song.audio_file_url,
            'stream_count': song.stream_count,
            'is_premium':   is_premium,
            'ad_required':  show_ad,
            'skip_allowed': is_premium,
        }, status=status.HTTP_200_OK)


class StreamHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        history = PlayHistory.objects.filter(
            user=request.user
        ).select_related('song__artist', 'song__album').order_by('-played_at')[:50]

        return Response({
            'history': PlayHistorySerializer(history, many=True).data
        }, status=status.HTTP_200_OK)


class SearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.query_params.get('q', '').strip()

        if not q:
            return Response({
                'query':   '',
                'songs':   [],
                'albums':  [],
                'artists': [],
            })

        cache_key = f'search_{q.lower()}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        songs = Song.objects.filter(
            Q(title__icontains=q) |
            Q(artist__name__icontains=q)
        ).select_related('artist', 'album', 'genre')[:10]

        albums = Album.objects.filter(
            Q(title__icontains=q) |
            Q(artist__name__icontains=q)
        )[:10]

        artists = Artist.objects.filter(name__icontains=q)[:10]

        data = {
            'query':   q,
            'songs':   SongSerializer(songs, many=True, context={'request': request}).data,
            'albums':  AlbumSerializer(albums, many=True, context={'request': request}).data,
            'artists': ArtistSerializer(artists, many=True, context={'request': request}).data,
        }
        cache.set(cache_key, data, timeout=60 * 5)  # cache for 5 minutes
        return Response(data)


class TrendingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cache_key = 'trending_songs'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        since = timezone.now() - timedelta(days=7)
        songs = Song.objects.filter(
            play_histories__played_at__gte=since
        ).annotate(
            recent_plays=Count('play_histories')
        ).order_by('-recent_plays').select_related('artist', 'album', 'genre')[:10]

        if songs.count() < 5:
            songs = Song.objects.select_related(
                'artist', 'album', 'genre'
            ).order_by('-stream_count')[:10]

        data = {
            'period': 'last_7_days',
            'songs':  SongSerializer(songs, many=True, context={'request': request}).data,
        }
        cache.set(cache_key, data, timeout=60 * 15)  # cache for 15 minutes
        return Response(data)


class TopArtistsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        top_artists = Artist.objects.annotate(
            total_streams=Count('songs__play_histories', distinct=True)
        ).order_by('-total_streams')[:10]

        return Response({
            'top_artists': ArtistSerializer(top_artists, many=True, context={'request': request}).data
        })


class NewReleasesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        thirty_days_ago = timezone.now() - timedelta(days=30)

        new_songs = Song.objects.filter(
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')[:10]

        new_albums = Album.objects.filter(
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')[:10]

        return Response({
            'new_songs':  SongSerializer(new_songs, many=True, context={'request': request}).data,
            'new_albums': AlbumSerializer(new_albums, many=True, context={'request': request}).data,
        })


class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        top_genres = PlayHistory.objects.filter(
            user=user
        ).values('song__genre__id').annotate(
            count=Count('song__genre__id')
        ).order_by('-count')[:5]

        genre_ids = [g['song__genre__id'] for g in top_genres if g['song__genre__id']]

        followed_artist_ids = Follow.objects.filter(
            user=user
        ).values_list('artist_id', flat=True)

        played_song_ids = PlayHistory.objects.filter(
            user=user
        ).values_list('song_id', flat=True)

        recommended = Song.objects.filter(
            Q(genre__id__in=genre_ids) |
            Q(artist_id__in=followed_artist_ids)
        ).exclude(
            id__in=played_song_ids
        ).annotate(
            stream_popularity=Count('play_histories')
        ).order_by('-stream_popularity').distinct()[:20]

        return Response({
            'based_on': 'listening history',
            'reason':   'Based on your top genres and followed artists',
            'songs':    SongSerializer(recommended, many=True, context={'request': request}).data
        })


class FollowArtistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, artist_id):
        try:
            artist = Artist.objects.get(id=artist_id)
        except Artist.DoesNotExist:
            return Response({'error': 'Artist not found'}, status=404)

        follow, created = Follow.objects.get_or_create(user=request.user, artist=artist)
        if not created:
            return Response({'message': 'Already following'}, status=400)
        return Response({'message': f'Now following {artist.name}'}, status=201)

    def delete(self, request, artist_id):
        try:
            follow = Follow.objects.get(user=request.user, artist_id=artist_id)
            follow.delete()
            return Response({'message': 'Unfollowed'}, status=204)
        except Follow.DoesNotExist:
            return Response({'error': 'Not following this artist'}, status=404)