# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import permissions
# from django.db.models import Count
# from django.utils import timezone
# from datetime import timedelta

# from music.models import Song, Artist, Genre
# from music.serializers import SongSerializer, ArtistSerializer
# from streaming.models import PlayHistory
# from users.models import User


# # ── Admin-only permission ─────────────────────────────────────────────────────

# class IsAdminUser(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return (
#             request.user
#             and request.user.is_authenticated
#             and request.user.is_admin_user
#         )


# # ── /admin/analytics/streams/ ─────────────────────────────────────────────────

# class StreamStatsView(APIView):
#     """
#     GET /admin/analytics/streams/
#     Daily / weekly / monthly stream totals + all-time total.
#     """
#     permission_classes = [IsAdminUser]

#     def get(self, request):
#         now = timezone.now()

#         daily   = PlayHistory.objects.filter(
#             played_at__gte=now - timedelta(days=1)
#         ).count()

#         weekly  = PlayHistory.objects.filter(
#             played_at__gte=now - timedelta(days=7)
#         ).count()

#         monthly = PlayHistory.objects.filter(
#             played_at__gte=now - timedelta(days=30)
#         ).count()

#         total   = PlayHistory.objects.count()

#         return Response({
#             "streams": {
#                 "daily":   daily,
#                 "weekly":  weekly,
#                 "monthly": monthly,
#                 "total":   total,
#             }
#         })


# # ── /admin/analytics/songs/ ───────────────────────────────────────────────────

# class MostStreamedSongsView(APIView):
#     """
#     GET /admin/analytics/songs/
#     Top 20 most-streamed songs of all time.
#     """
#     permission_classes = [IsAdminUser]

#     def get(self, request):
#         songs = Song.objects.select_related(
#             "artist", "album", "genre"
#         ).order_by("-stream_count")[:20]

#         return Response({
#             "most_streamed_songs": SongSerializer(songs, many=True).data,
#         })


# # ── /admin/analytics/users/ ───────────────────────────────────────────────────

# class MostActiveUsersView(APIView):
#     """
#     GET /admin/analytics/users/
#     Top 20 most active users by total stream count.
#     """
#     permission_classes = [IsAdminUser]

#     def get(self, request):
#         users = User.objects.annotate(
#             stream_count=Count("play_history")
#         ).order_by("-stream_count")[:20]

#         data = [
#             {
#                 "id":           u.id,
#                 "email":        u.email,
#                 "role":         u.role,
#                 "is_premium":   u.is_premium,
#                 "stream_count": u.stream_count,
#             }
#             for u in users
#         ]

#         return Response({"most_active_users": data})


# # ── /admin/analytics/genres/ ──────────────────────────────────────────────────

# class MostPlayedGenresView(APIView):
#     """
#     GET /admin/analytics/genres/
#     Most-played genres ranked by total streams.
#     """
#     permission_classes = [IsAdminUser]

#     def get(self, request):
#         genres = Genre.objects.annotate(
#             total_streams=Count("song__play_history")
#         ).order_by("-total_streams")[:10]

#         data = [
#             {
#                 "id":            g.id,
#                 "name":          g.name,
#                 "total_streams": g.total_streams,
#             }
#             for g in genres
#         ]

#         return Response({"most_played_genres": data})


# # ── /admin/analytics/top-artists/ ────────────────────────────────────────────

# class TopArtistsView(APIView):
#     """
#     GET /admin/analytics/top-artists/
#     Top 10 artists by total streams across all their songs.
#     """
#     permission_classes = [IsAdminUser]

#     def get(self, request):
#         artists = Artist.objects.annotate(
#             total_streams=Count("songs__play_history")
#         ).order_by("-total_streams")[:10]

#         data = [
#             {
#                 "id":            a.id,
#                 "name":          a.name,
#                 "total_streams": a.total_streams,
#             }
#             for a in artists
#         ]

#         return Response({"top_artists": data})
    
    
    
    
    
    
    
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from analytics.permissions import IsAdminUser, streams_over_time_chart
from music.models import Song, Artist, Genre
from music.serializers import SongSerializer, ArtistSerializer
from streaming.models import PlayHistory
from users.models import User
# from analytics.charts import (
#     most_streamed_songs_chart,
#     streams_over_time_chart,
#     top_artists_chart,
#     genres_pie_chart,
#     active_users_chart,
# )





# ── /admin/analytics/streams/ ─────────────────────────────────────────────────

class StreamStatsView(APIView):
    """
    GET /admin/analytics/streams/
    Daily / weekly / monthly / total stream counts.
    Includes a pandas-aggregated line chart (base64 PNG).
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        now = timezone.now()

        daily   = PlayHistory.objects.filter(
            played_at__gte=now - timedelta(days=1)
        ).count()
        weekly  = PlayHistory.objects.filter(
            played_at__gte=now - timedelta(days=7)
        ).count()
        monthly = PlayHistory.objects.filter(
            played_at__gte=now - timedelta(days=30)
        ).count()
        total   = PlayHistory.objects.count()

        # pandas + matplotlib — streams per day for the last 30 days
        chart_b64 = streams_over_time_chart(PlayHistory.objects)

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
                "format": "image/png;base64",
                "data":   chart_b64,
            },
        })

def most_streamed_songs_chart(songs_queryset, limit):
    raise NotImplementedError


# ── /admin/analytics/songs/ ───────────────────────────────────────────────────

class MostStreamedSongsView(APIView):
    """
    GET /admin/analytics/songs/
    Top 20 most-streamed songs with a pandas DataFrame summary
    and a horizontal bar chart.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        import pandas as pd

        songs_qs = Song.objects.select_related(
            "artist", "album", "genre"
        ).order_by("-stream_count")[:20]

        # Build pandas DataFrame for summary stats
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
                "top_genre":       (
                    df.groupby("genre__name")["stream_count"]
                    .sum().idxmax()
                    if "genre__name" in df.columns and not df["genre__name"].isna().all()
                    else None
                ),
            }

        chart_b64 = most_streamed_songs_chart(
            Song.objects.order_by("-stream_count"), limit=10
        )

        return Response({
            "most_streamed_songs": SongSerializer(songs_qs, many=True).data,
            "summary":             summary,
            "chart": {
                "type":   "horizontal_bar",
                "title":  "Top 10 Most Streamed Songs",
                "format": "image/png;base64",
                "data":   chart_b64,
            },
        })

def active_users_chart(user_data, limit=10):
    raise NotImplementedError


# ── /admin/analytics/users/ ───────────────────────────────────────────────────

class MostActiveUsersView(APIView):
    """
    GET /admin/analytics/users/
    Top 20 most active users by stream count with a bar chart.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        import pandas as pd

        users = User.objects.annotate(
            stream_count=Count("play_history")
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

        # pandas summary
        df = pd.DataFrame(user_data) if user_data else pd.DataFrame()
        summary = {}
        if not df.empty:
            summary = {
                "total_users":        len(df),
                "premium_users":      int(df["is_premium"].sum()),
                "free_users":         int((~df["is_premium"]).sum()),
                "avg_streams_per_user": round(float(df["stream_count"].mean()), 2),
                "highest_stream_count": int(df["stream_count"].max()),
            }

        chart_b64 = active_users_chart(user_data, limit=10)

        return Response({
            "most_active_users": user_data,
            "summary":           summary,
            "chart": {
                "type":   "horizontal_bar",
                "title":  "Top 10 Most Active Users",
                "format": "image/png;base64",
                "data":   chart_b64,
            },
        })

class genres_pie_chart:
    def __init__(self, genre_data, limit=None):
        self.genre_data = genre_data
        self.limit = limit

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


# ── /admin/analytics/genres/ ──────────────────────────────────────────────────

class MostPlayedGenresView(APIView):
    """
    GET /admin/analytics/genres/
    Most-played genres with a pie chart.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        import pandas as pd

        genres = Genre.objects.annotate(
            total_streams=Count("song__play_history")
        ).order_by("-total_streams")[:10]

        genre_data = [
            {
                "id":            g.id,
                "name":          g.name,
                "total_streams": g.total_streams,
            }
            for g in genres
        ]

        # pandas summary
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

        chart_b64 = genres_pie_chart(genre_data, limit=8)

        return Response({
            "most_played_genres": genre_data,
            "summary":            summary,
            "chart": {
                "type":   "pie",
                "title":  "Most-Played Genres",
                "format": "image/png;base64",
                "data":   chart_b64,
            },
        })

class top_artists_chart:
    def __init__(self, artist_data, limit=10):
        self.artist_data = artist_data
        self.limit = limit

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


# ── /admin/analytics/top-artists/ ────────────────────────────────────────────

class TopArtistsView(APIView):
    """
    GET /admin/analytics/top-artists/
    Top 10 artists by total streams with a bar chart.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        import pandas as pd

        artists = Artist.objects.annotate(
            total_streams=Count("songs__play_history")
        ).order_by("-total_streams")[:10]

        artist_data = [
            {
                "id":            a.id,
                "name":          a.name,
                "total_streams": a.total_streams,
            }
            for a in artists
        ]

        # pandas summary
        df = pd.DataFrame(artist_data) if artist_data else pd.DataFrame()
        summary = {}
        if not df.empty:
            summary = {
                "top_artist":           df.iloc[0]["name"] if len(df) > 0 else None,
                "top_artist_streams":   int(df.iloc[0]["total_streams"]) if len(df) > 0 else 0,
                "total_artists_tracked": len(df),
                "avg_streams_per_artist": round(float(df["total_streams"].mean()), 2),
            }

        chart_b64 = top_artists_chart(artist_data, limit=10)

        return Response({
            "top_artists": artist_data,
            "summary":     summary,
            "chart": {
                "type":   "bar",
                "title":  "Top Artists by Total Streams",
                "format": "image/png;base64",
                "data":   chart_b64,
            },
        })