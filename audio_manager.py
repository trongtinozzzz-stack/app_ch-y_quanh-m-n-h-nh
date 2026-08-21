import sys
import os
import random
import pygame

class AudioManager:
    def __init__(self, sounds_dir=None):
        self.sound_enabled = True
        self.sounds = []
        
        if sounds_dir is None:
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                base_dir = getattr(sys, '_MEIPASS')
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            sounds_dir = os.path.join(base_dir, "assets", "sounds")
            
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
            
        for file in os.listdir(self.sounds_dir):
            if file.endswith((".wav", ".mp3", ".ogg")):
                file_path = os.path.join(self.sounds_dir, file)
                try:
                    sound = pygame.mixer.Sound(file_path)
                    self.sounds.append(sound)
                except Exception as e:
                    print(f"[AudioManager] Could not load audio {file}: {e}")

    def play_random_sound(self):
        if not self.sound_enabled or not self.sounds:
            return
        try:
            sound = random.choice(self.sounds)
            sound.play()
        except Exception as e:
            print(f"[AudioManager] Error playing sound: {e}")

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        return self.sound_enabled
