from fpdf import FPDF
import requests
from PIL import Image
from io import BytesIO
import os
import tempfile
from photodata import PhotoboardShotData, TechnicalSpecs
from typing import List, Dict
import uuid

black_rgb = (0, 0, 0)
white_rgb = (255, 255, 255)

class PDFPhotoboard(FPDF):
    def header(self):
        self.set_fill_color(*white_rgb)
        self.rect(0, 0, self.w, self.h, 'F')

    def chapter_title(self, text):
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(*black_rgb)
        self.cell(0, 15, text, ln=1, align="C")
        self.ln(10)

    def section_title(self, title):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*black_rgb)
        self.cell(0, 10, title, ln=1)
        self.ln(2)

    def section_body(self, text):
        self.set_font("Helvetica", "", 12)
        self.set_text_color(*black_rgb)
        self.multi_cell(0, 8, text)
        self.ln(1)

    def add_image_from_url(self, url, max_width=120, max_height=90):
        try:
            response = requests.get(url)
            image = Image.open(BytesIO(response.content))
            temp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}.jpg")
            image.convert("RGB").save(temp_path)

            img_w, img_h = image.size
            aspect = img_h / img_w

            width = min(max_width, self.w - 40)
            height = width * aspect
            if height > max_height:
                height = max_height
                width = height / aspect

            x = (self.w - width) / 2
            y = self.get_y()
            self.image(temp_path, x=x, y=y, w=width, h=height)
            self.ln(height + 5)
        except Exception as e:
            self.section_body(f"Could not load image: {e}")
            self.ln(5)

def generate_photoboard_pdf(project_name: str, photoboard_data: List[PhotoboardShotData], file_path: str):
    pdf = PDFPhotoboard()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.chapter_title(f"{project_name} - Photoboard")

    for shot in sorted(photoboard_data, key=lambda x: (x.scene_number, x.shot_number)):
        pdf.section_title(f"Scene {shot.scene_number} - Shot {shot.shot_number}")
        pdf.section_body(f"{shot.description}")
        pdf.add_image_from_url(shot.image_url)

        # Technical Specs
        specs = shot.technical_specs
        spec_text = (
            f"Shot Type: {specs.shot_type}\n"
            f"Camera Angle: {specs.camera_angle}\n"
            f"Camera Movement: {specs.camera_movement}\n"
            f"Lens Recommendation: {specs.lens_recommendation}"
        )
        pdf.section_body(spec_text)

        if shot.annotations:
            pdf.section_body("Notes: " + ", ".join(shot.annotations))
        pdf.add_page()


    pdf.output(file_path)


example = [{
    "shot_id": "s1",
    "shot_number": 1,
    "scene_number": 1,
    "description": "Marcus looks out the window at the stormy sea.",
    "style": "Dramatic, low light",
    "image_url": "https://images.pexels.com/photos/1174732/pexels-photo-1174732.jpeg?auto=compress&cs=tinysrgb&w=800",
    "annotations": ["Use backlight", "Keep shadows strong"],
    "technical_specs": {
        "shot_type": "Close-up",
        "camera_angle": "Over-the-shoulder",
        "camera_movement": "Static",
        "lens_recommendation": "85mm"
    }
},
{
    "shot_id": "s1",
    "shot_number": 1,
    "scene_number": 1,
    "description": "Marcus looks out the window at the stormy sea.",
    "style": "Dramatic, low light",
    "image_url": "https://images.pexels.com/photos/1212984/pexels-photo-1212984.jpeg?auto=compress&cs=tinysrgb&w=800",
    "annotations": ["Use backlight", "Keep shadows strong"],
    "technical_specs": {
        "shot_type": "Close-up",
        "camera_angle": "Over-the-shoulder",
        "camera_movement": "Static",
        "lens_recommendation": "85mm"
    }
},
{
    "shot_id": "s1",
    "shot_number": 1,
    "scene_number": 1,
    "description": "Marcus looks out the window at the stormy sea.",
    "style": "Dramatic, low light",
    "image_url": "https://images.pexels.com/photos/1174732/pexels-photo-1174732.jpeg?auto=compress&cs=tinysrgb&w=800",
    "annotations": ["Use backlight", "Keep shadows strong"],
    "technical_specs": {
        "shot_type": "Close-up",
        "camera_angle": "Over-the-shoulder",
        "camera_movement": "Static",
        "lens_recommendation": "85mm"
    }
}]
