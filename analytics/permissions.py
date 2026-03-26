
# ── Admin-only permission ─────────────────────────────────────────────────────

from users import permissions


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_admin_user
        )

def streams_over_time_chart(play_history_queryset):
    raise NotImplementedError