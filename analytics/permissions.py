
# ── Admin-only permission ─────────────────────────────────────────────────────

from users import permissions



class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_admin_user
        )