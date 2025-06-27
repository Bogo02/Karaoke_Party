# Karaoke Party
  Karaoke Party is a Python based application developed as part of the bachelor's thesis project at Politehnica University of Timișoara.

## General description
  It provides an interactive environment where users can sing along with songs, view real-time lyrics, and receive a score based on the accuracy of their vocal pitch compared to reference data.

## Repository
The complete source code and auxiliary files are stored in this repository:
**https://github.com/Bogo02/Karaoke_Party/tree/main**

## Prerequisets
The application is developed in Python 3.13.2
The following libraries are used in the application:
- 'tkinter'
- 'pygame'
- 'pyaudio'
- 'numpy'
- 'PIL' (pillow)
- 'sqlite3'
- 'math'
- 'os'
- 'time'
- 'threading'
- 're'
- 'sys'
- 'filedialog'
- 'messagebox'
- 'Image'
- 'ImageTk'

Out of these, the following libraries are not implicitly included in Python and have to be separately installed:
- 'pygame'
- 'pyaudio'
- 'numpy'
- 'PIL'(Pillow)

They can be installed with the command: pip install pygame pyaudio numpy pillow

## Steps to run the application

1. Clone the repository: **https://github.com/Bogo02/Karaoke_Party/tree/main**
2. Install the necessary libraries: pip install pygame pyaudio numpy pillow
3. Run the application: python "Karaoke Party.py"

## Project structure
  Karaoke Party/
  
  ├── build             # Build folder for the executable file
  
  ├── Karaoke Party.py  # Main file
  
  ├── Karaoke Party.exe # Executable file
  
  ├── Karaoke Party.spec
  
  ├── Tracks/           # Audio + Lyrics + Pitch files
  
  │   └── [Song_name]/  # Each song has a folder
  
  │   ├── song.mp3
  
  │   ├── song.lrc
  
  │   ├── song.txt
  
  │   ├── song.png
  
  ├── leaderboard.db    # Local database (automatically created)
  
  ├──Karaoke_icon.ico   # Application icon
  
  ├──README.md          # This file

## Executable version
  The application is compiled into an executable .exe file for Windows, by using pyinstaller.
  The executable file is not included in this repository due to the file size limitations of GitHub, but can be provided or installed with the commands:
  - pip install pyinstaller  #for installing pyinstaller
  - pyinstaller --onefile --noconsole --add-data "Karaoke_icon.ico;."  "Karaoke Party.py" 
The file will be created in a dist folder, and will have to be taken out of the folder and placed in the main folder
