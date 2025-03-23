import subprocess
import os
import argparse
import youtube_search  # You need to install youtube-search-python for searching
import sys
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

music_dir = r"C:\Users\nmuzz\Music\with lrc" #just a default, the preferred dir is passed as an argument
yt_dlp_path = r"./yt-dlp.exe"
override = None #allows you to choose which video to download
# Set up argument parser with only artist and track as arguments
def get_arguments():
    parser = argparse.ArgumentParser(description="Download a track with yt-dlp.")
    parser.add_argument('--artist', type=str, default="Andrea Bocelli", help="Name of the artist.")
    parser.add_argument('--track', type=str, default="con te partiro", help="Name of the track.")
    parser.add_argument('--musicDir', type=str, default=music_dir, help="dir to place mp3")
    parser.add_argument('--language', type=str, default="italian", help="language to use")
    return parser.parse_args()

def convert_duration_to_seconds(duration_str):
    parts = duration_str.split(':')
    parts = [int(p) for p in parts]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    elif len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    else:
        return float('inf')

def search_youtube(artist, track, wordforlyrics, override):
    query = f"{artist} {track} {wordforlyrics}"
    print(f"\nSearching YouTube for: {query}")
    results = youtube_search.YoutubeSearch(query, max_results=2).to_dict() #you can choose how many videos to look at here

    if results:
        shortest_video = None
        shortest_duration = float('inf')
        for result in results:
            # Assuming the result has a 'duration' key, otherwise skip.
            duration_str = result.get('duration')
            if duration_str:
                seconds = convert_duration_to_seconds(duration_str)
                print(f"Video duration in seconds: {seconds}")
                if seconds < shortest_duration:
                    shortest_duration = seconds
                    shortest_video = result

        if shortest_video:
            if override:   
                shortest_video = results[0] #choose which video to download if override is set
                print(f"Shortest video choice overriden")
            else: 
                print(f"Downloaded shortest video")
            return f"https://www.youtube.com{shortest_video['url_suffix']}"
        else:
            print("Error: No video with duration information found.")
            return None
    else:
        print("Error: No results found on YouTube.")
        return None


# Function that performs the download using provided parameters
def download_track(artist, track, music_directory, yt_dlp_path, wordforlyrics, override):
    # Search for the YouTube URL
    url = search_youtube(artist, track, wordforlyrics, override)
    if not url:
        return

    # Construct the path to store the file
    fpath = os.path.join(music_directory, f"{artist} - {track}.mp3")

    # Run yt-dlp to download the track
    try:
        result = subprocess.run(
            [yt_dlp_path, url, "-x", "--audio-format", "mp3", "-o", fpath, "--force-overwrites"], #writing over existing videos by default
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print(f"Download successful. Track saved to {fpath}.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.decode()}")

def main():
    args = get_arguments()
    if args.language.lower() == "spanish":
        word4lyrics = "letra"
    elif args.language.lower() == "russian":
        word4lyrics = "тексты песен"
    elif args.language.lower() == "french":
        word4lyrics = "paroles"
    elif args.language.lower() == "chinese":
        word4lyrics = "歌词"
    else:
        word4lyrics = ""
    
    download_track(args.artist.lower(), args.track.lower(), args.musicDir, yt_dlp_path, word4lyrics, override)


if __name__ == "__main__":
    main()
