   
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, UserProfileSerializer, ChangePasswordSerializer
from billing.models import SubscriptionPlan, UserSubscription
from billing.serializers import UserSubscriptionSerializer, UpgradeSerializer

User = get_user_model()




class RegisterView(generics.CreateAPIView):
    """POST /auth/register/"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserProfileSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """POST /auth/login/ — returns access + refresh JWT tokens"""
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    """POST /auth/logout/ — blacklist the refresh token"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data["refresh"])
            token.blacklist()
            return Response({"detail": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "Invalid or missing token."}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /auth/profile/"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UpgradeView(APIView):
    """POST /auth/upgrade/ — upgrade or downgrade subscription plan"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = UpgradeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan_type = serializer.validated_data["plan_type"]

        # Get or create the requested plan
        defaults = {
            "free": {"name": "Free", "price": 0, "duration_days": 0},
            "premium": {"name": "Premium", "price": 1600.0, "duration_days": 30},
        }
        plan, _ = SubscriptionPlan.objects.get_or_create(
            plan_type=plan_type,
            defaults=defaults[plan_type],
        )

        # Update or create the subscription
        sub, created = UserSubscription.objects.get_or_create(
            user=request.user,
            defaults={"plan": plan},
        )
        if not created:
            sub.plan = plan
            sub.status = UserSubscription.Status.ACTIVE

        sub.set_expiry_from_plan()
        sub.save()

        # Sync User.is_premium and subscription_expiry fields
        user = request.user
        user.is_premium = (plan_type == "premium")
        user.role = plan_type if plan_type in ("free", "premium") else user.role
        user.subscription_expiry = sub.expiry
        user.save(update_fields=["is_premium", "role", "subscription_expiry"])

        return Response({
            "detail": f"Successfully switched to {plan.name} plan.",
            "subscription": UserSubscriptionSerializer(sub).data,
        })


class SubscriptionStatusView(APIView):
    """GET /auth/subscription/status/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            sub = request.user.subscription
            return Response({
                "user": request.user.email,
                "role": request.user.role,
                "is_premium": request.user.is_premium,
                "subscription_expiry": request.user.subscription_expiry,
                "subscription": UserSubscriptionSerializer(sub).data,
            })
        except UserSubscription.DoesNotExist:
            return Response({
                "user": request.user.email,
                "role": request.user.role,
                "is_premium": False,
                "subscription_expiry": None,
                "subscription": None,
            })


class ChangePasswordView(APIView):
    """POST /auth/change-password/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"old_password": "Incorrect password."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Password updated."})