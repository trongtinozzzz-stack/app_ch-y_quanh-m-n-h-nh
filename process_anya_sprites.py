import os
import shutil
from PIL import Image, ImageOps, ImageFilter
from collections import deque

IMAGE_SOURCE = r"C:\Users\ADMIN\.gemini\antigravity-ide\brain\760e5d3e-a47e-406a-940e-8923f1983beb\cute_anime_girl_chibi_1787317383716.jpg"
SPRITES_DIR = r"d:\app_chạy_quanh màn hình\assets\sprites"
BACKUP_DIR = r"d:\app_chạy_quanh màn hình\assets\sprites_backup"

os.makedirs(SPRITES_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# 1. Backup existing sprites
for f in os.listdir(SPRITES_DIR):
    if f.endswith(".png"):
        shutil.copy2(os.path.join(SPRITES_DIR, f), os.path.join(BACKUP_DIR, f))

# 2. Load and remove white background using outer flood-fill
img = Image.open(IMAGE_SOURCE).convert("RGBA")
w, h = img.size
pixels = img.load()

# Find background color from corner
corner_colors = [pixels[0, 0], pixels[w-1, 0], pixels[0, h-1], pixels[w-1, h-1]]
bg_r = sum(c[0] for c in corner_colors) / 4.0
bg_g = sum(c[1] for c in corner_colors) / 4.0
bg_b = sum(c[2] for c in corner_colors) / 4.0

def is_bg(r, g, b, a):
    # Near pure white or matches corner
    dist = ((r - bg_r)**2 + (g - bg_g)**2 + (b - bg_b)**2)**0.5
    return dist < 35 or (r > 240 and g > 240 and b > 240)

# Flood fill BFS starting from all borders
visited = [[False]*h for _ in range(w)]
queue = deque()

for x in range(w):
    queue.append((x, 0))
    queue.append((x, h-1))
    visited[x][0] = True
    visited[x][h-1] = True

for y in range(h):
    queue.append((0, y))
    queue.append((w-1, y))
    visited[0][y] = True
    visited[w-1][y] = True

alpha_mask = Image.new("L", (w, h), 255)
alpha_pixels = alpha_mask.load()

while queue:
    cx, cy = queue.popleft()
    r, g, b, a = pixels[cx, cy]
    if is_bg(r, g, b, a):
        alpha_pixels[cx, cy] = 0
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and not visited[nx][ny]:
                visited[nx][ny] = True
                queue.append((nx, ny))

# Soften alpha edges slightly for smooth anti-aliasing
alpha_smooth = alpha_mask.filter(ImageFilter.GaussianBlur(radius=0.8))
img.putalpha(alpha_smooth)

# Crop to bounding box with padding
bbox = img.getbbox()
if bbox:
    cropped = img.crop(bbox)
else:
    cropped = img

# Fit nicely into a 256x256 square canvas for crisp display
target_canvas_size = 256
cw, ch = cropped.size
scale = min((target_canvas_size - 16) / ch, (target_canvas_size - 16) / cw)
nw, nh = int(cw * scale), int(ch * scale)
cropped_resized = cropped.resize((nw, nh), Image.Resampling.LANCZOS)

base_sprite = Image.new("RGBA", (target_canvas_size, target_canvas_size), (0, 0, 0, 0))
ox = (target_canvas_size - nw) // 2
oy = target_canvas_size - nh - 8 # place feet near bottom
base_sprite.paste(cropped_resized, (ox, oy), cropped_resized)

# Save base idle 1
base_sprite.save(os.path.join(SPRITES_DIR, "idle_1.png"))

# Create idle 2 (subtle breathing/bobbing)
idle_2 = Image.new("RGBA", (target_canvas_size, target_canvas_size), (0, 0, 0, 0))
# Stretch slightly 101% width, 99% height for breathing
breathe_w, breathe_h = int(nw * 1.02), int(nh * 0.98)
breathe_resized = cropped.resize((breathe_w, breathe_h), Image.Resampling.LANCZOS)
breathe_ox = (target_canvas_size - breathe_w) // 2
breathe_oy = target_canvas_size - breathe_h - 8
idle_2.paste(breathe_resized, (breathe_ox, breathe_oy), breathe_resized)
idle_2.save(os.path.join(SPRITES_DIR, "idle_2.png"))

# Create walk frames (waddling animation)
# Walk Left 1: tilted -4 deg, hopped 4px
wl1_rot = base_sprite.rotate(4, resample=Image.Resampling.BICUBIC, translate=(0, -4))
wl1_rot.save(os.path.join(SPRITES_DIR, "walk_l1.png"))

# Walk Left 2: tilted -4 deg, hopped 4px opposite
wl2_rot = base_sprite.rotate(-4, resample=Image.Resampling.BICUBIC, translate=(0, -2))
wl2_rot.save(os.path.join(SPRITES_DIR, "walk_l2.png"))

# Walk Right frames (flipped horizontally)
wr1 = ImageOps.mirror(wl1_rot)
wr1.save(os.path.join(SPRITES_DIR, "walk_r1.png"))

wr2 = ImageOps.mirror(wl2_rot)
wr2.save(os.path.join(SPRITES_DIR, "walk_r2.png"))

# Dragged frame: stretched vertically with floating effect
drag_w, drag_h = int(nw * 0.94), int(nh * 1.06)
drag_resized = cropped.resize((drag_w, drag_h), Image.Resampling.LANCZOS)
dragged = Image.new("RGBA", (target_canvas_size, target_canvas_size), (0, 0, 0, 0))
drag_ox = (target_canvas_size - drag_w) // 2
drag_oy = (target_canvas_size - drag_h) // 2
dragged.paste(drag_resized, (drag_ox, drag_oy), drag_resized)
dragged.save(os.path.join(SPRITES_DIR, "dragged.png"))

# Clicked frame: bounced with slight heart or joyful scale
click_w, click_h = int(nw * 1.08), int(nh * 1.08)
click_resized = cropped.resize((click_w, click_h), Image.Resampling.LANCZOS)
clicked = Image.new("RGBA", (target_canvas_size, target_canvas_size), (0, 0, 0, 0))
click_ox = (target_canvas_size - click_w) // 2
click_oy = target_canvas_size - click_h - 12
clicked.paste(click_resized, (click_ox, click_oy), click_resized)
clicked.save(os.path.join(SPRITES_DIR, "clicked.png"))

print("All sprites successfully generated and updated in assets/sprites!")
