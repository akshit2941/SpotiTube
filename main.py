import os
import spotipy
import json
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


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
playlist_link = 'https://open.spotify.com/playlist/37i9dQZF1DWUVpAXiEPK8P?si=d64ac428641c4881'

# Fetch playlist tracks
playlist_tracks = fetch_playlist_tracks(playlist_link)

playlist=[]

# Iterate over tracks and print track names
for idx, track in enumerate(playlist_tracks['items']):
    playlist.append(track['track']['name'])    
    print(f"{idx + 1}: {track['track']['name']}")


# Define the scopes
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def authenticate():
    # Disable OAuthlib's HTTPS verification when running locally.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    
    creds = None
    token_file = 'token.json'
    
    # Check if token file exists
    if os.path.exists(token_file):
        with open(token_file, 'r') as token:
            creds = Credentials.from_authorized_user_info(json.load(token), scopes)
    
    # If there are no valid credentials available, prompt the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                "client_secret.json", scopes)
            flow.redirect_uri = 'http://localhost:5000/'
            creds = flow.run_local_server(port=5000)
        
        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)
    return youtube

def search_videos(youtube, query):
    request = youtube.search().list(
        part="snippet",
        maxResults=5,
        q=query
    )
    response = request.execute()
    video_ids = [item['id']['videoId'] for item in response['items'] if item['id']['kind'] == 'youtube#video']
    for video_id in video_ids:
        print(f"Video ID: {video_id}")
    return video_ids
def create_playlist(youtube, title):
    try:
        request = youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": "A playlist created by SpotiTube."
                },
                "status": {
                    "privacyStatus": "unlisted"  # Change to "public" if you want the playlist to be public
                }
            }
        )
        response = request.execute()
        print(f"Playlist '{title}' created.")
        return response['id']
    except googleapiclient.errors.HttpError as e:
        print(f"An error occurred while creating the playlist: {e}")
        return None

def add_video_to_playlist(youtube, video_id, playlist_id):
    try:
        request = youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        )
        response = request.execute()
        print(f"Added video {video_id} to playlist {playlist_id}")
        return response
    except googleapiclient.errors.HttpError as e:
        print(f"An error occurred while adding video to the playlist: {e}")
        return None

def main():
    youtube = authenticate()
    if youtube is None:
        print("Failed to authenticate with YouTube API.")
        return
    
    playlist_title = "SpotiTube Playlist"
    print("Creating playlist...")
    playlists = youtube.playlists().list(part="snippet", mine=True).execute()
    playlist_exists = any(playlist['snippet']['title'] == playlist_title for playlist in playlists['items'])
    if not playlist_exists:
        playlist_id = create_playlist(youtube, playlist_title)
        if playlist_id is None:
            print("Failed to create playlist.")
            return
    else:
        playlist_id = next((playlist['id'] for playlist in playlists['items'] if playlist['snippet']['title'] == playlist_title), None)
        if playlist_id is None:
            print("Failed to find playlist ID.")
            return
    
    print("Adding songs to playlist...")
    for song in playlist:
        query = f"{song} official audio"
        print(f"Searching for '{query}' on YouTube...")
        video_ids = search_videos(youtube, query)
        if video_ids:
            video_id = video_ids[0]  # Get the first video ID
            print(f"Adding '{song}' to playlist...")
            if add_video_to_playlist(youtube, video_id, playlist_id) is None:
                print("Failed to add video to playlist.")
                # You may choose to continue adding other songs or stop the process
        else:
            print(f"No search results found for '{song}'. Skipping...")
    print("All songs added to the playlist!")

if __name__ == "__main__":
    main()
