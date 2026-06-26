import json
from pathlib import Path

import pandas as pd

from config import RAW_DATA


def load_data():
    """
    Loads all Spotify Audio Streaming History JSON files
    into a single pandas DataFrame.
    """

    json_files = sorted(RAW_DATA.glob("Streaming_History_Audio_*.json"))

    if not json_files:
        raise FileNotFoundError(
            f"No Spotify JSON files found inside:\n{RAW_DATA}"
        )

    dataframes = []

    print("=" * 50)
    print("Loading Spotify Streaming History")
    print("=" * 50)

    for file in json_files:
        print(f"Loading {file.name}")

        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        df = pd.DataFrame(data)
        dataframes.append(df)

    df = pd.concat(dataframes, ignore_index=True)

    print("\nDone.")
    print(f"Files loaded : {len(json_files)}")
    print(f"Total records: {len(df):,}")

    return df


if __name__ == "__main__":
    df = load_data()

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nShape:")
    print(df.shape)

    print("\nFirst Row:")
    print(df.iloc[0])