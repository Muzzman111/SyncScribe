import requests
import json
import subprocess
import os

ENDPOINT = "http://127.0.0.1:5001" #koboldcpp llm endpoint
LYRICS_DIR = r"./Lyrics" #where the OG spanish lyrics are stored
LRC_SCRIPT = r"./LRCLib_API.py"
AUDIO_RIP_SCRIPT = r"./youtubedlp rip script.py"
MP3_DIR = r"C:\Users\nmuzz\Music\with lrc" #wherever you want your mp3 files stored
Retranslate = 0 #setting this to 1 will always rewrite your translated lrc file with the llm. 0 will let be if it already exists

track_name = "subeme la radio"                 #MUST ENTER
artist_name = "enrique iglesias"      #MUST ENTER

def get_lyrics(artist, track, file_path):
    """Fetches the lyrics from a local text file, reading line by line."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()  # Read file line by line
                synced_str = "".join(lines)  # Join the lines into a single string
                #print(synced_str)
                print(f"Used local Spanish lyrics")
            return synced_str
        except IOError as e:
            print(f"Error reading lyrics file: {e}")
    else:
        print("File not found locally.")

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
        else: print(f"API request sent")
        return synced_lyrics
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON from subprocess output: {e}")
    except Exception as e:
        print(f"Error extracting lyrics: {e}")
    
    return ""

def translate_lyrics(lyrics):
    prompt = (
        "Translate the following Spanish song lyrics into English. Preserve the timestamps right where they are and please do not forget them when you translate to English. End your output precisely when the song ends without any additional commentary.\n"
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
    print(f"Translating lyrics with local LLM...")
    response = requests.post(f"{ENDPOINT}/api/v1/generate", json=payload)
    if response.status_code == 200:
        return response.json().get("results", [{}])[0].get("text", "").strip()
    
    return f"Error: Request failed with status code {response.status_code}."

# Main execution
file_path = os.path.join(LYRICS_DIR, f"{artist_name} - {track_name}.lrc")
root, ext = os.path.splitext(file_path)     # Append " OG" before the file extension
file_path_OG = f"{root} OG{ext}"    
lyrics = get_lyrics(artist_name, track_name, file_path_OG)
#print(lyrics)

# Save original lyrics if the file is missing or empty/whitespace-only
save_original = True
if os.path.exists(file_path_OG):
    with open(file_path_OG, "r", encoding="utf-8") as file:
        if file.read().strip():
             save_original = False
if save_original:
    with open(file_path_OG, "w", encoding="utf-8") as file:
        file.write(lyrics)
    print(f"Original lyrics saved to {file_path_OG}")

translated_lyrics = None  # Initialize it to None to prevent the NameError
translated_file_path = os.path.join(MP3_DIR, f"{artist_name} - {track_name}.lrc")
if not os.path.exists(translated_file_path) or Retranslate: translated_lyrics = translate_lyrics(lyrics)   #translate the lyrics if they dont exist or I want to regenerate them but skip othewise
#print(translated_lyrics)   
if translated_lyrics:       # Save the translated lyrics to a file
    with open(translated_file_path, "w", encoding="utf-8") as file:
        file.write(translated_lyrics)
    print(f"Translated lyrics saved to {translated_file_path}")
elif not translated_lyrics and not os.path.exists(translated_file_path): print(f"Error in translation: {translated_lyrics}")
elif not translated_lyrics and os.path.exists(translated_file_path): print(f"Lyrics weren't translated because they already exist")

mp3_path = os.path.join(MP3_DIR, f"{artist_name} - {track_name}.mp3")
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
else: print("Track Already Exists")