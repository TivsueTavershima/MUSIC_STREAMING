import base64
import io
import matplotlib
matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
from django.utils import timezone
from datetime import timedelta


def streams_over_time_chart(play_history_queryset):
    last_30 = timezone.now() - timedelta(days=30)
    qs = play_history_queryset.filter(
        played_at__gte=last_30
    ).values('played_at__date').order_by('played_at__date')

    df = pd.DataFrame(list(qs), columns=['date', 'count']) if qs else pd.DataFrame()

    fig, ax = plt.subplots()
    if not df.empty:
        ax.plot(df['played_at__date'], df['count'])
    ax.set_title('Daily Streams — Last 30 Days')
    ax.set_xlabel('Date')
    ax.set_ylabel('Streams')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def most_streamed_songs_chart(songs_queryset, limit=10):
    songs = list(songs_queryset.values('title', 'stream_count')[:limit])
    df = pd.DataFrame(songs)

    fig, ax = plt.subplots()
    if not df.empty:
        ax.barh(df['title'], df['stream_count'])
    ax.set_title('Top Most Streamed Songs')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def active_users_chart(user_data, limit=10):
    df = pd.DataFrame(user_data[:limit])

    fig, ax = plt.subplots()
    if not df.empty:
        ax.barh(df['email'], df['stream_count'])
    ax.set_title('Most Active Users')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def genres_pie_chart(genre_data, limit=8):
    df = pd.DataFrame(genre_data[:limit])

    fig, ax = plt.subplots()
    if not df.empty:
        ax.pie(df['total_streams'], labels=df['name'], autopct='%1.1f%%')
    ax.set_title('Most Played Genres')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def top_artists_chart(artist_data, limit=10):
    df = pd.DataFrame(artist_data[:limit])

    fig, ax = plt.subplots()
    if not df.empty:
        ax.bar(df['name'], df['total_streams'])
    ax.set_title('Top Artists by Streams')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')