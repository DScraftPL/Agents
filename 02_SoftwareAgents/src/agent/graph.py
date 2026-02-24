"""LangGraph single-node graph template.

Returns a predefined response. Replace logic and configuration as needed.
"""

from __future__ import annotations

import os

from langchain_core.runnables import RunnableConfig

from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional

from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from langgraph.runtime import Runtime
from typing_extensions import TypedDict

from functools import partial

# from src.agent.prompts import SYSTEM_PROMPTS

SYSTEM_PROMPTS = {
    "define_task": """
    You are software engineer asistant, your goal is to define task problem to solve.

    User will provide you with problem to solve, app idea and with summary of conversation (optionaly). 

    Disregard any conversation, which is not about software engineering.
    
    Do not focus on:
    - technologies, 
    - testing, 
    - requirements 
    - challenges
    - planning
    - examples

    Your output has to have following categories:
    - Problem Statement
    - Objectives

    Provide output in raw Markdown, ready to save.
  """,
    "system_architecture": """
    You are software engineer asistant.
    
    User will provide you with defined task, your goal is to plan architecture of this system.
    If task is not defined, ask user about it.

    Disregard any conversation, which is not about software engineering.

    Do not focus on:
    - technologies, 
    - testing, 
    - requirements 
    - challenges
    - examples

    Provide output in Markdown, ready to save.
  """,
    "technology_chooser": """
    You are software engineer asistant.
    
    User will provide you with planned architecture and task, your goal is to provide the best technology to implement this.
    If task or architecture is not present, ask user about it.
    
    Do not provide a choice, choose one best tech-stack/frameworks you can think of.

    Disregard any conversation, which is not about software engineering.

    Do not focus on:
    - implementation, 
    - testing, 
    - examples

    Provide output in Markdown, ready to save.
  """,
    "implementation": """
    You are software engineer asistant.
    
    User will provide you with:
    - task,
    - planned architecture, 
    - technology
    If any of categories are missing, ask user about it.
    
    Your goal is to implement this task in given technology, following architecture.

    Disregard any conversation, which is not about software engineering.

    Provide only code, ready to save to file. 
  """,
    "code_review": """
    You are software engineer asistant.
    User will provide you with:
    - code
    - task
    - architecture

    Your goal is to review the code, pinpoint mistakes and vunerabilities. 

    Disregard any conversation, which is not about software engineering.

    Provide output in Markdown, ready to save.
  """,
    "docker": """
    You are software engineer asistant.

    Your goal is to provide Docker commands, based on user input. 
    
    Disregard any conversation, which is not about software engineering.

    Provide only docker command in plain text.
  """,
    "router": """
    You are software engineer asistant

    Disregard any conversation, which is not about software engineering.

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

llm = ChatOpenAI(model="gpt-4o")

def read_file(file_name: str, thread_id: str) -> str:
  file_name = f"static/markdown/{thread_id}/{file_name}"
  if os.path.exists(file_name):
    with open(file_name, "r") as f:
      file_content = f.read()
      return file_content
  else:
    raise RuntimeError("File cannot be read")

def save_file(file_name: str, content: str, thread_id: str):
    directory = f"static/markdown/{thread_id}"
    os.makedirs(directory, exist_ok=True) 
    file_name = os.path.join(directory, file_name)
    with open(file_name, "w") as f:
        f.write(content)

# for input and output, MessageState
  
@dataclass
class State(MessagesState):
  mode: Literal["define_task", "architecture_planning", "technology_chooser", "implement_code", "code_review", "docker_manager"]

def basic_node(state: State, config: RunnableConfig,  prompt_key: str, read_files: list[str], write_file: str) -> MessagesState:
  content = state["messages"][-1]
  thread_id = config["configurable"]["thread_id"]

  messages = [
    SystemMessage(SYSTEM_PROMPTS[prompt_key]),
    content
  ]

  for file_to_read in read_files:
    try:
      file_content = read_file(file_to_read, thread_id)
      messages.append(HumanMessage(file_content))
    except: 
      pass

  response = llm.invoke(messages)

  save_file(write_file, response.content.strip().strip("```").strip("markdown").strip("\n"), thread_id)

  return {"messages": [response]}

node_define_task = partial(basic_node, prompt_key="define_task", write_file="TASK.md", read_files=["TASK.md"])
node_system_architecture = partial(basic_node, prompt_key="system_architecture", write_file="ARCHITECTURE.md", read_files=["TASK.md", "ARCHITECTURE.md"])
node_technology_chooser = partial(basic_node, prompt_key="technology_chooser", write_file="TECHNOLOGY.md", read_files=["TASK.md", "ARCHITECTURE.md", "TECHNOLOGY.md"])
# node_implementation = partial(basic_node, prompt_key="implementation", write_file="TASK.md", read_files=[])
node_code_review = partial(basic_node, prompt_key="code_review", write_file="REVIEW.md", read_files=["CODE.md"])
node_docker = partial(basic_node, prompt_key="docker", write_file="DOCKER.md", read_files=[])

def node_implementation(state: State, config: RunnableConfig):   
  content = state["messages"][-1]
  thread_id = config["configurable"]["thread_id"]

  messages = [
    SystemMessage(SYSTEM_PROMPTS["implementation"]),
    content
  ]

  read_files=["TASK.md", "ARCHITECTURE.md", "TECHNOLOGY.md"]

  for file_to_read in read_files:
    try:
      file_content = read_file(file_to_read, thread_id)
      messages.append(HumanMessage(file_content))
    except: 
      pass

  response = llm.invoke(messages)

  write_file = "CODE.md"

  save_file(write_file, response.content, thread_id)

  return {"messages": [response]}

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
