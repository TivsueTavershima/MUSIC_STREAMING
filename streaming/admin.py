from django.contrib import admin
from .models import PlayHistory, Follow


# ── PlayHistory Admin ─────────────────────────────────────────────────────────

@admin.register(PlayHistory)
class PlayHistoryAdmin(admin.ModelAdmin):
    list_display    = ("user", "song", "played_at", "skipped")
    list_filter     = ("skipped", "played_at")
    search_fields   = ("user__email", "user__username", "song__title")
    ordering        = ("-played_at",)
    readonly_fields = ("played_at",)
    date_hierarchy  = "played_at"

    actions = ["mark_as_skipped", "mark_as_played"]

    # ── Custom Actions ────────────────────────────────────────────────────────

    @admin.action(description="Mark selected as skipped")
    def mark_as_skipped(self, request, queryset):
        updated = queryset.update(skipped=True)
        self.message_user(request, f"{updated} play history record(s) marked as skipped.")

    @admin.action(description="Mark selected as played")
    def mark_as_played(self, request, queryset):
        updated = queryset.update(skipped=False)
        self.message_user(request, f"{updated} play history record(s) marked as played.")


# ── Follow Admin ────────────────

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display    = ("user", "artist", "followed_at")
    list_filter     = ("followed_at",)
    search_fields   = ("user__email", "user__username", "artist__name")
    ordering        = ("-followed_at",)
    readonly_fields = ("followed_at",)