import os
import argparse
import youtube_search  # Requires youtube-search-python
import sys
import yt_dlp

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

music_dir = os.path.expandvars(r"%userprofile%\Music\Music with LRC Files")  # Default directory
override = None  # Allows choosing which video to download

def get_arguments():
    parser = argparse.ArgumentParser(description="Download a track with yt-dlp.")
    parser.add_argument('--artist', type=str, default="calle 13", help="Name of the artist.")
    parser.add_argument('--track', type=str, default="vamo animal", help="Name of the track.")
    parser.add_argument('--musicDir', type=str, default=music_dir, help="Directory to place MP3.")
    parser.add_argument('--language', type=str, default="spanish", help="Language to use.")
    return parser.parse_args()

def convert_duration_to_seconds(duration_str):
    parts = [int(p) for p in duration_str.split(':')]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    elif len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    return float('inf')

def search_youtube(artist, track, wordforlyrics, override):
    query = f"{artist} {track} {wordforlyrics}"
    print(f"\nSearching YouTube for: {query}")
    results = youtube_search.YoutubeSearch(query, max_results=2).to_dict()   #change how many results to get from youtube
    
    if results:
        shortest_video = None
        shortest_duration = float('inf')
        for result in results:
            duration_str = result.get('duration')
            if duration_str:
                seconds = convert_duration_to_seconds(duration_str)
                print(f"Video duration in seconds: {seconds}")
                if seconds < shortest_duration:
                    shortest_duration = seconds
                    shortest_video = result
        
        if shortest_video:
            if override:
                shortest_video = results[0]
                print("Shortest video choice overridden.")
            else:
                print("Downloaded shortest video.")
            return f"https://www.youtube.com{shortest_video['url_suffix']}"
        else:
            print("Error: No video with duration information found.")
    else:
        print("Error: No results found on YouTube.")
    return None

def download_track(artist, track, music_directory, wordforlyrics, override):
    url = search_youtube(artist, track, wordforlyrics, override)
    if not url:
        return

    fpath = os.path.join(music_directory, f"{artist} - {track}")
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': fpath + ".%(ext)s",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True,
        'quiet': False,
        'forceoverwrites': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print(f"Download successful. Track saved to {fpath}.mp3")

def main():
    args = get_arguments()
    language_map = {
        "spanish": "letra",
        "russian": "тексты песен",
        "french": "paroles",
        "chinese": "歌词"
    }
    word4lyrics = language_map.get(args.language.lower(), "")
    download_track(args.artist.lower(), args.track.lower(), args.musicDir, word4lyrics, override)

if __name__ == "__main__":
    main()
