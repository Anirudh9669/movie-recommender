import streamlit as st
import pickle
import gzip
import pandas as pd
import requests

# Function to fetch poster from OMDb API
def fetch_poster(title):
    api_key = st.secrets["omdb_api_key"]
    url = f"http://www.omdbapi.com/?t={title}&apikey={api_key}"
    data = requests.get(url).json()
    return data.get("Poster", None)

# Recommendation function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        title = movies.iloc[i[0]].title
        recommended_movies.append(title)
        recommended_posters.append(fetch_poster(title))

    return recommended_movies, recommended_posters

@st.cache_data
def load_data():
    movies_dict = pickle.load(open("movies_dict.pkl", "rb"))
    movies_df = pd.DataFrame(movies_dict)
    with gzip.open("similarity.pkl.gz", "rb") as f:
        similarity_matrix = pickle.load(f)
    return movies_df, similarity_matrix

with st.spinner("Loading data..."):
    movies, similarity = load_data()

st.set_page_config(page_title="Movie Recommendation System", layout="wide")

st.markdown("""
    <div style="text-align:center; margin-bottom: 25px;">
        <h1 style="color:#333;">Movie Recommendation System</h1>
        <p style="color:#666; font-size:18px;">Find movies similar to your favorites, with posters powered by OMDb API</p>
    </div>
""", unsafe_allow_html=True)

# Selectbox without placeholder option and with empty initial selection
selected_movie_name = st.selectbox(
    "Select a Movie",
    options=movies['title'].values,
    index=None,
    help="Start typing to search your favorite movie"
)

if st.button("Recommend") and selected_movie_name:
    with st.spinner("Fetching recommendations..."):
        recommendations, posters = recommend(selected_movie_name)

    st.markdown("---")

    # Always create 5 columns
    cols = st.columns(5, gap="medium")

    for idx, col in enumerate(cols):
        with col:
            poster = posters[idx]
            if poster:
                st.image(poster, use_container_width=True, caption=recommendations[idx])
            else:
                st.image("https://via.placeholder.com/150?text=No+Image", caption=recommendations[idx])

st.markdown("""
    <div style="text-align:center; margin-top:40px; font-size:12px; color:#999;">
        Powered by Streamlit & OMDb API
    </div>
""", unsafe_allow_html=True)
