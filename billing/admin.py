
# Register your models here.
from django.contrib import admin
from django.utils import timezone
from .models import SubscriptionPlan, UserSubscription


# ── SubscriptionPlan Admin ────────────────────────────────────────────────────

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display   = ("name", "plan_type", "price", "duration_days", "description")
    list_filter    = ("plan_type",)
    search_fields  = ("name", "plan_type")
    ordering       = ("price",)


# ── UserSubscription Admin ────────────────────────────────────────────────────

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display   = ("user", "plan", "status", "is_active_display", "expiry", "started_at", "updated_at")
    list_filter    = ("status", "plan__plan_type")
    search_fields  = ("user__email", "user__username", "plan__name")
    ordering       = ("-started_at",)
    readonly_fields = ("started_at", "updated_at", "is_active_display")
    date_hierarchy  = "started_at"

    actions = ["mark_as_cancelled", "mark_as_expired", "renew_subscription"]

    # ── Custom display for is_active property ─────────────────────────────────

    @admin.display(boolean=True, description="Is Active")
    def is_active_display(self, obj):
        return obj.is_active

    # ── Custom Actions ────────────────────────────────────────────────────────

    @admin.action(description="Cancel selected subscriptions")
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status=UserSubscription.Status.CANCELLED)
        self.message_user(request, f"{updated} subscription(s) marked as cancelled.")

    @admin.action(description="Mark selected subscriptions as expired")
    def mark_as_expired(self, request, queryset):
        updated = queryset.update(
            status=UserSubscription.Status.EXPIRED,
            expiry=timezone.now(),
        )
        self.message_user(request, f"{updated} subscription(s) marked as expired.")

    @admin.action(description="Renew selected subscriptions")
    def renew_subscription(self, request, queryset):
        count = 0
        for subscription in queryset:
            subscription.set_expiry_from_plan()
            subscription.status = UserSubscription.Status.ACTIVE
            subscription.save()
            count += 1
        self.message_user(request, f"{count} subscription(s) successfully renewed.")
        
        
