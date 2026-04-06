
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
    # LikeSongView,
    # LikedSongsView

)
from music.search import SearchView, TrendingView, RecommendationsView, NewReleasesView, TopArtistsView

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

        # Search and discovery
    path('search/',                  SearchView.as_view(),          name='search'),
    path('discover/trending/',       TrendingView.as_view(),        name='music-trending'),
    path('discover/new-releases/',   NewReleasesView.as_view(),     name='music-new-releases'),
    path('discover/recommendations/', RecommendationsView.as_view(), name='music-recommendations'),  # ← fixed 
]