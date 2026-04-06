from rest_framework import serializers
from .models import Genre, Artist, Album, Song
from rest_framework import serializers
from .models import Genre, Artist, Album, Song


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name", "description")


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ("id", "name", "bio", "image", "created_at")
        read_only_fields = ("created_at",)


class AlbumSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source="artist.name", read_only=True)
    genre_name = serializers.CharField(source="genre.name", read_only=True, default=None)

    class Meta:
        model = Album
        fields = (
            "id", "title", "artist", "artist_name",
            "genre", "genre_name", "cover_image",
            "release_date", "created_at",
        )
        read_only_fields = ("created_at",)


class SongSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source="artist.name", read_only=True)
    album_title = serializers.CharField(source="album.title", read_only=True, default=None)
    genre_name = serializers.CharField(source="genre.name", read_only=True, default=None)
    duration_display = serializers.ReadOnlyField()

    class Meta:
        model = Song
        fields = (
            "id",
            "title",
            "audio_file_url",
            "audio_file",
            "album",
            "album_title",
            "artist",
            "artist_name",
            "genre",
            "genre_name",
            "duration",
            "duration_display",
            "stream_count",
            "uploaded_by",
            "created_at",
        )
        read_only_fields = ("stream_count", "uploaded_by", "created_at")


class SongUploadSerializer(serializers.ModelSerializer):
    """Used by the admin upload endpoint — sets uploaded_by automatically."""

    class Meta:
        model = Song
        fields = (
            "id",
            "title",
            "audio_file_url",
            "audio_file",
            "album",
            "artist",
            "genre",
            "duration",
        )

    def create(self, validated_data):
        validated_data["uploaded_by"] = self.context["request"].user
        return super().create(validated_data)