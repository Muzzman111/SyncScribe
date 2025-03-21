import subprocess
import os
import argparse
import youtube_search  # You need to install youtube-search-python for searching

# Set up argument parser with only artist and track as arguments
def get_arguments():
    parser = argparse.ArgumentParser(description="Download a track with yt-dlp.")
    parser.add_argument('--artist', type=str, default = "Don Cheto", help="Name of the artist.")
    parser.add_argument('--track', type=str, default = "El Tatuado", help="Name of the track.")
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

# Main function
def main():
    # Get command-line arguments
    args = get_arguments()

    # Hardcoded values
    music_dir = r"C:\Users\nmuzz\Music\with lrc"
    yt_dlp_path = r"E:\Extra_Programs_2\yt-dlp.exe"
    output_format = "mp3"
    
    # Search for the YouTube URL
    url = search_youtube(args.artist, args.track)
    
    if not url:
        return
    
    # Construct the path to store the file
    fpath = os.path.join(music_dir, f"{args.artist} - {args.track}.mp3")
    
    # Run yt-dlp to download the track
    try:
        result = subprocess.run(
            [yt_dlp_path, url, "-x", "--audio-format", "mp3", "-o", fpath],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print(f"Download successful. Track saved to {fpath}.")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.decode()}")
        return

if __name__ == "__main__":
    main()
