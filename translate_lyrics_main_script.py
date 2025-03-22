import requests
import json
import subprocess
import os
import argparse

ENDPOINT = "http://127.0.0.1:5001"  # koboldcpp LLM endpoint
LYRICS_DIR = r"./Lyrics"  # Directory where original foreign language lyrics are stored
LRC_SCRIPT = r"./LRCLib_API.py"
AUDIO_RIP_SCRIPT = r"./youtubedlp rip script.py"
MP3_DIR = r"C:\Users\nmuzz\Music\with lrc"  # Destination for MP3 files

def get_arguments():
    parser = argparse.ArgumentParser(description="Parse track info and language to translate")
    parser.add_argument('--artist', type=str, default="grupo frontera", help="Name of the artist.")
    parser.add_argument('--track', type=str, default="un x100to", help="Name of the track.")
    parser.add_argument('--language', type=str, default="Spanish", help="Language to translate from.")
    parser.add_argument('--retranslate', type=int, default=1, help="1 = retranslate always, 0 = use existing translation.")
    return parser.parse_args()

def kobold_server_check():
    """Checks if the Kobold server is up and prints its version if available."""
     # Try to fetch the version info from the kobold server
    try:
        response = requests.get(f"{ENDPOINT}/api/extra/version", timeout=5)
        if response.status_code == 200:
            try:
                version = response.json().get("version", "Unknown")
                print(f"Kobold server is up and running! Version: {version}")
                return 1
            except (json.JSONDecodeError, ValueError):
                    print("Kobold server is up, but version info could not be parsed.")
        else:
            print(f"Kobold server returned unexpected status code: {response.status_code}")
    except Exception as e:
            print(f"Error connecting to Kobold server, make sure its running!: {e}")
    return 0

def get_lyrics(artist, track, file_path, language):
    """Fetches lyrics from a local file or via an API call if not found locally."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                lyrics = file.read().strip()
                if lyrics:
                    print(f"Used local {language} lyrics.")
                    return lyrics
        except IOError as e:
            print(f"Error reading lyrics file: {e}")
    print("File not found locally. Fetching from API...")

    result = subprocess.run(
        ["python3", LRC_SCRIPT, artist, track],
        capture_output=True, text=True
    )
    try:
        outer_data = json.loads(result.stdout)
        synced_str = outer_data.get("syncedLyrics", "")
        if not synced_str:
            raise ValueError("Empty syncedLyrics from API.")

        inner_data = json.loads(synced_str)
        synced_lyrics = inner_data.get("syncedLyrics", "")
        if not synced_lyrics:
            raise ValueError("Empty syncedLyrics in inner JSON.")
        
        print("API request successful.")
        return synced_lyrics
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error extracting lyrics: {e}")
    
    return ""

def translate_lyrics(lyrics, language):
    """Translates the provided lyrics into English while preserving timestamps."""
    prompt = (
        f"Translate the following {language} song lyrics into English. Preserve the timestamps and ensure accuracy. "
        "Do not add any additional commentary. The output should end precisely when the song ends.\n\n"
    )

    payload = {
        "prompt": f"<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}{lyrics}\n<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
        "max_length": 3000,
        "temperature": 0.25,
        "trim_stop": True,
        "stop_sequence": ["<|eot_id|>", "<|endoftext|>"],
        "bypass_eos": False,
        "cache_prompt": False,
    }
    
    print("Translating lyrics with local LLM...")
    response = requests.post(f"{ENDPOINT}/api/v1/generate", json=payload)
    
    if response.status_code == 200:
        return response.json().get("results", [{}])[0].get("text", "").strip()
    
    return f"Error: Request failed with status code {response.status_code}."

def process_lyrics(artist, track, language, retranslate):
    """
    Processes the lyrics by reading the original, saving it if needed,
    and translating (or reusing) the translated version.
    Returns a tuple (original_lyrics, translated_lyrics).
    """
    # Ensure the Lyrics directory exists
    if not os.path.exists(LYRICS_DIR):
        os.makedirs(LYRICS_DIR, exist_ok=True)

    file_path = os.path.join(LYRICS_DIR, f"{artist} - {track}.lrc")
    root, ext = os.path.splitext(file_path)
    file_path_OG = f"{root} OG{ext}"
    
    # Get original lyrics
    lyrics = get_lyrics(artist, track, file_path_OG, language)
    if not lyrics:
        print("Error: Lyrics not found. Exiting.")
        return None, None

    # Save original lyrics if not already saved or empty
    if not os.path.exists(file_path_OG) or not lyrics.strip():
        with open(file_path_OG, "w", encoding="utf-8") as file:
            file.write(lyrics)
        print(f"Original lyrics saved to {file_path_OG}")

    # Process translated lyrics
    if not os.path.exists(MP3_DIR):
        os.makedirs(MP3_DIR, exist_ok=True)
        
    translated_file_path = os.path.join(MP3_DIR, f"{artist} - {track}.lrc")
    translated_lyrics = None
    if not os.path.exists(translated_file_path) or retranslate:
        translated_lyrics = translate_lyrics(lyrics, language)
    
    if translated_lyrics:
        with open(translated_file_path, "w", encoding="utf-8") as file:
            file.write(translated_lyrics)
        print(f"Translated lyrics saved to {translated_file_path}")
    elif os.path.exists(translated_file_path):
        print("Lyrics already translated and exist.")
    else:
        print("Error in translation.")

    return lyrics, translated_lyrics

def download_track(artist, track):
    """Downloads the track's MP3 if it doesn't already exist."""
    mp3_path = os.path.join(MP3_DIR, f"{artist} - {track}.mp3")
    if not os.path.exists(mp3_path):
        try:
            result = subprocess.run(
                ["python3", AUDIO_RIP_SCRIPT, '--artist', artist, '--track', track, '--musicDir', MP3_DIR],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60
            )
            print(f"Download successful: {mp3_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error during download: {e.stderr.decode()}")
        except FileNotFoundError:
            print(f"Script not found: {AUDIO_RIP_SCRIPT}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
    else:
        print("Track already exists.")

def main():
    if not kobold_server_check(): 
        print(f"no kobold server")
        return
    args = get_arguments()
    artist_name = args.artist
    track_name = args.track
    language = args.language
    retranslate = args.retranslate

    # Process lyrics (original and translation)
    original_lyrics, translated_lyrics = process_lyrics(artist_name, track_name, language, retranslate)
    if not original_lyrics:
        return  # Exit if original lyrics are not found

    # Download the MP3 track if needed
    download_track(artist_name, track_name)

if __name__ == "__main__":
    main()
