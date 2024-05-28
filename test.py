import os
import json
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

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
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": "A playlist created by SpotiTube."
            },
            "status": {
                "privacyStatus": "private"  # Change to "public" if you want the playlist to be public
            }
        }
    )
    response = request.execute()
    print(f"Playlist '{title}' created.")
    return response['id']

def add_video_to_playlist(youtube, video_id, playlist_id):
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

def main():
    youtube = authenticate()
    query = "Wake Up in the sky"
    playlist_title = "SpotiTube Playlist"
    print("Searching for videos...")
    video_ids = search_videos(youtube, query)
    if video_ids:
        video_id = video_ids[0]  # Get the first video ID
        # Check if playlist exists, if not, create it
        playlists = youtube.playlists().list(part="snippet", mine=True).execute()
        playlist_exists = any(playlist['snippet']['title'] == playlist_title for playlist in playlists['items'])
        if not playlist_exists:
            playlist_id = create_playlist(youtube, playlist_title)
        else:
            playlist_id = next(playlist['id'] for playlist in playlists['items'] if playlist['snippet']['title'] == playlist_title)
        print("Adding video to playlist...")
        add_video_to_playlist(youtube, video_id, playlist_id)

if __name__ == "__main__":
    main()
