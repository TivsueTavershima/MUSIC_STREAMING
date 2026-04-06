
from django.urls import path
from music.views import LikedSongsView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    UpgradeView,
    SubscriptionStatusView,
    ChangePasswordView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="auth-token-refresh"),

    path("profile/", ProfileView.as_view(), name="auth-profile"),
    path("change-password/", ChangePasswordView.as_view(), name="auth-change-password"),

    path("upgrade/", UpgradeView.as_view(), name="auth-upgrade"),
    path("subscription/status/",  SubscriptionStatusView.as_view(), name="auth-subscription-status"),
    path('liked-songs/', LikedSongsView.as_view(), name='liked-songs'),
]


