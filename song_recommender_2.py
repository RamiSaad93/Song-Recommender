import streamlit as st
import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from thefuzz import process 
import random
import pickle
import requests
import base64
import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials

CLIENT_ID = "9b5b5cc291ca48f7a617daa5a23a857f"
CLIENT_SECRET = "d59dbf70305642bb95fc3cb746f0620a"

billboard_df = pd.read_csv("C:\\Users\\ramya\\OneDrive\\Documents\\GitHub\\Song--Recommender\\billboard_df.csv", index_col=0)
audio_features_df = pd.read_csv("C:\\Users\\ramya\\OneDrive\\Documents\\GitHub\\Song--Recommender\\total_af_df.csv", index_col=0)
df_final = pd.read_csv("C:\\Users\\ramya\\OneDrive\\Documents\\GitHub\\Song--Recommender\\df_final.csv", index_col=[0])

with open('kmeans_19.pkl', 'rb') as file:
    kmeans_19 = pickle.load(file)

with open('minmax.pkl', 'rb') as file:
    minmax = pickle.load(file)

def play_song(track_id):
    st.write(f"Listen to the song: [Click here](https://open.spotify.com/track/{track_id})")

def get_spotify_token(CLIENT_ID, CLIENT_SECRET):
    client_credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    client_credentials_b64 = base64.b64encode(client_credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {client_credentials_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)

    if response.status_code == 200:
        token = response.json().get("access_token")
        return token
    else:
        st.error(f"Failed to get token: {response.status_code} {response.text}")

token = get_spotify_token(CLIENT_ID, CLIENT_SECRET)

def get_song_name(recommended_song_id):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    url = f"https://api.spotify.com/v1/tracks/{recommended_song_id}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data['name']
    else:
        return "Error: Unable to retrieve song name"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

# Initialize session state variables to manage user interaction states
if "state" not in st.session_state:
    st.session_state.state = "input"
    st.session_state.song_pref = ""
    st.session_state.song_name = ""
    st.session_state.artist_name = ""
    st.session_state.recommended_song_id = ""

def process_song_matching(song_pref):
    return process.extractOne(song_pref.lower(), billboard_df['Song'])[1]

def recommend_a_song(song_pref):
    song_matching_percent = process_song_matching(song_pref)

    song_name = get_matched_song_name(song_pref)
    artist_name = get_artist_name(song_name)
    
    st.session_state.song_name = song_name
    st.session_state.artist_name = artist_name

    if song_matching_percent > 80:
        st.session_state.state = "confirm"
    else:
        st.session_state.state = "not_found"

def confirm_song():
    question = st.radio(f"Is this song ({st.session_state.song_name}) by ({st.session_state.artist_name}) the song you mean?", ("Yes", "No"))
    if question == "Yes":
        recommend_song_from_billboard()
    else:
        st.session_state.state = "search_others"

def search_others():
    st.write("Sorry, you are not cool enough to have your song in the Top 100 Billboard songs!")
    st.write("We will recommend you another song")
    
    song_pref = st.session_state.song_pref

    song_ref_names = []
    song_ref_ids = []
    song_ref_artist = []

    for i in sp.search(q=song_pref, limit=10)["tracks"]["items"][0:10]:
        song_ref_names.append(i['name'])
        song_ref_ids.append(i['id'])
        song_ref_artist.append(i['artists'][0]['name'])

    for name, track_id, artist in zip(song_ref_names, song_ref_ids, song_ref_artist):
        question_2 = st.radio(f"Is this song ({name}) by ({artist}) the song you mean?", ("Yes", "No"))
        if question_2 == "Yes":
            recommend_song_by_cluster(track_id)
            break
        elif question_2 == "No":
            st.write("Sorry, I will show you another song!")
            continue

def not_found():
    st.write("Sorry, you are not cool enough to have your song in the Top 100 Billboard songs!")
    st.write("We couldn't find the song you like, please try again with the correct name of the song.")
    st.session_state.state = "input"

def recommend_song_from_billboard():
    updated_billboard_df = billboard_df.drop(billboard_df[billboard_df['Song'] == st.session_state.song_name].index)
    recommended_song = random.choice(updated_billboard_df['Song'])
    artist_of_recommended_song = updated_billboard_df.loc[updated_billboard_df["Song"] == recommended_song, 'Artist'].values[0]                                 
    st.write(f"We can recommend you this song: ({recommended_song}) by {artist_of_recommended_song}")
    recommended_billboard_song_id = sp.search(q=recommended_song, limit=1, market="GB")["tracks"]["items"][0]["id"]
    play_song(recommended_billboard_song_id)

def recommend_song_by_cluster(track_id):
    song_ref_af = sp.audio_features(track_id)[0]
    song_ref_af = pd.DataFrame(song_ref_af, index=[0])
    song_ref_af.drop(columns=['type', 'uri', 'track_href', 'analysis_url', 'id'], inplace=True)
    song_ref_af_scaled = pd.DataFrame(minmax.transform(song_ref_af), columns=song_ref_af.columns)
    song_ref_cluster = kmeans_19.predict(song_ref_af_scaled)[0]
    recommended_song_id = df_final[df_final['KMeans_Cluster'] == song_ref_cluster].sample()['id'].values[0]
    recommended_song_name = get_song_name(recommended_song_id)
    st.write(f"We recommend you this song: {recommended_song_name}")
    play_song(recommended_song_id)

def get_artist_name(song_name):
    return billboard_df.loc[billboard_df["Song"] == song_name, 'Artist'].values[0]

def get_matched_song_name(song_pref):
    return process.extractOne(song_pref.lower(), billboard_df['Song'])[0]

# Main logic to control flow based on session state
if st.session_state.state == "input":
    song_pref = st.text_input("Enter the name of a song you like:")
    if st.button("Submit"):
        st.session_state.song_pref = song_pref
        recommend_a_song(song_pref)

elif st.session_state.state == "confirm":
    confirm_song()

elif st.session_state.state == "search_others":
    search_others()

elif st.session_state.state == "not_found":
    not_found()


