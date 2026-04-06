from rest_framework import serializers
from .models import Playlist, PlaylistItem, LikedSongs
from music.serializers import SongSerializer
from .models import Playlist, PlaylistItem, LikedSongs 
from music.serializers import SongSerializer
from streaming.models import PlayHistory


class PlaylistItemSerializer(serializers.ModelSerializer):
    song_detail = SongSerializer(source="song", read_only=True)

    class Meta:
        model = PlaylistItem
        fields = ("id", "song", "song_detail", "order", "added_at")
        read_only_fields = ("added_at",)


class StreamResponseSerializer(serializers.Serializer):
    song_id       = serializers.IntegerField()
    title         = serializers.CharField()
    artist        = serializers.CharField()
    audio_url     = serializers.CharField()
    stream_count  = serializers.IntegerField()
    is_premium    = serializers.BooleanField()
    ad_required   = serializers.BooleanField()
    skip_allowed  = serializers.BooleanField()
    message       = serializers.CharField(required=False, allow_blank=True)


class PlayHistorySerializer(serializers.ModelSerializer):  # ← add this
    song_title  = serializers.CharField(source="song.title", read_only=True)
    artist_name = serializers.CharField(source="song.artist.name", read_only=True)

    class Meta:
        model  = PlayHistory
        fields = [
            "id",
            "song",
            "song_title",
            "artist_name",
            "played_at",
            "skipped",
        ]
        read_only_fields = ["played_at"]


class PlaylistSerializer(serializers.ModelSerializer):
    items = PlaylistItemSerializer(many=True, read_only=True)
    song_count = serializers.SerializerMethodField()
    owner = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Playlist
        fields = (
            "id", "name", "description", "owner",
            "song_count", "items", "created_at", "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def get_song_count(self, obj):
        return obj.items.count()


class PlaylistCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ("id", "name", "description")

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class AddSongSerializer(serializers.Serializer):
    song_id = serializers.IntegerField()
    order   = serializers.IntegerField(default=0, required=False)


class LikedSongsSerializer(serializers.ModelSerializer):
    song_detail = SongSerializer(source="song", read_only=True)

    class Meta:
        model = LikedSongs
        fields = ("id", "song", "song_detail", "liked_at")
        read_only_fields = ("liked_at",)