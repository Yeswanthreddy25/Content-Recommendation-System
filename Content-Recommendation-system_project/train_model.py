import pandas as pd
import numpy as np
import joblib
import os
import requests
import time
from sklearn.ensemble import RandomForestClassifier

# Emoji Configuration
EMOJI_MAPPING = {
    '😊': {'label': 'Happy', 'negative': ['sad', 'gloom', 'breakup', 'remix']},
    '😢': {'label': 'Sad', 'negative': ['remix', 'club', 'dance', 'happy', 'party', 'mix', 'techno']},
    '😌': {'label': 'Calm', 'negative': ['rock', 'metal', 'techno', 'dubstep']},
    '🔥': {'label': 'Energetic', 'negative': ['lullaby', 'sleep', 'balled', 'slow']},
    '💪': {'label': 'Motivated', 'negative': ['sad', 'weak', 'slow']},
    '😴': {'label': 'Sleepy', 'negative': ['rock', 'pop', 'dance', 'drum', 'beat']},
    '🥰': {'label': 'Romantic', 'negative': ['breakup', 'hate', 'metal']},
    '😠': {'label': 'Angry', 'negative': ['calm', 'soft', 'love']},
    '🎉': {'label': 'Party', 'negative': ['acoustic', 'slow', 'sad']},
    '🙏': {'label': 'Devotion', 'negative': ['explicit']},
    '😎': {'label': 'Cool', 'negative': ['country', 'metal']},
    '💭': {'label': 'Thoughtful', 'negative': ['party', 'scream']},
    '🌙': {'label': 'Melancholic', 'negative': ['happy', 'upbeat', 'dance']},
}

# Localized Search Terms Configuration
# mood_key -> language -> [terms]
LOCALIZED_TERMS = {
    'Happy': {
        'English': ['happy hits', 'feel good pop', 'upbeat hits', 'walking on sunshine'],
        'Hindi': ['bollywood happy songs', 'hindi dance hits', 'punjabi bhangra', 'bollywood party'],
        'Spanish': ['latin pop hits', 'reggaeton fiesta', 'musica alegre', 'happy latin'],
        'Korean': ['k-pop upbeat', 'k-pop dance hits', 'happy k-pop', 'korean pop energy'],
        'Telugu': ['telugu dance hits', 'tollywood party', 'telugu upbeat', 'telugu mass songs'] 
    },
    'Sad': {
        'English': ['sad songs', 'heartbreak', 'piano ballads', 'cry me a river'],
        'Hindi': ['bollywood sad songs', 'arijit singh sad', 'hindi breakup', 'dard bhare'],
        'Spanish': ['musica triste', 'baladas romanticas', 'cortavenas', 'sad latin'],
        'Korean': ['k-pop ballad', 'k-drama ost sad', 'sad k-pop', 'korean heartbreak'],
        'Telugu': ['telugu sad songs', 'tollywood melody sad', 'telugu heartbreak', 'love failure telugu']
    },
    'Calm': {
        'English': ['acoustic chill', 'lo-fi beats', 'relaxing piano', 'stress relief'],
        'Hindi': ['bollywood acoustic', 'hindi lo-fi', 'sufi songs', 'calm hindi'],
        'Spanish': ['latin acoustic', 'guitarras relajantes', 'bossa nova', 'calm spanish'],
        'Korean': ['k-indie', 'korean acoustic', 'piano k-pop', 'calm k-drama'],
        'Telugu': ['telugu melody', 'telugu acoustic', 'calm tollywood', 'pleasant telugu']
    },
    'Energetic': {
        'English': ['workout hits', 'gym motivation', 'power rock', 'high energy pop'],
        'Hindi': ['bollywood workout', 'punjabi high energy', 'hindi gym songs', 'chak de india'],
        'Spanish': ['latin gym', 'reggaeton workout', 'zumba hits', 'energia latina'],
        'Korean': ['k-pop workout', 'k-pop high energy', 'gym k-pop', 'korean rock'],
        'Telugu': ['telugu workout', 'tollywood action', 'mass beats telugu', 'dsp hits high energy']
    },
    'Romantic': {
        'English': ['love songs', 'romantic ballads', 'wedding songs', 'first dance'],
        'Hindi': ['bollywood romantic', 'love songs hindi', 'arijit singh romantic', 'shreya ghoshal love'],
        'Spanish': ['musica romantica', 'latin love songs', 'bachata romantica', 'amor latino'],
        'Korean': ['k-drama romance', 'sweet k-pop', 'korean love songs', 'wedding k-pop'],
        'Telugu': ['telugu love songs', 'sid sriram melody', 'romantic tollywood', 'telugu duets']
    },
    'Party': {
        'English': ['party hits', 'club bangers', 'dance pop', 'house music'],
        'Hindi': ['bollywood party anthem', 'punjabi party mix', 'remix hindi', 'badshah hits'],
        'Spanish': ['fiesta latina', 'reggaeton hits', 'salsa party', 'club latino'],
        'Korean': ['k-pop party', 'club k-pop', 'korean edm', 'big bang hits'],
        'Telugu': ['telugu folk songs', 'teenmaar beats', 'tollywood party mix', 'ramuloo ramulaa']
    }
}

# Fallback for emojis not strictly mapped above (uses English + Lang Name)
DEFAULT_TERMS = {
    'Motivated': ['motivation', 'champions', 'success'],
    'Sleepy': ['sleep', 'lullaby', 'ambient'],
    'Angry': ['rock', 'metal', 'rage'],
    'Devotion': ['devotional', 'spiritual', 'gospel'],
    'Cool': ['cool', 'jazz', 'smooth'],
    'Thoughtful': ['focus', 'study', 'instrumental'],
    'Melancholic': ['lonely', 'sad', 'night']
}

# Languages to support
LANGUAGES = ['English', 'Hindi', 'Spanish', 'Korean', 'Telugu']

def fetch_from_itunes(term, limit=10):
    """
    Search iTunes API for tracks.
    """
    url = "https://itunes.apple.com/search"
    params = {
        'term': term,
        'media': 'music',
        'entity': 'song',
        'limit': limit
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get('results', [])
    except Exception as e:
        print(f"Error fetching {term}: {e}")
    return []

def get_search_terms(mood_label, lang):
    if mood_label in LOCALIZED_TERMS and lang in LOCALIZED_TERMS[mood_label]:
        return LOCALIZED_TERMS[mood_label][lang]
    
    # Fallback logic
    base_terms = DEFAULT_TERMS.get(mood_label, [mood_label.lower()])
    if lang == 'English':
        return base_terms
    return [f"{term} {lang}" for term in base_terms]

def build_dataset():
    print("Fetching data from iTunes (Free API)...")
    all_tracks = []
    
    # Common Negative Filters
    GLOBAL_NEGATIVE = ['karaoke', 'tribute', 'cover', 'ringtone', 'podcast', 'commentary']
    
    for lang in LANGUAGES:
        print(f"--- Fetching {lang} songs ---")
        for emoji, data in EMOJI_MAPPING.items():
            mood_label = data['label']
            terms = get_search_terms(mood_label, lang)
            
            for term in terms:
                results = fetch_from_itunes(term, limit=12)
                
                for item in results:
                    song_name = item.get('trackName', '')
                    artist_name = item.get('artistName', '')
                    collection_name = item.get('collectionName', '')
                    full_text = f"{song_name} {artist_name} {collection_name}".lower()
                    
                    # 1. Global Negative Filter
                    if any(bad in full_text for bad in GLOBAL_NEGATIVE):
                        continue
                        
                    # 2. Mood Specific Negative Filter
                    is_bad_match = False
                    if 'negative' in data:
                        for neg in data['negative']:
                            if neg in full_text:
                                is_bad_match = True
                                break
                    if is_bad_match:
                        # Extra check: if looking for 'Party' but found 'Acoustic', skip.
                        # But for Hindi Party, 'Remix' is actually GOOD. 
                        # So we might need to relax 'negative' for some languages?
                        # For now, strict filtering is safer for quality.
                        continue

                    # Basic info
                    track_info = {
                        'id': str(item.get('trackId')),
                        'name': song_name,
                        'artist': artist_name,
                        'album': collection_name,
                        'image_url': item.get('artworkUrl100').replace('100x100', '600x600'),
                        'preview_url': item.get('previewUrl'),
                        'predicted_emoji': emoji, 
                        'mood_label': mood_label,
                        'language': lang # Tag with language
                    }
                    all_tracks.append(track_info)
                time.sleep(0.1) 
            
    # Remove duplicates
    df = pd.DataFrame(all_tracks).drop_duplicates(subset=['id'])
    return df

def train_and_save_pipeline(df):
    # Since we don't have audio features (valence/energy) from iTunes,
    # We can't train a feature-based Classifier in the same way.
    # However, the app relies on 'predicted_emoji' column which we now have directly.
    # To keep the code consistent with app expectation of a "model",
    # We'll just save the labeled dataset.
    # If we really wanted a model, we'd need audio analysis (librosa) which is too heavy.
    # For this use case, Keyword Mapping IS the model.
    
    print("Training model... (Skipped: Using Direct Labeling)")
    
    # We create a dummy model object just to satisfy the file structure if needed,
    # but the app mainly uses the dataframe + labeled column.
    
    artifacts = {
        'model': None, # No RF model needed for keyword lookup
        'data': df
    }
    
    joblib.dump(artifacts, 'model.pkl')
    print(f"Model and Dataset with {len(df)} songs saved to model.pkl")

def main():
    df = build_dataset()
    
    if df.empty:
        print("iTunes returned no tracks. Check internet.")
        return

    # Create data directory if not exists
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/music_dataset.csv', index=False)
    print(f"Dataset saved with {len(df)} songs.")
    
    train_and_save_pipeline(df)

if __name__ == "__main__":
    main()
