# Readme

## Project Description

This project downloads time-stamped, foreign language lyrics from the lrclib.net API, translates them into English using a local language model, and retrieves the corresponding MP3. The song can then be played in the Quod Libet music player with both the original and translated lyrics scrolling in sync. KoboldCPP runs QWEN 2.5 7B for translation, and yt-dlp is used to download the MP3.

## Running the Script

1. **Start KoboldCPP**  
   - Click "Load" at the bottom of the window.  
   - Load the model preset you created earlier and click "Launch".

2. **Navigate to the Script Folder**  
   - Open your terminal and change directory into the project folder:  
     ```
     cd *yourpath*/Lyric_Translator
     ```

3. **Run the Script**  
   - Execute the script with the following command:
     ```
     python "translate_lyrics_main_script.py" --artist "enter artist name" --track "enter track name" --language "enter the song language"
     ```
   - Note: The arguments `--artist` and `--track` are required, while `--language` is optional.

## Windows Installation From Scratch

### Install Python and Get Requirements

1. **Install Python**  
   - Download and install Python from [python.org](https://www.python.org/downloads/release/python-3129/).  
   - Be sure to check the box to add Python to your PATH during installation.

2. **Install Python Requirements**  
   - Change directory to the script folder:
     ```
     cd *yourpath*/Lyric_Translator
     ```
   - Run the following command to install the required packages:
     ```
     pip install -r requirements.txt
     ```

### Install Supporting Software

1. **Download yt-dlp**  
   - Get `yt-dlp.exe` for downloading MP3s from [yt-dlp releases](https://github.com/yt-dlp/yt-dlp/releases/).  
   - Place the executable in the script directory: `*yourpath*/Lyric_Translator`.

2. **Download KoboldCPP**  
   - Download KoboldCPP for local LLM translation from [KoboldCPP releases](https://github.com/LostRuins/koboldcpp/releases/).  
   - Choose the `nocuda` version if you don’t have an NVIDIA GPU or the CUDA version if you do.  
   - Install KoboldCPP wherever you prefer.

3. **Download Quod Libet**  
   - Download the Quod Libet music player for displaying lyrics from [Quod Libet releases](https://github.com/quodlibet/quodlibet/releases/).  
   - A portable installation is ideal; you can place it in the script directory or any location of your choice.

4. **Download an AI Translation Model**  
   - Get the translation model from [Qwen2.5-7B-Instruct on Hugging Face](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/tree/main).  
   - Note: LLAMA 3 models may refuse translation due to violent content in song lyrics, but QWEN 2.5 7B works flawlessly.  
   - I used the Q5_k_m quantization and it worked well.  
   - If the model is split into multiple parts, ensure you download all of them.  
   - You can place the model anywhere on your system.

### One-time Configuration

#### Quod Libet Dual Lyrics Plugin Config

1. **Locate the Plugin Folder**  
   - Open File Explorer and navigate to the Quod Libet plugin folder. For example:  
     ```
     *yourpath*\quodlibet-4.6.0-portable\data\lib\python3.11\site-packages\quodlibet\ext\events
     ```  
     Or, if Quod Libet is in your Downloads folder:  
     ```
     %userprofile%\Downloads\quodlibet-4.6.0-portable\data\lib\python3.11\site-packages\quodlibet\ext\events
     ```

2. **Copy the Plugin File**  
   - Copy the file `SynchronizedLyricsDualLanguage.py` from the Lyric_Translator folder into the events folder from the previous step.

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
