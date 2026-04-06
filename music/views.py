       
from rest_framework import generics, permissions, filters, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from music.permission import IsAdminOrReadOnly
from django.shortcuts import get_object_or_404

from .models import Genre, Artist, Album, Song
from .serializers import (
    GenreSerializer,
    ArtistSerializer,
    AlbumSerializer,
    SongSerializer,
    SongUploadSerializer,
)

from playlists.models import Playlist, PlaylistItem, LikedSongs
from playlists.serializers import (
    PlaylistSerializer,
    PlaylistCreateSerializer,
    AddSongSerializer,
    LikedSongsSerializer,
)

# ── Genre ─────────────────────────────────────────────────────────────────────

class GenreListCreateView(generics.ListCreateAPIView):
    """GET /music/genres/  |  POST /music/genres/ (admin)"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]


# ── Artist ────────────────────────────────────────────────────────────────────

class ArtistListCreateView(generics.ListCreateAPIView):
    """GET /music/artists/  |  POST /music/artists/ (admin)"""
    queryset = Artist.objects.all().order_by("name")
    serializer_class = ArtistSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class ArtistDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET /music/artists/<id>/  |  PATCH/DELETE (admin)"""
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [IsAdminOrReadOnly]


class ArtistAlbumsView(generics.ListAPIView):
    """GET /music/artists/<id>/albums/"""
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Album.objects.filter(
            artist_id=self.kwargs["pk"]
        ).select_related("artist", "genre")


# ── Album ─────────────────────────────────────────────────────────────────────

class AlbumListCreateView(generics.ListCreateAPIView):
    """GET /music/albums/  |  POST /music/albums/ (admin)"""
    queryset = Album.objects.select_related("artist", "genre").all()
    serializer_class = AlbumSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "artist__name"]


class AlbumDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET /music/albums/<id>/  |  PATCH/DELETE (admin)"""
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [IsAdminOrReadOnly]


# ── Song ──────────────────────────────────────────────────────────────────────

class SongListView(generics.ListAPIView):
    """GET /music/songs/"""
    queryset = Song.objects.select_related(
        "artist", "album", "genre", "uploaded_by"
    ).all()
    serializer_class = SongSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "artist__name", "album__title", "genre__name"]
    ordering_fields = ["created_at", "stream_count", "title", "duration"]
    ordering = ["-created_at"]


class SongDetailView(generics.RetrieveAPIView):
    """GET /music/songs/<id>/"""
    queryset = Song.objects.select_related("artist", "album", "genre").all()
    serializer_class = SongSerializer
    permission_classes = [permissions.IsAuthenticated]


class SongUploadView(generics.CreateAPIView):
    """POST /music/upload/ — Admin only"""
    serializer_class = SongUploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if not self.request.user.is_admin_user:
            raise PermissionDenied("Only admins can upload music.")
        serializer.save(uploaded_by=self.request.user)





class LikedSongsView(generics.ListAPIView):
    """
    GET /users/liked-songs/
    Return all songs the authenticated user has liked.
    """
    serializer_class = LikedSongsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            LikedSongs.objects
            .filter(user=self.request.user)
            .select_related("song__artist", "song__album")
        )


class LikeSongView(APIView):
    """
    POST /music/like/<song_id>/
    Toggle like on a song.
    - First call  → likes the song   (201)
    - Second call → unlikes the song (200)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, song_id):
        song = get_object_or_404(Song, pk=song_id)

        liked, created = LikedSongs.objects.get_or_create(
            user=request.user,
            song=song,
        )

        if not created:
            liked.delete()
            return Response(
                {"detail": "Song unliked.", "liked": False, "song_id": song.id},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": "Song liked.", "liked": True, "song_id": song.id},
            status=status.HTTP_201_CREATED,
        )
        