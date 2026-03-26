from django.urls import path
from .views import StreamSongView

urlpatterns = [
    path('api/stream/<int:song_id>/', StreamSongView.as_view(), name='stream-song'),
]






from .views import (
    SearchView, TrendingView, TopArtistsView, 
    NewReleasesView, RecommendationView, FollowArtistView
)

urlpatterns = [
    # Search
    path('api/search/', SearchView.as_view(), name='search'),

    # Discover
    path('api/discover/trending/', TrendingView.as_view(), name='trending'),
    path('api/discover/top-artists/', TopArtistsView.as_view(), name='top-artists'),
    path('api/discover/new-releases/', NewReleasesView.as_view(), name='new-releases'),

    # Recommendations
    path('api/recommendations/', RecommendationView.as_view(), name='recommendations'),

    # Follow
    path('api/artists/<int:artist_id>/follow/', FollowArtistView.as_view(), name='follow-artist'),
]
# ```

# **Test in Postman:**
# ```
# # Search
# GET http://127.0.0.1:8000/api/search/?q=drake

# # Discover
# GET http://127.0.0.1:8000/api/discover/trending/
# GET http://127.0.0.1:8000/api/discover/top-artists/
# GET http://127.0.0.1:8000/api/discover/new-releases/

# # Recommendations (requires auth)
# GET http://127.0.0.1:8000/api/recommendations/
# Headers: Authorization: Bearer <your_token>

# # Follow artist
# POST http://127.0.0.1:8000/api/artists/1/follow/
# Headers: Authorization: Bearer <your_token>

# # Unfollow artist
# DELETE http://127.0.0.1:8000/api/artists/1/follow/
# Headers: Authorization: Bearer <your_token>








# ```

# **All available endpoints:**
# ```
# POST    /api/stream/1/      # stream a song
# ```

# **Test in Postman:**
# ```
# POST http://127.0.0.1:8000/api/stream/1/
# Headers: Authorization: Bearer <your_token>
# Body → raw JSON:
# {
#     "skipped": false
# }