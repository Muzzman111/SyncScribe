import requests
import json
import subprocess
import os

ENDPOINT = "http://127.0.0.1:5001"
LYRICS_DIR = r"./Lyrics"
LRC_SCRIPT = r"./LRCLib_API.py"
AUDIO_RIP_SCRIPT = r"./youtubedlp rip script.py"
MP3_DIR = r"C:\Users\nmuzz\Music\with lrc"
track_name = "el mayor de los ranas"
artist_name = "Victor Valverde"

def get_lyrics(artist, track, file_path):
    """Fetches only the synced lyrics from a local file or via an external script."""
    if os.path.exists(file_path):  # Try loading from local file first
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                outer_data = json.load(file)
            synced_str = outer_data.get("syncedLyrics")
            if synced_str:
                return synced_str
            else:
                raise Exception("Empty syncedLyrics")
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading lyrics file: {e}")
    
    # If local file isn't available or valid, run the external script.
    result = subprocess.run(
        ["python3", LRC_SCRIPT, artist, track],
        capture_output=True, text=True
    )
    try:
        outer_data = json.loads(result.stdout)
        synced_str = outer_data.get("syncedLyrics")
        if not synced_str:
            raise Exception("Empty syncedLyrics")
        # Parse the inner JSON to get the final synced lyrics.
        inner_data = json.loads(synced_str)
        synced_lyrics = inner_data.get("syncedLyrics")
        if not synced_lyrics:
            raise Exception("Empty syncedLyrics in inner JSON")
        return synced_lyrics
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON from subprocess output: {e}")
    except Exception as e:
        print(f"Error extracting lyrics: {e}")
    
    return ""

def translate_lyrics(lyrics):
    prompt = (
        "Translate the following Spanish song lyrics into English. Preserve the timestamps right where they are and please do not forget them when you translate to English. End your output precisely when the song ends without any additional commentary."
    )
   
    payload = {
        "prompt": f"<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}{lyrics}\n<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
        "max_length": 2500,
        "temperature": 0.25,
        "trim_stop": True,
        "stop_sequence": ["<|eot_id|>", "<|endoftext|>"],
        "bypass_eos": False,
        "keep": 0
    }
    response = requests.post(f"{ENDPOINT}/api/v1/generate", json=payload)
    if response.status_code == 200:
        return response.json().get("results", [{}])[0].get("text", "").strip()
    
    return f"Error: Request failed with status code {response.status_code}."

# Main execution
file_path = os.path.join(LYRICS_DIR, f"{artist_name} - {track_name}.lrc")

lyrics = get_lyrics(artist_name, track_name, file_path)
#print(lyrics)
translated_lyrics = translate_lyrics(lyrics)
#print(translated_lyrics)

# Save the translated lyrics to a file
if translated_lyrics and not translated_lyrics.startswith("Error:"):
    # Save translated lyrics
    translated_file_path = os.path.join(MP3_DIR, f"{artist_name} - {track_name}.lrc")
    with open(translated_file_path, "w", encoding="utf-8") as file:
        file.write(translated_lyrics)
    print(f"\nTranslated lyrics saved to {translated_file_path}")

    # Save original lyrics if the file is missing or empty/whitespace-only
    save_original = True
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            if file.read().strip():
                save_original = False

    if save_original:
    # Append " OG" before the file extension
        root, ext = os.path.splitext(file_path)
        file_path_OG = f"{root} OG{ext}"
        with open(file_path_OG, "w", encoding="utf-8") as file:
            file.write(lyrics)
        print(f"Original lyrics saved to {file_path_OG}")
else:
    print(f"Error in translation: {translated_lyrics}")

mp3_path = os.path.join(MP3_DIR, f"{artist_name} - {track_name}.mp3")
# Check if the MP3 file already exists
if not os.path.exists(mp3_path):
    try:
        result = subprocess.run(
            ["python3", AUDIO_RIP_SCRIPT, '--artist', artist_name, '--track', track_name],
            check=True,  # Raise an exception if the command fails
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=60  # Timeout after 60 seconds
    )
        print(f"Download successful: {mp3_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during download: {e.stderr.decode()}")
    except FileNotFoundError:
        print(f"Script not found: {AUDIO_RIP_SCRIPT}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
else: print("Track Exists")