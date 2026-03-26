
# from rest_framework import serializers
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = [
#             'email',
#             'username',
#             'password',
#             'role'
#         ]

#     def create(self, validated_data):
#         password = validated_data.pop('password')
#         user = User(**validated_data)
#         user.set_password(password)  # 🔥 hashes password
#         user.save()
#         return user
    
#     def create_superuser(self, email, password, extra_fields):
#         extra_fields.setdefault(is_staff=True)
#         extra_fields.setdefault(is_superuser=True)
#         return self.create_user(self, email, password, extra_fields)



from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label="Confirm password")

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password2")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)

        # Auto-create free subscription on register
        from billing.models import SubscriptionPlan, UserSubscription
        free_plan, _ = SubscriptionPlan.objects.get_or_create(
            plan_type=SubscriptionPlan.PlanType.FREE,
            defaults={"name": "Free", "price": 0, "duration_days": 0},
        )
        sub = UserSubscription(user=user, plan=free_plan)
        sub.set_expiry_from_plan()
        sub.save()

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    subscription_plan = serializers.SerializerMethodField()
    subscription_expiry = serializers.DateTimeField(read_only=True)
    subscription_active = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id", "username", "email", "role", "is_premium",
            "subscription_expiry", "subscription_plan", "subscription_active",
            "date_joined",
        )
        read_only_fields = ("id", "email", "role", "is_premium",
                            "subscription_expiry", "date_joined")

    def get_subscription_plan(self, obj):
        try:
            return obj.subscription.plan.name
        except Exception:
            return "Free"

    def get_subscription_active(self, obj):
        return obj.subscription_is_active


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])