
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd  # ✅ Make sure this is included
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)
CORS(app)  # 👈 this enables CORS for all routes

# Load data and train KNN
df = pd.read_csv("dataset_normalized_final.csv")
non_feature_cols = ['Unnamed: 0', 'track_id', 'album_name', 'track_name', 'explicit']
feature_cols = [col for col in df.columns if col not in non_feature_cols and df[col].dtype in ['float64', 'int64']]
track_names = df['track_name']
features = df[feature_cols]

knn = NearestNeighbors(n_neighbors=6, metric='euclidean')
knn.fit(features)

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
                'distance': round(float(dist), 4)
            })
        return jsonify(results)
    else:
        return jsonify({'error': 'Song not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
'''python second.py
then double click on  the first.html file in your file'''