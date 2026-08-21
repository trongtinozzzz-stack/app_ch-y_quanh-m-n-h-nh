import sys
import os
import random
import pygame

class AudioManager:
    def __init__(self, sounds_dir=None):
        self.sound_enabled = True
        self.sounds = []
        self.sound_index = 0
        self.playlist = []
        
        if sounds_dir is None:
            if getattr(sys, 'frozen', False):
                app_dir = os.path.dirname(sys.executable)
            else:
                app_dir = os.path.dirname(os.path.abspath(__file__))
            
            external_sounds = os.path.join(app_dir, "assets", "sounds")
            if os.path.exists(external_sounds):
                sounds_dir = external_sounds
            elif getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                sounds_dir = os.path.join(getattr(sys, '_MEIPASS'), "assets", "sounds")
            else:
                sounds_dir = external_sounds
            
        self.sounds_dir = sounds_dir
        self._init_mixer()
        self.load_sounds()

    def _init_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception as e:
            print(f"[AudioManager] Warning: Could not initialize pygame.mixer: {e}")

    def load_sounds(self):
        self.sounds = []
        if not os.path.exists(self.sounds_dir):
            print(f"[AudioManager] Warning: Sounds folder not found at {self.sounds_dir}")
            return
            
        for file in sorted(os.listdir(self.sounds_dir)):
            if file.endswith((".wav", ".mp3", ".ogg")):
                file_path = os.path.join(self.sounds_dir, file)
                try:
                    sound = pygame.mixer.Sound(file_path)
                    self.sounds.append(sound)
                except Exception as e:
                    print(f"[AudioManager] Could not load audio {file}: {e}")
        
        self._reshuffle_playlist()
        print(f"[AudioManager] Loaded {len(self.sounds)} sound effects.")

    def _reshuffle_playlist(self):
        if not self.sounds:
            self.playlist = []
            return
        indices = list(range(len(self.sounds)))
        random.shuffle(indices)
        self.playlist = indices
        self.sound_index = 0

    def play_random_sound(self):
        """Plays the next sound in a shuffled cycle so every click gets a different cute sound!"""
        if not self.sound_enabled or not self.sounds:
            return
        try:
            if self.sound_index >= len(self.playlist):
                self._reshuffle_playlist()
            
            current_idx = self.playlist[self.sound_index]
            self.sound_index += 1
            
            sound = self.sounds[current_idx]
            sound.play()
        except Exception as e:
            print(f"[AudioManager] Error playing sound: {e}")

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        return self.sound_enabled

