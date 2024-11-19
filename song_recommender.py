import streamlit as st
import pandas as pd
import numpy as np
import random
import pickle
import requests
import base64
from thefuzz import process
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from IPython.display import IFrame
CLIENT_ID = "9b5b5cc291ca48f7a617daa5a23a857f"
CLIENT_SECRET = "d59dbf70305642bb95fc3cb746f0620a"

# Load data and models
billboard_df = pd.read_csv("C:\\Users\\ramya\\OneDrive\\Documents\\GitHub\\Song--Recommender\\billboard_df.csv", index_col=0)
audio_features_df = pd.read_csv("C:\\Users\\ramya\\OneDrive\\Documents\\GitHub\\Song--Recommender\\total_af_df.csv", index_col=0)
df_final = pd.read_csv("C:\\Users\\ramya\\OneDrive\\Documents\\GitHub\\Song--Recommender\\df_final.csv", index_col=0)

with open('kmeans_19.pkl', 'rb') as file:
    kmeans_19 = pickle.load(file)

with open('minmax.pkl', 'rb') as file:
    minmax = pickle.load(file)

# Spotify authentication
def get_spotify_token(CLIENT_ID, CLIENT_SECRET):
    client_credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    client_credentials_b64 = base64.b64encode(client_credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {client_credentials_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)

    if response.status_code == 200:
        token = response.json().get("access_token")
        return token
    else:
        raise Exception(f"Failed to get token: {response.status_code} {response.text}")

token = get_spotify_token(CLIENT_ID, CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

def get_song_name(recommended_song_id):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/tracks/{recommended_song_id}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data['name']
    else:
        return "Error: Unable to retrieve song name"

def play_song(track_id):
    return st.components.v1.iframe(f"https://open.spotify.com/embed/track/{track_id}", width=320, height=80)

# Song Recommendation Function
def recommend_a_song(song_pref):
    song_ref_names = []
    song_ref_ids = []
    song_ref_artist = []

    song_matching_percent = process.extractOne(song_pref.lower(), billboard_df['Song'])[1]
    song_name = process.extractOne(song_pref.lower(), billboard_df['Song'])[0]
    artist_name = billboard_df.loc[billboard_df["Song"] == song_name, 'Artist'].values[0]

    if song_matching_percent > 80:
        question = st.radio(f"Is this song ({song_name}) by ({artist_name}) the song you mean?", ("Yes", "No"))
        
        if question == "Yes":
            updated_billboard_df = billboard_df.drop(billboard_df[billboard_df['Song'] == song_name].index)
            recommended_song = random.choice(updated_billboard_df['Song'])
            artist_of_recommended_song = updated_billboard_df.loc[updated_billboard_df["Song"] == recommended_song, 'Artist'].values[0]
            st.write(f"We can recommend you this song: ({recommended_song}) by {artist_of_recommended_song}")
            recommended_billboard_song_id = sp.search(q=recommended_song, limit=1, market="GB")["tracks"]["items"][0]["id"]
            play_song(recommended_billboard_song_id)
        
        elif question == "No":
            st.write("Sorry, you are not cool enough to have your song in the Top 100 Billboard songs! We will recommend you another song.")
            
            for i in sp.search(q=song_pref, limit=10)["tracks"]["items"][0:10]:
                song_ref_names.append(i['name'])
                song_ref_ids.append(i['id'])
                song_ref_artist.append(i['artists'][0]['name'])

            for name, track_id, artist in zip(song_ref_names, song_ref_ids, song_ref_artist):
                question_2 = st.radio(f"Is this song ({name}) by ({artist}) the song you mean?", ("Yes", "No"))
                
                if question_2 == "Yes":
                    song_ref_af = sp.audio_features(track_id)[0]
                    song_ref_af = pd.DataFrame(song_ref_af, index=[0])
                    song_ref_af.drop(columns=['type', 'uri', 'track_href', 'analysis_url', 'id'], inplace=True)
                    song_ref_af_scaled = pd.DataFrame(minmax.transform(song_ref_af), columns=song_ref_af.columns)
                    song_ref_cluster = kmeans_19.predict(song_ref_af_scaled)[0]
                    recommended_song_id = df_final[df_final['KMeans_Cluster'] == song_ref_cluster].sample()['id'].values[0]
                    recommended_song_name = get_song_name(recommended_song_id)
                    st.write(f"We recommend you this song: {recommended_song_name}")
                    play_song(recommended_song_id)
                    break
    else:
        st.write("Sorry, you are not cool enough to have your song in the Top 100 Billboard songs! We will recommend you another song.")

        for i in sp.search(q=song_pref, limit=10)["tracks"]["items"][0:10]:
            song_ref_names.append(i['name'])
            song_ref_ids.append(i['id'])
            song_ref_artist.append(i['artists'][0]['name'])

        for name, track_id, artist in zip(song_ref_names, song_ref_ids, song_ref_artist):
            question_2 = st.radio(f"Is this song ({name}) by ({artist}) the song you mean?", ("Yes", "No"))
            
            if question_2 == "Yes":
                song_ref_af = sp.audio_features(track_id)[0]
                song_ref_af = pd.DataFrame(song_ref_af, index=[0])
                song_ref_af.drop(columns=['type', 'uri', 'track_href', 'analysis_url', 'id'], inplace=True)
                song_ref_af_scaled = pd.DataFrame(minmax.transform(song_ref_af), columns=song_ref_af.columns)
                song_ref_cluster = kmeans_19.predict(song_ref_af_scaled)[0]
                recommended_song_id = df_final[df_final['KMeans_Cluster'] == song_ref_cluster].sample()['id'].values[0]
                recommended_song_name = get_song_name(recommended_song_id)
                st.write(f"We recommend you this song: {recommended_song_name}")
                play_song(recommended_song_id)
                break

# Streamlit App
st.title('Song Recommender')

song_pref = st.text_input("Enter a song name:")

if st.button("Recommend"):
    if song_pref:
        recommend_a_song(song_pref)
    else:
        st.write("Please enter a song name.")
