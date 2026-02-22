"""LangGraph single-node graph template.

Returns a predefined response. Replace logic and configuration as needed.
"""

from __future__ import annotations

import os

from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional

from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from langgraph.runtime import Runtime
from typing_extensions import TypedDict

llm = ChatOpenAI(model="gpt-4o")

@dataclass
class InputState(MessagesState):
  temp: Optional[str]
  
@dataclass
class State(MessagesState):
  mode: Literal["define_task", "architecture_planning", "technology_chooser", "implement_code", "code_review", "docker_manager"] | None
  summary: str | None

def node_define_task(state: State) -> State:
  SYSTEM_PROMPT = """
    You are software engineer asistant, your goal is to define task problem to solve.

    Disregard any conversation, which is not about software engineering.
    
    Do not focus on:
    - technologies, 
    - testing, 
    - requirements 
    - challenges
    - planning
    - examples

    Provide output in Markdown, ready to save to file, it should be short and straight to the point.
  """

  content = state["messages"][-1]

  messages = [
    SystemMessage(SYSTEM_PROMPT),
    content
  ]

  response = llm.invoke(messages)

  return {"messages": [response]}

def node_system_architecture(state: State):
  SYSTEM_PROMPT = """
    You are software engineer asistant.
    User will provide you with defined task, your goal is to plan architecture of this system.

    Disregard any conversation, which is not about software engineering.

    Do not focus on:
    - technologies, 
    - testing, 
    - requirements 
    - challenges
    - examples

    Provide output in Markdown, ready to save to file, it should be short and straight to the point.
  """

  content = state["messages"][-1]

  messages = [
    SystemMessage(SYSTEM_PROMPT),
    content
  ]

  response = llm.invoke(messages)

  return {"messages": [response]}

def node_technology_chooser(state: State):
  SYSTEM_PROMPT = """
    You are software engineer asistant.
    User will provide you with planned architecture, your goal is to provide the best technology to implement this.
    Do not provide a choice, choose one best tech-stack/frameworks you can think of.

    Disregard any conversation, which is not about software engineering.

    Do not focus on:
    - implementation, 
    - testing, 
    - examples

    Provide output in Markdown, ready to save to file, it should be short and straight to the point.
  """

  content = state["messages"][-1]

  messages = [
    SystemMessage(SYSTEM_PROMPT),
    content
  ]

  response = llm.invoke(messages)

  return {"messages": [response]}

# use subgraphs or something similar
# one router decides which graph to use, changing mode

# to define new graphs, use langgraph.json

task_graph = (
  StateGraph(State)
  .add_node("node_define_task", node_define_task)
  .add_edge("__start__", "node_define_task")
  .compile()
)

arch_graph = (
  StateGraph(State)
  .add_node("node_system_architecture", node_system_architecture)
  .add_edge("__start__", "node_system_architecture")
  .compile()
)

tech_graph = (
  StateGraph(State)
  .add_node("node_technology_chooser", node_technology_chooser)
  .add_edge("__start__", "node_technology_chooser")
  .compile()
)

  # if os.path.exists("static/file.md"):
  #   with open("static/file.md", "r") as f:
  #     file_content = f.read()
  #     messages += [HumanMessage(content=file_content)]

  # with open("static/file.md", "w") as f:
  #   f.write(response.content)