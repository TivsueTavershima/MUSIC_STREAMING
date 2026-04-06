from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Playlist, PlaylistItem, LikedSongs
from .serializers import (
    PlaylistSerializer,
    PlaylistCreateSerializer,
    AddSongSerializer,
    # LikedSongsSerializer,
)
from music.models import Song      
from rest_framework import generics, permissions, status
from django.db.models import F
from .serializers import PlayHistorySerializer
from music.models import Song







class PlaylistCreateView(generics.CreateAPIView):
    """
    POST /playlists/create/
    Create a new playlist for the authenticated user.
    Body: { "name": "...", "description": "..." }
    """
    serializer_class = PlaylistCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        playlist = serializer.save()
        return Response(
            PlaylistSerializer(playlist).data,
            status=status.HTTP_201_CREATED,
        )


class PlaylistAddSongView(APIView):
    """
    POST /playlists/<id>/add/
    Add a song to the playlist.
    Body: { "song_id": <int>, "order": <int> (optional) }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        playlist = get_object_or_404(Playlist, pk=pk, user=request.user)

        serializer = AddSongSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        song = get_object_or_404(Song, pk=serializer.validated_data["song_id"])
        order = serializer.validated_data.get("order", 0)

        item, created = PlaylistItem.objects.get_or_create(
            playlist=playlist,
            song=song,
            defaults={"order": order},
        )

        if not created:
            return Response(
                {"detail": "Song is already in this playlist."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "detail": "Song added to playlist.",
                "playlist_id": playlist.id,
                "song_id": song.id,
                "order": item.order,
            },
            status=status.HTTP_201_CREATED,
        )

class MyPlaylistsView(generics.ListAPIView):
    """
    GET /playlists/my/
    Return all playlists that belong to the authenticated user.
    """
    serializer_class = PlaylistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Playlist.objects
            .filter(user=self.request.user)
            .select_related("user")
            .prefetch_related("songs")
            [:50]
        )

        

# ── Streaming restriction constants ───────────────────────────────────────────
FREE_AD_EVERY_N_SONGS  = 5   # free users see an ad every 5 streams
FREE_SKIP_LIMIT        = 6   # free users can only skip 6 times per session (last 60 min)


def _get_free_user_session_count(user):
    """
    Count how many songs the user has streamed in the current session window.
    We use all-time count for ad frequency (every 5th stream gets an ad),
    and the last 60 minutes for skip limit tracking.
    """
    from django.utils import timezone
    from datetime import timedelta
    since = timezone.now() - timedelta(hours=1)
    return Playlist.objects.filter(user=user, played_at__gte=since).count()


def _check_subscription(user):
    """
    Returns a dict describing what the user is allowed to do.

    Free users:
      - ad_required = True every 5 streams (based on total stream count mod 5)
      - skip_allowed = False once they've hit FREE_SKIP_LIMIT in the last hour

    Premium users:
      - ad_required  = False  (never)
      - skip_allowed = True   (always)
    """
    is_premium = user.is_premium

    if is_premium:
        return {
            "is_premium":   True,
            "ad_required":  False,
            "skip_allowed": True,
            "message":      "Premium — unlimited streaming, no ads.",
        }

    # Free user — count total historical plays to decide if ad is due
    total_plays = Playlist.objects.filter(user=user).count()
    ad_required = (total_plays > 0) and (total_plays % FREE_AD_EVERY_N_SONGS == 0)

    # Skip limit: check streams in the last hour
    session_count = _get_free_user_session_count(user)
    skip_allowed  = session_count < FREE_SKIP_LIMIT

    msg_parts = []
    if ad_required:
        msg_parts.append("Ad playing before this track.")
    if not skip_allowed:
        msg_parts.append(f"Skip limit of {FREE_SKIP_LIMIT} reached for this hour.")

    return {
        "is_premium":   False,
        "ad_required":  ad_required,
        "skip_allowed": skip_allowed,
        "message":      " ".join(msg_parts),
    }


# ── POST /stream/<song_id>/ ───────────────────────────────────────────────────

class StreamSongView(APIView):
    """
    POST /stream/<song_id>/

    1. Checks subscription level → determines ads / skip limits
    2. Atomically increments stream_count on the Song
    3. Stores a PlayHistory record
    4. Returns audio URL + restriction flags
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, song_id):
        song = get_object_or_404(Song, pk=song_id)

        # 1. Check subscription level
        restrictions = _check_subscription(request.user)

        # 2. Atomically increment stream count (no race conditions)
        Song.objects.filter(pk=song_id).update(stream_count=F("stream_count") + 1)
        song.refresh_from_db()

        # 3. Store play history
        Playlist.objects.create(user=request.user, song=song)

        # 4. Resolve the audio URL
        audio_url = (
            song.audio_file_url
            or (song.audio_file.url if song.audio_file else "")
        )

        return Response(
            {
                "song_id":      song.id,
                "title":        song.title,
                "artist":       song.artist.name,
                "audio_url":    audio_url,
                "stream_count": song.stream_count,
                **restrictions,
            },
            status=status.HTTP_200_OK,
        )

