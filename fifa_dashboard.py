import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load data from memory (assume it's available)
@st.cache_data
def load_data():
    return pd.read_csv("datasets/players_20.csv")

fifa = load_data()

st.set_page_config(page_title="FIFA 20 Dashboard", layout="wide")
st.title("\U0001F3C0 FIFA 20 Players Analysis Dashboard")

# Sidebar filters
nationalities = st.sidebar.multiselect("Select Nationalities:", fifa['nationality'].unique())
clubs = st.sidebar.multiselect("Select Clubs:", fifa['club'].dropna().unique())
positions = st.sidebar.multiselect("Select Positions:", fifa['player_positions'].dropna().unique())

filtered_data = fifa.copy()
if nationalities:
    filtered_data = filtered_data[filtered_data['nationality'].isin(nationalities)]
if clubs:
    filtered_data = filtered_data[filtered_data['club'].isin(clubs)]
if positions:
    filtered_data = filtered_data[filtered_data['player_positions'].isin(positions)]

# Tabs
overview, stats, comparisons = st.tabs(["Overview", "Stats", "Comparisons"])

with overview:
    st.subheader("Top Player Highlights")
    top_player = filtered_data.sort_values(by="overall", ascending=False).iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Top Player", top_player['short_name'])
    c2.metric("Overall Rating", int(top_player['overall']))
    c3.metric("Potential", int(top_player['potential']))

    st.markdown("---")
    st.subheader("Top 10 Nationalities by Player Count")
    top_nations = filtered_data['nationality'].value_counts().head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=top_nations.values, y=top_nations.index, ax=ax)
    st.pyplot(fig)

    st.subheader("Top 10 Clubs by Average Overall")
    top_clubs = filtered_data.groupby('club')['overall'].mean().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=top_clubs.values, y=top_clubs.index, ax=ax)
    st.pyplot(fig)

with stats:
    st.subheader("Attribute Distributions")
    selected_attr = st.selectbox("Select Attribute to View Distribution:", ['age', 'height_cm', 'weight_kg', 'overall', 'potential'])
    fig, ax = plt.subplots()
    sns.histplot(filtered_data[selected_attr], bins=30, kde=True, ax=ax)
    st.pyplot(fig)

    st.subheader("Correlation Heatmap of Key Attributes")
    attr_cols = ['pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic']
    corr_data = filtered_data[attr_cols].dropna()
    fig, ax = plt.subplots()
    sns.heatmap(corr_data.corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

with comparisons:
    st.subheader("Compare Two Players")
    player_names = filtered_data['short_name'].unique()
    player1 = st.selectbox("Select First Player:", player_names, index=0)
    player2 = st.selectbox("Select Second Player:", player_names, index=1)

    def get_player_stats(name):
        return filtered_data[filtered_data['short_name'] == name][['pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic']].mean()

    p1_stats = get_player_stats(player1)
    p2_stats = get_player_stats(player2)

    comp_df = pd.DataFrame({player1: p1_stats, player2: p2_stats})
    st.bar_chart(comp_df)

    st.subheader("Wage vs Overall Scatterplot")
    if 'wage_eur' in filtered_data.columns:
        fig, ax = plt.subplots()
        sns.scatterplot(data=filtered_data, x='overall', y='wage_eur', hue='player_positions', ax=ax)
        st.pyplot(fig)
