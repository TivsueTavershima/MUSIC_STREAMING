   
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from analytics.permissions import IsAdminUser
from music.models import Song, Artist, Genre
from music.serializers import SongSerializer, ArtistSerializer
from streaming.models import PlayHistory
from users.models import User
from users.permissions import IsAdminUserRole
from analytics.charts import (
    streams_over_time_chart,
    most_streamed_songs_chart,
    active_users_chart,
    genres_pie_chart,
    top_artists_chart,
)







class StreamStatsView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        now = timezone.now()

        daily   = PlayHistory.objects.filter(played_at__gte=now - timedelta(days=1)).count()
        weekly  = PlayHistory.objects.filter(played_at__gte=now - timedelta(days=7)).count()
        monthly = PlayHistory.objects.filter(played_at__gte=now - timedelta(days=30)).count()
        total   = PlayHistory.objects.count()

        # streams per day for last 30 days
        from django.db.models import Count
        from django.db.models.functions import TruncDate

        daily_data = (
            PlayHistory.objects
            .filter(played_at__gte=now - timedelta(days=30))
            .annotate(date=TruncDate("played_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        return Response({
            "streams": {
                "daily":   daily,
                "weekly":  weekly,
                "monthly": monthly,
                "total":   total,
            },
            "chart": {
                "type":   "line",
                "title":  "Daily Streams — Last 30 Days",
                "labels": [str(d["date"]) for d in daily_data],
                "data":   [d["count"] for d in daily_data],
            },
        })


class MostStreamedSongsView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        import pandas as pd

        songs_qs = Song.objects.select_related(
            "artist", "album", "genre"
        ).order_by("-stream_count")[:20]

        data = list(songs_qs.values(
            "id", "title", "artist__name", "genre__name", "stream_count", "duration"
        ))

        df = pd.DataFrame(data) if data else pd.DataFrame()
        summary = {}
        if not df.empty:
            summary = {
                "total_streams":   int(df["stream_count"].sum()),
                "mean_streams":    round(float(df["stream_count"].mean()), 2),
                "median_streams":  round(float(df["stream_count"].median()), 2),
                "max_streams":     int(df["stream_count"].max()),
                "min_streams":     int(df["stream_count"].min()),
                "top_genre": (
                    df.groupby("genre__name")["stream_count"].sum().idxmax()
                    if "genre__name" in df.columns and not df["genre__name"].isna().all()
                    else None
                ),
            }

        top10 = list(songs_qs.values("title", "stream_count")[:10])

        return Response({
            "most_streamed_songs": SongSerializer(songs_qs, many=True).data,
            "summary": summary,
            "chart": {
                "type":   "horizontal_bar",
                "title":  "Top 10 Most Streamed Songs",
                "labels": [s["title"] for s in top10],
                "data":   [s["stream_count"] for s in top10],
            },
        })


class MostActiveUsersView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        import pandas as pd

        users = User.objects.annotate(
            stream_count=Count("play_histories")
        ).order_by("-stream_count")[:20]

        user_data = [
            {
                "id":           u.id,
                "email":        u.email,
                "role":         u.role,
                "is_premium":   u.is_premium,
                "stream_count": u.stream_count,
            }
            for u in users
        ]

        df = pd.DataFrame(user_data) if user_data else pd.DataFrame()
        summary = {}
        if not df.empty:
            summary = {
                "total_users":          len(df),
                "premium_users":        int(df["is_premium"].sum()),
                "free_users":           int((~df["is_premium"]).sum()),
                "avg_streams_per_user": round(float(df["stream_count"].mean()), 2),
                "highest_stream_count": int(df["stream_count"].max()),
            }

        top10 = user_data[:10]

        return Response({
            "most_active_users": user_data,
            "summary": summary,
            "chart": {
                "type":   "horizontal_bar",
                "title":  "Top 10 Most Active Users",
                "labels": [u["email"] for u in top10],
                "data":   [u["stream_count"] for u in top10],
            },
        })


class MostPlayedGenresView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        import pandas as pd

        genres = Genre.objects.annotate(
            total_streams=Count("song__play_histories", distinct=True)
        ).order_by("-total_streams")[:10]

        genre_data = [
            {
                "id":            g.id,
                "name":          g.name,
                "total_streams": g.total_streams,
            }
            for g in genres
        ]

        df = pd.DataFrame(genre_data) if genre_data else pd.DataFrame()
        summary = {}
        if not df.empty and df["total_streams"].sum() > 0:
            df["share_pct"] = (
                df["total_streams"] / df["total_streams"].sum() * 100
            ).round(2)
            summary = {
                "top_genre":       df.iloc[0]["name"],
                "top_genre_share": float(df.iloc[0]["share_pct"]),
                "genres_tracked":  len(df),
            }
            genre_data = df.to_dict(orient="records")

        return Response({
            "most_played_genres": genre_data,
            "summary": summary,
            "chart": {
                "type":   "pie",
                "title":  "Most-Played Genres",
                "labels": [g["name"] for g in genre_data],
                "data":   [g["total_streams"] for g in genre_data],
            },
        })

class TopArtistsView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        import pandas as pd

        artists = Artist.objects.annotate(
            total_streams=Count("songs__play_histories", distinct=True)
        ).order_by("-total_streams")[:10]

        artist_data = [
            {
                "id":            a.id,
                "name":          a.name,
                "total_streams": a.total_streams,
            }
            for a in artists
        ]

        df = pd.DataFrame(artist_data) if artist_data else pd.DataFrame()
        summary = {}
        if not df.empty:
            summary = {
                "top_artist":             df.iloc[0]["name"] if len(df) > 0 else None,
                "top_artist_streams":     int(df.iloc[0]["total_streams"]) if len(df) > 0 else 0,
                "total_artists_tracked":  len(df),
                "avg_streams_per_artist": round(float(df["total_streams"].mean()), 2),
            }

        return Response({
            "top_artists": artist_data,
            "summary": summary,
            "chart": {
                "type":   "bar",
                "title":  "Top Artists by Total Streams",
                "labels": [a["name"] for a in artist_data],
                "data":   [a["total_streams"] for a in artist_data],
            },
        })


# TopArtistsView
artists = Artist.objects.annotate(
    total_streams=Count("songs__play_histories")
).order_by("-total_streams")[:10]

# MostPlayedGenresView
genres = Genre.objects.annotate(
    total_streams=Count("song__play_histories")
).order_by("-total_streams")[:10]