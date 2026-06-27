import pandas as pd
from itertools import combinations
from collections import Counter
import math


def longest_song_streaks(df, top_n=20):
    streaks = []

    current_song = None
    streak = 0
    start_time = None

    for _, row in df.iterrows():

        song = row["song"]

        if song == current_song:
            streak += 1
        else:
            if current_song is not None:
                streaks.append({
                    "Song": current_song,
                    "Streak": streak,
                    "Started": start_time
                })

            current_song = song
            streak = 1
            start_time = row["timestamp"]

    if current_song is not None:
        streaks.append({
            "Song": current_song,
            "Streak": streak,
            "Started": start_time
        })

    streaks = pd.DataFrame(streaks)

    return (
        streaks
        .sort_values("Streak", ascending=False)
        .head(top_n)
    )

def burnout_evergreen(df, min_total_plays=15):
    monthly = (
        df.groupby(["song", "year", "month"])
        .size()
        .reset_index(name="plays")
    )

    summary = (
        monthly.groupby("song")
        .agg(
            total_plays=("plays", "sum"),
            peak_month=("plays", "max"),
            active_months=("plays", "count"),
            avg_month=("plays", "mean")
        )
        .reset_index()
    )

    summary = summary[summary["total_plays"] >= min_total_plays]

    summary["burnout_score"] = (
        summary["peak_month"] / summary["avg_month"]
    )

    burnout = (
        summary.sort_values("burnout_score", ascending=False)
        .head(15)
    )

    evergreen = (
        summary.sort_values(
            ["active_months", "total_plays"],
            ascending=False
        )
        .head(15)
    )

    return burnout, evergreen

def create_sessions(df, gap_minutes=30):
    df = df.sort_values("timestamp").copy()

    gap = df["timestamp"].diff().dt.total_seconds().div(60)

    df["new_session"] = gap.isna() | (gap > gap_minutes)

    df["session_id"] = df["new_session"].cumsum()

    return df

def session_statistics(df):

    sessions = (
        df.groupby("session_id")
        .agg(
            Start=("timestamp", "min"),
            End=("timestamp", "max"),
            Songs=("song", "count"),
            Unique_Songs=("song", "nunique"),
            Artists=("artist", "nunique"),
            Minutes_Played=("minutes_played", "sum")
        )
        .reset_index(drop=True)
    )

    sessions["Duration"] = (
        sessions["End"] - sessions["Start"]
    ).dt.total_seconds() / 60

    sessions = sessions.sort_values(
        "Songs",
        ascending=False
    )

    return sessions

def song_groups(df, top_n=100):
    pair_counts = {}

    sessions = df.groupby("session_id")

    for _, session in sessions:

        songs = session["song"].drop_duplicates().tolist()

        if len(songs) < 2:
            continue

        for pair in combinations(sorted(songs), 2):

            pair_counts[pair] = pair_counts.get(pair, 0) + 1

    rows = []

    for pair, count in pair_counts.items():

        rows.append({
            "Song 1": pair[0],
            "Song 2": pair[1],
            "Sessions Together": count
        })

    result = pd.DataFrame(rows)

    result = result.sort_values(
        "Sessions Together",
        ascending=False
    )

    return result.head(top_n)

def recurring_song_groups(df, min_group_size=4, top_n=20):
    sessions = (
        df.groupby("session_id")["song"]
        .apply(lambda x: sorted(set(x)))
        .tolist()
    )

    counter = Counter()

    n = len(sessions)

    for i in range(n):
        for j in range(i + 1, n):

            common = set(sessions[i]) & set(sessions[j])

            if len(common) >= min_group_size:
                counter[frozenset(common)] += 1

    rows = []

    for songs, count in counter.items():

        rows.append({
            "Songs": "\n".join(sorted(songs)),
            "Group Size": len(songs),
            "Repeated Sessions": count + 1
        })

    result = (
        pd.DataFrame(rows)
        .sort_values(
            ["Repeated Sessions", "Group Size"],
            ascending=False
        )
        .head(top_n)
    )

    return result

def nostalgia_score(df, top_n=100):

    rows = []

    for song, group in df.groupby("song"):

        group = group.sort_values("timestamp").reset_index(drop=True)

        if len(group) < 3:
            continue

        gaps = group["timestamp"].diff().dt.days

        gap_index = gaps.idxmax()

        if pd.isna(gap_index):
            continue

        gap_days = gaps.iloc[gap_index]

        previous_play = group.iloc[gap_index - 1]["timestamp"]
        comeback_play = group.iloc[gap_index]["timestamp"]

        score = gap_days * math.log(len(group) + 1)

        rows.append({
            "Song": song,
            "Nostalgia Score": round(score, 2),
            "Gap (Days)": int(gap_days),
            "Last Heard": previous_play.strftime("%d %b %Y"),
            "Rediscovered": comeback_play.strftime("%d %b %Y"),
            "Total Plays": len(group)
        })

    result = pd.DataFrame(rows)

    return result.sort_values(
        "Nostalgia Score",
        ascending=False
    ).head(top_n)