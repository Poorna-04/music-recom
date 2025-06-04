
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import random

app = Flask(__name__, static_url_path='/static')
CORS(app)

# Load the dataset
df = pd.read_csv(r"C:\Users\poorn\OneDrive\Desktop\internship\dataset_normalized_final.csv")
non_feature_cols = ['Unnamed: 0', 'track_id', 'album_name', 'track_name', 'explicit']
feature_cols = [col for col in df.columns if col not in non_feature_cols and df[col].dtype in ['float64', 'int64']]
track_names = df['track_name']
features = df[feature_cols]

# Fit the KNN model
knn = NearestNeighbors(n_neighbors=6, metric='euclidean')
knn.fit(features)

# Dummy cover images (use Spotify API or static images for production)
def get_dummy_cover():
    return "https://via.placeholder.com/100"

# Homepage route
@app.route('/')
def home():
    return render_template('home.html')

# Song details route
@app.route('/song/<song_name>')
def song_details(song_name):
    return render_template('song.html')

# Recommendation endpoint
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    song_name = data.get('song_name', '').strip()

    if song_name in track_names.values:
        index = track_names[track_names == song_name].index[0]
        song_features = features.iloc[[index]]
        distances, indices = knn.kneighbors(song_features)

        results = []
        for idx, dist in zip(indices[0][1:], distances[0][1:]):
            results.append({
                'track_name': track_names.iloc[idx],
                'distance': round(float(dist), 4),
                'cover': get_dummy_cover(),
                'artist': df.iloc[idx]['album_name']
            })
        return jsonify(results)
    else:
        return jsonify({'error': 'Song not found'}), 404

# Endpoint to get random songs for home carousel
@app.route('/random-songs')
def random_songs():
    random_indices = random.sample(range(len(df)), 15)
    results = []
    for idx in random_indices:
        results.append({
            'name': df.iloc[idx]['track_name'],
            'cover': get_dummy_cover()
        })
    return jsonify(results)

# Popular tracks endpoint
@app.route('/popular-tracks', methods=['POST'])
def popular_tracks():
    data = request.get_json()
    song_name = data.get('song_name', '').strip()
    if song_name not in df['track_name'].values:
        return jsonify({'error': 'Song not found'}), 404

    artist_name = df[df['track_name'] == song_name]['album_name'].values[0]
    artist_songs = df[df['album_name'] == artist_name]['track_name'].value_counts().head(5).index.tolist()

    results = []
    for track in artist_songs:
        results.append({
            'track_name': track,
            'cover': get_dummy_cover(),
            'explicit': random.choice([True, False])
        })
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
