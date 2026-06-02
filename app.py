import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Page Configuration (This styles the browser tab)
st.set_page_config(page_title="IMDb 2024 Analytics", page_icon="🎬", layout="wide")

st.title("🎬 IMDb 2024 Data Scraping & Visualizations")
st.markdown("Welcome to the interactive Capstone dashboard. This application pulls processed movie metadata directly from our local **SQLite Database**.")

# 2. Connect to our SQL Database and load the data into Pandas
conn = sqlite3.connect("imdb_movies.db")
df = pd.read_sql_query("SELECT * FROM movies", conn)
conn.close()

# --- SIDEBAR INTERACTIVE FILTERS ---
st.sidebar.header("🔍 Interactive Filter Applications")

# Filter A: Genre Multi-select dropdown
all_genres = sorted(list(df['Genre'].unique()))
selected_genres = st.sidebar.multiselect("Select Genres:", options=all_genres, default=all_genres)

# Filter B: Rating Slider (e.g., Only show movies rated > 7.0)
min_rating = st.sidebar.slider("Minimum IMDb Rating:", min_value=0.0, max_value=10.0, value=5.0, step=0.1)

# Filter C: Voting Counts Slider
max_votes_in_db = int(df['Voting_Counts'].max())
selected_votes = st.sidebar.slider("Minimum Votes Received:", min_value=0, max_value=max_votes_in_db, value=1000, step=1000)

# Filter D: Duration Slider (Runtime in Minutes)
min_duration, max_duration = st.sidebar.slider("Movie Duration Range (Minutes):", min_value=60, max_value=180, value=(90, 165))

# --- APPLYING THE FILTERS TO THE DATA ---
# This updates the entire dataset instantly when a user changes a filter on the left
filtered_df = df[
    (df['Genre'].isin(selected_genres)) &
    (df['Ratings'] >= min_rating) &
    (df['Voting_Counts'] >= selected_votes) &
    (df['Duration'] >= min_duration) &
    (df['Duration'] <= max_duration)
]

# --- DISPLAY DATA TABLE ---
st.subheader("📋 Dynamic Data Explorer")
st.markdown(f"Showing **{len(filtered_df)}** movies matching your active filter criteria.")
st.dataframe(filtered_df, use_container_width=True)

st.write("---") # Visual breaking line

# --- VISUALIZATIONS SECTION ---
st.subheader("📊 Business Insight Visualizations")

# Split the dashboard into two clean side-by-side columns
col1, col2 = st.columns(2)

with col1:
    # Use Case 1: Top 10 Movies by Rating & Votes
    st.markdown("### 🏆 Top Movies by Rating")
    if not filtered_df.empty:
        top_10 = filtered_df.nlargest(10, 'Ratings')
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x="Ratings", y="Movie_Name", data=top_10, ax=ax, palette="viridis", hue="Movie_Name", legend=False)
        ax.set_xlabel("IMDb Rating")
        ax.set_ylabel("")
        st.pyplot(fig)
    else:
        st.warning("No data matches current filters to display chart.")

with col2:
    # Use Case 2: Genre Distribution Bar Chart
    st.markdown("### 🎭 Movie Distribution by Genre")
    if not filtered_df.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.countplot(x="Genre", data=filtered_df, ax=ax, palette="magma", hue="Genre", legend=False)
        ax.set_xlabel("Genre Name")
        ax.set_ylabel("Number of Movies")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.warning("No data matches current filters to display chart.")

st.write("---")

col3, col4 = st.columns(2)

with col3:
    # Use Case 3: Duration Insights Across Genres
    st.markdown("### 🕒 Average Runtime by Genre")
    if not filtered_df.empty:
        avg_dur = filtered_df.groupby('Genre')['Duration'].mean().reset_index()
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x="Duration", y="Genre", data=avg_dur, ax=ax, palette="coolwarm", hue="Genre", legend=False)
        ax.set_xlabel("Average Duration (Minutes)")
        st.pyplot(fig)
    else:
        st.warning("No data available.")

with col4:
    # Use Case 4: Correlation Analysis (Scatter plot of Rating vs Votes)
    st.markdown("### 📈 Relationship: Ratings vs. Voting Counts")
    if not filtered_df.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.scatterplot(x="Ratings", y="Voting_Counts", data=filtered_df, ax=ax, hue="Genre", s=100)
        ax.set_xlabel("IMDb Rating")
        ax.set_ylabel("Total Votes")
        st.pyplot(fig)
    else:
        st.warning("No data available.")

st.write("---")

# Use Case 5: Duration Extremes (Cards Display)
st.markdown("### 💎 Movie Duration Extremes (Shortest & Longest)")
if not filtered_df.empty:
    shortest_movie = filtered_df.loc[filtered_df['Duration'].idxmin()]
    longest_movie = filtered_df.loc[filtered_df['Duration'].idxmax()]
    
    card1, card2 = st.columns(2)
    card1.metric(label="⏱️ Shortest Movie Runtime", value=f"{shortest_movie['Duration']} mins", delta=shortest_movie['Movie_Name'])
    card2.metric(label="🎥 Longest Movie Runtime", value=f"{longest_movie['Duration']} mins", delta=longest_movie['Movie_Name'])
else:
    st.warning("No extreme metrics found.")