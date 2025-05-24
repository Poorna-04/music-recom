import streamlit as st
import pandas as pd
import openai
import numpy as np

# Set your OpenAI API key
openai.api_key = "your_openai_api_key_here"

# Load dataset
df = pd.read_csv("dataset_normalized_final.csv")

track_names = pd.read_csv("dataset_normalized_final.csv")[['track_name']]
df_with_names = pd.concat([track_names, df], axis=1)

# Function to extract audio features using GPT
def get_audio_features_from_text(user_input):
    prompt = f"""
    Given the user request: '{user_input}', return relevant audio features from:
    [danceability, energy, valence, tempo, acousticness, instrumentalness]

    Classify each from 0 (low) to 1 (high), based on the mood.
    Also suggest possible genres from ['pop', 'rock', 'classical', 'hip hop', 'jazz'].
    Respond ONLY in JSON format like:
    {{"danceability": 0.8, "energy": 0.9, "valence": 0.6, "genres": ["pop", "hip hop"]}}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return eval(response['choices'][0]['message']['content'])
    except Exception as e:
        st.error(f"Error from GPT: {e}")
        return {}

# Function to recommend songs
def filter_songs_by_features(df, features):
    mask = np.ones(len(df), dtype=bool)
    for key in features:
        if key != 'genres':
            mask &= (df[key] >= features[key] - 0.1) & (df[key] <= features[key] + 0.1)
    return df[mask]

# Streamlit UI
st.title("🎶 AI-Powered Music Recommender")

user_input = st.text_input("Describe what kind of music you want:")

if st.button("Get Recommendations") and user_input:
    with st.spinner("Thinking..."):
        features = get_audio_features_from_text(user_input)
        if features:
            recommendations = filter_songs_by_features(df_with_names, features)
            if not recommendations.empty:
                st.subheader("🎵 Recommended Songs")
                for name in recommendations['track_name'].head(5):
                    st.write("•", name)
            else:
                st.warning("No matching songs found!")
