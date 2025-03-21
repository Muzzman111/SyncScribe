import requests
import argparse
import json

BASE_URL = "https://lrclib.net/api/get"

def fetch_lyrics(artist, track):
    params = {"artist_name": artist, "track_name": track}
    response = requests.get(BASE_URL, params=params)
    if response.ok:
        # Output only JSON
        print(json.dumps({"syncedLyrics": response.text}))
    else:
        print(json.dumps({"error": f"{response.status_code}: {response.text}"}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch lyrics from LRCLib API")
    parser.add_argument("artist_name", nargs="?", default="Gabito Ballesteros", help="Artist name")
    parser.add_argument("track_name", nargs="?", default="Presidente", help="Track name")
    args = parser.parse_args()
    
    # Remove the extra print statement to avoid interfering with JSON output
    fetch_lyrics(args.artist_name, args.track_name)
