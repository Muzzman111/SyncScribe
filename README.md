# Readme

## Project Description

This project downloads time-stamped foreign language lyrics for any song, translates them into English using an AI model, and retrieves the corresponding MP3 from YouTube. The songs can then be played in the Quod Libet music player, with both the original and translated lyrics scrolling in sync. The lyrics are fetched using the lrclib.net API in LRC format, translation is powered by KoboldCPP running QWEN 2.5 7B on your device, and yt-dlp is used to download the MP3s.

## Running the Script

1. **Start KoboldCPP Server**
   - Launch KoboldCPP and click "Load" at the bottom of the window. 
   - Select your saved Kobold preset. (If you haven't set up a preset, refer to the "KoboldCPP Model Config" section.)
   - Click "Launch" to load the model weights and start the server.

2. **Prepare the CSV File with Song Details**  
   - Open the music_data.csv file using Excel, Google Sheets, or your preferred spreadsheet tool.
   - Enter the details for each song you wish to download and translate
   - Note: English songs can be downloaded too. Translation will be automatically skipped if you fill out the language column of the csv with "english"
   - Any song missing the artist or track name will be skipped.

3. **Run the Script**  
   - Execute the script with the following command if you are using the music_data csv file:
      ```
      python "translate_lyrics_main_script.py" --file
      ```
   - Songs may be downloaded individually like this:
      ```
      python "translate_lyrics_main_script.py" --artist "enter artist name" --track "enter track name" --language "enter the song language"
      ```
   - Note: The arguments `--artist` and `--track` are required, while `--language` is optional but recommended.

## Windows Installation From Scratch

### Install Python and Get Requirements

1. **Install Python**  
   - Download and install Python from [python.org](https://www.python.org/downloads/release/python-3129/).  
   - Be sure to check the box to add Python to your PATH during installation.

2. **Install Python Requirements**  
   - Change directory to the script folder:
     ```
     cd /SyncScribe
     ```
   - Run the following command to install the required packages:
     ```
     pip install -r requirements.txt
     ```

### Install Supporting Software

1. **Download Quod Libet**  
   - Download the Quod Libet music player for displaying lyrics from [Quod Libet releases](https://github.com/quodlibet/quodlibet/releases/).  
   - A portable installation is ideal; you can place it in the script directory or any location of your choice.

2. **Download KoboldCPP**  
   - Download KoboldCPP for local LLM translation from [KoboldCPP releases](https://github.com/LostRuins/koboldcpp/releases/).  
   - Choose the `nocuda` version if you don’t have an NVIDIA GPU or the CUDA version if you do.  
   - Install KoboldCPP wherever you prefer.

3. **Download a Large Language Model**
   - Get the translation model from [Qwen2.5-7B-Instruct on Hugging Face](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/tree/main).  
   - Note: LLAMA 3 models may refuse translation due to violent content in song lyrics, but QWEN 2.5 7B works flawlessly.  
   - I used the Q5_k_m quantization and it worked well.  
   - If the model is split into multiple parts, ensure you download all of them.  
   - You can place the model anywhere on your system.

### One-time Configuration

#### Quod Libet Dual Lyrics Plugin Config

1. **Locate the Plugin Folder**  
   - Open File Explorer and navigate to the Quod Libet plugin folder. It is located at this path within the Quod Libet folder:  
     ```
     \quodlibet-4.6.0-portable\data\lib\python3.11\site-packages\quodlibet\ext\events
     ```  
     Or, if Quod Libet is in your Downloads folder, you can paste:  
     ```
     %userprofile%\Downloads\quodlibet-4.6.0-portable\data\lib\python3.11\site-packages\quodlibet\ext\events
     ```

2. **Copy the Plugin File**  
   - Copy "SynchronizedLyricsDualLanguage.py" from the quod_libet_plugin/ folder into the events folder you opened in the previous step.

3. **Activate the Plugin**  
   - Open Quod Libet, navigate to **File > Plugins**, scroll down until you see "Synchronized Lyrics Dual Language," check the box, and close the dialog.  
   - This plugin enables you to view lyrics in both languages while listening.

#### KoboldCPP Model Config

1. **Set Presets**  
   - Open KoboldCPP and choose a preset at the top:  
     - Select "use Vulkan" if you don’t have an NVIDIA GPU.  
     - Select "use CUBLAS" if you do have one.  
     - Select "use CPU" if neither of the above options work.

2. **Set Context**  
   - Use the slider to set the "Context Size" to 6144. A smaller context may not be sufficient for longer songs.

3. **Enable Memlock**  
   - Click on "Hardware" in the vertical menu on the left.  
   - Check the box for "Use memlock" near the bottom.  
   - This ensures the model stays in memory without paging out to your disk.

4. **Load the Model**  
   - Click "Load Model" at the bottom and select your model. If your model consists of multiple parts, select part 1.

5. **Save Preset**  
   - Click "Save Preset" at the bottom of the KoboldCPP window and save the configuration in the same folder as your model.  
   - This allows you to load the preset for future sessions without reconfiguring everything.

### Troubleshooting

**Error Downloading Lyrics**
- Most of the time this happens because you made a typo entering the artist or track name
- There is also a chance lrclib.net does not have synced lyrics for a particular song. In that case there is not much you can do if you want time synced lyrics.

**Audio and Lyrics out of Sync**
- Happens sometimes when the script downloads an MP3 of a music video with extra fluff at the beginning.
- The youtube_rip_script.py automatically downloads the shortest of the first 2 youtube results but you can broaden the search to choose the shortest of any amount of results on line 32 of the aforementioned script
