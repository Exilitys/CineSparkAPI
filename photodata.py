from pydantic import BaseModel
from typing import List

class TechnicalSpecs(BaseModel):
    shot_type: str
    camera_angle: str
    camera_movement: str
    lens_recommendation: str

class PhotoboardShotData(BaseModel):
    shot_id: str
    shot_number: int
    scene_number: int
    description: str
    style: str
    image_url: str
    annotations: List[str]
    technical_specs: TechnicalSpecs