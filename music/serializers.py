from rest_framework import serializers
from .models import Genre, Artist, Album, Song


# class GenreSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Genre
#         fields = "__all__"


# class ArtistSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Artist
#         fields = "__all__"


# class AlbumSerializer(serializers.ModelSerializer):
#     artist = ArtistSerializer(read_only=True)

#     class Meta:
#         model = Album
#         fields = "__all__"


# class SongSerializer(serializers.ModelSerializer):
#     artist = ArtistSerializer(read_only=True)
#     album = AlbumSerializer(read_only=True)
#     genre = GenreSerializer(read_only=True)

#     class Meta:
#         model = Song
#         fields = "__all__"


















# from rest_framework import serializers
# from .models import Genre, Artist, Album, Song


# class GenreSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Genre
#         fields = ['id', 'name']
    
#     def validate_name(self, value):
#         return value.strip().title()
      

# class ArtistSerializer(serializers.ModelSerializer):
#     profile_image = serializers.SerializerMethodField()

#     class Meta:
#         model = Artist
#         fields = ['id', 'name', 'bio', 'profile_image']
#         read_only_fields = ['id']

#     def get_profile_image(self, obj):
#         if obj.profile_image:
#             return obj.profile_image.url
#         return None

#     def validate_name(self, value):
#         return value.strip().title()

#     def validate_bio(self, value):
#         return value.strip()
      
# class AlbumSerializer(serializers.ModelSerializer):
#     artist = ArtistSerializer(read_only=True)
#     artist_id = serializers.PrimaryKeyRelatedField(
#         queryset=Artist.objects.all(), write_only=True, source='artist'
#     )
#     cover_image = serializers.SerializerMethodField()

#     class Meta:
#         model = Album
#         fields = ['id', 'title', 'artist', 'artist_id', 'release_date', 
#                   'cover_image', 'description', 'created_at']
#         read_only_fields = ['id', 'created_at']

#     def get_cover_image(self, obj):
#         if obj.cover_image:
#             return obj.cover_image.url
#         return None

#     def validate_title(self, value):
#         return value.strip().title()

#     def validate_description(self, value):
#         return value.strip()

# class SongSerializer(serializers.ModelSerializer):
#     artist = ArtistSerializer(read_only=True)
#     artist_id = serializers.PrimaryKeyRelatedField(
#         queryset=Artist.objects.all(), write_only=True, source='artist'
#     )
#     album = AlbumSerializer(read_only=True)
#     album_id = serializers.PrimaryKeyRelatedField(
#         queryset=Album.objects.all(), write_only=True, source='album', 
#         required=False, allow_null=True
#     )
#     genres = GenreSerializer(many=True, read_only=True)
#     genre_ids = serializers.PrimaryKeyRelatedField(
#         many=True, queryset=Genre.objects.all(), write_only=True, source='genres'
#     )
#     cover_image = serializers.SerializerMethodField()
#     duration_formatted = serializers.ReadOnlyField()

#     class Meta:
#         model = Song
#         fields = ['id', 'title', 'artist', 'artist_id', 'album', 'album_id',
#                   'genres', 'genre_ids', 'audio_file', 'cover_image',
#                   'duration', 'duration_formatted', 'stream_count', 'lyrics',
#                   'is_explicit', 'is_available', 'created_at']
#         read_only_fields = ['id', 'stream_count', 'uploaded_by', 'created_at']

#     def get_cover_image(self, obj):
#         if obj.cover_image:
#             return obj.cover_image.url
#         return None

#     def validate_title(self, value):
#         return value.strip().title()
 
 
 
 
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