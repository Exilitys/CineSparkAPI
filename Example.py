from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import json

# Load environment variables
load_dotenv()

# Global variable to store the story content
document_content = ""

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

@tool
def update(content: str) -> str:
    """Updates the document with the provided story content."""
    global document_content
    document_content = content
    return f"The story has been updated successfully! The current story is:\n{document_content}"

@tool
def save(filename: str) -> str:
    """Save the current story to a text file and finish the process."""
    global document_content
    if not filename.endswith('.txt'):
        filename = f"{filename}.txt"
    try:
        with open(filename, 'w') as file:
            file.write(document_content)
        print(f"\n💾 Story has been saved to: {filename}")
        return f"Story has been saved successfully to '{filename}'."
    except Exception as e:
        return f"Error saving story: {str(e)}"

tools = [update, save]

# Using Gemini for story generation and tool binding
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash").bind_tools(tools)

# Agent logic
def our_agent(state: AgentState) -> AgentState:
    global document_content
    system_prompt = SystemMessage(content=f"""
You are StoryBot, a professional story and film development assistant.

Follow this workflow:
1. When the user provides a story idea or logline, generate a JSON with:
   - logline
   - synopsis
   - main_characters (with name, role, short desc)
   - structure (Act I, Act II, Act III with summaries)
2. Use the 'update' tool with the full generated JSON result.
3. Then generate a detailed SHOTLIST in JSON with:
   - scene_number
   - shot_type (e.g., Wide, Close-up, Over-the-shoulder)
   - shot_description
   - link to related part in act or scene
4. Ask the user for changes. If any are requested, revise the JSON and call 'update' again.
5. When the user is satisfied and says “save”, use the 'save' tool.

Current stored story:
{document_content}
""")

    if not state["messages"]:
        user_input = "Please provide your story idea, premise, or logline to begin."
        user_message = HumanMessage(content=user_input)
    else:
        user_input = input("\nHow should we continue with the story? ")
        print(f"\n👤 USER: {user_input}")
        user_message = HumanMessage(content=user_input)

    all_messages = [system_prompt] + list(state["messages"]) + [user_message]
    response = model.invoke(all_messages)

    print(f"\n🤖 AI: {response.content}")
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"🔧 USING TOOLS: {[tc['name'] for tc in response.tool_calls]}")

    return {"messages": list(state["messages"]) + [user_message, response]}

# Whether to continue or stop
def should_continue(state: AgentState) -> str:
    messages = state["messages"]
    if not messages:
        return "continue"
    for message in reversed(messages):
        if (isinstance(message, ToolMessage) and 
            "saved" in message.content.lower() and
            "story" in message.content.lower()):
            return "end"
    return "continue"

# Optional: readable message printing
def print_messages(messages):
    if not messages:
        return
    for message in messages[-3:]:
        if isinstance(message, ToolMessage):
            print(f"\n🛠️ TOOL RESULT: {message.content}")

# LangGraph definition
graph = StateGraph(AgentState)
graph.add_node("agent", our_agent)
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("agent")
graph.add_edge("agent", "tools")
graph.add_conditional_edges("tools", should_continue, {"continue": "agent", "end": END})
app = graph.compile()

# Runner
def run_story_agent():
    print("\n ===== STORYBOT =====")
    state = {"messages": []}
    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            print_messages(step["messages"])
    print("\n ===== STORYBOT FINISHED =====")

if __name__ == "__main__":
    run_story_agent()
