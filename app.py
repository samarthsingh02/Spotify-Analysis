import streamlit as st
import pandas as pd
import plotly.express as px
from src.analysis import longest_song_streaks
from src.analysis import burnout_evergreen

st.set_page_config(
    page_title="Spotify Analysis",
    page_icon="🎵",
    layout="wide"
)

DATA_PATH = "data/processed/spotify_history.parquet"


@st.cache_data
def load_data():
    return pd.read_parquet(DATA_PATH)


df = load_data()

st.title("Spotify Analysis")

st.caption("2022 - 2026")

st.divider()

# ------------------ Sidebar ------------------

year = st.sidebar.selectbox(
    "Year",
    ["All"] + sorted(df["year"].unique().tolist())
)

if year != "All":
    df = df[df["year"] == year]

# ------------------ Top Stats ------------------

total_plays = len(df)
total_hours = df["minutes_played"].sum() / 60
unique_songs = df["song"].nunique()
unique_artists = df["artist"].nunique()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Songs Played", f"{total_plays:,}")
c2.metric("Listening Hours", f"{total_hours:,.1f}")
c3.metric("Unique Songs", f"{unique_songs:,}")
c4.metric("Artists", f"{unique_artists:,}")

st.divider()

# ------------------ Top Songs ------------------

left, right = st.columns(2)

with left:
    st.subheader("Top Songs")

    top_songs = (
        df.groupby("song")
        .size()
        .sort_values(ascending=False)
        .head(15)
    )

    st.dataframe(top_songs)

with right:
    st.subheader("Top Artists")

    top_artists = (
        df.groupby("artist")
        .size()
        .sort_values(ascending=False)
        .head(15)
    )

    st.dataframe(top_artists)

st.divider()

# ------------------ Monthly Listening ------------------

monthly = (
    df.groupby(["year", "month_name"])
    .size()
    .reset_index(name="plays")
)

fig = px.bar(
    monthly,
    x="month_name",
    y="plays",
    color="year",
    title="Monthly Listening"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Biggest Obsessions")

obsessions = longest_song_streaks(df)

st.dataframe(
    obsessions,
    use_container_width=True,
    hide_index=True
)

st.divider()

burnout, evergreen = burnout_evergreen(df)

left, right = st.columns(2)

with left:
    st.subheader("Burnout Songs")
    st.dataframe(
        burnout[
            [
                "song",
                "total_plays",
                "peak_month",
                "active_months",
                "burnout_score"
            ]
        ],
        hide_index=True,
        use_container_width=True
    )

with right:
    st.subheader("Evergreen Songs")
    st.dataframe(
        evergreen[
            [
                "song",
                "total_plays",
                "active_months"
            ]
        ],
        hide_index=True,
        use_container_width=True
    )