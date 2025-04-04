import logging
import os
import json
import subprocess
import argparse
import threading
import requests
import csv
import sys


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")   # Setup logging

ENDPOINT = "http://127.0.0.1:5001"  # Koboldcpp LLM endpoint
LRC_SCRIPT = r"./LRCLib_API.py"
AUDIO_RIP_SCRIPT = r"./youtubedlp_rip_script.py"
MP3_DIR = os.path.expandvars(r"%userprofile%\Music\Music with LRC Files")
LYRICS_DIR = MP3_DIR
MUSIC_DATA_PATH = r"./music_data.csv"

def get_arguments():
    parser = argparse.ArgumentParser(description="Parse track info and language to translate")
    parser.add_argument('--artist', type=str, default="david bisbal", help="Name of the artist.")
    parser.add_argument('--track', type=str, default="ave maría", help="Name of the track.")
    parser.add_argument('--language', type=str, default="spanish", help="Language of the track.")
    parser.add_argument('--retranslate', type=int, default=0, help="1 = retranslate always, 0 = use existing translation. 2 = never run translation on english")
    parser.add_argument('--file', action='store_true', help="Enable file loading mode")
    return parser.parse_args()

def kobold_server_check():
    """Check if the Kobold server is available and print its version."""
    try:
        response = requests.get(f"{ENDPOINT}/api/extra/version", timeout=5)
        response.raise_for_status()  # Raises HTTPError for bad responses
        version = response.json().get("version", "Unknown")
        logging.info(f"Kobold server is up and running! Version: {version}")
        return True
    except requests.RequestException as e:
        logging.error(f"Error connecting to Kobold server: {e}")
    except (json.JSONDecodeError, ValueError):
        logging.error("Kobold server is up, but version info could not be parsed.")
    return False

def read_file(file_path):
    """Read content from a file, returning its content or an empty string on error."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read().strip()
    except IOError as e:
        logging.error(f"Error reading file {file_path}: {e}")
    return ""

def save_file(file_path, content):
    """Save content to a file."""
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        logging.info(f"Saved file to {file_path}")
    except IOError as e:
        logging.error(f"Error writing file {file_path}: {e}")

def get_lyrics(artist, track, file_path, language):
    """Fetches lyrics from a local file or via an API call if not found locally."""
    if os.path.exists(file_path):
        lyrics = read_file(file_path)
        if lyrics:
            logging.info(f"Used local {language} lyrics.")
            return lyrics
    logging.info("Fetching lyrics from API...")
    result = subprocess.run(
        ["python3", LRC_SCRIPT, artist, track],
        capture_output=True, text=True
    )
    try:
        outer_data = json.loads(result.stdout)
        synced_str = outer_data.get("syncedLyrics", "")
        if not synced_str:
            raise ValueError("Empty Lyrics from API.")
        inner_data = json.loads(synced_str)
        synced_lyrics = inner_data.get("syncedLyrics", "")
        if not synced_lyrics:
            raise ValueError("Empty Lyrics in inner JSON.")
        logging.info("API request successful.")
        return synced_lyrics
    except (json.JSONDecodeError, ValueError) as e:
        logging.error(f"Error extracting lyrics: {e}")
    return ""

def translate_lyrics(lyrics, language):
    """Translates the provided lyrics into English while preserving timestamps."""
    prompt = (
        f"Translate the following {language} lyrics into English. Preserve the timestamps exactly as they appear, ensuring they remain correctly placed in the output. (Dont forget the timestamp in front of the first line!) "
        "Do not add any additional commentary. The output should end precisely when the song ends and always be in English.\n\n"
    )
    payload = {
        "prompt": f"<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}{lyrics}\n<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
        "max_length": 4000,
        "temperature": 0.2,
        "trim_stop": True,
        "stop_sequence": ["<|eot_id|>", "<|endoftext|>"],
        "bypass_eos": False,
        "cache_prompt": False,
    }
    
    logging.info("Translating lyrics with local LLM...")
    response = requests.post(f"{ENDPOINT}/api/v1/generate", json=payload)
    if response.ok:
        return response.json().get("results", [{}])[0].get("text", "").strip()
    else:
        error_msg = f"Error: Request failed with status code {response.status_code}."
        logging.error(error_msg)
        return error_msg

def download_track(artist, track, language):
    """Downloads the track's MP3 if it doesn't already exist."""
    mp3_path = os.path.join(MP3_DIR, f"{artist} - {track}.mp3")
    if os.path.exists(mp3_path):
        logging.info("Track already exists, skipping download.")
        return
    try:
        result = subprocess.run(
            ["python3", AUDIO_RIP_SCRIPT, '--artist', artist, '--track', track, '--musicDir', MP3_DIR, '--language', language],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60
        )
        logging.info(f"MP3 download successful with yt-dlp: {mp3_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during download: {e.stderr.decode()}")
    except FileNotFoundError:
        logging.error(f"Script not found: {AUDIO_RIP_SCRIPT}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")

def process_lyrics(artist, track, language, retranslate):
    """
    Processes the lyrics by reading the original, saving it if needed,
    and translating (or reusing) the translated version.
    Returns a tuple (original_lyrics, translated_lyrics).
    """
    os.makedirs(LYRICS_DIR, exist_ok=True)
    os.makedirs(MP3_DIR, exist_ok=True)
    
    file_path = os.path.join(LYRICS_DIR, f"{artist} - {track}.lrc")
    root, ext = os.path.splitext(file_path)
    file_path_OG = f"{root} OG{ext}"
    
    # Get original lyrics
    lyrics = get_lyrics(artist, track, file_path_OG, language)
    if not lyrics:
        logging.error(f"Error: Synced lyrics not found for {artist} - {track}. Exiting.")
        return None, None

    # Save original lyrics if needed
    if not os.path.exists(file_path_OG) or not lyrics.strip():
        save_file(file_path_OG, lyrics)

    # Start the MP3 download in a separate thread
    download_thread = threading.Thread(target=download_track, args=(artist, track, language))
    download_thread.start()
    
    translated_file_path = os.path.join(MP3_DIR, f"{artist} - {track}.lrc")
    translated_lyrics = None

    if language.lower() == "english":
        retranslate = 2

    if retranslate == 1:
        translated_lyrics = translate_lyrics(lyrics, language)      # Always retranslate
    elif retranslate == 0:
        if not os.path.exists(translated_file_path):        # Use existing translation if available, else translate
            translated_lyrics = translate_lyrics(lyrics, language)
    elif retranslate == 2:
        logging.info("Translation skipped because language is English")     #never translate english
    
    if translated_lyrics and "Error:" not in translated_lyrics:
        save_file(translated_file_path, translated_lyrics)
    elif os.path.exists(translated_file_path):
        logging.info("Translated lyrics already exist, skipping translation.")
    else:
        if retranslate != 2:
            logging.error("Error in translation.")
    
    download_thread.join()
    logging.info(f"Script completed successfully for {artist} - {track}.")
    return lyrics, translated_lyrics

def main():
    if not kobold_server_check():
        logging.error("No kobold server available. Exiting.")
        sys.exit(1)  # Exit with a nonzero status to indicate an error

    args = get_arguments()
    retranslate = args.retranslate
    if args.file:
        with open(MUSIC_DATA_PATH, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)  # Reads CSV and converts rows into dictionaries
            music_data = [row for row in reader]  # List of dictionaries
            for data in music_data:
                artist = data['Artist'].lower()
                track = data['Track Name'].lower()
                language = data['Language']
                if not artist or not track:
                    continue
                process_lyrics(artist, track, language, retranslate)
    else:
        artist = args.artist.lower()
        track = args.track.lower()
        language = args.language

        process_lyrics(artist, track, language, retranslate)

if __name__ == "__main__":
    main()