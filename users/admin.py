    
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from .models import User


# ── User Admin ────────────────────────────────────────────────────────────────

@admin.register(User)
class UserAdmin(BaseUserAdmin):

    # ── Custom Display ────────────────────────────────────────────────────────

    @admin.display(boolean=True, description="Subscription Active")
    def subscription_is_active_display(self, obj):
        return obj.subscription_is_active

    # ── List Display ──────────────────────────────────────────────────────────

    list_display    = (
        "email", "username", "role", "is_premium",
        "subscription_is_active_display", "subscription_expiry", "is_active", "is_staff"
    )
    list_filter     = ("role", "is_premium", "is_active", "is_staff")
    search_fields   = ("email", "username")
    ordering        = ("email",)
    readonly_fields = ("last_login", "date_joined", "subscription_is_active_display")

    fieldsets = (
        ("Account Info", {
            "fields": ("email", "username", "password")
        }),
        ("Role & Subscription", {
            "fields": ("role", "is_premium", "subscription_expiry", "subscription_is_active_display")
        }),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        ("Important Dates", {
            "fields": ("last_login", "date_joined")
        }),
    )

    add_fieldsets = (
        ("Create New User", {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2", "role", "is_premium")
        }),
    )

    actions = [
        "make_premium",
        "revoke_premium",
        "make_admin",
        "make_free",
    ]

    # ── Custom Actions ────────────────────────────────────────────────────────

    @admin.action(description="Grant premium to selected users")
    def make_premium(self, request, queryset):
        updated = queryset.update(
            is_premium=True,
            role=User.Role.PREMIUM,
            subscription_expiry=timezone.now() + timezone.timedelta(days=30),
        )
        self.message_user(request, f"{updated} user(s) upgraded to premium.")

    @admin.action(description="Revoke premium from selected users")
    def revoke_premium(self, request, queryset):
        updated = queryset.update(
            is_premium=False,
            role=User.Role.FREE,
            subscription_expiry=None,
        )
        self.message_user(request, f"{updated} user(s) revoked from premium.")

    @admin.action(description="Make selected users admin")
    def make_admin(self, request, queryset):
        updated = queryset.update(
            role=User.Role.ADMIN,
            is_staff=True,
        )
        self.message_user(request, f"{updated} user(s) granted admin role.")

    @admin.action(description="Downgrade selected users to free")
    def make_free(self, request, queryset):
        updated = queryset.update(
            role=User.Role.FREE,
            is_premium=False,
            subscription_expiry=None,
        )
        self.message_user(request, f"{updated} user(s) downgraded to free.")