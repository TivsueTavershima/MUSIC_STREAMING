from django.db import models
from music.models import Artist, Genre, Song
from django.contrib.auth import get_user_model

User = get_user_model()


# class Genre(models.Model):
#     name = models.CharField(max_length=100, unique=True)

#     def __str__(self):
#         return self.name


# class Artist(models.Model):
#     name = models.CharField(max_length=255)
#     total_streams = models.PositiveBigIntegerField(default=0, db_index=True)

#     def __str__(self):
#         return self.name

#     class Meta:
#         ordering = ["-total_streams"]


# class Song(models.Model):
#     title = models.CharField(max_length=255)
#     artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="songs")
#     genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True, related_name="songs")
#     total_streams = models.PositiveBigIntegerField(default=0, db_index=True)
#     release_date = models.DateField()

#     def __str__(self):
#         return f"{self.title} — {self.artist.name}"

#     class Meta:
#         ordering = ["-total_streams"]


class Stream(models.Model):
    """One row per play event. Powers daily / weekly / monthly trend queries."""

    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="streams")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="streams")
    streamed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.song.title} streamed at {self.streamed_at}"

    class Meta:
        ordering = ["-streamed_at"]


class UserActivity(models.Model):
    """Tracks stream totals per user — powers the most active users ranking."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="activity")
    total_streams = models.PositiveBigIntegerField(default=0, db_index=True)
    last_streamed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} — {self.total_streams} streams"

    class Meta:
        ordering = ["-total_streams"]


class GenreStreamStat(models.Model):
    """Daily aggregated stream count per genre. Powers the most-played genre ranking."""

    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name="stream_stats")
    date = models.DateField(db_index=True)
    stream_count = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f"{self.genre.name} — {self.date} — {self.stream_count}"

    class Meta:
        unique_together = ("genre", "date")
        ordering = ["-stream_count"]