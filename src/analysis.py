import pandas as pd


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