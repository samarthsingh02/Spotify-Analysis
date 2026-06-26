import pandas as pd

from loader import load_data
from config import PROCESSED_DATA


def preprocess():
    df = load_data()

    # Keep only songs
    df = df[df["master_metadata_track_name"].notna()].copy()

    # Rename columns
    df = df.rename(columns={
        "ts": "timestamp",
        "master_metadata_track_name": "track",
        "master_metadata_album_artist_name": "artist",
        "master_metadata_album_album_name": "album"
    })

    # Datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Extra columns
    df["year"] = df["timestamp"].dt.year
    df["month"] = df["timestamp"].dt.month
    df["month_name"] = df["timestamp"].dt.month_name()
    df["day"] = df["timestamp"].dt.day
    df["weekday"] = df["timestamp"].dt.day_name()
    df["hour"] = df["timestamp"].dt.hour
    df["date"] = df["timestamp"].dt.date

    df["seconds_played"] = df["ms_played"] / 1000
    df["minutes_played"] = df["ms_played"] / 60000

    df["song"] = df["track"] + " - " + df["artist"]

    # Keep useful columns
    df = df[
        [
            "timestamp",
            "year",
            "month",
            "month_name",
            "day",
            "weekday",
            "hour",
            "date",
            "track",
            "artist",
            "album",
            "song",
            "spotify_track_uri",
            "ms_played",
            "seconds_played",
            "minutes_played",
            "platform",
            "reason_start",
            "reason_end",
            "shuffle",
            "skipped",
            "offline",
            "incognito_mode",
        ]
    ]

    output_file = PROCESSED_DATA / "spotify_history.parquet"
    df.to_parquet(output_file, index=False)

    print("\nDone!")
    print(f"Songs: {len(df):,}")
    print(f"Saved to:\n{output_file}")

    return df


if __name__ == "__main__":
    preprocess()