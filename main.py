# python -m uvicorn main:app --reload

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from langgraph.graph import StateGraph, END
from typing import List, TypedDict, Dict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import json
import re
from pydantic import BaseModel

import uuid
import tempfile
import os
from scriptdata import ScriptData
from shotdata import ShotData
from topdfStory import generate_story_pdf
from topdfShot import generate_shot_pdf
from topdfphoto import generate_photoboard_pdf
from photodata import PhotoboardShotData

load_dotenv()

class AgentState(TypedDict):
    story:dict
    idea:List[HumanMessage]
    shot:List[dict]
    photo: str
    finish:bool



model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")


#########################CREATE STORY##########################################################
def create_story_node(state : AgentState) -> AgentState:
    '''A story node that gneerate a story based on the user story idea'''

    system_prompt = SystemMessage(content="""
   You are a professional story and film development assistant.

    Your task is to respond with a valid JSON object **only**, no explanations or text outside of the JSON.

    The expected structure:
    {
    "logline": "string",
    "synopsis": "string",
    "three_act_structure": {
        "act1": "string",
        "act2": "string",
        "act3": "string"
    },
    "characters": [
        {
        "name": "string",
        "description": "string",
        "motivation": "string",
        "arc": "string"
        }
    ],
    "scenes": [
        {
        "title": "string",
        "setting": "string",
        "description": "string",
        "characters": ["string"],
        "key_actions": ["string"]
        }
    ]
    }
    Respond only with this JSON.
    """)

    story_message = HumanMessage(content=json.dumps(state["story"], indent=2))
    all_messages = [system_prompt, story_message]
    all_messages += state["idea"]

    # all_messages = [system_prompt] + list(state["story"]) +  state["idea"]

    response = model.invoke(all_messages)

    raw_output = response.content.strip()

    # Remove triple backticks and `json` label if present
    raw_output = re.sub(r"^```json\s*", "", raw_output)
    raw_output = re.sub(r"```$", "", raw_output)

    try:
        parsed_story = json.loads(raw_output)
    except json.JSONDecodeError:
        parsed_story = {"error": "Failed to parse AI response as JSON", "raw": response.content}

    state['story'] = parsed_story

    print(f"\n🤖 AI: {parsed_story}")

    return state

graph = StateGraph(AgentState)

graph.add_node("story_generator", create_story_node)
graph.set_entry_point('story_generator')
graph.add_edge('story_generator', END)
graph_story = graph.compile()

#########################CREATE SHOT##########################################################

def create_shot_node(state : AgentState) -> AgentState:
    '''A shot node that gneerate a shhot based on the user story'''

    system_prompt = SystemMessage(content="""
    You are a professional Director of Photography.

    Your job is to create a SHOTLIST in JSON format based on the following story.

    Your task is to respond with a valid JSON object **only**, no explanations or text outside of the JSON.

    The expected structure:
        [
    {
        "shot_number": 0,
        "scene_number": 0,
        "shot_type": "string",
        "camera_angle": "string",
        "camera_movement": "string",
        "description": "string",
        "lens_recommendation": "string",
        "estimated_duration": 0,
        "notes": "string"
    },
    {
        "shot_number": 0,
        "scene_number": 0,
        "shot_type": "string",
        "camera_angle": "string",
        "camera_movement": "string",
        "description": "string",
        "lens_recommendation": "string",
        "estimated_duration": 0,
        "notes": "string"
    }
    ]
    Respond only with this JSON.

    Please generate 5 well-thought-out shots.
    
    """)

    story_message = HumanMessage(content=json.dumps(state["story"], indent=2))
    shot_message = HumanMessage(content=json.dumps(state["shot"], indent=2)) if state["shot"] else None
    all_messages = [system_prompt, story_message]
    if shot_message:
        all_messages.append(shot_message)
    all_messages += state["idea"]
    # all_messages = [system_prompt] + list(state["story"]) + [state["shot"]] + state["idea"]

    response = model.invoke(all_messages)

    raw_output = response.content.strip()

    # Remove triple backticks and `json` label if present
    raw_output = re.sub(r"^```json\s*", "", raw_output)
    raw_output = re.sub(r"```$", "", raw_output)

    try:
        parsed_shot = json.loads(raw_output)
    except json.JSONDecodeError:
        parsed_shot = {"error": "Failed to parse AI response as JSON", "raw": response.content}

    state['shot'] = parsed_shot

    print(f"\n🤖 AI: {parsed_shot}")

    return state



graph = StateGraph(AgentState)

graph.add_node("shot_generator", create_shot_node)
graph.set_entry_point('shot_generator')
graph.add_edge('shot_generator', END)
graph_shot = graph.compile()


###############--PHOTOBOARD GENERATION--##################
def create_photo_node(state : AgentState) -> AgentState:
    '''A photboard node that gneerate a photboard based on the user shotlist'''

    system_prompt = SystemMessage(content="""
    You are a professional Director of Photography.

    Your job is to create a PHOTO based on the following shot.
    
    """)

    all_messages = [system_prompt] + [AIMessage(content=state["shot"])]

    response = model.invoke(all_messages)

    raw_output = response.content.strip()

    # Remove triple backticks and `json` label if present
    raw_output = re.sub(r"^```json\s*", "", raw_output)
    raw_output = re.sub(r"```$", "", raw_output)

    try:
        parsed_shot = json.loads(raw_output)
    except json.JSONDecodeError:
        parsed_shot = {"error": "Failed to parse AI response as JSON", "raw": response.content}

    state['shot'] = parsed_shot

    print(f"\n🤖 AI: {parsed_shot}")

    return state



graph = StateGraph(AgentState)

graph.add_node("shot_generator", create_shot_node)
graph.set_entry_point('shot_generator')
graph.add_edge('shot_generator', END)
graph_shot = graph.compile()



#################-FASTAPI-########################

app = FastAPI()

# Allow local frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cinesparkai.online"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Call the model to generate the story, if the story already exist, than idea is treated as a suggestion from user
# If story not exist yet, then story is parse in as empty string
class StoryRequest(BaseModel):
    idea: str
    story: dict = {}


@app.post("/generate_story")
async def generate_story(request: StoryRequest):
    state = {
        'idea': [HumanMessage(content=request.idea)],
        'story': request.story,
        'shot': "",
        'finish': False
    }
    result = graph_story.invoke(state)
    return {
    "story": result["story"] 
}

#Idea acts ad suggestion, story is in JSON Format
class ShotRequest(BaseModel):
    idea: str = " "
    story: dict
    shot: List = []

@app.post("/generate_shot")
async def generate_shot(request : ShotRequest):
    state = {
    'idea': [HumanMessage(content=request.idea)],
    'story': request.story,   
    'shot': request.shot,    
    'finish': False 
    } 
    result = graph_shot.invoke(state)
    return {"shot" : result["shot"]}


##################----GENERATE PDF Story---#############
class PDFStoryRequest(BaseModel):
    project_name: str
    story: ScriptData

@app.post("/generate-pdf-story")
async def generate_pdf_story(data : PDFStoryRequest) -> FileResponse:
    temp_dir = tempfile.gettempdir()  
    filename = f"{uuid.uuid4().hex}.pdf"
    filepath = os.path.join(temp_dir, filename)

    generate_story_pdf(data.project_name, data.story, filepath)
    return FileResponse(filepath, filename=filename, media_type="application/pdf")

##################----GENERATE PDF Shot---#############
class PDFShotRequest(BaseModel):
    project_name: str
    shot: List[ShotData]

@app.post("/generate-pdf-shot")
async def generate_pdf_shot(data : PDFShotRequest) -> FileResponse:
    temp_dir = tempfile.gettempdir()  
    filename = f"{uuid.uuid4().hex}.pdf"
    filepath = os.path.join(temp_dir, filename)

    generate_shot_pdf(data.project_name, data.shot, filepath)
    return FileResponse(filepath, filename=filename, media_type="application/pdf")


print("loading")

##################----GENERATE PDF Photboard---#############
class PDFPhotoRequest(BaseModel):
    project_name: str
    photo: List[PhotoboardShotData]

@app.post("/generate-pdf-photo")
async def generate_pdf_photo(data : PDFPhotoRequest) -> FileResponse:
    temp_dir = tempfile.gettempdir()  
    filename = f"{uuid.uuid4().hex}.pdf"
    filepath = os.path.join(temp_dir, filename)

    generate_photoboard_pdf(data.project_name, data.photo, filepath)
    return FileResponse(filepath, filename=filename, media_type="application/pdf")


print("loading")

