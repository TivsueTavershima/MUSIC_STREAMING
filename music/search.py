
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from music.models import Song, Artist, Album, Genre
from music.serializers import SongSerializer, ArtistSerializer, AlbumSerializer
from streaming.models import PlayHistory





class SearchView(APIView):
    """
    GET /search/?q=...
    Searches across songs, albums, and artists simultaneously.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        q = request.query_params.get("q", "").strip()

        if not q:
            return Response({
                "query":   "",
                "songs":   [],
                "albums":  [],
                "artists": [],
            })

        songs = Song.objects.filter(
            Q(title__icontains=q)
            | Q(artist__name__icontains=q)
            | Q(album__title__icontains=q)
            | Q(genre__name__icontains=q)
        ).select_related("artist", "album", "genre").distinct()[:10]

        albums = Album.objects.filter(
            Q(title__icontains=q)
            | Q(artist__name__icontains=q)
        ).select_related("artist", "genre").distinct()[:5]

        artists = Artist.objects.filter(
            name__icontains=q
        )[:5]

        return Response({
            "query":   q,
            "songs":   SongSerializer(songs,   many=True).data,
            "albums":  AlbumSerializer(albums, many=True).data,
            "artists": ArtistSerializer(artists, many=True).data,
        })


class TrendingView(APIView):
    """
    GET /discover/trending/
    Top 10 songs by stream count in the last 7 days.
    Falls back to all-time top if fewer than 5 results.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        since = timezone.now() - timedelta(days=7)

        songs = Song.objects.filter(
            play_histories__played_at__gte=since  # fixed
        ).annotate(
            recent_plays=Count("play_histories")  # fixed
        ).order_by("-recent_plays").select_related("artist", "album", "genre")[:10]

        if songs.count() < 5:
            songs = Song.objects.select_related(
                "artist", "album", "genre"
            ).order_by("-stream_count")[:10]

        return Response({
            "period": "last_7_days",
            "songs":  SongSerializer(songs, many=True).data,
        })


class TopArtistsView(APIView):
    """
    GET /discover/top-artists/
    Top 10 artists by total streams across all their songs.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        artists = Artist.objects.annotate(
            total_streams=Count("songs__play_histories", distinct=True)  # fixed
        ).order_by("-total_streams")[:10]

        data = ArtistSerializer(artists, many=True).data
        for i, artist in enumerate(artists):
            data[i]["total_streams"] = artist.total_streams

        return Response({
            "artists": data,
        })


class NewReleasesView(APIView):
    """
    GET /discover/new-releases/
    Songs added in the last 30 days, newest first.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        since = timezone.now() - timedelta(days=30)

        songs = Song.objects.filter(
            created_at__gte=since
        ).select_related("artist", "album", "genre").order_by("-created_at")[:20]

        return Response({
            "period": "last_30_days",
            "songs":  SongSerializer(songs, many=True).data,
        })


class RecommendationsView(APIView):
    """
    GET /discover/recommendations/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        history = (
            PlayHistory.objects
            .filter(user=user)
            .select_related("song__genre", "song__artist")
            [:50]
        )

        if not history.exists():
            songs = Song.objects.select_related(
                "artist", "album", "genre"
            ).order_by("-stream_count")[:10]

            return Response({
                "based_on": "trending",
                "reason":   "No listening history yet — showing top songs.",
                "songs":    SongSerializer(songs, many=True).data,
            })

        played_song_ids = [h.song_id for h in history]

        genre_ids = [h.song.genre_id for h in history if h.song.genre_id]
        top_genre_id = (
            max(set(genre_ids), key=genre_ids.count) if genre_ids else None
        )

        artist_ids = [h.song.artist_id for h in history if h.song.artist_id]
        top_artist_id = (
            max(set(artist_ids), key=artist_ids.count) if artist_ids else None
        )

        filters = Q()
        if top_genre_id:
            filters |= Q(genre_id=top_genre_id)
        if top_artist_id:
            filters |= Q(artist_id=top_artist_id)

        songs = Song.objects.filter(filters).exclude(
            id__in=played_song_ids
        ).select_related("artist", "album", "genre").order_by("-stream_count")[:10]

        if not songs.exists():
            songs = Song.objects.select_related(
                "artist", "album", "genre"
            ).order_by("-stream_count")[:10]

        reasons = []
        if top_genre_id:
            try:
                genre_name = Genre.objects.get(pk=top_genre_id).name
                reasons.append(f"genre: {genre_name}")
            except Genre.DoesNotExist:
                pass
        if top_artist_id:
            try:
                artist_name = Artist.objects.get(pk=top_artist_id).name
                reasons.append(f"artist: {artist_name}")
            except Artist.DoesNotExist:
                pass

        return Response({
            "based_on": "history",
            "reason":   f"Based on your listening history ({', '.join(reasons)}).",
            "songs":    SongSerializer(songs, many=True).data,
        })