       
from rest_framework import generics, permissions, filters, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from music.permission import IsAdminOrReadOnly

from .models import Genre, Artist, Album, Song
from .serializers import (
    GenreSerializer,
    ArtistSerializer,
    AlbumSerializer,
    SongSerializer,
    SongUploadSerializer,
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




