


from django.urls import path
from .views import (
    GenreListCreateView,
    ArtistListCreateView,
    ArtistDetailView,
    ArtistAlbumsView,
    AlbumListCreateView,
    AlbumDetailView,
    SongListView,
    SongDetailView,
    SongUploadView,
)

urlpatterns = [
    # Genres
    path("genres/",                      GenreListCreateView.as_view(),  name="genre-list"),

    # Artists
    path("artists/",                     ArtistListCreateView.as_view(), name="artist-list"),
    path("artists/<int:pk>/",            ArtistDetailView.as_view(),     name="artist-detail"),
    path("artists/<int:pk>/albums/",     ArtistAlbumsView.as_view(),     name="artist-albums"),

    # Albums
    path("albums/",                      AlbumListCreateView.as_view(),  name="album-list"),
    path("albums/<int:pk>/",             AlbumDetailView.as_view(),      name="album-detail"),

    # Songs — exactly as shown in the spec
    path("songs/",                       SongListView.as_view(),         name="song-list"),
    path("songs/<int:pk>/",              SongDetailView.as_view(),       name="song-detail"),

    # Upload — Admin only
    path("upload/",                      SongUploadView.as_view(),       name="song-upload"),
]