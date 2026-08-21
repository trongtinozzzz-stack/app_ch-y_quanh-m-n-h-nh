import sys
import os
import json
import base64
import random
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageEnhance
from PyQt5.QtCore import QThread, pyqtSignal

def load_api_key():
    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        return key
    
    # Try reading local config.json
    base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("gemini_api_key", "")
        except Exception:
            pass
    return ""

def get_base_dirs():
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    sprites_dir = os.path.join(app_dir, "assets", "sprites")
    os.makedirs(sprites_dir, exist_ok=True)
    return app_dir, sprites_dir

def detect_face_with_gemini(image_path, api_key=None):
    """
    Uses Gemini Vision API to detect the exact face bounding box of the girl in the photo.
    Returns normalized [ymin, xmin, ymax, xmax] in 0..1000 range or None.
    """
    if not api_key:
        api_key = load_api_key()
    if not api_key:
        print("[Gemini AI] No API Key provided.")
        return None
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                "Locate the primary face of the person in this image. "
                                "Return ONLY a JSON object with: "
                                "{\"face_box_2d\": [ymin, xmin, ymax, xmax]} "
                                "where coordinates are normalized between 0 and 1000. "
                                "Do not include markdown or formatting outside JSON."
                            )
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg" if not image_path.lower().endswith(".png") else "image/png",
                                "data": img_b64
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        }
        
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            result = response.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            data = json.loads(text)
            box = data.get("face_box_2d")
            if box and len(box) == 4:
                print(f"[Gemini AI] Face detected at box: {box}")
                return box
        else:
            print(f"[Gemini AI] API error: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        print(f"[Gemini AI] Exception during face detection: {e}")
    return None

def generate_chibi_from_face(image_path, api_key=None, output_dir=None):
    """
    Blends the user's face photo onto the cute Anya chibi body:
    - Retains Anya's hair, ahoge, cone hair accessories, dress, and hands holding cocoa.
    - Replaces the inner face with the girl's photo in a cute chibi oval mask.
    - Adds anime blush and lighting effects.
    - Generates all 8 sprite frames for Desktop Pet.
    """
    if not api_key:
        api_key = load_api_key()
    app_dir, default_sprites_dir = get_base_dirs()
    if output_dir is None:
        output_dir = default_sprites_dir

    print(f"[AIGenerator] Processing face image with Gemini AI: {image_path}")

    try:
        input_img = Image.open(image_path).convert("RGBA")
        iw, ih = input_img.size

        # 1. Detect face via Gemini API
        face_box = detect_face_with_gemini(image_path, api_key)
        
        if face_box:
            ymin, xmin, ymax, xmax = face_box
            # Convert 0..1000 to image pixels
            top = int(ymin * ih / 1000)
            left = int(xmin * iw / 1000)
            bottom = int(ymax * ih / 1000)
            right = int(xmax * iw / 1000)
            
            # Add padding around face
            fw = right - left
            fh = bottom - top
            pad_x = int(fw * 0.15)
            pad_y = int(fh * 0.15)
            
            crop_left = max(0, left - pad_x)
            crop_top = max(0, top - pad_y)
            crop_right = min(iw, right + pad_x)
            crop_bottom = min(ih, bottom + pad_y)
            
            face_crop = input_img.crop((crop_left, crop_top, crop_right, crop_bottom))
        else:
            # Fallback: Center crop
            min_dim = min(iw, ih)
            left = (iw - min_dim) // 2
            top = int(ih * 0.1) # higher top for portrait face
            if top + min_dim > ih:
                top = (ih - min_dim) // 2
            face_crop = input_img.crop((left, top, left + min_dim, top + min_dim))

        # 2. Enhance face for anime blend (slightly brighter, softer)
        face_crop = ImageEnhance.Color(face_crop).enhance(1.1)
        face_crop = ImageEnhance.Brightness(face_crop).enhance(1.05)
        face_crop = ImageEnhance.Contrast(face_crop).enhance(1.02)

        # 3. Base Anya template
        base_template_path = os.path.join(output_dir, "idle_1.png")
        if not os.path.exists(base_template_path):
            import process_anya_sprites
        
        base_template = Image.open(base_template_path).convert("RGBA")
        tw, th = base_template.size

        # Anya face region in 256x256 canvas:
        # Center ~ (128, 102), Width ~ 88, Height ~ 82
        target_face_w, target_face_h = 92, 86
        face_resized = face_crop.resize((target_face_w, target_face_h), Image.Resampling.LANCZOS)

        # Create smooth feathered oval mask for face
        face_mask = Image.new("L", (target_face_w, target_face_h), 0)
        mask_draw = ImageDraw.Draw(face_mask)
        mask_draw.ellipse([2, 2, target_face_w - 2, target_face_h - 2], fill=255)
        face_mask = face_mask.filter(ImageFilter.GaussianBlur(radius=2.0))

        # Face canvas
        face_layer = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        face_pos_x = 128 - target_face_w // 2
        face_pos_y = 66
        face_layer.paste(face_resized, (face_pos_x, face_pos_y), face_mask)

        # Add cute rosy blush overlay on cheeks
        blush_layer = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        blush_draw = ImageDraw.Draw(blush_layer)
        blush_color = (255, 120, 150, 140)
        blush_draw.ellipse([face_pos_x + 6, face_pos_y + 44, face_pos_x + 26, face_pos_y + 60], fill=blush_color)
        blush_draw.ellipse([face_pos_x + target_face_w - 26, face_pos_y + 44, face_pos_x + target_face_w - 6, face_pos_y + 60], fill=blush_color)
        blush_layer = blush_layer.filter(ImageFilter.GaussianBlur(radius=2.5))

        # Composite:
        # Bottom: Base Anya body
        # Middle: User Face
        # Top: Anya front bangs and hair horns overlay
        composite_sprite = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        
        # 1. Base template underneath
        composite_sprite.paste(base_template, (0, 0), base_template)
        # 2. Paste new user face
        composite_sprite.paste(face_layer, (0, 0), face_layer)
        # 3. Paste cute blush
        composite_sprite.paste(blush_layer, (0, 0), blush_layer)

        # 4. Re-overlay Anya's front bangs / hair clips so the face sits naturally behind hair
        # Cut bangs from original Anya
        bangs_mask = Image.new("L", (tw, th), 0)
        b_draw = ImageDraw.Draw(bangs_mask)
        # Hair bangs polygon / curve
        b_draw.polygon([
            (60, 20), (196, 20), (205, 75), (185, 70), (170, 85), 
            (150, 72), (135, 88), (120, 72), (105, 86), (90, 70), 
            (70, 80), (52, 70)
        ], fill=255)
        bangs_mask = bangs_mask.filter(ImageFilter.GaussianBlur(radius=1.2))
        
        bangs_layer = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        bangs_layer.paste(base_template, (0, 0), bangs_mask)
        composite_sprite.paste(bangs_layer, (0, 0), bangs_layer)

        # Save idle_1
        composite_sprite.save(os.path.join(output_dir, "idle_1.png"))

        # Generate Idle 2 (subtle breathing)
        idle_2 = composite_sprite.resize((int(tw * 1.02), int(th * 0.98)), Image.Resampling.LANCZOS)
        idle_2_canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        idle_2_canvas.paste(idle_2, ((tw - idle_2.width) // 2, th - idle_2.height - 4), idle_2)
        idle_2_canvas.save(os.path.join(output_dir, "idle_2.png"))

        # Generate Walk Frames
        wl1 = composite_sprite.rotate(4, resample=Image.Resampling.BICUBIC, translate=(0, -4))
        wl1.save(os.path.join(output_dir, "walk_l1.png"))
        
        wl2 = composite_sprite.rotate(-4, resample=Image.Resampling.BICUBIC, translate=(0, -2))
        wl2.save(os.path.join(output_dir, "walk_l2.png"))

        wr1 = ImageOps.mirror(wl1)
        wr1.save(os.path.join(output_dir, "walk_r1.png"))
        
        wr2 = ImageOps.mirror(wl2)
        wr2.save(os.path.join(output_dir, "walk_r2.png"))

        # Dragged
        drag = composite_sprite.resize((int(tw * 0.94), int(th * 1.06)), Image.Resampling.LANCZOS)
        drag_canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        drag_canvas.paste(drag, ((tw - drag.width) // 2, (th - drag.height) // 2), drag)
        drag_canvas.save(os.path.join(output_dir, "dragged.png"))

        # Clicked
        clicked = composite_sprite.resize((int(tw * 1.08), int(th * 1.08)), Image.Resampling.LANCZOS)
        clicked_canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        clicked_canvas.paste(clicked, ((tw - clicked.width) // 2, th - clicked.height - 10), clicked)
        clicked_canvas.save(os.path.join(output_dir, "clicked.png"))

        print(f"[AIGenerator] Successfully generated all sprites with custom face!")
        return True, "Thành công"

    except Exception as e:
        print(f"[AIGenerator] Error generating chibi: {e}")
        return False, str(e)


class AIGeneratorThread(QThread):
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, image_path, api_key=None, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.api_key = api_key or load_api_key()

    def run(self):
        success, result = generate_chibi_from_face(self.image_path, self.api_key)
        self.finished_signal.emit(success, result)
