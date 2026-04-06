
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from rest_framework import permissions
from billing.serializers import SubscriptionPlanSerializer
from .models import SubscriptionPlan
from .models import UserSubscription

class UpgradeSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        plan = SubscriptionPlan.objects.get(name="PREMIUM")
        expiry = timezone.now() + timedelta(days=30)

        user.is_premium = True
        user.subscription_expiry = expiry
        user.save()

        UserSubscription.objects.create(
            user=user,
            plan=plan,
            expiry_date=expiry
        )

        return Response({
            "message": "Successfully upgraded to PREMIUM",
            "expiry": expiry
        })
        

class PlanListView(APIView):
    """GET /billing/plans/ — public list of all available plans"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        plans = SubscriptionPlan.objects.all()
        return Response(SubscriptionPlanSerializer(plans, many=True).data)
