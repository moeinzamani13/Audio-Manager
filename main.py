import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import pygame
from pygame import mixer
import threading
import time

class AudioPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Player")
        self.root.geometry("600x400")
        self.root.resizable(True, True)  # Allow the window to be resizable

        mixer.init()

        self.playlist = []
        self.audio_controls = []
        self.playing_sounds = {}
        self.looping_sounds = {}
        self.stop_event = threading.Event()

        self.create_widgets()

        # Bind the close event to the stop_all_sounds method
        self.root.protocol("WM_DELETE_WINDOW", self.stop_all_sounds)

    def create_widgets(self):
        self.load_button = tk.Button(self.root, text="Load", command=self.load_files, bg="lightblue", font=("Arial", 12, "bold"))
        self.load_button.pack(pady=10)

        self.track_frame = tk.Frame(self.root, bg="lightgrey")
        self.track_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def load_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav")])
        for file in files:
            self.playlist.append(file)
            self.add_audio_controls(file)

    def add_audio_controls(self, file):
        frame = tk.Frame(self.track_frame, bg="white", bd=2, relief=tk.RIDGE)
        frame.pack(fill=tk.X, pady=5)

        truncated_file = file.split("/")[-1]
        if len(truncated_file) > 20:
            truncated_file = truncated_file[:17] + "..."

        label = tk.Label(frame, text=truncated_file, bg="white", font=("Arial", 10))
        label.pack(side=tk.LEFT, padx=5)

        sound = mixer.Sound(file)
        self.playing_sounds[file] = False
        self.looping_sounds[file] = False

        loop_button = tk.Button(frame, text="Loop Off", bg="red", font=("Arial", 10))
        loop_button.config(command=lambda f=file, b=loop_button: self.toggle_loop(f, b))
        loop_button.pack(side=tk.LEFT, padx=5)

        toggle_button = tk.Button(frame, text="Play", bg="lightgreen", font=("Arial", 10))
        toggle_button.config(command=lambda f=file, s=sound, b=toggle_button, lb=loop_button: self.toggle_audio(f, s, b, lb))
        toggle_button.pack(side=tk.LEFT, padx=5)

        volume_slider = tk.Scale(frame, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL, label="Volume", command=lambda v, s=sound: s.set_volume(float(v)), bg="white")
        volume_slider.set(0.5)
        volume_slider.pack(side=tk.LEFT, padx=5)

        progress = ttk.Progressbar(frame, orient="horizontal", length=200, mode="determinate")
        progress.pack(side=tk.LEFT, padx=10)

        duration_label = tk.Label(frame, text="00:00", bg="white", font=("Arial", 10))
        duration_label.pack(side=tk.LEFT, padx=5)

        self.audio_controls.append((file, toggle_button, loop_button, volume_slider, progress, duration_label))

    def toggle_audio(self, file, sound, button, loop_button):
        if not self.playing_sounds[file]:
            loops = -1 if self.looping_sounds[file] else 0
            sound.play(loops=loops)
            self.playing_sounds[file] = True
            button.config(text="Stop", bg="red")
            loop_button.config(state=tk.DISABLED)  # Disable the loop button
            self.update_progress(file, sound)
        else:
            sound.stop()
            self.playing_sounds[file] = False
            button.config(text="Play", bg="lightgreen")
            loop_button.config(state=tk.NORMAL)  # Enable the loop button
            self.stop_event.set()

    def toggle_loop(self, file, button):
        self.looping_sounds[file] = not self.looping_sounds[file]
        button.config(text="Loop On" if self.looping_sounds[file] else "Loop Off", bg="lightgreen" if self.looping_sounds[file] else "red")

    def update_progress(self, file, sound):
        def progress():
            self.stop_event.clear()
            while self.playing_sounds[file] and not self.stop_event.is_set():
                length = sound.get_length()
                start_time = time.perf_counter()
                while self.playing_sounds[file] and (time.perf_counter() - start_time) < length:
                    elapsed_time = time.perf_counter() - start_time
                    for control in self.audio_controls:
                        if control[0] == file:
                            control[4]["maximum"] = length
                            control[4]["value"] = elapsed_time
                            control[5].config(text=time.strftime("%M:%S", time.gmtime(elapsed_time)))
                    self.root.update_idletasks()
                    time.sleep(0.05)
                if self.playing_sounds[file]:
                    for control in self.audio_controls:
                        if control[0] == file:
                            control[4]["value"] = 0
                            control[5].config(text="00:00")
                            if not self.looping_sounds[file]:
                                control[1].config(text="Play", bg="lightgreen")
                                control[2].config(state=tk.NORMAL)  # Enable the loop button
                                self.playing_sounds[file] = False

        threading.Thread(target=progress).start()

    def stop_all_sounds(self):
        for file in self.playing_sounds:
            if self.playing_sounds[file]:
                mixer.Sound(file).stop()
        mixer.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioPlayer(root)
    root.mainloop()
