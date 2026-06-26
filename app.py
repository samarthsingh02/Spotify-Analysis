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

st.sidebar.title("Filters")

filter_type = st.sidebar.selectbox(
    "Time Range",
    [
        "All Time",
        "Year",
        "Month",
        "Custom Range"
    ]
)

filtered_df = df.copy()

if filter_type == "Year":
    year = st.sidebar.selectbox(
        "Year",
        sorted(df["year"].unique(), reverse=True)
    )
    filtered_df = filtered_df[filtered_df["year"] == year]

elif filter_type == "Month":
    year = st.sidebar.selectbox(
        "Year",
        sorted(df["year"].unique(), reverse=True)
    )

    month = st.sidebar.selectbox(
        "Month",
        [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December"
        ]
    )

    filtered_df = filtered_df[
        (filtered_df["year"] == year)
        &
        (filtered_df["month_name"] == month)
    ]

elif filter_type == "Custom Range":

    start = st.sidebar.date_input(
        "From",
        df["timestamp"].min().date()
    )

    end = st.sidebar.date_input(
        "To",
        df["timestamp"].max().date()
    )

    filtered_df = filtered_df[
        (filtered_df["date"] >= start)
        &
        (filtered_df["date"] <= end)
    ]

df = filtered_df

# ------------------ Top Stats ------------------

total_plays = len(df)
total_hours = df["minutes_played"].sum() / 60
unique_songs = df["song"].nunique()
unique_artists = df["artist"].nunique()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Song Plays", f"{total_plays:,}")
c2.metric("Listening Hours", f"{total_hours:,.0f}")
c3.metric("Unique Songs", f"{unique_songs:,}")
c4.metric("Unique Artists", f"{unique_artists:,}")

st.divider()

# ------------------ Top Songs ------------------

st.subheader("Top Songs")

top_songs = (
    df.groupby(["track", "artist"])
    .size()
    .reset_index(name="Plays")
    .sort_values("Plays", ascending=False)
)

st.dataframe(
    top_songs,
    hide_index=True,
    use_container_width=True,
    height=700
)

st.divider()

# ------------------ Top Artists ------------------

st.subheader("Top Artists")

top_artists = (
    df.groupby("artist")
    .size()
    .reset_index(name="Plays")
    .sort_values("Plays", ascending=False)
)

st.dataframe(
    top_artists,
    hide_index=True,
    use_container_width=True,
    height=500
)

st.divider()

# ------------------ Top Albums ------------------

st.subheader("Top Albums")

top_albums = (
    df.groupby(["album", "artist"])
    .size()
    .reset_index(name="Plays")
    .sort_values("Plays", ascending=False)
)

st.dataframe(
    top_albums,
    hide_index=True,
    use_container_width=True,
    height=500
)

st.divider()

# ------------------ Monthly Listening ------------------

month_order = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]

monthly = (
    df.groupby(["year", "month", "month_name"])
    .size()
    .reset_index(name="Plays")
)

monthly["month_name"] = pd.Categorical(
    monthly["month_name"],
    categories=month_order,
    ordered=True
)

monthly = monthly.sort_values(
    ["year", "month"]
)

fig = px.line(
    monthly,
    x="month",
    y="Plays",
    color="year",
    markers=True,
    title="Monthly Listening"
)

fig.update_layout(
    xaxis=dict(
        tickmode="array",
        tickvals=list(range(1, 13)),
        ticktext=month_order
    )
)

st.plotly_chart(fig, use_container_width=True)

# ------------------ Biggest Obsessions ------------------

st.divider()

obsessions = longest_song_streaks(df, 100)

obsessions["Started"] = pd.to_datetime(
    obsessions["Started"]
).dt.strftime("%d %b %Y")

st.subheader("Biggest Obsessions")

st.dataframe(
    obsessions,
    hide_index=True,
    use_container_width=True,
    height=600
)

st.divider()

# ------------------ Burnout and Evergreen ------------------

burnout, evergreen = burnout_evergreen(df)

burnout["burnout_score"] = burnout["burnout_score"].round(2)

burnout = burnout.rename(
    columns={
        "song": "Song",
        "total_plays": "Total Plays",
        "peak_month": "Peak Month Plays",
        "active_months": "Active Months",
        "burnout_score": "Burnout Score"
    }
)

evergreen = evergreen.rename(
    columns={
        "song": "Song",
        "total_plays": "Total Plays",
        "active_months": "Active Months"
    }
)

left, right = st.columns(2)

with left:
    st.subheader("Burnout Songs")
    st.dataframe(
        burnout,
        hide_index=True,
        use_container_width=True,
        height=600
    )

with right:
    st.subheader("Evergreen Songs")
    st.dataframe(
        evergreen,
        hide_index=True,
        use_container_width=True,
        height=600
    )