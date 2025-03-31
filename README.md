# Readme

## Project Description

This project downloads time-stamped foreign language lyrics for any song or list of songs, translates them into English using an AI model, and retrieves the corresponding MP3 from YouTube. The songs can then be played in the Quod Libet music player, with both the original and translated lyrics scrolling in sync. The lyrics are fetched using the lrclib.net API in LRC format, translation is powered by KoboldCPP running QWEN 2.5 7B on your device, and yt-dlp is used to download the MP3s.

## Running the Script

1. **Start KoboldCPP Server**
   - Launch KoboldCPP and click "Load" at the bottom of the window. 
   - Select your saved Kobold preset. (If you haven't set up a preset, refer to the "KoboldCPP Model Config" section.)
   - Click "Launch" to load the model weights and start the server.

2. **Prepare the CSV File with Song Details**
   - Filling out the csv allows you to run the script with the argument "--file" and download multiple songs at a time.
   - Open the music_data.csv file using Excel, Google Sheets, or your preferred spreadsheet tool.
   - Enter the details for each song you wish to download and translate
   - Note: English songs can be downloaded too. Translation will be automatically skipped if you fill out the language column of the csv with "english"

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
   - Note: You can use any model of your choice but LLAMA 3 models may refuse translation due to violent content in song lyrics. QWEN 2.5 7B works flawlessly.  
   - I used the Q5_k_m quantization and it worked well.  
   - If the model is split into multiple parts, ensure you download all of them.

### One-time Configuration

#### KoboldCPP Model Config

1. **Set Presets**  
   - Open KoboldCPP and choose a preset at the top:  
     - Select "use Vulkan" if you don’t have an NVIDIA GPU.  
     - Select "use CUBLAS" if you do have one.  
     - Select "use CPU" if neither of the above options work.

2. **Set Context**  
   - Use the slider to set the "Context Size" to 8192. 
   - Smaller context may not be sufficient for longer songs. The tradeoff is larger context runs slower.

3. **Enable Memlock**  
   - Click on "Hardware" in the vertical menu on the left.  
   - Check the box for "Use memlock" near the bottom.  
   - This ensures the model stays in memory without paging out to your disk.

4. **Load the Model**  
   - Click "Load Model" at the bottom and select your model. If your model consists of multiple parts, select part 1.

5. **Save Preset**  
   - Click "Save Preset" at the bottom of the KoboldCPP window and save the configuration in the same folder as your model.  
   - This allows you to load the preset for future sessions without reconfiguring everything.

#### Quod Libet Dual Lyrics Plugin Config
   Adding the modified plugin to Quod Libet allows you to view song lyrics side by side in both the original language and English.
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

### Known Issues

**Error Downloading Lyrics**
   - This can happen if you misspell the artist or track name.
   - There is also a chance lrclib.net does not have synced lyrics for a particular song. In that case you would have to look somewhere else to find synced lyrics.

**Audio and Lyrics out of Sync**
   - Happens occasionally when the script downloads an MP3 of a music video with fluff at the beginning.
   - The youtube_rip_script.py automatically downloads the shortest video from the first two YouTube search results. However, you can modify the script to select a specific song or expand the search to consider more results. This can be adjusted on line 32 of the script.
   - There is a txt in the plugins folder called "how to add or remove time from the start of an mp3.txt" that uses ffmpeg to cut or add time to a song to get it in sync with the lyrics.

**LLM Screws up the Translation**
   - Can happen if your song is too long for the context and Kobold shifts your prompt out of the models awareness. The solution is to allocate more context in koboldcpp and the prompt variable in the main script.
   - This can also occur when using too small of a model with poor prompt adherance.
   - If for any reason you want to retranslate and regenerate the lrc file, run the script with the retranslate arguement set to 1.