import os
import math
import struct
import wave

SOUNDS_DIR = r"d:\app_chạy_quanh màn hình\assets\sounds"
os.makedirs(SOUNDS_DIR, exist_ok=True)

SAMPLE_RATE = 44100

def write_wav(filename, samples):
    filepath = os.path.join(SOUNDS_DIR, filename)
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        packed = b''.join(struct.pack('<h', max(-32767, min(32767, int(s * 32767)))) for s in samples)
        wav_file.writeframes(packed)
    print(f"Generated sound: {filename}")

# 1. Pop Bubble (Cute deep bubble pop)
def gen_pop_bubble():
    duration = 0.15
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        p = i / n
        freq = 300 + 700 * math.exp(-p * 12)
        env = (1 - p) ** 1.5
        s = math.sin(2 * math.pi * freq * t) * env * 0.7
        samples.append(s)
    write_wav("pop_bubble.wav", samples)

# 2. Cute Poyo (Upward cute bounce chirp)
def gen_cute_poyo():
    duration = 0.22
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        p = i / n
        freq = 520 + 900 * (p ** 1.8)
        env = math.sin(math.pi * (p ** 0.6))
        s = math.sin(2 * math.pi * freq * t) * env * 0.6
        samples.append(s)
    write_wav("cute_poyo.wav", samples)

# 3. Magic Sparkle (Twinkling dual-tone chime)
def gen_sparkle():
    duration = 0.28
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        p = i / n
        env = math.exp(-p * 6)
        s1 = math.sin(2 * math.pi * 1320 * t) # E6
        s2 = math.sin(2 * math.pi * 1760 * t) # A6
        s3 = math.sin(2 * math.pi * 2640 * t) # E7
        s = (s1 * 0.4 + s2 * 0.3 + s3 * 0.2) * env * 0.7
        samples.append(s)
    write_wav("magic_sparkle.wav", samples)

# 4. Soft Meow / Nya (Cute anime kitty mew)
def gen_soft_meow():
    duration = 0.32
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        p = i / n
        # pitch rises then falls
        freq = 700 + 400 * math.sin(math.pi * p)
        env = math.sin(math.pi * p) ** 0.8
        # harmonics
        s = (math.sin(2 * math.pi * freq * t) * 0.6 + 0.3 * math.sin(4 * math.pi * freq * t)) * env * 0.6
        samples.append(s)
    write_wav("soft_meow.wav", samples)

# 5. Boing Jump (Bouncy spring effect)
def gen_boing_jump():
    duration = 0.25
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        p = i / n
        mod = math.sin(2 * math.pi * 35 * t)
        freq = 400 + 500 * p + 80 * mod
        env = (1 - p) ** 0.7
        s = math.sin(2 * math.pi * freq * t) * env * 0.6
        samples.append(s)
    write_wav("boing_jump.wav", samples)

# 6. Squeak Toy (High cute squeeze)
def gen_squeak():
    duration = 0.18
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        p = i / n
        freq = 1100 + 800 * math.exp(-p * 8)
        env = math.sin(math.pi * p)
        s = (math.sin(2 * math.pi * freq * t) + 0.2 * math.sin(4 * math.pi * freq * t)) * env * 0.5
        samples.append(s)
    write_wav("cute_squeak.wav", samples)

# 7. Drop Bell (Tiny crystal bell)
def gen_drop_bell():
    duration = 0.30
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        p = i / n
        env = math.exp(-p * 8)
        s = (math.sin(2 * math.pi * 1046.5 * t) * 0.5 + math.sin(2 * math.pi * 2093 * t) * 0.3) * env * 0.7
        samples.append(s)
    write_wav("drop_bell.wav", samples)

# 8. Happy Jingle (2-note ascending cute chime C-G)
def gen_happy_jingle():
    duration = 0.30
    n = int(SAMPLE_RATE * duration)
    half = n // 2
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        if i < half:
            p = i / half
            freq = 880 # A5
            env = math.exp(-p * 5)
        else:
            p = (i - half) / (n - half)
            freq = 1320 # E6
            env = math.exp(-p * 4)
        s = math.sin(2 * math.pi * freq * t) * env * 0.6
        samples.append(s)
    write_wav("happy_jingle.wav", samples)

# 9. Waku Waku Sparkle (Glissando fast sweep)
def gen_waku_waku():
    duration = 0.24
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        p = i / n
        freq = 600 + 1200 * (p ** 2)
        env = math.sin(math.pi * p) ** 0.5
        s = (math.sin(2 * math.pi * freq * t) * 0.7 + 0.2 * math.sin(6 * math.pi * freq * t)) * env * 0.6
        samples.append(s)
    write_wav("waku_waku.wav", samples)

# 10. Cute Chirp (Tiny bird-like chirp)
def gen_cute_chirp():
    duration = 0.16
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        p = i / n
        freq = 1400 + 600 * math.sin(math.pi * p * 2)
        env = (1 - p) ** 1.2
        s = math.sin(2 * math.pi * freq * t) * env * 0.6
        samples.append(s)
    write_wav("cute_chirp.wav", samples)

def main():
    gen_pop_bubble()
    gen_cute_poyo()
    gen_sparkle()
    gen_soft_meow()
    gen_boing_jump()
    gen_squeak()
    gen_drop_bell()
    gen_happy_jingle()
    gen_waku_waku()
    gen_cute_chirp()
    print("10 cute sound effects generated successfully!")

if __name__ == "__main__":
    main()
