'''from dotenv import load_dotenv
import os

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
print(client_id, client_secret)
'''
import os
import pandas as pd
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables from .env file
load_dotenv()

# No need to explicitly fetch the client_id or client_secret if you set them as SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET
auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

# List of tracks to search (modify as needed)
tracks = [
    "Blinding Lights",
    "Shape of You",
    "Levitating",
    "Peaches",
    "Someone Like You"
]

# Define columns to extract from audio features
feature_keys = [
    'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
    'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms'
]

data = []

# Process each track
for track_name in tracks:
    results = sp.search(q=track_name, type='track', limit=1)
    items = results['tracks']['items']
    if not items:
        print(f"Track not found: {track_name}")
        continue

    track = items[0]
    track_id = track['id']
    features = sp.audio_features([track_id])[0]

    if not features:
        print(f"No features found for: {track_name}")
        continue

    track_data = {
        'name': track['name'],
        'artist': track['artists'][0]['name'],
        'id': track_id
    }

    for key in feature_keys:
        track_data[key] = features[key]

    data.append(track_data)

# Save to DataFrame and CSV
df = pd.DataFrame(data)
df.to_csv("spotify_dataset.csv", index=False)
print("Data saved to spotify_dataset.csv")
'''
import logging
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time

# Enable detailed logging for debugging
logging.basicConfig(level=logging.INFO)

# Replace with your actual Spotify API credentials
client_id = '46bf26a25fb74e92b4437aed65227788'
client_secret = 'ba60599ca4b744a28a8df7f6b9d5f66c'


# Authenticate using client credentials
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Function to retrieve all tracks from a playlist
def get_playlist_tracks(playlist_id):
    results = sp.playlist_items(playlist_id, market='US')  # specify market
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

# Extract track metadata (name, artist, ID)
def extract_track_info(track):
    track_info = track.get('track')
    if track_info is None:
        return None
    return {
        'song_name': track_info.get('name'),
        'artist': track_info['artists'][0]['name'] if track_info.get('artists') else None,
        'track_id': track_info.get('id')
    }

# Retrieve audio features for a track
def get_audio_features(track_id):
    features = sp.audio_features([track_id])[0]
    return features

# Build dataset from a playlist
def build_dataset_from_playlist(playlist_id):
    tracks = get_playlist_tracks(playlist_id)
    data = []
    for item in tracks:
        info = extract_track_info(item)
        if info is None or info['track_id'] is None:
            continue
        features = get_audio_features(info['track_id'])
        if features is None:
            continue
        combined = {**info, **features}
        data.append(combined)
        time.sleep(0.1)  # be kind to the Spotify API
    return pd.DataFrame(data)

# --- MAIN EXECUTION ---

# ✅ Use just the playlist ID (NOT the full URL or URI)
playlist_id = '37i9dQZF1DXcBWIGoYBM5M'  # Spotify's "Today's Top Hits"

# Generate dataset
df = build_dataset_from_playlist(playlist_id)

# Save to CSV
df.to_csv('spotify_playlist_dataset.csv', index=False)

print("Dataset created with", len(df), "songs")
'''