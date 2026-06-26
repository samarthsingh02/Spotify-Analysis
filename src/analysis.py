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

