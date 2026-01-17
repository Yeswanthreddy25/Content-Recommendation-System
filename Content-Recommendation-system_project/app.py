import streamlit as st
import pandas as pd
import joblib
import os
import json
import random
import requests
import altair as alt
from ytmusicapi import YTMusic

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SoundBox - Mood Music",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONFIG & DATA LOADING ---
@st.cache_resource
def load_data_pipeline():
    if os.path.exists('model.pkl'):
        return joblib.load('model.pkl')
    return None

def load_liked_songs():
    if os.path.exists('liked_songs.json'):
        with open('liked_songs.json', 'r') as f:
            return json.load(f)
    return []

def save_liked_songs(liked_list):
    with open('liked_songs.json', 'w') as f:
        json.dump(liked_list, f)

# Initialize Session State
if 'liked_songs' not in st.session_state:
    st.session_state.liked_songs = load_liked_songs()
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'Dashboard'
if 'selected_emoji' not in st.session_state:
    st.session_state.selected_emoji = None
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'current_video_id' not in st.session_state:
    st.session_state.current_video_id = None
if 'current_playing_song_name' not in st.session_state:
    st.session_state.current_playing_song_name = None
if 'last_selected_lang' not in st.session_state:
    st.session_state.last_selected_lang = 'English'

# Load Assets
artifacts = load_data_pipeline()
if artifacts:
    df_songs = artifacts['data']
    # Ensure language column exists for compatibility
    if 'language' not in df_songs.columns:
        df_songs['language'] = 'English'
else:
    st.error("Dataset not found. Please run `train_model.py` first to fetch data from iTunes.")
    st.stop()

# --- HELPER FUNCTIONS ---
def search_itunes(query, limit=10):
    url = "https://itunes.apple.com/search"
    params = {'term': query, 'media': 'music', 'entity': 'song', 'limit': limit}
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            results = []
            for item in response.json().get('results', []):
                results.append({
                    'id': str(item.get('trackId')),
                    'name': item.get('trackName'),
                    'artist': item.get('artistName'),
                    'album': item.get('collectionName'),
                    'image_url': item.get('artworkUrl100').replace('100x100', '600x600'),
                    'preview_url': item.get('previewUrl'),
                })
            return results
    except:
        return []
    return []

@st.cache_resource
def get_ytmusic():
    return YTMusic()

def get_youtube_video_id(query):
    try:
        yt = get_ytmusic()
        results = yt.search(query, filter='songs', limit=1)
        if results:
            return results[0]['videoId']
        # Fallback to general search if song filter fails
        results = yt.search(query, limit=1)
        if results:
            return results[0]['videoId']
    except Exception as e:
        print(f"YouTube Search Error: {e}")
    return None

# --- CUSTOM CSS (NETFLIX STYLE) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Poppins:wght@400;700&display=swap');

    /* MAIN BACKGROUND */
    .stApp {
        background-color: #141414;
        color: #ffffff;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* HIDE SIDEBAR */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* NAVBAR */
    .nav-container {
        display: flex;
        justify_content: space-between;
        align_items: center;
        padding: 10px 20px;
        background: linear-gradient(to bottom, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0) 100%);
        position: sticky;
        top: 0;
        z-index: 999;
    }
    
    /* BRANDING */
    .netflix-brand {
        font-family: 'Bebas Neue', sans-serif;
        color: #E50914;
        font-size: 3.5rem; /* Increased from 2.5rem */
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        letter-spacing: 2px;
    }
    
    /* NAV BUTTONS */
    .stButton button {
        background-color: transparent !important;
        color: #e5e5e5 !important;
        border: none !important;
        font-weight: bold;
        transition: color 0.3s;
    }
    .stButton button:hover {
        color: #b3b3b3 !important;
    }
    .stButton button:focus {
        color: #ffffff !important;
    }
    
    /* PRIMARY (ACTIVE) BUTTON HIGHLIGHT */
    div[data-testid="stButton"] button[kind="primary"] {
        background-color: #E50914 !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 0 15px rgba(229, 9, 20, 0.4);
    }
    
    /* HERO BANNER */
    .hero-container {
        position: relative;
        width: 100%;
        height: 400px;
        background: linear-gradient(to top, #141414 10%, transparent 100%),
                    url('https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?q=80&w=2070&auto=format&fit=crop'); 
        background-size: cover;
        background-position: center;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        padding: 40px;
        margin-bottom: 20px;
        border-radius: 8px;
    }
    
    .hero-title {
        font-size: 5rem; /* Increased from 4rem */
        font-weight: 800;
        color: white;
        margin-bottom: 10px;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.8);
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: #e5e5e5;
        max-width: 600px;
        margin-bottom: 20px;
        text-shadow: 1px 1px 5px rgba(0,0,0,0.8);
    }
    
    /* MOOD ROW */
    .mood-item {
        background-color: #181818;
        border: 1px solid #333;
        border-radius: 4px;
        padding: 10px;
        text-align: center;
        cursor: pointer;
        transition: transform 0.2s, border-color 0.2s;
    }
    .mood-item:hover {
        transform: scale(1.05);
        border-color: #E50914;
    }
    
    /* SONG CARD (POSTER STYLE) */
    .song-card {
        background-color: #2F2F2F;
        border-radius: 4px;
        overflow: hidden;
        transition: transform 0.3s;
        margin-bottom: 20px;
        height: 100%;
        position: relative;
    }
    .song-card:hover {
        transform: scale(1.05);
        z-index: 10;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }
    .song-card img {
        width: 100%;
        aspect-ratio: 1/1;
        object-fit: cover;
    }
    .card-content {
        padding: 10px;
    }
    .song-title {
        font-size: 0.9rem;
        font-weight: bold;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        color: white;
    }
    .song-artist {
        font-size: 0.75rem;
        color: #b3b3b3;
    }
</style>
""", unsafe_allow_html=True)

# --- NAVBAR & NAVIGATION ---
# Top Bar: Brand | Navigation | Language
c_brand, c_nav1, c_nav2, c_nav3, c_lang = st.columns([2, 1, 1, 1, 1.5])

with c_brand:
    st.markdown('<div class="netflix-brand">EMOTIFY</div>', unsafe_allow_html=True)

with c_nav1:
    if st.button("Home"):
        st.session_state.current_view = 'Dashboard'
with c_nav2:
    if st.button("My List"): # Netflix terminology for Favorites
        st.session_state.current_view = 'Favorites'
with c_nav3:
    if st.button("Search"):
        st.session_state.current_view = 'Search'

with c_lang:
    # Minimalist language selector
    available_langs = ['English', 'Hindi', 'Spanish', 'Korean', 'Telugu']
    if 'language' in df_songs.columns:
        data_langs = sorted(df_songs['language'].dropna().unique().tolist())
        available_langs = sorted(list(set(available_langs + data_langs)))
        
    default_index = 0
    if 'English' in available_langs:
        default_index = available_langs.index('English')
    
    # Using label_visibility="collapsed" for cleaner look
    selected_lang = st.selectbox("Lang", available_langs, index=default_index, label_visibility="collapsed")
    
    # DETECT LANGUAGE CHANGE
    if selected_lang != st.session_state.last_selected_lang:
        st.session_state.last_selected_lang = selected_lang
        # If a mood was selected, automatically refresh recommendations for the new language
        if st.session_state.selected_emoji:
            mask = (df_songs['predicted_emoji'] == st.session_state.selected_emoji)
            if 'language' in df_songs.columns:
                mask = mask & (df_songs['language'] == selected_lang)
            recs = df_songs[mask]
            if not recs.empty:
                st.session_state.recommendations = recs.sample(min(20, len(recs))).to_dict('records')
            else:
                st.session_state.recommendations = []
        else:
            st.session_state.recommendations = [] # Clear if no mood selected
        st.rerun()

# --- MAIN CONTENT ---
view = st.session_state.current_view

# --- GLOBAL VIDEO PLAYER ---
if st.session_state.current_video_id:
    # Moved to "Middle" (Main Column) as requested
    st.markdown("---")
    c_video, c_info = st.columns([2, 1])
    # Custom Autoplay Embed
    embed_url = f"https://www.youtube.com/embed/{st.session_state.current_video_id}?autoplay=1&rel=0"
    st.components.v1.html(f"""
        <iframe width="100%" height="450" src="{embed_url}" 
                frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen style="border-radius:12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
        </iframe>
    """, height=480)
    
    if st.button("Stop Player", key="close_player_main"):
        st.session_state.current_video_id = None
        st.session_state.current_playing_song_name = None
        st.rerun()
    st.markdown("---")

if view == 'Dashboard':
    # --- HERO SECTION ---
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">FEEL THE BEAT</div>
        <div class="hero-subtitle">Discover the perfect soundtrack for your current mood. Select an option below to start listening.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- MOOD ROW (Horizontal) ---
    st.markdown("### 🎭 Browse by Mood")
    emojis = {
        'Happy': '😊', 'Sad': '😢', 'Relaxed': '😌', 
        'Energy': '🔥', 'Focus': '💪', 'Sleep': '😴',
        'Love': '🥰', 'Angry': '😠', 'Party': '🎉'
    }
    
    # Create a horizonatal scrollable-like feel with columns
    cols = st.columns(len(emojis))
    for i, (label, emoji) in enumerate(emojis.items()):
        with cols[i]:
            # Highlight logic: use primary type for selected emoji
            is_selected = (st.session_state.selected_emoji == emoji)
            if st.button(f"{emoji}\n{label}", 
                         key=f"mood_{i}", 
                         use_container_width=True,
                         type="primary" if is_selected else "secondary"):
                st.session_state.selected_emoji = emoji
                
                # Filter Logic
                mask = (df_songs['predicted_emoji'] == emoji)
                if 'language' in df_songs.columns:
                    mask = mask & (df_songs['language'] == selected_lang)
                recs = df_songs[mask]
                
                if not recs.empty:
                    st.session_state.recommendations = recs.sample(min(20, len(recs))).to_dict('records') # Increased sample size for grid
                else:
                    st.warning(f"No {selected_lang} songs found for this mood.")
                    st.session_state.recommendations = []

    # --- SONG POSTER GRID ---
    st.markdown(f"### 🍿 Top Picks for You ({selected_lang})")
    
    active_list = st.session_state.recommendations
    if not active_list:
         # Default/Trending
         if 'language' in df_songs.columns:
             default_recs = df_songs[df_songs['language'] == selected_lang]
             if not default_recs.empty:
                 active_list = default_recs.sample(min(12, len(default_recs))).to_dict('records')
         
         if not active_list:
             active_list = df_songs.sample(min(12, len(df_songs))).to_dict('records')
         
         st.caption("Trending Now")
    else:
        st.caption(f"Because you're feeling {st.session_state.selected_emoji}")

    # Display Grid (4 columns)
    cols = st.columns(4)
    for i, song in enumerate(active_list):
        with cols[i % 4]:
            # CLICKABLE POSTER WRAPPER
            # We use a button that looks like a card
            st.markdown(f"""
            <div class="song-card">
                <img src="{song.get('image_url') or 'https://placehold.co/300x300'}" />
                <div class="card-content">
                    <div class="song-title">{song['name']}</div>
                    <div class="song-artist">{song['artist']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action Buttons below the card
            c_play, c_like = st.columns([3, 1])
            with c_play:
                # MAKING THIS THE MAIN ACTION - Clicking Play also covers the 'poster' intent
                if st.button("▶ Play", key=f"grid_play_{song['id']}", use_container_width=True, type="primary"):
                     st.toast(f"Starting {song['name']}...")
                     vid_id = get_youtube_video_id(f"{song['name']} {song['artist']} audio")
                     if vid_id:
                         st.session_state.current_video_id = vid_id
                         st.session_state.current_playing_song_name = song['name']
                         st.rerun()
            with c_like:
                is_liked = any(s['id'] == song['id'] for s in st.session_state.liked_songs)
                if st.button("❤️" if is_liked else "➕", key=f"grid_like_{song['id']}", use_container_width=True):
                    if is_liked:
                        st.session_state.liked_songs = [s for s in st.session_state.liked_songs if s['id'] != song['id']]
                    else:
                        st.session_state.liked_songs.append(song)
                    save_liked_songs(st.session_state.liked_songs)
                    st.rerun()

if view == 'Search':
    st.markdown(f"### 🔍 Find Your Track ({selected_lang})")
    search_query = st.text_input("", placeholder=f"Search {selected_lang} songs...")
    
    if search_query:
        st.markdown(f"Results for '{search_query}'")
        
        # Append Language to Query to respect filter
        full_query = f"{search_query} {selected_lang}"
        results = search_itunes(full_query) 
        
        cols = st.columns(4)
        for i, song in enumerate(results):
            with cols[i % 4]:
                st.markdown(f"""
                <div class="song-card">
                    <img src="{song.get('image_url') or 'https://placehold.co/300x300'}" />
                    <div class="card-content">
                        <div class="song-title">{song['name']}</div>
                        <div class="song-artist">{song['artist']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Action Buttons
                c_play, c_like = st.columns([3, 1])
                with c_play:
                    if st.button("▶ Play Now", key=f"s_play_{song['id']}", use_container_width=True, type="primary"):
                         st.toast(f"Loading {song['name']}...")
                         vid_id = get_youtube_video_id(f"{song['name']} {song['artist']} audio")
                         if vid_id:
                             st.session_state.current_video_id = vid_id
                             st.session_state.current_playing_song_name = song['name']
                             st.rerun()
                with c_like:
                    is_liked = any(s['id'] == song['id'] for s in st.session_state.liked_songs)
                    if st.button("❤️" if is_liked else "➕", key=f"s_like_{song['id']}", use_container_width=True):
                         if is_liked:
                            st.session_state.liked_songs = [s for s in st.session_state.liked_songs if s['id'] != song['id']]
                         else:
                            st.session_state.liked_songs.append(song)
                         save_liked_songs(st.session_state.liked_songs)
                         st.rerun()

if view == 'Favorites':
    st.markdown("### ❤️ My List")
    if st.session_state.liked_songs:
        cols = st.columns(4)
        for i, song in enumerate(st.session_state.liked_songs):
            with cols[i % 4]:
                st.markdown(f"""
                <div class="song-card">
                    <img src="{song.get('image_url') or 'https://placehold.co/300x300'}" />
                    <div class="card-content">
                        <div class="song-title">{song['name']}</div>
                        <div class="song-artist">{song['artist']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c_play, c_remove = st.columns([3, 1])
                with c_play:
                    if st.button("▶ Play Now", key=f"f_play_{song['id']}", use_container_width=True, type="primary"):
                         st.toast(f"Starting...")
                         vid_id = get_youtube_video_id(f"{song['name']} {song['artist']} audio")
                         if vid_id:
                             st.session_state.current_video_id = vid_id
                             st.session_state.current_playing_song_name = song['name']
                             st.rerun()
                with c_remove:
                    if st.button("❌", key=f"f_remove_{song['id']}", use_container_width=True):
                        st.session_state.liked_songs.remove(song)
                        save_liked_songs(st.session_state.liked_songs)
                        st.rerun()
    else:
        st.info("No liked songs yet.")


