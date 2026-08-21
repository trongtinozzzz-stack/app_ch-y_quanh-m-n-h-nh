import sys
import os
import json
import base64
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageEnhance
from PyQt5.QtCore import QThread, pyqtSignal

def load_api_key():
    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        return key
    
    # Check config.json next to executable or script
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

def analyze_girl_photo_with_gemini(image_path, api_key=None):
    """
    Sends the girl's photo to Gemini 2.5 Flash to extract:
    - Precise face bounding box
    - Eye color & Eye style
    - Skin tone RGB
    - Expression (smile, cute, happy)
    """
    if not api_key:
        api_key = load_api_key()
    if not api_key:
        print("[Gemini AI] Warning: No API Key provided.")
        return None

    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")

        prompt = (
            "You are an anime character artist. Analyze this photo of a person/girl to create an Anya Forger chibi face. "
            "Return ONLY a JSON object with: "
            "\"face_box_2d\": [ymin, xmin, ymax, xmax] (normalized 0 to 1000), "
            "\"skin_tone_rgb\": [r, g, b] (fair soft anime skin tone like [255, 235, 225]), "
            "\"eye_color_rgb\": [r, g, b] (matching her eye color or warm hazel/brown/green/blue like [45, 120, 80]), "
            "\"expression\": \"happy\" | \"smile\" | \"gentle\", "
            "\"lip_color_rgb\": [r, g, b] (soft pink or coral lip tone)"
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
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
                "temperature": 0.2,
                "response_mime_type": "application/json"
            }
        }
        
        response = requests.post(url, json=payload, timeout=20)
        if response.status_code == 200:
            result = response.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            data = json.loads(text)
            print(f"[Gemini AI] Analysis result: {data}")
            return data
        else:
            print(f"[Gemini AI] API error: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        print(f"[Gemini AI] Exception during analysis: {e}")
    return None

def generate_anime_chibi_face(crop_face, ai_data, canvas_size=(100, 92)):
    """
    Renders an authentic Anya-style Anime Chibi Face customized from the girl's photo and AI analysis:
    - Smooth anime porcelain skin with cel-shaded tone
    - Custom anime sparkling eyes (based on her eye color) with highlights
    - Rosy anime blush
    - Cute anime mouth & eyelashes
    - Soft integration of real facial features
    """
    cw, ch = canvas_size
    face_img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    draw = ImageDraw.Draw(face_img)

    # 1. Colors from Gemini or defaults
    skin = ai_data.get("skin_tone_rgb", [255, 230, 220]) if ai_data else [255, 230, 220]
    skin_color = (max(220, skin[0]), max(200, skin[1]), max(195, skin[2]), 255)
    
    eye_col = ai_data.get("eye_color_rgb", [45, 140, 85]) if ai_data else [45, 140, 85]
    eye_color = (eye_col[0], eye_col[1], eye_col[2], 255)
    eye_dark = (max(0, eye_col[0]-30), max(0, eye_col[1]-30), max(0, eye_col[2]-30), 255)
    
    line_color = (60, 45, 55, 255) # soft anime lineart

    # 2. Draw soft Chibi head oval
    draw.ellipse([4, 4, cw - 4, ch - 4], fill=skin_color)

    # 3. Blend filtered real face features (for likeness: nose/mouth/skin texture)
    if crop_face:
        # Soften & filter
        cf = crop_face.resize((cw - 12, ch - 12), Image.Resampling.LANCZOS)
        cf = ImageEnhance.Color(cf).enhance(0.9)
        cf = ImageEnhance.Brightness(cf).enhance(1.15)
        cf = ImageEnhance.Contrast(cf).enhance(0.95)
        
        # Feathered inner mask
        blend_mask = Image.new("L", (cw - 12, ch - 12), 0)
        b_draw = ImageDraw.Draw(blend_mask)
        b_draw.ellipse([6, 6, cw - 18, ch - 18], fill=110) # semi-transparent blend
        blend_mask = blend_mask.filter(ImageFilter.GaussianBlur(radius=3.0))
        
        face_img.paste(cf, (6, 6), blend_mask)

    # 4. Draw large sparkling Anime Chibi Eyes
    # Left Eye
    lx1, ly1, lx2, ly2 = 18, 28, 40, 56
    draw.ellipse([lx1, ly1, lx2, ly2], fill=(255, 255, 255, 255), outline=line_color, width=2)
    draw.ellipse([lx1+2, ly1+3, lx2-2, ly2-1], fill=eye_color)
    draw.ellipse([lx1+3, ly1+4, lx2-3, ly1+14], fill=eye_dark)
    # Highlights (Catchlights)
    draw.ellipse([lx1+4, ly1+5, lx1+10, ly1+11], fill=(255, 255, 255, 255))
    draw.ellipse([lx1+11, ly1+13, lx1+14, ly1+16], fill=(255, 255, 255, 220))
    # Eyelashes
    draw.arc([lx1-2, ly1-4, lx2+3, ly1+16], start=190, end=350, fill=line_color, width=3)
    draw.line([(lx2+1, ly1+2), (lx2+5, ly1-1)], fill=line_color, width=2)

    # Right Eye
    rx1, ry1, rx2, ry2 = cw - 40, 28, cw - 18, 56
    draw.ellipse([rx1, ry1, rx2, ry2], fill=(255, 255, 255, 255), outline=line_color, width=2)
    draw.ellipse([rx1+2, ry1+3, rx2-2, ry2-1], fill=eye_color)
    draw.ellipse([rx1+3, ry1+4, rx2-3, ry1+14], fill=eye_dark)
    # Highlights
    draw.ellipse([rx1+4, ry1+5, rx1+10, ry1+11], fill=(255, 255, 255, 255))
    draw.ellipse([rx1+11, ry1+13, rx1+14, ry1+16], fill=(255, 255, 255, 220))
    # Eyelashes
    draw.arc([rx1-3, ry1-4, rx2+2, ry1+16], start=190, end=350, fill=line_color, width=3)
    draw.line([(rx2+1, ry1+2), (rx2+5, ry1-1)], fill=line_color, width=2)

    # 5. Eyebrows (Cute soft arch)
    draw.arc([lx1+1, ly1-10, lx2+1, ly1], start=210, end=330, fill=line_color, width=2)
    draw.arc([rx1-1, ry1-10, rx2-1, ry1], start=210, end=330, fill=line_color, width=2)

    # 6. Anime Nose Dot
    draw.ellipse([cw // 2 - 1, 52, cw // 2 + 1, 54], fill=line_color)

    # 7. Cute Anime Smile Mouth
    lip = ai_data.get("lip_color_rgb", [255, 110, 120]) if ai_data else [255, 110, 120]
    lip_color = (lip[0], lip[1], lip[2], 255)
    mx = cw // 2
    my = 62
    draw.chord([mx - 7, my, mx + 7, my + 9], start=0, end=180, fill=lip_color, outline=line_color, width=2)
    # tiny tooth highlight
    draw.chord([mx - 4, my, mx + 4, my + 3], start=0, end=180, fill=(255, 255, 255, 255))

    # 8. Rosy Anime Cheek Blush
    blush_img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    b_draw2 = ImageDraw.Draw(blush_img)
    b_color = (255, 120, 150, 150)
    b_draw2.ellipse([lx1 - 4, ly1 + 18, lx1 + 16, ly1 + 30], fill=b_color)
    b_draw2.ellipse([rx2 - 16, ry1 + 18, rx2 + 4, ry1 + 30], fill=b_color)
    blush_img = blush_img.filter(ImageFilter.GaussianBlur(radius=2.0))
    face_img.paste(blush_img, (0, 0), blush_img)

    return face_img

def generate_chibi_from_face(image_path, api_key=None, output_dir=None):
    """
    Main function called when user selects a photo:
    1. Analyzes with Gemini AI.
    2. Generates stylized Anime Chibi Face.
    3. Blends with Anya body & pink hair bangs/accessories.
    4. Saves all 8 animated sprites.
    """
    if not api_key:
        api_key = load_api_key()
    
    app_dir, default_sprites_dir = get_base_dirs()
    if output_dir is None:
        output_dir = default_sprites_dir

    print(f"[AIGenerator] Processing girl photo with Gemini AI: {image_path}")

    try:
        input_img = Image.open(image_path).convert("RGBA")
        iw, ih = input_img.size

        # 1. Gemini AI Analysis
        ai_data = analyze_girl_photo_with_gemini(image_path, api_key)
        
        # 2. Crop face based on Gemini coordinates or smart center fallback
        if ai_data and "face_box_2d" in ai_data:
            box = ai_data["face_box_2d"]
            ymin, xmin, ymax, xmax = box
            top = max(0, int(ymin * ih / 1000))
            left = max(0, int(xmin * iw / 1000))
            bottom = min(ih, int(ymax * ih / 1000))
            right = min(iw, int(xmax * iw / 1000))
            
            # Padding
            pad_x = int((right - left) * 0.12)
            pad_y = int((bottom - top) * 0.12)
            crop_left = max(0, left - pad_x)
            crop_top = max(0, top - pad_y)
            crop_right = min(iw, right + pad_x)
            crop_bottom = min(ih, bottom + pad_y)
            face_crop = input_img.crop((crop_left, crop_top, crop_right, crop_bottom))
        else:
            min_dim = min(iw, ih)
            left = (iw - min_dim) // 2
            top = max(0, int(ih * 0.08))
            if top + min_dim > ih:
                top = (ih - min_dim) // 2
            face_crop = input_img.crop((left, top, left + min_dim, top + min_dim))

        # 3. Generate Anime Chibi Face
        custom_face = generate_anime_chibi_face(face_crop, ai_data, canvas_size=(96, 88))

        # 4. Load Anya Base Template
        base_template_path = os.path.join(output_dir, "idle_1.png")
        if not os.path.exists(base_template_path):
            import process_anya_sprites
        
        base_template = Image.open(base_template_path).convert("RGBA")
        tw, th = base_template.size # 256x256

        # Smooth oval feather mask for face placement
        face_layer = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        face_x = (tw - custom_face.width) // 2
        face_y = 66
        
        face_mask = Image.new("L", custom_face.size, 0)
        fm_draw = ImageDraw.Draw(face_mask)
        fm_draw.ellipse([2, 2, custom_face.width - 2, custom_face.height - 2], fill=255)
        face_mask = face_mask.filter(ImageFilter.GaussianBlur(radius=2.0))
        
        face_layer.paste(custom_face, (face_x, face_y), face_mask)

        # Composite layers:
        # 1. Base Anya Body
        # 2. Custom Face
        # 3. Anya Front Hair Bangs & Ahoge & Horns
        composite = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        composite.paste(base_template, (0, 0), base_template)
        composite.paste(face_layer, (0, 0), face_layer)

        # Re-apply front bangs from base Anya
        bangs_mask = Image.new("L", (tw, th), 0)
        b_draw = ImageDraw.Draw(bangs_mask)
        b_draw.polygon([
            (60, 20), (196, 20), (205, 75), (185, 70), (170, 85), 
            (150, 72), (135, 88), (120, 72), (105, 86), (90, 70), 
            (70, 80), (52, 70)
        ], fill=255)
        bangs_mask = bangs_mask.filter(ImageFilter.GaussianBlur(radius=1.2))
        
        bangs_layer = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        bangs_layer.paste(base_template, (0, 0), bangs_mask)
        composite.paste(bangs_layer, (0, 0), bangs_layer)

        # 5. Generate & Save all 8 frames
        # Idle 1
        composite.save(os.path.join(output_dir, "idle_1.png"))

        # Idle 2 (subtle breathing)
        idle_2 = composite.resize((int(tw * 1.02), int(th * 0.98)), Image.Resampling.LANCZOS)
        idle_2_canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        idle_2_canvas.paste(idle_2, ((tw - idle_2.width) // 2, th - idle_2.height - 4), idle_2)
        idle_2_canvas.save(os.path.join(output_dir, "idle_2.png"))

        # Walk frames
        wl1 = composite.rotate(4, resample=Image.Resampling.BICUBIC, translate=(0, -4))
        wl1.save(os.path.join(output_dir, "walk_l1.png"))
        
        wl2 = composite.rotate(-4, resample=Image.Resampling.BICUBIC, translate=(0, -2))
        wl2.save(os.path.join(output_dir, "walk_l2.png"))

        wr1 = ImageOps.mirror(wl1)
        wr1.save(os.path.join(output_dir, "walk_r1.png"))
        
        wr2 = ImageOps.mirror(wl2)
        wr2.save(os.path.join(output_dir, "walk_r2.png"))

        # Dragged
        drag = composite.resize((int(tw * 0.94), int(th * 1.06)), Image.Resampling.LANCZOS)
        drag_canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        drag_canvas.paste(drag, ((tw - drag.width) // 2, (th - drag.height) // 2), drag)
        drag_canvas.save(os.path.join(output_dir, "dragged.png"))

        # Clicked
        clicked = composite.resize((int(tw * 1.08), int(th * 1.08)), Image.Resampling.LANCZOS)
        clicked_canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        clicked_canvas.paste(clicked, ((tw - clicked.width) // 2, th - clicked.height - 10), clicked)
        clicked_canvas.save(os.path.join(output_dir, "clicked.png"))

        print(f"[AIGenerator] All 8 chibi animation frames generated successfully!")
        return True, "Thành công"

    except Exception as e:
        print(f"[AIGenerator] Error: {e}")
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
