from django.urls import path
from .views import (
    PlaylistCreateView,
    PlaylistAddSongView,
    MyPlaylistsView,
    LikeSongView,
    StreamSongView
)

urlpatterns = [
    # POST /playlists/create/
    path("create/",           PlaylistCreateView.as_view(),   name="playlist-create"),

    # POST /playlists/<id>/add/
    path("<int:pk>/add/",     PlaylistAddSongView.as_view(),  name="playlist-add-song"),

    # GET  /playlists/my/
    path("my/",               MyPlaylistsView.as_view(),      name="my-playlists"),
    
    path('music/like/<int:song_id>/', LikeSongView.as_view(), name='like_song'),
    
     # POST /stream/<song_id>/
    path("<int:song_id>/", StreamSongView.as_view(),  name="stream-song"),

]