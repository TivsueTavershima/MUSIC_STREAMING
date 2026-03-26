from rest_framework import serializers

from music.models import Song
from .models import PlayHistory
from music.serializers import SongSerializer


        
        
class PlayHistorySerializer(serializers.ModelSerializer):
    song = SongSerializer(read_only=True)
    song_id = serializers.PrimaryKeyRelatedField(
        queryset=Song.objects.all(), write_only=True, source='song'
    )

    class Meta:
        model = PlayHistory
        fields = ['id', 'song', 'song_id', 'played_at']
        read_only_fields = ['id', 'played_at']