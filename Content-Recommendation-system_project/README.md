# 🍿 Emotify - Music Recommendation

A cinematic, full-stack music recommendation system that matches your mood with the perfect soundtrack using Machine Learning. Built with Streamlit, powered by the iTunes API, and integrated with YouTube Music for full playback.

## ✨ Features
- **Netflix Aesthetics**: A premium, dark-themed UI with horizontal mood sliders and poster grids.
- **Mood-Based Discovery**: Select from 9 core emotions (😊, 😢, 🔥, etc.) to get instant curated playlists.
- **Multi-Language Support**: Discover music in **English, Hindi, Spanish, Korean, and Telugu**.
- **Smart Search**: Search for any track, artist, or album across the globe.
- **My List**: Save your favorite tracks to a persistent personal collection.
- **Seamless Playback**: Watch and listen to music videos directly in the app via YouTube integration.

## 🚀 Getting Started

### 1. Install Dependencies
Ensure you have Python installed, then run:
```bash
pip install -r requirements.txt
```

### 2. No API Keys Needed!
> [!IMPORTANT]
> It uses the free iTunes Search API for discovery and `ytmusicapi` for playback components, making it "plug-and-play" ready out of the box.

### 3. Initialize the Model
Before running the app, fetch the latest data and prepare the recommendation engine:
```bash
python train_model.py
```
*This creates `model.pkl` and `data/music_dataset.csv`.*

### 4. Run the App
Launch the Streamlit dashboard:
```bash
python -m streamlit run app.py
```
Open `http://localhost:8501` in your browser to start your cinematic music journey.

## 📂 Project Structure
- `app.py`: The main Netflix-style dashboard and application logic.
- `train_model.py`: Data ingestion (iTunes) and keyword-based mood labeling.
- `model.pkl`: Serialized dataset and mood mapping artifacts.
- `liked_songs.json`: Your persisted "My List" collection.
- `requirements.txt`: Project dependencies and environment specs.
