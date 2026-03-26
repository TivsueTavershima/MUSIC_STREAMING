from django.contrib import admin
from .models import Playlist, PlaylistItem, LikedSongs


# ── PlaylistItem Inline ───────────────────────────────────────────────────────

class PlaylistItemInline(admin.TabularInline):
    model         = PlaylistItem
    extra         = 0
    fields        = ("song", "order", "added_at")
    readonly_fields = ("added_at",)
    ordering      = ("order", "added_at")


# ── Playlist Admin ────────────────────────────────────────────────────────────

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display    = ("name", "user", "song_count", "created_at", "updated_at")
    list_filter     = ("created_at", "updated_at")
    search_fields   = ("name", "user__email", "user__username")
    ordering        = ("-updated_at",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy  = "created_at"
    inlines         = [PlaylistItemInline]

    @admin.display(description="Songs")
    def song_count(self, obj):
        return obj.items.count()


# ── PlaylistItem Admin ────────────────────────────────────────────────────────

@admin.register(PlaylistItem)
class PlaylistItemAdmin(admin.ModelAdmin):
    list_display    = ("playlist", "song", "order", "added_at")
    list_filter     = ("added_at",)
    search_fields   = ("playlist__name", "song__title", "playlist__user__email")
    ordering        = ("order", "added_at")
    readonly_fields = ("added_at",)


# ── LikedSongs Admin ──────────────────────────────────────────────────────────

@admin.register(LikedSongs)
class LikedSongsAdmin(admin.ModelAdmin):
    list_display    = ("user", "song", "liked_at")
    list_filter     = ("liked_at",)
    search_fields   = ("user__email", "user__username", "song__title")
    ordering        = ("-liked_at",)
    readonly_fields = ("liked_at",)
    date_hierarchy  = "liked_at"