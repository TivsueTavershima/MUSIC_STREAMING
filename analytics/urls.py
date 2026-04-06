from django.urls import path
from .views import (
    StreamStatsView,
    MostStreamedSongsView,
    MostActiveUsersView,
    MostPlayedGenresView,
    TopArtistsView,
)


urlpatterns = [
    # Daily/weekly/monthly stream totals
    path("streams/",     StreamStatsView.as_view(),       name="analytics-streams"),

    # Most-streamed songs
    path("songs/",       MostStreamedSongsView.as_view(), name="analytics-songs"),

    # Most active users
    path("users/",       MostActiveUsersView.as_view(),   name="analytics-users"),

    # Most-played genres
    path("genres/",      MostPlayedGenresView.as_view(),  name="analytics-genres"),

    # Top artists
    path("top-artists/", TopArtistsView.as_view(),        name="analytics-top-artists"),
    
]