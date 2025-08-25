import streamlit as st
import pickle
import gzip
import pandas as pd
import requests
from streamlit_js_eval import streamlit_js_eval

# Function to fetch poster
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

    recommended_movies, recommended_posters = [], []

    for i in movies_list:
        title = movies.iloc[i[0]].title
        recommended_movies.append(title)
        recommended_posters.append(fetch_poster(title))

    return recommended_movies, recommended_posters

# Load and cache data
@st.cache_data
def load_data():
    movies_dict = pickle.load(open("movies_dict.pkl", "rb"))
    movies_df = pd.DataFrame(movies_dict)
    with gzip.open("similarity.pkl.gz", "rb") as f:
        similarity_matrix = pickle.load(f)
    return movies_df, similarity_matrix

movies, similarity = load_data()

# Streamlit page config
st.set_page_config(page_title="Movie Recommendation System", layout="wide")

# Get screen width dynamically using streamlit-js
screen_width = streamlit_js_eval(js_expressions="window.innerWidth")

# Determine number of columns based on screen width
if screen_width is not None:
    if screen_width > 1200:
        num_cols = 5
    elif screen_width > 768:
        num_cols = 3
    else:
        num_cols = 1
else:
    # Fallback if JS eval not supported: default to 3
    num_cols = 3

# Title and description
st.markdown("""
<div style="text-align:center; margin-bottom: 25px;">
    <h1 style="color:#333;">Movie Recommendation System</h1>
    <p style="color:#666; font-size:18px;">Find movies similar to your favorites, with posters powered by OMDb API</p>
</div>
""", unsafe_allow_html=True)

movie_options = ["Select a movie..."] + list(movies['title'].values)
selected_movie_name = st.selectbox(
    "Select a Movie",
    options=movie_options,
    index=0,
    help="Start typing to search your favorite movie"
)

# Recommend button and results
if st.button("Recommend") and selected_movie_name != "Select a movie...":
    with st.spinner("Fetching recommendations..."):
        recommendations, posters = recommend(selected_movie_name)

    st.markdown("---")

    cols = st.columns(num_cols, gap="medium")

    for idx, col in enumerate(cols):
        with col:
            if idx < len(posters):
                if posters[idx]:
                    st.image(posters[idx], use_column_width=True, caption=recommendations[idx])
                else:
                    st.image("https://via.placeholder.com/150?text=No+Image", caption=recommendations[idx])

# Footer
st.markdown("""
<div style="text-align:center; margin-top:40px; font-size:12px; color:#999;">
    Powered by Streamlit & OMDb API
</div>
""", unsafe_allow_html=True)
