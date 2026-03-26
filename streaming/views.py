from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from music.models import Song
from music.serializers import AlbumSerializer, ArtistSerializer
from .models import Follow, PlayHistory  
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Song, PlayHistory
from .serializers import SongSerializer
      
from django.db.models import Count
from datetime import timedelta
from django.utils import timezone

        
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.db.models import Q
from .models import Song, Artist
from music.models import Album







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

        # --- Streaming restrictions for free users ---
        if not is_premium:
            # Check skip limit (max 6 skips per hour)
            one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
            skip_count = PlayHistory.objects.filter(
                user=user,
                played_at__gte=one_hour_ago,
                skipped=True
            ).count()

            if skip_count >= 6:
                return Response({
                    'error': 'Skip limit reached',
                    'message': 'Free users can only skip 6 times per hour.',
                    'upgrade': True
                }, status=status.HTTP_403_FORBIDDEN)

            # Check if ad is needed (every 5 songs)
            recent_streams = PlayHistory.objects.filter(
                user=user,
                played_at__gte=one_hour_ago
            ).count()

            show_ad = recent_streams > 0 and recent_streams % 5 == 0

        else:
            show_ad = False

        # --- Increase stream count ---
        song.stream_count += 1
        song.save(update_fields=['stream_count'])

        # --- Store play history ---
        skipped = request.data.get('skipped', False)
        PlayHistory.objects.create(
            user=user,
            song=song,
            skipped=skipped
        )

        return Response({
            'message': 'Stream recorded',
            'song': SongSerializer(song, context={'request': request}).data,
            'show_ad': show_ad,
            'is_premium': is_premium,
            'stream_count': song.stream_count
        }, status=status.HTTP_200_OK)
        
        



class SearchView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        query = request.query_params.get('q', '')

        if not query:
            return Response({'error': 'Query parameter q is required'}, status=400)

        songs = Song.objects.filter(
            Q(title__icontains=query) |
            Q(artist__name__icontains=query)
        )[:10]

        albums = Album.objects.filter(
            Q(title__icontains=query) |
            Q(artist__name__icontains=query)
        )[:10]

        artists = Artist.objects.filter(
            name__icontains=query
        )[:10]

        return Response({
            'songs': SongSerializer(songs, many=True, context={'request': request}).data,
            'albums': AlbumSerializer(albums, many=True, context={'request': request}).data,
            'artists': ArtistSerializer(artists, many=True, context={'request': request}).data,
        })
        
        
        
      
  


class TrendingView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        # most streamed songs in last 7 days
        seven_days_ago = timezone.now() - timedelta(days=7)
        trending_songs = Song.objects.filter(
            play_histories__played_at__gte=seven_days_ago
        ).annotate(
            recent_streams=Count('play_histories')
        ).order_by('-recent_streams')[:20]

        return Response({
            'trending': SongSerializer(trending_songs, many=True, context={'request': request}).data
        })


class TopArtistsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        # artists with most streams
        top_artists = Artist.objects.annotate(
            total_streams=Count('songs__play_histories')
        ).order_by('-total_streams')[:10]

        return Response({
            'top_artists': ArtistSerializer(top_artists, many=True, context={'request': request}).data
        })


class NewReleasesView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        # songs and albums released in last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)

        new_songs = Song.objects.filter(
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')[:10]

        new_albums = Album.objects.filter(
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')[:10]

        return Response({
            'new_songs': SongSerializer(new_songs, many=True, context={'request': request}).data,
            'new_albums': AlbumSerializer(new_albums, many=True, context={'request': request}).data,
        })
        
        
class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # --- genres user listens to most ---
        top_genres = PlayHistory.objects.filter(
            user=user
        ).values(
            'song__genres__id'
        ).annotate(
            count=Count('song__genres__id')
        ).order_by('-count')[:5]

        genre_ids = [g['song__genres__id'] for g in top_genres if g['song__genres__id']]

        # --- artists user follows ---
        followed_artist_ids = Follow.objects.filter(
            user=user
        ).values_list('artist_id', flat=True)

        # --- songs already played ---
        played_song_ids = PlayHistory.objects.filter(
            user=user
        ).values_list('song_id', flat=True)

        # --- recommend songs based on genres and followed artists ---
        recommended = Song.objects.filter(
            Q(genres__id__in=genre_ids) |
            Q(artist_id__in=followed_artist_ids)
        ).exclude(
            id__in=played_song_ids  # exclude already played songs
        ).annotate(
            stream_popularity=Count('play_histories')
        ).order_by('-stream_popularity').distinct()[:20]

        return Response({
            'recommended': SongSerializer(recommended, many=True, context={'request': request}).data
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