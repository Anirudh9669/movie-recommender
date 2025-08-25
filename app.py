import streamlit as st
import pickle,gzip
import pandas as pd
import requests

# Function to fetch poster from OMDb API
def fetch_poster(title):
    api_key =  st.secrets["omdb_api_key"] # Replace with your OMDb key
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

# Load data
movies_dict = pickle.load(open("movies_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)

# Load similarity from compressed file
with gzip.open("similarity.pkl.gz", "rb") as f:
    similarity = pickle.load(f)

# Streamlit UI
st.set_page_config(page_title="Movie Recommender", page_icon="", layout="wide")

st.markdown(
    """
    <h1 style='text-align: center; color: white;'>Movie Recommendation System</h1>
    <p style='text-align: center; color: gray; font-size:18px;'>Find similar movies with posters powered by OMDb API</p>
    """,
    unsafe_allow_html=True
)

selected_movie_name = st.selectbox(
    "Select a Movie",
    movies['title'].values,
    index=None,
    placeholder="Type a movie title...",
)

if st.button("Recommend") and selected_movie_name:
    recommendations, posters = recommend(selected_movie_name)

    st.markdown("---")
    cols = st.columns(5, gap="large")

    for idx, col in enumerate(cols):
        with col:
            st.image(posters[idx], use_container_width=True, caption=recommendations[idx])
