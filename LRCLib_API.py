import requests
import argparse
import json

BASE_URL = "https://lrclib.net/api/get"

HEADERS = {
    "Lrclib-Client": "NicksLyricFetcher v1.0.0 (private project)",
    "User-Agent": "NicksLyricFetcher v1.0.0 (private project)"
}

def fetch_lyrics(artist, track):
    params = {"artist_name": artist, "track_name": track}
    response = requests.get(BASE_URL, params=params, headers=HEADERS)
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
    
    fetch_lyrics(args.artist_name, args.track_name)
