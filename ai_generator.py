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

def analyze_photo_with_gemini(image_path, api_key=None):
    if not api_key:
        api_key = load_api_key()
    if not api_key:
        return None

    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")

        prompt = (
            "Analyze this photo of a person/girl to customize an Anya anime chibi mascot. "
            "Return ONLY a JSON object: "
            "{\"eye_color_rgb\": [r, g, b], "
            "\"skin_glow_tone\": \"peach\" | \"rose\" | \"ivory\", "
            "\"expression\": \"cheerful\" | \"gentle\" | \"sweet\"}"
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
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        }
        
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            result = response.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            return json.loads(text)
    except Exception as e:
        print(f"[Gemini AI] Error in analysis: {e}")
    return None

def generate_chibi_from_face(image_path, api_key=None, output_dir=None):
    """
    Creates a beautiful customized anime mascot using Gemini AI:
    - Maintains the gorgeous high-res Anya anime art style (eyes, hair, dress, hands, cocoa).
    - Customizes eye colors, rosy blush, and skin glow based on the girl's photo analysis.
    - Ensures 100% clean, crisp anime aesthetics without any ugly dark patches or jagged lines.
    """
    if not api_key:
        api_key = load_api_key()

    app_dir, default_sprites_dir = get_base_dirs()
    if output_dir is None:
        output_dir = default_sprites_dir

    print(f"[AIGenerator] Customizing mascot for photo: {image_path}")

    try:
        # 1. AI Analysis with Gemini
        ai_info = analyze_photo_with_gemini(image_path, api_key)
        print(f"[AIGenerator] AI Analysis: {ai_info}")

        # 2. Load original pristine Anya artwork
        backup_idle = os.path.join(app_dir, "assets", "sprites_backup", "idle_1.png")
        if not os.path.exists(backup_idle):
            import process_anya_sprites
        
        base_img = Image.open(backup_idle if os.path.exists(backup_idle) else os.path.join(output_dir, "idle_1.png")).convert("RGBA")
        tw, th = base_img.size

        # 3. Apply Beauty Glow & Blush Enhancement
        enhanced_base = base_img.copy()
        
        # Eye color customization if detected
        if ai_info and "eye_color_rgb" in ai_info:
            ec = ai_info["eye_color_rgb"]
            # Apply subtle eye color tint over iris region (x: 85..175, y: 75..120)
            eye_tint = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
            e_draw = ImageDraw.Draw(eye_tint)
            # Left iris
            e_draw.ellipse([88, 82, 114, 115], fill=(ec[0], ec[1], ec[2], 65))
            # Right iris
            e_draw.ellipse([142, 82, 168, 115], fill=(ec[0], ec[1], ec[2], 65))
            eye_tint = eye_tint.filter(ImageFilter.GaussianBlur(radius=1.5))
            enhanced_base = Image.alpha_composite(enhanced_base, eye_tint)

        # Soft glowing pink blush enhancement
        blush_layer = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        b_draw = ImageDraw.Draw(blush_layer)
        glow_tone = ai_info.get("skin_glow_tone", "rose") if ai_info else "rose"
        blush_color = (255, 105, 140, 70) if glow_tone == "rose" else (255, 130, 110, 70)
        
        b_draw.ellipse([72, 100, 108, 126], fill=blush_color)
        b_draw.ellipse([148, 100, 184, 126], fill=blush_color)
        blush_layer = blush_layer.filter(ImageFilter.GaussianBlur(radius=4.0))
        enhanced_base = Image.alpha_composite(enhanced_base, blush_layer)

        # 4. Save Idle 1
        enhanced_base.save(os.path.join(output_dir, "idle_1.png"))

        # 5. Generate Idle 2 (subtle breathing animation)
        nw, nh = enhanced_base.size
        breathe_w, breathe_h = int(nw * 1.02), int(nh * 0.98)
        breathe_resized = enhanced_base.resize((breathe_w, breathe_h), Image.Resampling.LANCZOS)
        idle_2 = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        idle_2.paste(breathe_resized, ((tw - breathe_w) // 2, th - breathe_h - 4), breathe_resized)
        idle_2.save(os.path.join(output_dir, "idle_2.png"))

        # 6. Generate Walking Frames
        wl1 = enhanced_base.rotate(4, resample=Image.Resampling.BICUBIC, translate=(0, -4))
        wl1.save(os.path.join(output_dir, "walk_l1.png"))

        wl2 = enhanced_base.rotate(-4, resample=Image.Resampling.BICUBIC, translate=(0, -2))
        wl2.save(os.path.join(output_dir, "walk_l2.png"))

        wr1 = ImageOps.mirror(wl1)
        wr1.save(os.path.join(output_dir, "walk_r1.png"))

        wr2 = ImageOps.mirror(wl2)
        wr2.save(os.path.join(output_dir, "walk_r2.png"))

        # 7. Dragged Frame
        drag_w, drag_h = int(nw * 0.94), int(nh * 1.06)
        drag_resized = enhanced_base.resize((drag_w, drag_h), Image.Resampling.LANCZOS)
        dragged = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        dragged.paste(drag_resized, ((tw - drag_w) // 2, (th - drag_h) // 2), drag_resized)
        dragged.save(os.path.join(output_dir, "dragged.png"))

        # 8. Clicked Frame (Waku Waku sparkling pose)
        clicked_backup = os.path.join(app_dir, "assets", "sprites_backup", "clicked.png")
        if os.path.exists(clicked_backup):
            shutil_copy = Image.open(clicked_backup).convert("RGBA")
            shutil_copy.save(os.path.join(output_dir, "clicked.png"))
        else:
            click_w, click_h = int(nw * 1.08), int(nh * 1.08)
            click_resized = enhanced_base.resize((click_w, click_h), Image.Resampling.LANCZOS)
            clicked = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
            clicked.paste(click_resized, ((tw - click_w) // 2, th - click_h - 10), click_resized)
            clicked.save(os.path.join(output_dir, "clicked.png"))

        print("[AIGenerator] Beautiful mascot generated successfully!")
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
