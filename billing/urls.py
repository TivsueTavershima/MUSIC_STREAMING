# from django.contrib import admin
# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from music.views import GenreViewSet, ArtistViewSet, AlbumViewSet, SongViewSet
# from playlists.views import PlaylistViewSet, PlaylistItemViewSet
# from streaming.views import PlayHistoryViewSet, StreamingViewSet
# from billing.views import SubscriptionPlanViewSet

# router = DefaultRouter()

# router.register(r"genres", GenreViewSet)
# router.register(r"artists", ArtistViewSet)
# router.register(r"albums", AlbumViewSet)
# router.register(r"songs", SongViewSet)
# router.register(r"playlists", PlaylistViewSet)
# router.register(r"playlist-items", PlaylistItemViewSet)
# router.register(r"history", PlayHistoryViewSet)
# router.register(r"stream", StreamingViewSet)
# router.register(r"plans", SubscriptionPlanViewSet)

# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path("api/", include(router.urls)),
# ]



# # billing/urls.py
# from django.urls import path

# from billing.views import UpgradeSubscriptionView




# urlpatterns = [
  
# path("auth/upgrade/", UpgradeSubscriptionView.as_view(), name="upgrade")
# ]



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import SubscriptionPlan
from .serializers import SubscriptionPlanSerializer
from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription

from django.urls import path
from .views import PlanListView, UpgradeSubscriptionView

 

urlpatterns = [
    path("plans/", PlanListView.as_view(), name="billing-plans"),
    path("auth/upgrade/", UpgradeSubscriptionView.as_view(), name="upgrade")
]


