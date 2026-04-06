from django.urls import path
from .views import (
    SearchView, TrendingView, TopArtistsView,StreamHistoryView,
    NewReleasesView, RecommendationView, FollowArtistView,StreamSongView
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView



urlpatterns = [
    path('history/', StreamHistoryView.as_view(), name='stream-history'),
    path('trending/',  TrendingView.as_view(), name='trending'),
    path('top-artists/', TopArtistsView.as_view(), name='top-artists'),
    path('new-releases/', NewReleasesView.as_view(), name='new-releases'),
    path('recommendations/', RecommendationView.as_view(), name='recommendations'),
    path('search/', SearchView.as_view(), name='search'),
    path('<int:song_id>/', StreamSongView.as_view(), name='stream-song'),  # last
    path('api/schema/',  SpectacularAPIView.as_view()),
    path('api/docs/',  SpectacularSwaggerView.as_view(url_name='schema'),  name='swagger-ui'),
    
]