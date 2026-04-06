from rest_framework import serializers

from music.models import Song
from .models import PlayHistory
from music.serializers import SongSerializer


        


class PlayHistorySerializer(serializers.ModelSerializer):
    song = SongSerializer(read_only=True)

    class Meta:
        model = PlayHistory
        fields = ['id', 'song', 'played_at', 'skipped']