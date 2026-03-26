from django.db import models
from django.conf import settings
from music.models import Artist, Song




class PlayHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='play_histories')
    song = models.ForeignKey("music.Song", on_delete=models.CASCADE, related_name='play_histories')
    played_at = models.DateTimeField(auto_now_add=True)
    skipped = models.BooleanField(default=False)
    
class Follow(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='followers')
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'artist']
        ordering = ['-followed_at']

    def __str__(self):
        return f"{self.user} follows {self.artist.name}"