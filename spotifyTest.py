import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables from .env file
load_dotenv()

# Get Spotify API credentials from environment variables
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

# Initialize Spotipy client
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Function to extract playlist ID from Spotify playlist link
def get_playlist_id(playlist_link):
    playlist_id = playlist_link.split('/')[-1].split('?')[0]
    return playlist_id

# Function to fetch playlist tracks
def fetch_playlist_tracks(playlist_link):
    playlist_id = get_playlist_id(playlist_link)
    results = sp.playlist_tracks(playlist_id)
    return results

# Example playlist link
playlist_link = 'https://open.spotify.com/playlist/2KoqkwAUVt72zMyy3N3ezq?si=2f646fdbe228443f'

# Fetch playlist tracks
playlist_tracks = fetch_playlist_tracks(playlist_link)

# Iterate over tracks and print track names
for idx, track in enumerate(playlist_tracks['items']):
    print(f"{idx + 1}: {track['track']['name']}")
