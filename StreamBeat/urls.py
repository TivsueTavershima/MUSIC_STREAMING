"""
URL configuration for StreamBeat project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView
# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerUIView

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('auth/', include('users.urls')),
    
#     path('auth/login/', TokenObtainPairView.as_view()),
#     path('api/analytics/', include('analytics.urls')),
#     path("billing/", include("billing.urls")),
#     path("music/", include("music.urls")),
#     path("playlists/", include("playlists.urls")),
#     path("stream/", include("streaming.urls")),
#     path("users/", include("users.urls")),
#     path('stream/', include('streaming.urls')),
#     path('', include('streaming.urls')),
    
# ]






# urlpatterns = [
#     # path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
#     # path('api/docs/', SpectacularSwaggerUIView.as_view(url_name='schema'), name='swagger-ui'),
#     # path('django-admin/', admin.site.urls),          # moved to avoid conflict
#     # path('admin/analytics/', include('analytics.urls')),  # /admin/analytics/streams/ etc.

#     # path('auth/', include('users.urls')),             # register, login, profile, etc.
#     # path('auth/login/', TokenObtainPairView.as_view()),

#     # path('billing/', include('billing.urls')),        # /billing/plans/
#     # path('music/', include('music.urls')),            # /music/songs/, /music/like/ etc.
#     # path('playlists/', include('playlists.urls')),    # /playlists/my/, /playlists/create/ etc.
#     # path('users/', include('users.urls')),            # /users/liked-songs/
#     # path('stream/', include('streaming.urls')),       # /stream/<id>/, /stream/history/
#     # # path('search/', SearchView.as_view(), name='search'),         # /search/?q=
#     # path('discover/', include('streaming.urls')),    # /discover/trending/ etc.
# ]



from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from streaming.views import SearchView
from music.search import SearchView, TrendingView, RecommendationsView, NewReleasesView, TopArtistsView

# urlpatterns = [
#     path('admin/',           admin.site.urls),
#     path('admin/analytics/', include('analytics.urls')),
#     path('auth/',            include('users.urls')),
#     path('auth/login/',      TokenObtainPairView.as_view()),
#     path('billing/',         include('billing.urls')),
#     path('music/',           include('music.urls')),
#     path('playlists/',       include('playlists.urls')),
#     path('users/',           include('users.urls')),
#     path('stream/',          include('streaming.urls')),
#     # path('', include('music.discovery_urls')), # search/discover routes at root
#     # path('search/',          SearchView.as_view(),        name='search'),
#     path('',        include('music.urls')),
#     # path('api/schema/',      SpectacularAPIView.as_view(),                       name='schema'),
#     # path('api/docs/',        SpectacularSwaggerView.as_view(url_name='schema'),  name='swagger-ui'),
# ]



# urlpatterns = [
#     path('admin/',           admin.site.urls),
#     path('admin/analytics/', include('analytics.urls')),
#     path('auth/',            include('users.urls')),
#     path('billing/',         include('billing.urls')),
#     path('music/',           include('music.urls')),
#     path('playlists/',       include('playlists.urls')),
#     path('users/',           include('users.urls')),  # ← only liked-songs here
#     path('stream/',          include('streaming.urls')),
#     path('',                 include('music.urls')),
    
# ]



# main urls.py
urlpatterns = [
    path('django-admin/',           admin.site.urls),
    path('admin/analytics/', include('analytics.urls')),
    path('auth/',            include('users.urls')),
    path('billing/',         include('billing.urls')),
    path('music/',           include('music.urls')),      # ← keep only this
    path('playlists/',       include('playlists.urls')),
    path('users/',           include('users.urls')),
    path('stream/',          include('streaming.urls')),
    path('',                 include('music.urls')),  # ← only search/discover
]