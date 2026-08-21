import sys
import os
import requests
from PIL import Image, ImageDraw
from PyQt5.QtCore import QThread, pyqtSignal

def generate_chibi_from_face(image_path, api_key=None, output_dir=None):
    """
    Placeholder/API Wrapper function to transform a face image into Chibi Mascot sprites.
    
    If api_key is provided:
        Calls Replicate / OpenAI image generation API with the input photo as reference.
    Else (Mock / Local mode):
        Uses Pillow to process the face image, composite cute Chibi ears, blush, 
        and generate new mascot sprite frames.
    """
    if output_dir is None:
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_dir = getattr(sys, '_MEIPASS')
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, "assets", "sprites")

    os.makedirs(output_dir, exist_ok=True)

    if api_key:
        print(f"[AIGenerator] API Key detected. Sending {image_path} to AI API...")
        # API Placeholder call structure (e.g. Replicate / OpenAI DALL-E / SDXL)
        # headers = {"Authorization": f"Bearer {api_key}"}
        # payload = {"input_image": image_path, "prompt": "Cute chibi cat pet mascot, vector anime style"}
        # response = requests.post("https://api.replicate.com/v1/predictions", json=payload, headers=headers)
        # return response.json()
        pass

    print(f"[AIGenerator] Processing face image locally (Mock mode): {image_path}")

    try:
        # Load user face image
        face_img = Image.open(image_path).convert("RGBA")
        
        # Crop & resize face into a cute round chibi head
        w, h = face_img.size
        min_dim = min(w, h)
        left = (w - min_dim) // 2
        top = (h - min_dim) // 2
        face_cropped = face_img.crop((left, top, left + min_dim, top + min_dim))
        face_resized = face_cropped.resize((72, 72), Image.Resampling.LANCZOS)

        # Create 128x128 sprite canvas
        canvas = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        # Draw Chibi Ears
        body_color = (255, 200, 210, 255)
        inner_ear = (255, 120, 160, 255)
        outline = (70, 50, 60, 255)

        # Ears
        draw.polygon([(26, 30), (12, 4), (46, 20)], fill=body_color, outline=outline, width=2)
        draw.polygon([(28, 28), (18, 10), (44, 22)], fill=inner_ear)
        draw.polygon([(82, 20), (116, 4), (102, 30)], fill=body_color, outline=outline, width=2)
        draw.polygon([(84, 22), (110, 10), (100, 28)], fill=inner_ear)

        # Mask user face into circular shape
        mask = Image.new("L", (72, 72), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, 72, 72), fill=255)

        # Paste face into canvas head area
        canvas.paste(face_resized, (28, 26), mask)

        # Overlay Head Border & Cute Blush
        draw.ellipse([26, 24, 102, 100], outline=outline, width=3)
        draw.ellipse([28, 68, 44, 80], fill=(255, 120, 150, 150))
        draw.ellipse([84, 68, 100, 80], fill=(255, 120, 150, 150))

        # Save customized idle_1 sprite
        output_file = os.path.join(output_dir, "idle_1.png")
        canvas.save(output_file)
        print(f"[AIGenerator] Custom mascot face generated: {output_file}")
        return True, output_file
    except Exception as e:
        print(f"[AIGenerator] Error generating chibi: {e}")
        return False, str(e)


class AIGeneratorThread(QThread):
    """
    QThread worker to run AI generation asynchronously without freezing the GUI.
    """
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, image_path, api_key=None, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.api_key = api_key

    def run(self):
        success, result = generate_chibi_from_face(self.image_path, self.api_key)
        self.finished_signal.emit(success, result)
