
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


