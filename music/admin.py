from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Genre, Artist, Album, Song


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "artist", "genre", "release_date")
    list_filter = ("genre",)
    search_fields = ("title", "artist__name")


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "artist", "album", "genre",
                    "duration", "stream_count", "uploaded_by", "created_at")
    list_filter = ("genre",)
    search_fields = ("title", "artist__name", "album__title")
    readonly_fields = ("stream_count", "created_at")