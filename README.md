# SyntheticAudioGenerator
SyntheticAudioGenerator is a simple script created for BiomojoLLC to create vast quantities of audio training data using a variable length array of audio generating services, including Resemble.ai, Replica Studios, Google API, and an Amazon service. 


```bash 
git clone https://github.com/BioMojoLLC/SyntheticAudioGenerator.git
```

```diff 
+ ### Setup
+ ```
1) Copy settings_template.py into settings.py.
2) Open up settings.py and fill out all of the fields with your user information for each service.
3) Create a directory with any number of .txt files containing your input sentences.
4) Create a keywords.txt file, with each key word on a new line. These words are what the program will be creating data for.
5) Optionally create a directory for audio to be saved to. 
6) Run

### Setting up your virtual environment
```bash
apt-get update
apt-get install python3-venv
python3 -m venv data-venv
source venv/bin/activate

pip3 install SyntheticAudioGenerator/requirements.txt
```

### How to Run
All file/folder paths are relative to your **working directory**, not the main.py file. 
```bash
python main.py --text_dir <path/to/text/dir> --audio_dir <path/to/output/dir> --keywords <path/to/keyword.txt> --mins_per_term <integer> 
```

There is also support for short options.
```bash
python main.py -t <path/to/text/dir> -a <path/to/output/dir> -k <path/to/keyword.txt> -m <integer> 

