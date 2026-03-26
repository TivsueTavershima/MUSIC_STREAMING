# from django.db import models
# from cloudinary.models import CloudinaryField
# from django.contrib.auth import get_user_model


# User = get_user_model()


# class Artist(models.Model):
#     name = models.CharField(max_length=200)
#     bio = models.TextField(blank=True, default='')  # ← Add default=''
#     profile_image = CloudinaryField(folder="artists/", blank=True, null=True)
#     def __str__(self):
#         return self.name

 
    
# class Album(models.Model):
#     title = models.CharField(max_length=200)
#     artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='albums')
#     release_date = models.DateField(null=True, blank=True)
#     cover_image = CloudinaryField(folder="songs/covers/", blank=True, null=True)
#     # genres = models.ManyToManyField(Genre, blank=True, related_name='albums')  # missing
#     description = models.TextField(blank=True, default='')                     # missing
#     created_at = models.DateTimeField(auto_now_add=True)                       # missing

#     def __str__(self):
#         return f"{self.title} by {self.artist}"  

# class Genre(models.Model):
#     name = models.CharField(max_length=100, unique=True)

#     def __str__(self):
#         return self.name

# class Song(models.Model):
#     title = models.CharField(max_length=200)
#     artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
#     album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True)
#     genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
#     # audio_file = CloudinaryField('audio', resource_type="video")
#     audio_file  = CloudinaryField(folder="songs/audio/",  blank=True, null=True)
#     cover_image = CloudinaryField('image', blank=True, null=True)
#     duration = models.CharField(max_length=10, blank=True, null=True)  # e.g., "3:45"
#     stream_count = models.BigIntegerField(default=0)
#     uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.title} - {self.artist}"
    
 
    
    
    
    
    
    
    
    
    
from django.db import models
from django.conf import settings


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Artist(models.Model):
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to="artists/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="albums")
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    cover_image = models.ImageField(upload_to="albums/", blank=True, null=True)
    release_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} — {self.artist.name}"


class Song(models.Model):
    title = models.CharField(max_length=200)
    audio_file_url = models.URLField(blank=True, help_text="Cloudinary or CDN URL for the audio file")
    audio_file = models.FileField(upload_to="songs/", blank=True, null=True)
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True, related_name="songs")
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="songs")
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    duration = models.PositiveIntegerField(default=0, help_text="Duration in seconds")
    stream_count = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_songs",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} — {self.artist.name}"

    @property
    def duration_display(self):
        mins, secs = divmod(self.duration, 60)
        return f"{mins}:{secs:02d}"
    
    
    