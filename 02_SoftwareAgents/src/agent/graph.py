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

# System prompts for all nodes
SYSTEM_PROMPTS = {
    "define_task": """
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
  """,
    "system_architecture": """
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
  """,
    "technology_chooser": """
    You are software engineer asistant.
    User will provide you with planned architecture, your goal is to provide the best technology to implement this.
    Do not provide a choice, choose one best tech-stack/frameworks you can think of.

    Disregard any conversation, which is not about software engineering.

    Do not focus on:
    - implementation, 
    - testing, 
    - examples

    Provide output in Markdown, ready to save to file, it should be short and straight to the point.
  """,
    "implementation": """
    You are software engineer asistant.
    
    User will provide you with:
    - task,
    - planned architecture, 
    - technology
    
    Your goal is to implement this task in given technology, following architecture.

    Disregard any conversation, which is not about software engineering.

    Provide only code, ready to save to file
  """,
    "code_review": """
    You are software engineer asistant.
    User will provide you with:
    - code
    - task
    - architecture

    Your goal is to review the code, pinpoint mistakes and vunerabilities. 

    Disregard any conversation, which is not about software engineering.

    Provide output in Markdown, ready to save to file, it should be short and straight to the point.
  """,
    "docker": """
    You are software engineer asistant.

    Your goal is to provide Docker commands, based on user input. 
    
    Disregard any conversation, which is not about software engineering.

    Provide only command. 
  """,
    "router": """
    You are software engineer asistant

    Decide, where to redirect user message:
    - "define_task" - user provides App idea or ask questions about problem
    - "architecture_planning" - user asks about architecture, provides task
    - "technology_chooser" - user asks about technology, provides architecture
    - "implement_code" - user wants to create code in specific technology and architecture
    - "code_review" - user asks you to review provided code
    - "docker_manager" - user needs docker command

    Reply only with provided key
  """
}

# for input and output, MessageState
  
@dataclass
class State(MessagesState):
  mode: Literal["define_task", "architecture_planning", "technology_chooser", "implement_code", "code_review", "docker_manager"] | None
  summary: str | None

def node_define_task(state: State) -> State:
  content = state["messages"][-1]

  messages = [
    SystemMessage(SYSTEM_PROMPTS["define_task"]),
    content
  ]

  response = llm.invoke(messages)

  return {"messages": [response]}

def node_system_architecture(state: State):
  content = state["messages"][-1]

  messages = [
    SystemMessage(SYSTEM_PROMPTS["system_architecture"]),
    content
  ]

  response = llm.invoke(messages)

  return {"messages": [response]}

def node_technology_chooser(state: State):
  content = state["messages"][-1]

  messages = [
    SystemMessage(SYSTEM_PROMPTS["technology_chooser"]),
    content
  ]

  response = llm.invoke(messages)

  return {"messages": [response]}

def node_implementation(state: State):
  content = state["messages"][-1]

  messages = [
    SystemMessage(SYSTEM_PROMPTS["implementation"]),
    content
  ]

  response = llm.invoke(messages)

  return {"messages": [response]}

def node_code_review(state: State):
  content = state["messages"][-1]

  messages = [
    SystemMessage(SYSTEM_PROMPTS["code_review"]),
    content
  ]

  response = llm.invoke(messages)

  return {"messages": [response]}

def node_docker(state: State):
  content = state["messages"][-1]

  messages = [
    SystemMessage(SYSTEM_PROMPTS["docker"]),
    content
  ]

  response = llm.invoke(messages)

  return {"messages": [response]}

def node_router(state: MessagesState) -> State:
  content = state["messages"][-1]

  messages = [
    SystemMessage(SYSTEM_PROMPTS["router"]),
    content
  ]

  response = llm.invoke(messages)

  return {"messages": [content], "mode": response.content}

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

  # if os.path.exists("static/file.md"):
  #   with open("static/file.md", "r") as f:
  #     file_content = f.read()
  #     messages += [HumanMessage(content=file_content)]

  # with open("static/file.md", "w") as f:
  #   f.write(response.content)