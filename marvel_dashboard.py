import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load data from memory (assume it's available)
@st.cache_data
def load_data():
    return pd.read_csv("datasets/characters_stats.csv")

marvel = load_data()

st.set_page_config(page_title="Marvel Dashboard", layout="wide")
st.title("\U0001F9B8 Marvel Superhero Stats Dashboard")

# Sidebar filters
alignments = st.sidebar.multiselect("Select Alignments:", marvel['Alignment'].dropna().unique())
filtered_data = marvel.copy()
if alignments:
    filtered_data = filtered_data[filtered_data['Alignment'].isin(alignments)]

# Tabs
overview, stats, comparisons = st.tabs(["Overview", "Stats", "Comparisons"])

with overview:
    st.subheader("Top Hero/Villain Highlights")
    top_hero = filtered_data.sort_values(by="Total", ascending=False).iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Top Character", top_hero['Name'])
    c2.metric("Alignment", top_hero['Alignment'])
    c3.metric("Total Power", int(top_hero['Total']))

    st.markdown("---")
    st.subheader("Alignment Distribution")
    fig, ax = plt.subplots()
    sns.countplot(data=filtered_data, x='Alignment', ax=ax, palette='Set2')
    st.pyplot(fig)

    st.subheader("Average Power Stats by Alignment")
    attributes = ['Intelligence', 'Strength', 'Speed', 'Durability', 'Power', 'Combat']
    avg_stats = filtered_data.groupby('Alignment')[attributes].mean()
    fig, ax = plt.subplots(figsize=(10,6))
    avg_stats.T.plot(kind='bar', ax=ax)
    st.pyplot(fig)

with stats:
    st.subheader("Attribute Distributions")
    selected_attr = st.selectbox("Select Attribute:", ['Intelligence', 'Strength', 'Speed', 'Durability', 'Power', 'Combat', 'Total'])
    fig, ax = plt.subplots()
    sns.histplot(filtered_data[selected_attr], bins=20, kde=True, ax=ax, color='purple')
    st.pyplot(fig)

    st.subheader("Attribute Correlation Heatmap")
    corr = filtered_data[attributes].corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)

with comparisons:
    st.subheader("Compare Two Characters")
    names = filtered_data['Name'].unique()
    char1 = st.selectbox("Select First Character:", names, index=0)
    char2 = st.selectbox("Select Second Character:", names, index=1)

    def get_stats(name):
        return filtered_data[filtered_data['Name'] == name][attributes].mean()

    s1 = get_stats(char1)
    s2 = get_stats(char2)

    comp_df = pd.DataFrame({char1: s1, char2: s2})
    st.bar_chart(comp_df)

    st.subheader("Scatterplot: Intelligence vs Combat")
    fig, ax = plt.subplots()
    sns.scatterplot(data=filtered_data, x='Intelligence', y='Combat', hue='Alignment', ax=ax)
    st.pyplot(fig)
