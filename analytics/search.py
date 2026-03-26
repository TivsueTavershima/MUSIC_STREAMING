
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from music.models import Song, Artist, Album, Genre
from music.serializers import SongSerializer, ArtistSerializer, AlbumSerializer
from streaming.models import PlayHistory


# ── /search/?q=... ────────────────────────────────────────────────────────────

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


# ── /discover/trending/ ───────────────────────────────────────────────────────

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
            play_history__played_at__gte=since
        ).annotate(
            recent_plays=Count("play_history")
        ).order_by("-recent_plays").select_related("artist", "album", "genre")[:10]

        # Cold start fallback — not enough recent data
        if songs.count() < 5:
            songs = Song.objects.select_related(
                "artist", "album", "genre"
            ).order_by("-stream_count")[:10]

        return Response({
            "period": "last_7_days",
            "songs":  SongSerializer(songs, many=True).data,
        })


# ── /discover/top-artists/ ────────────────────────────────────────────────────

class TopArtistsView(APIView):
    """
    GET /discover/top-artists/
    Top 10 artists by total streams across all their songs.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        artists = Artist.objects.annotate(
            total_streams=Count("songs__play_history")
        ).order_by("-total_streams")[:10]

        data = ArtistSerializer(artists, many=True).data
        # Attach total_streams to each artist in the response
        for i, artist in enumerate(artists):
            data[i]["total_streams"] = artist.total_streams

        return Response({
            "artists": data,
        })


# ── /discover/new-releases/ ───────────────────────────────────────────────────

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


# ── /discover/recommendations/ ────────────────────────────────────────────────

class RecommendationsView(APIView):
    """
    GET /discover/recommendations/

    Recommendation logic based on:
      1. Most played songs  → find genres + artists from top plays
      2. Genres user listens to → find more songs in those genres
      3. Artists user follows (most played) → find more songs by those artists

    Cold start (no history) → fall back to trending.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # Fetch the user's top 50 play history records
        history = (
            PlayHistory.objects
            .filter(user=user)
            .select_related("song__genre", "song__artist")
            [:50]
        )

        # Cold start — user has no history yet
        if not history.exists():
            songs = Song.objects.select_related(
                "artist", "album", "genre"
            ).order_by("-stream_count")[:10]

            return Response({
                "based_on": "trending",
                "reason":   "No listening history yet — showing top songs.",
                "songs":    SongSerializer(songs, many=True).data,
            })

        # ── 1. Most played songs ───────────────────────────────
        played_song_ids = [h.song_id for h in history]

        # ── 2. Genres user listens to ─────────────────────────
        genre_ids = [h.song.genre_id for h in history if h.song.genre_id]
        top_genre_id = (
            max(set(genre_ids), key=genre_ids.count) if genre_ids else None
        )

        # ── 3. Artists user follows (most played) ─────────────
        artist_ids = [h.song.artist_id for h in history if h.song.artist_id]
        top_artist_id = (
            max(set(artist_ids), key=artist_ids.count) if artist_ids else None
        )

        # Build recommendation queryset — exclude already played songs
        filters = Q()
        if top_genre_id:
            filters |= Q(genre_id=top_genre_id)
        if top_artist_id:
            filters |= Q(artist_id=top_artist_id)

        songs = Song.objects.filter(filters).exclude(
            id__in=played_song_ids
        ).select_related("artist", "album", "genre").order_by("-stream_count")[:10]

        # If still empty, fall back to top songs regardless of played status
        if not songs.exists():
            songs = Song.objects.select_related(
                "artist", "album", "genre"
            ).order_by("-stream_count")[:10]

        # Build a human-readable reason
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