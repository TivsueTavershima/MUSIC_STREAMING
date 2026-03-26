from django.contrib import admin
from .models import Stream, UserActivity, GenreStreamStat


# ── Stream Admin ──────────────────────────────────────────────────────────────

@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display  = ("song", "user", "streamed_at")
    list_filter   = ("streamed_at",)
    search_fields = ("song__title", "user__username", "user__email")
    ordering      = ("-streamed_at",)
    date_hierarchy = "streamed_at"
    readonly_fields = ("streamed_at",)


# ── UserActivity Admin ────────────────────────────────────────────────────────

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display  = ("user", "total_streams", "last_streamed_at")
    list_filter   = ("last_streamed_at",)
    search_fields = ("user__username", "user__email")
    ordering      = ("-total_streams",)
    readonly_fields = ("total_streams", "last_streamed_at")


# ── GenreStreamStat Admin ─────────────────────────────────────────────────────

@admin.register(GenreStreamStat)
class GenreStreamStatAdmin(admin.ModelAdmin):
    list_display  = ("genre", "date", "stream_count")
    list_filter   = ("date", "genre")
    search_fields = ("genre__name",)
    ordering      = ("-stream_count",)
    date_hierarchy = "date"
    readonly_fields = ("genre", "date", "stream_count")