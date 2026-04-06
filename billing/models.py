

from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class SubscriptionPlan(models.Model):
    class PlanType(models.TextChoices):
        FREE = "free", "Free"
        PREMIUM = "premium", "Premium"

    name = models.CharField(max_length=50)
    plan_type = models.CharField(max_length=10, choices=PlanType.choices, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    description = models.TextField(blank=True)
    duration_days = models.PositiveIntegerField(default=30, help_text="Subscription length in days")

    def __str__(self):
        return f"{self.name} (${self.price}/mo)"


class UserSubscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)
    expiry = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} — {self.plan.name}"

    @property
    def is_active(self):
        if self.status != self.Status.ACTIVE:
            return False
        if self.expiry and self.expiry < timezone.now():
            return False
        return True

    def set_expiry_from_plan(self):
        if self.plan.plan_type == SubscriptionPlan.PlanType.FREE:
            self.expiry = None
        else:
            self.expiry = timezone.now() + timedelta(days=self.plan.duration_days)