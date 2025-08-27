import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load Data
@st.cache_data
def load_data():
    matches = pd.read_csv("datasets/matches.csv")
    deliveries = pd.read_csv("datasets/deliveries.csv")
    return matches, deliveries

matches, deliveries = load_data()

# Title and Sidebar
st.title("🏏 IPL Data Dashboard")
st.sidebar.title("Navigation")
option = st.sidebar.radio("Select Analysis", [
    "Overview",
    "Team Wins",
    "Top Batsmen",
    "Top Bowlers",
    "Powerplay Stats",
    "Super Over Stats",
    "Home vs Away Wins",
    "Player vs Team",
    "Season & Team Filter",            
    "Compare Players",                 
    "Performance Trends by Season"     
])

# Common Style
sns.set_style("whitegrid")

# Page Logic

if option == "Overview":
    st.markdown("### IPL Seasons Overview")
    matches_per_season = matches['season'].value_counts().sort_index()
    fig, ax = plt.subplots()
    sns.lineplot(x=matches_per_season.index, y=matches_per_season.values, marker='o', ax=ax)
    ax.set_title('Matches Played Per Season')
    st.pyplot(fig)

elif option == "Team Wins":
    st.markdown("### Most Match Wins by Teams")
    team_wins = matches['winner'].value_counts()
    fig, ax = plt.subplots()
    sns.barplot(x=team_wins.values, y=team_wins.index, ax=ax)
    st.pyplot(fig)

elif option == "Top Batsmen":
    st.markdown("### Top 10 Run Scorers")
    top_batsmen = deliveries.groupby('batsman')['batsman_runs'].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=top_batsmen.values, y=top_batsmen.index, palette='crest', ax=ax)
    st.pyplot(fig)

elif option == "Top Bowlers":
    st.markdown("### Most Economical Bowlers (min 300 balls)")
    legal = deliveries[(deliveries['wide_runs'] == 0) & (deliveries['noball_runs'] == 0)]
    balls = legal.groupby('bowler').size()
    runs = legal.groupby('bowler')['total_runs'].sum()
    economy = (runs / balls) * 6
    economy = economy[balls >= 300].sort_values().head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=economy.values, y=economy.index, ax=ax)
    st.pyplot(fig)

elif option == "Powerplay Stats":
    st.markdown("### Powerplay Runs by Team")
    pp = deliveries[deliveries['over'] <= 6]
    pp_runs = pp.groupby('batting_team')['total_runs'].sum().sort_values(ascending=False)
    fig, ax = plt.subplots()
    sns.barplot(x=pp_runs.values, y=pp_runs.index, ax=ax)
    st.pyplot(fig)

elif option == "Super Over Stats":
    st.markdown("### Super Over Performance")
    so = deliveries[deliveries['is_super_over'] == 1]
    so_runs = so.groupby('batting_team')['total_runs'].sum().sort_values(ascending=False)
    fig, ax = plt.subplots()
    sns.barplot(x=so_runs.values, y=so_runs.index, ax=ax)
    st.pyplot(fig)

elif option == "Home vs Away Wins":
    st.markdown("### Home vs Away Win Count")
    matches['home_win'] = matches['team1'] == matches['winner']
    matches['away_win'] = matches['team2'] == matches['winner']
    fig, ax = plt.subplots()
    sns.barplot(x=["Home Wins", "Away Wins"], y=[matches['home_win'].sum(), matches['away_win'].sum()],
                palette=["#bcaaa4", "#a1887f"], ax=ax)
    st.pyplot(fig)

elif option == "Player vs Team":
    player = st.selectbox("Select a Player", sorted(deliveries['batsman'].unique()))
    player_data = deliveries[deliveries['batsman'] == player]
    team_runs = player_data.groupby('bowling_team')['batsman_runs'].sum().sort_values(ascending=False)
    fig, ax = plt.subplots()
    sns.barplot(x=team_runs.values, y=team_runs.index, ax=ax)
    ax.set_title(f'Runs Scored by {player} vs Each Team')
    st.pyplot(fig)

# 🎯 Match filters by season/team
elif option == "Season & Team Filter":
    st.markdown("### Filter Matches by Season and Team")
    season = st.selectbox("Select Season", sorted(matches['season'].unique()))
    team = st.selectbox("Select Team", sorted(set(matches['team1'].unique()).union(matches['team2'].unique())))
    filtered = matches[(matches['season'] == season) & ((matches['team1'] == team) | (matches['team2'] == team))]
    st.write(f"Showing {len(filtered)} matches for **{team}** in **{season}**")
    st.dataframe(filtered[['date', 'team1', 'team2', 'winner', 'venue']].reset_index(drop=True))

# 📈 Compare batting/bowling between two players
elif option == "Compare Players":
    st.markdown("### Compare Two Players")

    players = sorted(set(deliveries['batsman'].unique()) & set(deliveries['bowler'].unique()))
    player1 = st.selectbox("Select Player 1", players, index=0)
    player2 = st.selectbox("Select Player 2", players, index=1)

    tab = st.radio("Compare By", ["Batting", "Bowling"])

    if tab == "Batting":
        bat1 = deliveries[deliveries['batsman'] == player1]['batsman_runs'].sum()
        bat2 = deliveries[deliveries['batsman'] == player2]['batsman_runs'].sum()
        fig, ax = plt.subplots()
        sns.barplot(x=[bat1, bat2], y=[player1, player2], ax=ax, palette="pastel")
        ax.set_xlabel("Total Runs")
        st.pyplot(fig)

    else:  # Bowling comparison
        wickets = deliveries[deliveries['player_dismissed'].notna()]
        bowl1 = wickets[wickets['bowler'] == player1]['player_dismissed'].count()
        bowl2 = wickets[wickets['bowler'] == player2]['player_dismissed'].count()
        fig, ax = plt.subplots()
        sns.barplot(x=[bowl1, bowl2], y=[player1, player2], ax=ax, palette="muted")
        ax.set_xlabel("Total Wickets")
        st.pyplot(fig)

# ⏳ Performance over time
elif option == "Performance Trends by Season":
    st.markdown("### Season-wise Performance of a Player")
    player = st.selectbox("Select Player", sorted(deliveries['batsman'].unique()))
    merged = deliveries.merge(matches[['id', 'season']], left_on='match_id', right_on='id')
    season_runs = merged[merged['batsman'] == player].groupby('season')['batsman_runs'].sum()

    fig, ax = plt.subplots()
    sns.lineplot(x=season_runs.index, y=season_runs.values, marker='o', ax=ax, color="#a1887f")
    ax.set_title(f'{player} - Runs per Season')
    ax.set_ylabel("Runs")
    st.pyplot(fig)
