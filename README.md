# 🎶 Song Recommendation Program

Welcome to the **Song Recommendation Program**! This project offers personalized song recommendations using both the Billboard Top 100 songs and Spotify audio features. The program takes in a user’s favorite song and recommends another similar song based on popularity or audio feature similarity.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Data Sources](#data-sources)
- [Methodology](#methodology)
  - [Part 1: Billboard Top 100 Recommendations](#part-1-billboard-top-100-recommendations)
  - [Part 2: Audio Feature-Based Recommendations with Spotify](#part-2-audio-feature-based-recommendations-with-spotify)
- [Usage](#usage)
- [Results](#results)
- [Future Improvements](#future-improvements)

---

## 🎯 Project Overview

This song recommendation project aims to provide a simple and effective way to find new music based on user preferences. The recommendation system operates in two main parts:

1. **Popular Songs Recommendation** – Recommends a song from the top 100 Billboard hits.
2. **Audio Feature-Based Recommendation** – Uses Spotify audio features to recommend songs with similar characteristics.

By using a K-means clustering model, the program analyzes over 12,000 songs to create meaningful clusters and suggest songs based on audio similarity.

## 📚 Data Sources

- **Billboard Top 100**: Data for the top 100 most popular songs globally, scraped from the Billboard website.
- **Spotify Audio Features**: Accessed via the Spotify API for detailed audio features such as danceability, energy, loudness, and more.

## 🔬 Methodology

The project is divided into two parts, each handling recommendations based on different criteria.

### Part 1: Billboard Top 100 Recommendations

- **Objective**: If the user’s song is in the current Billboard Top 100 songs, recommend another random song from the top 100.
- **Process**:
  1. **Data Scraping**: A web scraper gathers the top 100 songs list from Billboard.
  2. **Song Match Check**: The program checks if the user’s favorite song exists in the top 100 and matching it using **the fuzz** library.
  3. **Random Recommendation**: If the song is found, a different song from the Billboard list is recommended.

### Part 2: Audio Feature-Based Recommendations with Spotify

- **Objective**: If the song isn’t in the Billboard Top 100, recommend a song based on Spotify’s audio features.
- **Process**:
  1. **Spotify API**: Retrieve audio features for the user’s input song.
  2. **Audio Features Dataset**: A dataset of over 12,000 songs with their audio features is used.
  3. **K-means Clustering Model**: Songs are grouped into clusters based on their audio features (trained on audio features like energy, danceability, loudness, etc.).
  4. **Cluster Prediction**: The program predicts the cluster of the user’s song and recommends a similar song from the same cluster.

> **Note**: The K-means model is trained separately and saved as a `.pkl` file for efficient reuse.

## 🚀 Usage

1. **Input a song title** – Enter the title of a song you enjoy.
2. **Receive a recommendation**:
   - If the song is in the Billboard Top 100, you’ll receive another popular song recommendation.
   - If the song is not in the Top 100, you’ll get a recommendation based on audio similarity using the K-means clustering model.

## 📊 Results

### Sample Recommendation Scenarios

1. **Billboard Top 100 Match**:
   - User song: “Shape of You”
   - Recommendation: “Blinding Lights” (random selection from Billboard Top 100)

2. **Audio Feature-Based Recommendation**:
   - User song: “Unknown Indie Track”
   - Spotify Audio Features Retrieved: High energy, moderate danceability, low acousticness
   - Cluster Prediction: Cluster 4 (e.g., Indie Rock/Alternative)
   - Recommendation: “Somebody Else” by The 1975

## 🔧 Future Improvements

- **Enhanced Clustering**: Experiment with different clustering methods or deeper feature engineering to refine song groupings.
- **User Feedback**: Allow users to like or dislike recommendations, adjusting future recommendations based on their feedback.
- **Genre-based Filtering**: Include genre-specific recommendations for even more personalized suggestions.
