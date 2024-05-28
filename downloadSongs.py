from pytube import Playlist
import os

# Function to download audio from YouTube video and convert to MP3
def download_audio(video_url, output_path):
    playlist = Playlist(video_url)
    for video in playlist.videos:
        audio_stream = video.streams.filter(only_audio=True).first()
        if audio_stream:
            audio_file = audio_stream.download(output_path=output_path)
            mp3_file = os.path.splitext(audio_file)[0] + ".mp3"
            os.rename(audio_file, mp3_file)
            print(f"Downloaded and converted: {mp3_file}")
        else:
            print(f"No audio stream found for: {video.title}")

# Example playlist URL
playlist_url = 'https://www.youtube.com/playlist?list=PLNfR1danGpVhb4_JwKER81ogSJ2wDlsmw'

# Output directory for downloaded MP3 files
output_directory = 'downloaded_songs'

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Download audio from the playlist and convert to MP3
download_audio(playlist_url, output_directory)
