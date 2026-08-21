import os
import math
import struct
import wave
from PIL import Image, ImageDraw

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

os.makedirs(SPRITES_DIR, exist_ok=True)
os.makedirs(SOUNDS_DIR, exist_ok=True)

def create_chibi_sprite(filename, expression="happy", pose="idle", eye_blink=False, leg_pos=0):
    size = (128, 128)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Colors
    body_color = (255, 183, 178, 255)     # Cute soft pink body
    inner_ear = (255, 105, 180, 255)     # Hot pink inner ear
    eye_color = (40, 40, 60, 255)        # Dark cute eyes
    cheek_color = (255, 120, 150, 180)   # Blush pink cheeks
    outline_color = (70, 50, 60, 255)    # Soft dark outline

    # Shadow/Glow under mascot
    draw.ellipse([24, 110, 104, 124], fill=(0, 0, 0, 40))

    # Legs animation
    leg_offset_l = 0
    leg_offset_r = 0
    if pose == "walk_left":
        leg_offset_l = -4 if leg_pos == 0 else 4
        leg_offset_r = 4 if leg_pos == 0 else -4
    elif pose == "walk_right":
        leg_offset_l = 4 if leg_pos == 0 else -4
        leg_offset_r = -4 if leg_pos == 0 else 4
    elif pose == "dragged":
        leg_offset_l = -6
        leg_offset_r = -6

    # Draw Feet (Cute paws)
    draw.ellipse([34 + leg_offset_l, 98, 54 + leg_offset_l, 116], fill=body_color, outline=outline_color, width=3)
    draw.ellipse([74 + leg_offset_r, 98, 94 + leg_offset_r, 116], fill=body_color, outline=outline_color, width=3)

    # Draw Body / Head (Chibi style: big head, round body)
    head_bbox = [20, 18, 108, 102]
    if pose == "dragged":
        head_bbox = [24, 12, 104, 104] # stretched vertically

    # Ears
    # Left Ear
    draw.polygon([(26, 30), (12, 4), (46, 20)], fill=body_color, outline=outline_color)
    draw.polygon([(28, 28), (18, 10), (44, 22)], fill=inner_ear)
    # Right Ear
    draw.polygon([(82, 20), (116, 4), (102, 30)], fill=body_color, outline=outline_color)
    draw.polygon([(84, 22), (110, 10), (100, 28)], fill=inner_ear)

    # Main Head/Face circle
    draw.ellipse(head_bbox, fill=body_color, outline=outline_color, width=3)

    # Cheeks (Blush)
    draw.ellipse([28, 64, 44, 76], fill=cheek_color)
    draw.ellipse([84, 64, 100, 76], fill=cheek_color)

    # Eyes
    if eye_blink or expression == "surprised_blink":
        # Closed eyes ^ ^
        draw.arc([36, 48, 52, 64], start=200, end=340, fill=eye_color, width=4)
        draw.arc([76, 48, 92, 64], start=200, end=340, fill=eye_color, width=4)
    elif expression == "surprised" or pose == "dragged":
        # Big wide eyes O O
        draw.ellipse([34, 44, 54, 66], fill=eye_color)
        draw.ellipse([74, 44, 94, 66], fill=eye_color)
        # Pupil Highlights
        draw.ellipse([38, 46, 46, 54], fill=(255, 255, 255, 255))
        draw.ellipse([78, 46, 86, 54], fill=(255, 255, 255, 255))
    elif expression == "clicked":
        # Happy star / squint eyes > <
        draw.line([(36, 48), (50, 58)], fill=eye_color, width=4)
        draw.line([(36, 58), (50, 48)], fill=eye_color, width=4)
        draw.line([(78, 48), (92, 58)], fill=eye_color, width=4)
        draw.line([(78, 58), (92, 48)], fill=eye_color, width=4)
    else:
        # Normal cute eyes
        draw.ellipse([36, 46, 52, 66], fill=eye_color)
        draw.ellipse([76, 46, 92, 66], fill=eye_color)
        # Catchlights
        draw.ellipse([40, 48, 47, 55], fill=(255, 255, 255, 255))
        draw.ellipse([80, 48, 87, 55], fill=(255, 255, 255, 255))
        draw.ellipse([38, 57, 42, 61], fill=(255, 255, 255, 255))
        draw.ellipse([78, 57, 82, 61], fill=(255, 255, 255, 255))

    # Mouth / Nose
    draw.ellipse([62, 58, 66, 62], fill=outline_color) # nose
    if expression == "clicked":
        # Open mouth :D
        draw.chord([56, 62, 72, 76], start=0, end=180, fill=(255, 100, 100, 255), outline=outline_color, width=2)
    elif expression == "surprised" or pose == "dragged":
        # O mouth
        draw.ellipse([58, 65, 70, 77], fill=(255, 100, 100, 255), outline=outline_color, width=2)
    else:
        # Cute :3 mouth
        draw.arc([54, 62, 64, 70], start=0, end=160, fill=outline_color, width=3)
        draw.arc([64, 62, 74, 70], start=20, end=180, fill=outline_color, width=3)

    img.save(os.path.join(SPRITES_DIR, filename))
    print(f"Generated sprite: {filename}")

def generate_wav_sound(filename, duration=0.25, freq_start=600, freq_end=1200):
    filepath = os.path.join(SOUNDS_DIR, filename)
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1) # mono
        wav_file.setsampwidth(2) # 16-bit
        wav_file.setframerate(sample_rate)
        
        for i in range(n_samples):
            t = i / float(sample_rate)
            progress = i / float(n_samples)
            # Frequency glide / chirp
            current_freq = freq_start + (freq_end - freq_start) * (progress ** 0.5)
            # Amplitude envelope (fade out)
            env = math.sin(math.pi * progress)
            val = math.sin(2.0 * math.pi * current_freq * t) * env * 0.5
            sample = int(val * 32767)
            wav_file.writeframes(struct.pack('<h', sample))
    print(f"Generated sound: {filename}")

def main():
    import process_anya_sprites
    import generate_sounds
    generate_sounds.main()
    print("All Anya mascot sprites and 10 cute sound effects generated successfully!")

if __name__ == "__main__":
    main()


