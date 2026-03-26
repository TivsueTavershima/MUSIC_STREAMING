from rest_framework import serializers
from .models import Stream, UserActivity, GenreStreamStat, Song, Genre
from django.contrib.auth import get_user_model

User = get_user_model()


class StreamSerializer(serializers.ModelSerializer):
    song_title = serializers.CharField(source="song.title", read_only=True)
    artist_name = serializers.CharField(source="song.artist.name", read_only=True)

    class Meta:
        model = Stream
        fields = ["id", "song", "song_title", "artist_name", "user", "streamed_at"]
        read_only_fields = ["streamed_at"]


class UserActivitySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = UserActivity
        fields = ["id", "user", "username", "total_streams", "last_streamed_at"]
        read_only_fields = ["total_streams", "last_streamed_at"]


class GenreStreamStatSerializer(serializers.ModelSerializer):
    genre_name = serializers.CharField(source="genre.name", read_only=True)

    class Meta:
        model = GenreStreamStat
        fields = ["id", "genre", "genre_name", "date", "stream_count"]


# ── Analytics response serializers ───────────────────────────────────────────

class StreamTrendSerializer(serializers.Serializer):
    """One bucket in the daily / weekly / monthly trend chart."""
    period = serializers.CharField()
    stream_count = serializers.IntegerField()
    unique_listeners = serializers.IntegerField()


class MostActiveUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    total_streams = serializers.IntegerField()
    last_streamed_at = serializers.DateTimeField()


class MostPlayedGenreSerializer(serializers.Serializer):
    genre_id = serializers.IntegerField()
    genre_name = serializers.CharField()
    stream_count = serializers.IntegerField()
    percentage = serializers.FloatField()