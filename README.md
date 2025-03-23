*Readme*


Project Description

    This project downloads time-stamped, foreign language lyrics from the lrclib.net API, translates them to English using a local language model, and retrieves the corresponding MP3. The song can then played in the Quod Libet music player with both the original and translated lyrics rolling in sync. KoboldCPP runs QWEN 2.5 7B for translation, and yt-dlp is used to download the MP3.


Running the Script

    Start KoboldCPP and click "Load" at the bottom of the window. Load the model preset you made earlier and click "Launch"

    To run the script, first cd into the folder with: cd *yourpath*/Lyric_Translator

    Now you can run the script with the following command: python "translate_lyrics_main_script.py" --artist "enter artist name" --track "enter track name" --language "enter the song language"
        The arguments "--artist" and "--track" are required while "--language" is optional.


Windows Installation From Scratch

    Install Python and Get Requirements

        Install Python if you dont have it: https://www.python.org/downloads/release/python-3129/
            Make sure to check the box to put Python on path during installation

        cd to the script folder: cd *yourpath*/Lyric_Translator

        run: pip install requirements.txt

    Install Supporting Software

        Download yt-dlp.exe (youtube download player) for downloading song MP3s: https://github.com/yt-dlp/yt-dlp/releases/
            Must go in the script dir "*yourpath*/Lyric_Translator" 

        Download Koboldcpp for local LLM translating: https://github.com/LostRuins/koboldcpp/releases/
            Install the koboldcpp nocuda version if you dont have an NVDIA GPU and obviously the CUDA version if you do
            This program can go where ever you want it

        Download Quod Libet music player for displaying lyrics while listening: https://github.com/quodlibet/quodlibet/releases/
            Portable installation is ideal, you can put it in the script dir or anywhere else you want it

        Download an AI model to translate your lyrics: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/tree/main
            I found the LLAMA 3 models would refuse translation becuase of violent content in song lyrics but QWEN 2.5 7B worked flawlessly
            I used the Q5_k_m quantization and it worked well. Dont forget to download both parts if the model is in two parts.
            You can put the model anywhere.


    One time Config

        Quod Libet Dual Lyrics Plugin Config

            Open the file explorer and paste this in to move to the plugin folder of Quod Libet: *yourpath*\quodlibet-4.6.0-portable\data\lib\python3.11\site-packages\quodlibet\ext\events
            Or if you put Quod in downloads: %userprofile%\Downloads\quodlibet-4.6.0-portable\data\lib\python3.11\site-packages\quodlibet\ext\events

            Copy the python file "SynchronizedLyricsDualLanguage.py" from the Lyric_Translator folder into the events folder you moved to in step 1

            Open Quod Libet and click: File > plugins, scroll down until you see "Synchronized Lyrics Dual Language", check the box and close. Setup done.
            This plugin lets you see the lyrics of both languages while you listen to the song.


        KoboldCPP Model Config

            Set Presets:
                Open KoboldCPP and under "presets" at the top, select either "use Vulkan" if you dont have NVIDIA gpu, "use CUBLAS" if you do, and "use CPU" if those other two dont work
            
            Set Context:
                Use the slider to set the "Context Size" to 6144. Too much smaller and a large song may run out of context.

            Set Memlock:
                Click "Hardware" in the vertical menu on the left.
                Look near the bottom and check the box that says "Use memlock"
                This makes it so the model stays in memory and doesnt page out to your disk.

            Load Model:
                Click load model at the bottom and select your model. If it has multiple parts, select part 1.

            Save Preset:
                Click save preset at the bottom of the Kobold window and save it in the same folder as your model.
                This makes it so you dont have to do this config every time and just load the preset.
