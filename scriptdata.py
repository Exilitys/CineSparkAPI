from pydantic import BaseModel
from typing import List, Dict

class Character(BaseModel):
    name: str
    description: str
    motivation: str
    arc: str

class Scene(BaseModel):
    title: str
    setting: str
    description: str
    characters: List[str]
    key_actions: List[str]

class ScriptData(BaseModel):
    logline: str
    synopsis: str
    three_act_structure: Dict[str, str]
    characters: List[Character]
    scenes: List[Scene]