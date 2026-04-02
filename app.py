import streamlit as st
import pickle
import pandas as pd
import random

# --- 1. Page Configuration & CSS ---
st.set_page_config(page_title="FilmFinder Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1 { color: #E50914; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 800; letter-spacing: -1px; }
    
    .movie-card {
        background-color: #1a1c23;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        transition: transform 0.3s;
        min-height: 160px; 
    }
    .movie-card:hover { transform: scale(1.02); background-color: #252833; }
    
    .stSelectbox label { color: #ffffff !important; font-size: 1.2rem; }
    
    .stButton>button {
        background-color: #E50914;
        color: white;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        border-radius: 4px;
        width: 100%;
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: transparent; border-radius: 4px 4px 0px 0px; padding-top: 10px; color: #fff; }
    .stTabs [aria-selected="true"] { border-bottom: 3px solid #E50914; color: #fff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Data Loading & Extraction ---
movies_dict = pickle.load(open('artifacts/movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))

# Extract unique actors, directors, and genres for dropdowns
all_actors, all_directors, all_genres = set(), set(), set()

for cast_list in movies['cast']: all_actors.update(cast_list)
for crew_list in movies['crew']: all_directors.update(crew_list)
for genre_list in movies['genres']: all_genres.update(genre_list)

actor_list = sorted(list(all_actors))
director_list = sorted(list(all_directors))
genre_list = sorted(list(all_genres))

# Hex colors for genres
GENRE_COLORS = {
    'Animation': '#345b8e', 'Fantasy': '#8b6b32', 'Adventure': '#715285', 'Action': '#dc3545',
    'Comedy': '#e0a800', 'Crime': '#343a40', 'Documentary': '#17a2b8', 'Drama': '#28a745',
    'Family': '#e83e8c', 'History': '#6c757d', 'Horror': '#800000', 'Music': '#117a8b',
    'Mystery': '#6610f2', 'Romance': '#d63384', 'Science Fiction': '#0dcaf0', 'TV Movie': '#20c997',
    'Thriller': '#e53e3e', 'War': '#5c4033', 'Western': '#fd7e14'
}

def get_genre_html(genres):
    html = "<div style='margin: 8px 0;'>"
    for g in genres[:3]: 
        color = GENRE_COLORS.get(g, '#555555')
        html += f"<span style='background-color: {color}; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; color: white; margin-right: 6px; display: inline-block;'>{g}</span>"
    html += "</div>"
    return html

# --- 3. Logic Functions ---
def extract_data(row):
    return {'title': row['title'], 'year': row['year'], 'rating': row['vote_average'], 'genres': row['genres']}

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:7]
    return [extract_data(movies.iloc[i[0]]) for i in movies_list]

def surprise_me():
    top_200 = movies.sort_values(by='vote_average', ascending=False).head(200)
    return [extract_data(row) for _, row in top_200.sample(3).iterrows()]

def recommend_by_actor(actor_name):
    actor_movies = movies[movies['cast'].apply(lambda x: actor_name in x)]
    top = actor_movies.sort_values(by='vote_average', ascending=False).head(6)
    return [extract_data(row) for _, row in top.iterrows()]

def recommend_by_director(director_name):
    director_movies = movies[movies['crew'].apply(lambda x: director_name in x)]
    top = director_movies.sort_values(by='vote_average', ascending=False).head(6)
    return [extract_data(row) for _, row in top.iterrows()]

def recommend_by_genre(genre_name):
    genre_movies = movies[movies['genres'].apply(lambda x: genre_name in x)]
    top = genre_movies.sort_values(by='vote_average', ascending=False).head(12)
    return [extract_data(row) for _, row in top.iterrows()]

def render_movie_grid(recommendations, columns_per_row=3, border_color="#E50914"):
    """Helper function to render grids dynamically"""
    # Create enough columns to hold all recommendations
    cols = []
    for _ in range(0, len(recommendations), columns_per_row):
        cols.extend(st.columns(columns_per_row))
        
    for i, movie in enumerate(recommendations):
        with cols[i]:
            genres_pills = get_genre_html(movie['genres'])
            st.markdown(f"""
                <div class="movie-card" style="border-left: 5px solid {border_color};">
                    <h3 style='margin:0; color:white;'>{movie['title']}</h3>
                    {genres_pills}
                    <p style='color:#999; margin:0;'>📅 {int(movie['year'])} &nbsp; | &nbsp; <span style='color:#ffc107; font-weight:bold;'>⭐ {round(movie['rating'], 1)}/10</span></p>
                </div>
            """, unsafe_allow_html=True)

# --- 4. UI Layout ---
st.title('Movies 4 You')
st.subheader('Discover Movies Based on Your Taste')
st.write("##")

# Four Tabs now!
tab1, tab2, tab3, tab4 = st.tabs(["🍿 Find Similar Movies", "🎭 Top by Actor", "🎬 Top by Director", "🌟 Top by Genre"])

# --- TAB 1: Movie Search & Surprise Me ---
with tab1:
    st.markdown("<p style='color:#ffffff; font-size: 1.1rem; margin-bottom: 5px;'>Start typing a movie you enjoyed:</p>", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1: selected_movie = st.selectbox('Movie', movies['title'].values, label_visibility="collapsed")
        with col2: find_btn = st.button('Find Matches')
        with col3: surprise_btn = st.button('🎲 Surprise Me')

    st.divider()

    if find_btn:
        st.write(f"### Because you liked **{selected_movie}**, you might enjoy:")
        render_movie_grid(recommend(selected_movie), border_color="#E50914")

    elif surprise_btn:
        st.write("### 🎲 Curated Top-Tier Picks For You:")
        render_movie_grid(surprise_me(), border_color="#ffc107")

# --- TAB 2: Actor Search ---
with tab2:
    st.markdown("<p style='color:#ffffff; font-size: 1.1rem; margin-bottom: 5px;'>Select your favorite actor:</p>", unsafe_allow_html=True)
    with st.container():
        col_a, col_b = st.columns([3, 1])
        with col_a: selected_actor = st.selectbox('Actor', actor_list, label_visibility="collapsed")
        with col_b: actor_btn = st.button('Find Best Movies', key='actor_btn')
            
    st.divider()
    
    if actor_btn:
        recs = recommend_by_actor(selected_actor)
        if not recs:
            st.warning(f"We don't have enough data for {selected_actor} yet!")
        else:
            st.write(f"### Top critically acclaimed movies starring **{selected_actor}**:")
            render_movie_grid(recs, border_color="#4CAF50")

# --- TAB 3: Director Search ---
with tab3:
    st.markdown("<p style='color:#ffffff; font-size: 1.1rem; margin-bottom: 5px;'>Select a visionary director:</p>", unsafe_allow_html=True)
    with st.container():
        col_c, col_d = st.columns([3, 1])
        with col_c: selected_director = st.selectbox('Director', director_list, label_visibility="collapsed")
        with col_d: dir_btn = st.button('Find Masterpieces', key='dir_btn')
            
    st.divider()
    
    if dir_btn:
        recs = recommend_by_director(selected_director)
        if not recs:
            st.warning(f"We don't have enough data for {selected_director} yet!")
        else:
            st.write(f"### Top 6 highest-rated films directed by **{selected_director}**:")
            render_movie_grid(recs, border_color="#9C27B0") # Purple accent for directors

# --- TAB 4: Genre Search ---
with tab4:
    st.markdown("<p style='color:#ffffff; font-size: 1.1rem; margin-bottom: 5px;'>Pick a genre to explore:</p>", unsafe_allow_html=True)
    with st.container():
        col_e, col_f = st.columns([3, 1])
        with col_e: selected_genre = st.selectbox('Genre', genre_list, label_visibility="collapsed")
        with col_f: genre_btn = st.button('Explore Genre', key='genre_btn')
            
    st.divider()
    
    if genre_btn:
        recs = recommend_by_genre(selected_genre)
        st.write(f"### Top 12 must-watch **{selected_genre}** movies:")
        # Uses the same grid helper, but it will automatically expand to 4 rows for 12 items!
        render_movie_grid(recs, border_color="#00BCD4") # Cyan accent for genres