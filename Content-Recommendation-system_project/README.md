# 🎵 Emoji Music Recommendation System

A full-stack Python web application that recommends music based on emoji emotions using Machine Learning and the Spotify API.

## Features
- **Emoji Selector**: Click an emoji (😊, 😢, 🔥, etc.) to get songs matching that mood.
- **ML Recommendations**: Uses a RandomForestClassifier and Audio Feature Mapping.
- **Spotify Integration**: Search for real songs, artists, and albums.
- **Music Playback**: 30-second audio previews for supported tracks.
- **Favorites**: Like songs to save them to your personal sidebar collection (persisted across sessions).

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Spotify Configuration (Optional but Recommended)**:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) and create an app.
   - Open `config.py` and replace the placeholders with your `Client ID` and `Client Secret`.
   - *If you skip this, the app will run in "Offline Mode" using synthetic/mock data.*

3. **Data Generation**:
   Run the training script to fetch data (or generate synthetic data) and train the model:
   ```bash
   python train_model.py
   ```
   *This creates `model.pkl` and `data/music_dataset.csv`.*

4. **Run the App**:
   ```bash
   streamlit run app.py
   ```
   The app will open in your browser at `http://localhost:8501`.

## File Structure
- `app.py`: Main Streamlit application.
- `train_model.py`: Script to fetch/generate data and train the ML model.
- `config.py`: Configuration file for API keys.
- `model.pkl`: Saved Machine Learning model and dataset.
- `liked_songs.json`: Stores your liked songs.
- `data/`: Contains the music dataset CSV.
