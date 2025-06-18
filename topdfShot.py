from fpdf import FPDF
from shotdata import ShotData
from typing import List, Dict

# Data strcutre example 
data = [
    {
        "shot_number": 1,
        "scene_number": 1,
        "shot_type": "Wide Shot",
        "camera_angle": "High Angle",
        "camera_movement": "Static",
        "description": "Establishing shot of the lighthouse at dawn, surrounded by mist and crashing waves",
        "lens_recommendation": "24mm wide-angle lens",
        "estimated_duration": 8,
        "notes": "Golden hour lighting, emphasize isolation"
    },
    {
        "shot_number": 2,
        "scene_number": 1,
        "shot_type": "Medium Shot",
        "camera_angle": "Eye-level",
        "camera_movement": "Pan",
        "description": "Marcus moving through lighthouse interior, checking equipment methodically",
        "lens_recommendation": "50mm standard lens",
        "estimated_duration": 12,
        "notes": "Handheld for intimate feel"
    },
    {
        "shot_number": 3,
        "scene_number": 1,
        "shot_type": "Close-up",
        "camera_angle": "Eye-level",
        "camera_movement": "Static",
        "description": "Close-up of Marcus's weathered hands adjusting lighthouse mechanism",
        "lens_recommendation": "85mm portrait lens",
        "estimated_duration": 4,
        "notes": "Focus on texture and routine"
    },
    {
        "shot_number": 4,
        "scene_number": 2,
        "shot_type": "Wide Shot",
        "camera_angle": "Low Angle",
        "camera_movement": "Dolly",
        "description": "Marcus walking down rocky shore, storm debris scattered around",
        "lens_recommendation": "35mm lens",
        "estimated_duration": 10,
        "notes": "Steadicam for smooth movement"
    },
    {
        "shot_number": 5,
        "scene_number": 2,
        "shot_type": "Extreme Close-up",
        "camera_angle": "High Angle",
        "camera_movement": "Static",
        "description": "Marcus's eyes widening as he first sees Naia",
        "lens_recommendation": "100mm macro lens",
        "estimated_duration": 3,
        "notes": "Capture moment of discovery"
    },
    {
        "shot_number": 6,
        "scene_number": 3,
        "shot_type": "POV",
        "camera_angle": "Eye-level",
        "camera_movement": "Handheld",
        "description": "Naia's perspective as she awakens in the makeshift pool",
        "lens_recommendation": "28mm wide lens",
        "estimated_duration": 6,
        "notes": "Underwater housing for partial submersion"
    }
]

black_rgb = (0, 0, 0)
white_rgb = (255, 255, 255)

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.ln(5)
    
    def chapter_title(self, text):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*black_rgb)
        self.cell(0, 10, text, ln=1, align="C")
        self.ln(2)

    def table_header(self, col_widths):
        self.set_font("Helvetica", "B", 10)
        headers = ["Shot #", "Scene", "Type", "Angle", "Movement", "Description", "Lens", "Duration", "Notes"]
        for i, header in enumerate(headers):
            self.multi_cell(col_widths[i], 8, header, border=1, align="C", max_line_height=self.font_size, new_x="RIGHT", new_y="TOP")
        self.ln()

    def table_row(self, shot, col_widths):
        
        

        self.set_font("Helvetica", "", 9)

        values = [
          str(shot.shot_number),
          str(shot.scene_number),
          shot.shot_type,
          shot.camera_angle,
          shot.camera_movement,
          shot.description,
          shot.lens_recommendation,
          str(shot.estimated_duration),
          shot.notes
        ]

        # Calculate number of lines each cell would take
        line_counts = [
            len(self.multi_cell(col_widths[i], 5, val, split_only=True))
            for i, val in enumerate(values)
        ]
        max_lines = max(line_counts)
        row_height = max_lines * 5  # 5mm per line

        line_height = [row_height / line for line in line_counts]

        x_start = self.get_x()
        y_start = self.get_y()

        # Draw each cell manually
        for i, val in enumerate(values):
            self.set_xy(x_start + sum(col_widths[:i]), y_start)
            self.multi_cell(col_widths[i], line_height[i], val, border=1, align="L")

            # Reset Y position so the next cell stays aligned
            self.set_xy(x_start + sum(col_widths[:i+1]), y_start)

        # Move cursor to the beginning of the next row
        self.set_xy(x_start, y_start + row_height)

    def get_string_height(self, w, text):
        return self.get_string_width(text) / w * self.font_size + 2

def generate_shot_pdf(project_name: str, data: List[ShotData], file_path: str):
    pdf = PDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    col_widths = [14, 14, 20, 20, 20, 70, 25, 20, 70]

    pdf.chapter_title(f"{project_name} - Shot List")
    pdf.table_header(col_widths)
    for shot in data:
    # Estimate the row height
      values = [
          str(shot.shot_number),
          str(shot.scene_number),
          shot.shot_type,
          shot.camera_angle,
          shot.camera_movement,
          shot.description,
          shot.lens_recommendation,
          str(shot.estimated_duration),
          shot.notes
      ]
      
      # Use split_only=True to get line count for each cell
      line_counts = [
          len(pdf.multi_cell(col_widths[i], 5, val, split_only=True))
          for i, val in enumerate(values)
      ]
      max_lines = max(line_counts)
      estimated_row_height = max_lines * 5  # 5 mm per line

      # Check if there's enough space left on the page
      if pdf.get_y() + estimated_row_height > pdf.h - pdf.b_margin:
          pdf.add_page()
          pdf.table_header(col_widths)

      # Now draw the row
      pdf.table_row(shot, col_widths)

    pdf.output(file_path)