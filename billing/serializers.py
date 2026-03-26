# from rest_framework import serializers
# from .models import SubscriptionPlan


# class SubscriptionPlanSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SubscriptionPlan
#         fields = "__all__"



from rest_framework import serializers
from .models import SubscriptionPlan, UserSubscription


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ("id", "name", "plan_type", "price", "description", "duration_days")


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = UserSubscription
        fields = ("id", "plan", "status", "expiry", "started_at", "is_active", "days_remaining")

    def get_days_remaining(self, obj):
        if obj.expiry is None:
            return None
        from django.utils import timezone
        delta = obj.expiry - timezone.now()
        return max(0, delta.days)


class UpgradeSerializer(serializers.Serializer):
    plan_type = serializers.ChoiceField(choices=["free", "premium"])
    
    