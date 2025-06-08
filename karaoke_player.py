import math
import tkinter as tk
import pygame
import os
import time
import threading
import re
import pyaudio  
import numpy as np  
from PIL import Image, ImageTk
import sqlite3

TRACKS_FOLDER = os.path.join(os.path.dirname(__file__), "Tracks")

def parse_lrc(file_path):
    lyrics = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('['):
                try:
                    time_tag = line[line.index('[')+1:line.index(']')]
                    minutes, seconds = time_tag.split(':')
                    total_seconds = int(minutes) * 60 + float(seconds)
                    text = line[line.index(']')+1:].strip()
                    lyrics.append((total_seconds, text))
                except:
                    continue
    return lyrics

def create_db():
    conn= sqlite3.connect('leaderboard.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS leaderboard (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    song_name TEXT NOT NULL,
                    player_name TEXT NOT NULL,
                    score INTEGER NOT NULL
                )''')
    conn.commit()
    conn.close()

def get_leaderboard(song_name):
    conn = sqlite3.connect('leaderboard.db')
    c = conn.cursor()
    c.execute('SELECT player_name, score FROM leaderboard WHERE song_name = ? ORDER BY score DESC LIMIT 15', (song_name,))
    results= c.fetchall()
    conn.close()
    return results

def save_score(song_name, score, master):
    def on_submit():
        name= name_entry.get().strip()
        if name:
            conn = sqlite3.connect('leaderboard.db')
            c = conn.cursor()
            c.execute('INSERT INTO leaderboard (song_name, player_name, score) VALUES (?,?,?)', (song_name, name, score))
            conn.commit()
            c.close()
            popup.destroy()
    
    leaderboard = get_leaderboard(song_name)
    if len(leaderboard) < 10 or score > leaderboard[-1][1]:
        popup = tk.Toplevel(master)
        popup.title("High Score!")
        popup.geometry("300x150")
        popup.grab_set()

        tk.Label(popup, text = "High score! Enter your name: ").pack(pady = 10)
        name_entry = tk.Entry(popup, font = ("Arial", 14))
        name_entry.pack(pady = 5)
        submit_btn = tk.Button(popup, text = "Submit", command = on_submit)
        submit_btn.pack(pady = 10)
        name_entry.focus_set()

create_db()

class KaraokeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Karaoke Party")
        self.geometry("1240x800")

        pygame.mixer.init()

        self.menu_frame = MenuFrame(self)
        self.karaoke_frame = KaraokeFrame(self)
        self.score_frame = ScoreFrame(self) 

        self.menu_frame.pack(fill="both", expand=True)

    def show_menu(self):
        self.karaoke_frame.pack_forget()
        self.score_frame.pack_forget()
        self.menu_frame.pack(fill="both", expand=True)

    def show_score(self, score_value):
        self.karaoke_frame.pack_forget()
        self.menu_frame.pack_forget()
        self.score_frame.display_score(score_value)
        self.score_frame.pack(fill = "both", expand = True)

    def show_karaoke(self, song_folder):
        self.menu_frame.pack_forget()
        self.score_frame.pack_forget()
        self.karaoke_frame.load_song(song_folder)
        self.karaoke_frame.pack(fill="both", expand=True)

class MenuFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg='Lavender')
        self.master = master
        self.load_song_list()

    def load_song_list(self):
        self.song_images = []
        for folder_name in os.listdir(TRACKS_FOLDER):
            folder_path = os.path.join(TRACKS_FOLDER, folder_name)
            if os.path.isdir(folder_path):
                files = os.listdir(folder_path)
                if any(f.endswith(('.mp3','.m4a')) for f in files) and any(f.endswith('.lrc') for f in files):
                    song_box = tk.Frame(self, bg='Lavender', highlightbackground="black", highlightthickness=1)
                    song_box.pack(pady=10, padx=20, fill="x")

                    image_file=  next((f for f in files if f.lower().endswith((".jpeg",".png"))),None) 
                    if image_file:  
                        image_path = os.path.join(folder_path, image_file)   
                        img = Image.open(image_path)  
                        img = img.resize((60, 60))  
                        photo = ImageTk.PhotoImage(img)  
                        self.song_images.append(photo) 
                        img_label = tk.Label(song_box, image=photo, bg='white') 
                        img_label.pack(side="left", padx=10)  
                    
                    label = tk.Label(song_box, text=folder_name, font=("Arial", 18), bg="Lavender", anchor="w")
                    label.pack(side="left", padx=10, pady=10)

                    play_button = tk.Button(song_box, text="▶️ Play", command=lambda folder=folder_name: self.master.show_karaoke(folder))
                    play_button.pack(side="right", padx=10)

                    leaderboard_button = tk.Button(song_box, text = "Leaderboard", command = lambda folder = folder_name: self.show_leaderboard(folder))
                    leaderboard_button.pack(side = "right", padx = 10)
    
    def show_leaderboard(self, song_name):
        leaderboard = get_leaderboard(song_name)

        popup = tk.Toplevel(self)
        popup.title(f"Leaderboard - {song_name}")
        popup.geometry("600x400")
        popup.grab_set()

        tk.Label(popup,text = f"Leaderboard for '{song_name}'", font = ("Arial",14)).pack(pady=10)

        if leaderboard:
            for i, (name, score) in enumerate(leaderboard, start=1):
                entry_text = f"{i}. {name} - {score} points"
                tk.Label(popup, text=entry_text, font=("Arial", 14)).pack(anchor="w", padx=20)
        else:
            tk.Label(popup, text="No scores yet!", font=("Arial", 14)).pack(pady=20)


class ScoreFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg='white')
        self.master = master

        self.score_label = tk.Label(self, text = "", font = ("Arial", 50), bg = 'white')
        self.score_label.pack(pady= 100)

        self.back_button = tk.Button(self, text = "Back to Menu", font = ("Arial", 18), command = lambda:self.master.karaoke_frame.back_to_menu())
        self.back_button.pack(pady = 20)

    def display_score(self, score_value):
        self.score_label.config(text=f"FINAL SCORE: \n{score_value} points")
    

class KaraokeFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg='white')
        self.master = master
        self.lyrics = []
        self.pitch_segments = []
        self.current_line = 0
        self.playing = False
        self.current_page=0
        self.page_duration=5

        self.total_hits = 0
        self.green_hits = 0
        self.yellow_hits = 0
        self.red_hits = 0

        #SCORE TEXT SHOWN AT THE TOP
        self.score_label = tk.Label(self, text="Score: 0 (0%)", font=("Arial", 18), bg="white")
        self.score_label.pack(pady=10)

        # PITCH BOXES DISPLAY
        self.canvas = tk.Canvas(self, width=1000, height=500, bg="white", highlightthickness=0)
        self.canvas.pack(padx=10)
        self.page_duration = 4
        self.current_page = 0

        # LYRICS Display at Bottom
        self.lyrics_label = tk.Label(self, text="", font=("Arial", 28), bg="white", wraplength=800)
        self.lyrics_label.pack(side="top", pady=(70, 20))

        # BUTTONS 
        self.controls_frame = tk.Frame(self, bg="white")
        self.controls_frame.pack(side="bottom", pady=18)

        self.back_button = tk.Button(self.controls_frame, text="Back to Menu", font=("Arial", 14), command=self.back_to_menu)
        self.back_button.pack(side="left", padx=20)

        # MIC VARIABLES 
        self.latest_pitch = 0
        self.mic_thread = None  
        self.mic_running = False   

    def load_song(self, song_folder):
        folder_path = os.path.join(TRACKS_FOLDER, song_folder)
        audio_file = None
        lrc_file = None
        fqz_file = None

        for file in os.listdir(folder_path):
            if file.endswith(('.mp3','.m4a')):
                audio_file = os.path.join(folder_path, file)
            elif file.endswith('.lrc'):
                lrc_file = os.path.join(folder_path, file)
            elif file.endswith('.txt'):
                fqz_file = os.path.join(folder_path, file)

        if fqz_file:
            self.pitch_segments = KaraokeFrame.parse_pitch_file(fqz_file)

        if audio_file and lrc_file:
            self.lyrics = parse_lrc(lrc_file)
            self.current_line = 0
            self.current_song_name = song_folder
            self.start_song(audio_file)

    def start_song(self, audio_path):
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        self.playing = True

        self.mic_running = True  
        self.mic_thread = threading.Thread(target=self.listen_to_mic)  
        self.mic_thread.start()  

        threading.Thread(target=self.update_lyrics_and_pitch).start()

    def stop_song(self):
        self.playing = False
        self.mic_running = False  
        pygame.mixer.music.stop()
        self.lyrics_label.config(text="")

        #Final score 
        score_value = self.green_hits * 20 + self.yellow_hits * 10 + self.red_hits * 2
        #max_possible_score = len(self.pitch_segments) * 20
        #percentage = (score_value / max_possible_score) * 100 if max_possible_score else 0 
 
        self.score_label.config(text=f"Score: {score_value} ")

        self.master.show_score(score_value)
        save_score(self.current_song_name, score_value, self.master)

        #reset values if song interrupted/changed
        self.total_hits = 0
        self.green_hits = 0
        self.yellow_hits = 0
        self.red_hits = 0
        self.score_label.config(text="Score: 0 (0%)")

        #Reset pitch segments
        self.pitch_segments = []


    def back_to_menu(self):
        self.stop_song()
        self.master.show_menu()
        self.pitch_segments = []

    def update_lyrics_and_pitch(self):
        start_time = time.time()
        canvas_width = 1000
        canvas_height = 500
        pitch_min = 0
        pitch_max = 500
        page_duration = self.page_duration

        current_page_start = 1
        sang_boxes = []

        while self.playing:
            if not pygame.mixer.music.get_busy():
                self.stop_song()
                break
            elapsed = time.time() - start_time

            # Update lyrics text
            if self.current_line < len(self.lyrics):
                timestamp, text = self.lyrics[self.current_line]
                if elapsed >= timestamp:
                    self.lyrics_label.config(text=text)
                    self.current_line += 1

            # Calculate current page based on elapsed time and page duration
            page_start = math.floor(elapsed / page_duration) * page_duration
            page_end = page_start + page_duration

            # Clear canvas when page changes to avoid clutter
            if page_start != current_page_start:
                current_page_start = page_start
                self.canvas.delete("pitch")
                self.canvas.delete("sang")

            # PITCH BOXES
            
            for seg_start, seg_end, pitch in self.pitch_segments:
                if seg_end < page_start or seg_start > page_end:
                    continue

                seg_start_clipped = max(seg_start, page_start)
                seg_end_clipped = min(seg_end, page_end)

                x1 = ((seg_start_clipped - page_start) / page_duration) * canvas_width
                x2 = ((seg_end_clipped - page_start) / page_duration) * canvas_width
                y = canvas_height - ((pitch - pitch_min) / (pitch_max - pitch_min)) * canvas_height

                self.canvas.create_rectangle(x1, y - 10, x2, y + 10, fill="", outline="black",tags="pitch")

            #SANG BOXES

            if self.latest_pitch > 0:

                sang_width = (0.025 / page_duration) * canvas_width
                sang_height = 18

                sang_x = ((elapsed - page_start) / page_duration) * canvas_width - sang_width / 2
                sang_y = canvas_height - ((self.latest_pitch - pitch_min) / (pitch_max - pitch_min)) * canvas_height

                # Determine color by accuracy
                closest_diff = 500
                scored = False
                for seg_start, seg_end, pitch in self.pitch_segments:
                    if seg_start <= elapsed <= seg_end:
                        diff = abs(self.latest_pitch - pitch)
                        if diff < closest_diff:
                            closest_diff = diff
                        scored = True
            
                if scored:
                    #self.total_hits +=1
                    if closest_diff <= 10:
                        self.green_hits +=1
                        color = "green"
                    elif closest_diff <= 30:
                        self.yellow_hits +=1
                        color = "yellow"
                    else:
                        self.red_hits +=1
                        color = "red"
                

                #Calculate score
                score_value = self.green_hits * 20 + self.yellow_hits * 10 + self.red_hits * 2
                #max_possible_score = len(self.pitch_segments) * 20
                #percentage = (score_value / max_possible_score) * 100 if max_possible_score else 0  

                self.score_label.config(text=f"Score: {score_value}")

                # Draw the sang box
                if scored:
                    box = self.canvas.create_rectangle(
                        sang_x, sang_y - sang_height / 2,
                        sang_x + sang_width, sang_y + sang_height / 2,
                        fill=color, outline="",tags="sang"
                    )
                    sang_boxes.append(box)

            else:
                pass

            # PARSER LINE
            playhead_x = ((elapsed - page_start) / page_duration) * canvas_width
            self.canvas.delete("playhead")
            self.canvas.create_line(playhead_x , 0 , playhead_x , canvas_height, fill="lightblue", width=2, tags="playhead")

            time.sleep(0.016)



    @staticmethod
    def parse_time_to_seconds(time_str):
        minutes, seconds = time_str.split(':')
        return int(minutes) * 60 + float(seconds)

    @staticmethod
    def parse_pitch_file(file_path):
        segments = []
        with open(file_path, 'r') as f:
            for line in f:
                match = re.match(r"\[(.*?),(.*?)\] ([\d.]+)Hz", line.strip())
                if match:
                    start_str, end_str, pitch_str = match.groups()
                    start = KaraokeFrame.parse_time_to_seconds(start_str)
                    end = KaraokeFrame.parse_time_to_seconds(end_str)
                    pitch = float(pitch_str)
                    segments.append((start, end, pitch))
        return segments
        
    def listen_to_mic(self):   
        FORMAT = pyaudio.paInt16  # 16-bit audio
        CHANNELS = 1  # Mono audio
        RATE = 44100  # Sampling rate (CD quality)
        BUFFER_SIZE = 1024  # Frames per buffer (audio chunk size) 

        p = pyaudio.PyAudio()  

        def detect_pitch(audio_data, rate):   
            fft_spectrum = np.fft.fft(audio_data)   
            freqs = np.fft.fftfreq(len(fft_spectrum), d=1 / rate)  

            magnitude = np.abs(fft_spectrum)  

            peak_index = np.argmax(magnitude[:len(magnitude) // 2])   
            
            return abs(freqs[peak_index])  

        def callback(in_data, frame_count, time_info, status):   
            if not self.mic_running:  
                return (in_data, pyaudio.paComplete)  

            audio_data = np.frombuffer(in_data, dtype=np.int16)  
            pitch = detect_pitch(audio_data, RATE)  
            if pitch > 50:  
                adjusted_pitch = pitch / (2 ** 0.25)  # Lowered by a quarter octave
                self.latest_pitch = adjusted_pitch 
            else:  
                self.latest_pitch = 0
            return (in_data, pyaudio.paContinue)  

        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,   
                        input=True, frames_per_buffer=BUFFER_SIZE,   
                        stream_callback=callback)  
        stream.start_stream()  

        while self.mic_running and stream.is_active():   
            time.sleep(0.016)  

        stream.stop_stream()  
        stream.close()  
        p.terminate()   


if __name__ == "__main__":
    app = KaraokeApp()
    app.mainloop()
