import subprocess
import os
import argparse
import youtube_search  # You need to install youtube-search-python for searching

music_dir = r"C:\Users\nmuzz\Music\with lrc" #just a default, the preferred dir is passed as an argument
yt_dlp_path = r"./yt-dlp.exe"
# Set up argument parser with only artist and track as arguments
def get_arguments():
    parser = argparse.ArgumentParser(description="Download a track with yt-dlp.")
    parser.add_argument('--artist', type=str, default="Bobby Pulido", help="Name of the artist.")
    parser.add_argument('--track', type=str, default="Desvelado", help="Name of the track.")
    parser.add_argument('--musicDir', type=str, default=music_dir, help="dir to place mp3")
    return parser.parse_args()

# Search YouTube for the artist and track
def search_youtube(artist, track):
    query = f"{artist} {track} lyrics"
    print(f"\nSearching YouTube for: {query}")
    results = youtube_search.YoutubeSearch(query, max_results=1).to_dict()

    if results:
        return f"https://www.youtube.com{results[0]['url_suffix']}"
    else:
        print("Error: No results found on YouTube.")
        return None

# Function that performs the download using provided parameters
def download_track(artist, track, music_directory, yt_dlp_path):
    # Search for the YouTube URL
    url = search_youtube(artist, track)
    if not url:
        return

    # Construct the path to store the file
    fpath = os.path.join(music_directory, f"{artist} - {track}.mp3")

    # Run yt-dlp to download the track
    try:
        result = subprocess.run(
            [yt_dlp_path, url, "-x", "--audio-format", "mp3", "-o", fpath],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print(f"Download successful. Track saved to {fpath}.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.decode()}")

def main():
    args = get_arguments()

    download_track(args.artist, args.track, args.musicDir, yt_dlp_path)

if __name__ == "__main__":
    main()
