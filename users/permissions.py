from rest_framework.permissions import BasePermission



class IsAdminUserRole(BasePermission):
    """Only admin role users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin_user


class IsFreeUser(BasePermission):
    """Only free tier users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "free"


class IsPremiumUser(BasePermission):
    """Only premium users with active subscription."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.subscription_is_active


class IsRegularUser(BasePermission):
    """Only non-admin users (free or premium)."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and not request.user.is_admin_user