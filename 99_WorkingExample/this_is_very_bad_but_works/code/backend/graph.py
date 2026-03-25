from __future__ import annotations

import base64
import json
import re

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from typing_extensions import TypedDict, Annotated
from dataclasses import dataclass
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.graph.message import add_messages

load_dotenv()

llm = ChatOpenAI(model="gpt-4o")


def tool_image(query: str, image_url: str) -> str:
    """Parses image with LLM.
    """

    SYSTEM_PROMPT = """
    You are a chef, when user uploads image derive it's recipe

    Provide only instructions, nothing else, NO INGREDIENTS

    Provide result in form of a bullet list, no nesting list
  """

    user_message = query
    content = [
        {"type": "text", "text": user_message},
        {"type": "image_url", "image_url": {"url": image_url}},
    ]
    messages = [SystemMessage(SYSTEM_PROMPT), HumanMessage(content=content)]

    response = llm.invoke(messages)
    return response.content


def convert_to_json(query: str) -> str:
    """Convert recipe and ingredients to JSON text."""

    SYSTEM_PROMPT = """
    You are a chef assitant.

    User will provide you recipe nad ingredients with measurments. Your goal is to summarise last message and convert this data to JSON file.

    Provide only JSON data, nothing more.

    Your json schema:
    {
      <dish1>: {
        "ingredients": [
          <ingredient_name>,
          ...
        ],
        "recipe": [
          <step1>,
          <step2>,
          ...
        ]
      },
      ...
    }
  """

    user_message = query
    content = [{"type": "text", "text": user_message}]
    messages = [SystemMessage(SYSTEM_PROMPT), HumanMessage(content=content)]

    response = llm.invoke(messages)
    try:
        parsed = json.loads(response.content)
        return json.dumps(parsed, indent=2)
    except json.JSONDecodeError:
        return json.dumps({"error": "Could not parse", "raw": response.content})


def generate_recipe_image(recipe: str):
    """
    Generate image from provided recipe
    """

    filename = f"recipe.png"
    path = f"static/images/{filename}"

    image_model = ChatOpenAI(model="gpt-4.1-mini")

    prompt = f"""
    Food photography of:
    {recipe}
  """

    result = image_model.invoke(
        prompt, tools=[{"type": "image_generation", "quality": "low"}])
    image = next(
        item for item in result.content_blocks if item["type"] == "image"
    )

    image_bytes = base64.b64decode(image["base64"])

    with open(path, "wb") as f:
        f.write(image_bytes)

    return f"Path to image: {path}"


tools = [tool_image, convert_to_json, generate_recipe_image]


@dataclass
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    recipe_data: dict | None


llm_with_tools = llm.bind_tools(tools)


def node_router(state: State):
    """Route incoming messages to either the LLM or the image tool.
    """

    messages = state["messages"]

    SYSTEM_PROMPT = """
        You are a helpful chef assistant. 

        Disregard any conversation, which is not about cooking.

        - If the user uploads image, call tool_images
        - If the user wants recipe converted to JSON, call convert_to_json
        - When user will ask you about specific dish, your task is to provide recipe and list of ingredients (with measurments).
        - For all other questions, answer directly
    """

    system = SystemMessage(SYSTEM_PROMPT)
    response = llm_with_tools.invoke([system] + messages)
    pattern = r"```json\s*(.*?)\s*```"
    matches = re.findall(pattern, response.content, re.DOTALL)

    data = None
    for i, match in enumerate(matches, 1):
        try:
            data = json.loads(match)
            print(f"JSON #{i} extracted:", data)
        except json.JSONDecodeError as e:
            print(f"JSON #{i} is invalid:", e)

    return {"messages": [response], "recipe_data": data}


saver = MemorySaver()

graph = (
    StateGraph(State)
    .add_node("tools", ToolNode(tools))
    .add_node("node_router", node_router)
    .add_edge("__start__", "node_router")
    .add_conditional_edges("node_router", tools_condition)
    .add_edge("tools", "node_router")
    .compile(name="Merged Agents", checkpointer=saver)
)
