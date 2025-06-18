from pydantic import BaseModel
from typing import List, Dict

class ShotData(BaseModel):
  shot_number: int
  scene_number: int
  shot_type: str
  camera_angle: str
  camera_movement: str
  description: str
  lens_recommendation: str
  estimated_duration: int
  notes: str