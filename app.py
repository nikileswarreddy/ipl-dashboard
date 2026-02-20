import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(page_title="IPL Analytics Dashboard", layout="wide", page_icon="🏏")

st.markdown("""
    <style>
        .block-container { padding-top: 1rem; }
        h1 { color: #f0a500; }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────
@st.cache_data
def load_data():
    matches = pd.read_csv("matches.csv")
    deliveries = pd.read_csv("deliveries.csv")
    matches["date"] = pd.to_datetime(matches["date"])
    return matches, deliveries

matches, deliveries = load_data()

# ─────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/8/84/IPL_logo.png/200px-IPL_logo.png", width=120)
st.sidebar.title("🏏 IPL Dashboard")
st.sidebar.markdown("---")

all_seasons = sorted(matches["season"].unique())
selected_season = st.sidebar.selectbox("📅 Select Season", ["All"] + all_seasons)

all_teams = sorted(set(matches["team1"].unique()) | set(matches["team2"].unique()))
selected_team = st.sidebar.selectbox("🏟️ Select Team", ["All"] + all_teams)

# Filter
df = matches.copy()
if selected_season != "All":
    df = df[df["season"] == selected_season]
if selected_team != "All":
    df = df[(df["team1"] == selected_team) | (df["team2"] == selected_team)]

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.title("🏏 IPL Sports Analytics Dashboard")
st.markdown(f"Showing data for: **{selected_season} Season** | **{selected_team}**")
st.markdown("---")

# ─────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("🎯 Total Matches", len(df))
col2.metric("🏟️ Venues", df["venue"].nunique())
col3.metric("🌆 Cities", df["city"].nunique())
col4.metric("🏆 Seasons", df["season"].nunique())

st.markdown("---")

# ─────────────────────────────────────────
# ROW 1: Most Wins + Toss Decision
# ─────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Most Wins by Team")
    wins = df["winner"].value_counts().reset_index()
    wins.columns = ["Team", "Wins"]
    fig = px.bar(wins, x="Wins", y="Team", orientation="h",
                 color="Wins", color_continuous_scale="Oranges",
                 title="Total Wins per Team")
    fig.update_layout(yaxis=dict(categoryorder="total ascending"), height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🪙 Toss Decision")
    toss = df["toss_decision"].value_counts().reset_index()
    toss.columns = ["Decision", "Count"]
    fig = px.pie(toss, names="Decision", values="Count",
                 color_discrete_sequence=["#f0a500", "#1f77b4"],
                 title="Bat vs Field after Toss")
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────
# ROW 2: Season-wise Matches + Toss Winner vs Match Winner
# ─────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Matches per Season")
    season_matches = matches.groupby("season").size().reset_index(name="Matches")
    fig = px.line(season_matches, x="season", y="Matches",
                  markers=True, title="Matches Played Each Season",
                  color_discrete_sequence=["#f0a500"])
    fig.update_layout(xaxis_title="Season", yaxis_title="Matches")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🎲 Does Winning Toss Help Win Match?")
    df_toss = df.copy()
    df_toss["toss_match_win"] = df_toss["toss_winner"] == df_toss["winner"]
    toss_effect = df_toss["toss_match_win"].value_counts().reset_index()
    toss_effect.columns = ["Won Match After Toss", "Count"]
    toss_effect["Won Match After Toss"] = toss_effect["Won Match After Toss"].map({True: "Yes", False: "No"})
    fig = px.pie(toss_effect, names="Won Match After Toss", values="Count",
                 color_discrete_sequence=["#2ecc71", "#e74c3c"],
                 title="Toss Winner = Match Winner?")
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────
# ROW 3: Top Venues + Player of the Match
# ─────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏟️ Top 10 Venues by Matches Hosted")
    venue_counts = df["venue"].value_counts().head(10).reset_index()
    venue_counts.columns = ["Venue", "Matches"]
    fig = px.bar(venue_counts, x="Matches", y="Venue", orientation="h",
                 color="Matches", color_continuous_scale="Blues",
                 title="Most Used Venues")
    fig.update_layout(yaxis=dict(categoryorder="total ascending"), height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🌟 Top 10 Player of the Match Awards")
    potm = df["player_of_match"].value_counts().head(10).reset_index()
    potm.columns = ["Player", "Awards"]
    fig = px.bar(potm, x="Awards", y="Player", orientation="h",
                 color="Awards", color_continuous_scale="Purples",
                 title="Most Player of the Match Awards")
    fig.update_layout(yaxis=dict(categoryorder="total ascending"), height=400)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────
# ROW 4: TOP BATSMEN & BOWLERS (from deliveries)
# ─────────────────────────────────────────
st.markdown("---")
st.header("🎯 Player Performance")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏏 Top 10 Run Scorers (All Time)")
    top_batsmen = deliveries.groupby("batter")["batsman_runs"].sum().reset_index()
    top_batsmen.columns = ["Batter", "Total Runs"]
    top_batsmen = top_batsmen.sort_values("Total Runs", ascending=False).head(10)
    fig = px.bar(top_batsmen, x="Total Runs", y="Batter", orientation="h",
                 color="Total Runs", color_continuous_scale="Reds",
                 title="Highest Run Scorers in IPL History")
    fig.update_layout(yaxis=dict(categoryorder="total ascending"), height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🎳 Top 10 Wicket Takers (All Time)")
    wickets = deliveries[deliveries["is_wicket"] == 1]
    # Exclude run outs (not credited to bowler)
    wickets = wickets[wickets["dismissal_kind"] != "run out"]
    top_bowlers = wickets.groupby("bowler")["is_wicket"].sum().reset_index()
    top_bowlers.columns = ["Bowler", "Wickets"]
    top_bowlers = top_bowlers.sort_values("Wickets", ascending=False).head(10)
    fig = px.bar(top_bowlers, x="Wickets", y="Bowler", orientation="h",
                 color="Wickets", color_continuous_scale="Greens",
                 title="Most Wickets in IPL History")
    fig.update_layout(yaxis=dict(categoryorder="total ascending"), height=400)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────
# ROW 5: Win by Runs / Win by Wickets
# ─────────────────────────────────────────
st.markdown("---")
st.header("📊 Match Result Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏃 Win Margin by Runs (Top Matches)")
    by_runs = df[df["result"] == "runs"].nlargest(10, "result_margin")[["winner","result_margin","season"]]
    fig = px.bar(by_runs, x="result_margin", y="winner", orientation="h",
                 color="result_margin", color_continuous_scale="Oranges",
                 hover_data=["season"],
                 title="Biggest Wins by Runs")
    fig.update_layout(yaxis_title="Winning Team", xaxis_title="Runs", height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🎯 Win Margin by Wickets (Top Matches)")
    by_wkts = df[df["result"] == "wickets"].nlargest(10, "result_margin")[["winner","result_margin","season"]]
    fig = px.bar(by_wkts, x="result_margin", y="winner", orientation="h",
                 color="result_margin", color_continuous_scale="Blues",
                 hover_data=["season"],
                 title="Biggest Wins by Wickets")
    fig.update_layout(yaxis_title="Winning Team", xaxis_title="Wickets", height=400)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────
# RAW DATA TABLE
# ─────────────────────────────────────────
st.markdown("---")
with st.expander("📋 View Raw Match Data"):
    st.dataframe(df[["season","date","team1","team2","winner","venue","player_of_match","toss_winner","toss_decision"]].reset_index(drop=True), use_container_width=True)

st.markdown("---")
st.caption("Built with ❤️ using Streamlit & Plotly | IPL Data Dashboard")