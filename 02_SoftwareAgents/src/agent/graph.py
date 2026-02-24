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

from functools import partial

from src.agent.prompts import SYSTEM_PROMPTS

llm = ChatOpenAI(model="gpt-4o")

def read_file(file_name: str):
  if os.path.exists(file_name):
    with open(file_name, "r") as f:
      file_content = f.read()
      return file_content
    
  raise RuntimeError("File cannot be read")

def save_file(file_name: str, content: str):
  with open(file_name, "w") as f:
    f.write(content)

# for input and output, MessageState
  
@dataclass
class State(MessagesState):
  mode: Literal["define_task", "architecture_planning", "technology_chooser", "implement_code", "code_review", "docker_manager"] | None
  summary: str | None

def basic_node(state: State, prompt_key: str) -> MessagesState:
  content = state["messages"][-1]

  messages = [
    SystemMessage(SYSTEM_PROMPTS[prompt_key]),
    content
  ]

  response = llm.invoke(messages)

  return {"messages": [response]}

node_define_task = partial(basic_node, prompt_key="define_task")
node_system_architecture = partial(basic_node, prompt_key="system_architecture")
node_technology_chooser = partial(basic_node, prompt_key="technology_chooser")
node_implementation = partial(basic_node, prompt_key="implementation")
node_code_review = partial(basic_node, prompt_key="code_review")
node_docker = partial(basic_node, prompt_key="docker")

def node_router(state: MessagesState) -> State:
  content = state["messages"][-1]

  messages = [
    SystemMessage(SYSTEM_PROMPTS["router"]),
    content
  ]

  response = llm.invoke(messages)
  mode = response.content.strip().strip('"')

  return {"messages": [content], "mode": mode}

def edge_router(state: State) -> Literal["define_task", "architecture_planning", "technology_chooser", "implement_code", "code_review", "docker_manager", "__end__"]:
  mode = state["mode"]
  nodes = ["define_task", "architecture_planning", "technology_chooser", "implement_code", "code_review", "docker_manager"]

  if mode not in nodes:
    return "__end__"
  
  return mode

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

impl_graph = (
  StateGraph(State)
  .add_node("node_implementation", node_implementation)
  .add_edge("__start__", "node_implementation")
  .compile()
)

code_graph = (
  StateGraph(State)
  .add_node("node_code_review", node_code_review)
  .add_edge("__start__", "node_code_review")
  .compile()
)

dock_graph = (
  StateGraph(State)
  .add_node("node_docker", node_docker)
  .add_edge("__start__", "node_docker")
  .compile()
)

main_graph = (
  StateGraph(MessagesState)
  .add_node("node_router", node_router)
  .add_node("define_task", task_graph)
  .add_node("architecture_planning", arch_graph)
  .add_node("technology_chooser", tech_graph)
  .add_node("implement_code", impl_graph)
  .add_node("code_review", code_graph)
  .add_node("docker_manager", dock_graph)
  .add_edge("__start__", "node_router")
  .add_conditional_edges("node_router", edge_router)
  .compile()
)
