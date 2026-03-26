# from django.urls import path
# from rest_framework_simplejwt.views import TokenObtainPairView
# from users.views import RegisterView, SubscriptionStatusView, UpgradeSubscriptionView




# urlpatterns = [
#     path("register/", RegisterView.as_view(), name="register"),
#     path("login/", TokenObtainPairView.as_view(), name="login"),
#     path("upgrade/", UpgradeSubscriptionView.as_view(), name="upgrade"),
#     path("subscription/status/", SubscriptionStatusView.as_view(), name="subscription-status")
# ]

from django.urls import path
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
    # ── Auth ──────────────────────────────────────────────────
    path("register/",             RegisterView.as_view(),           name="auth-register"),
    path("login/",                LoginView.as_view(),              name="auth-login"),
    path("logout/",               LogoutView.as_view(),             name="auth-logout"),
    path("token/refresh/",        TokenRefreshView.as_view(),       name="auth-token-refresh"),

    # ── Profile ───────────────────────────────────────────────
    path("profile/",              ProfileView.as_view(),            name="auth-profile"),
    path("change-password/",      ChangePasswordView.as_view(),     name="auth-change-password"),

    # ── Subscription (as shown in Milestone 2) ────────────────
    path("upgrade/",              UpgradeView.as_view(),            name="auth-upgrade"),
    path("subscription/status/",  SubscriptionStatusView.as_view(), name="auth-subscription-status"),
]