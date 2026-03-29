"""LangGraph single-node graph template.

Returns a predefined response. Replace logic and configuration as needed.
"""

from __future__ import annotations
from typing import Literal

from typing import Literal

from langgraph.graph import MessagesState, StateGraph
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from openai import BaseModel

from functools import partial

from src.prompts import SYSTEM_PROMPTS
from src.nodes.basic import basic_node
from src.states import LinterState, State
from src.config import llm
from src.nodes.implementation import node_implementation
from src.nodes.docker import node_docker
from src.nodes.review import node_code_review
from src.nodes.linter import node_linter
from src.rag import ingest_all

node_define_task = partial(
    basic_node, prompt_key="define_task", write_file="TASK.md", read_files=["TASK.md"])
node_system_architecture = partial(basic_node, prompt_key="system_architecture",
                                   write_file="ARCHITECTURE.md", read_files=["TASK.md", "ARCHITECTURE.md"])
node_technology_chooser = partial(basic_node, prompt_key="technology_chooser", write_file="TECHNOLOGY.md", read_files=[
                                  "TASK.md", "ARCHITECTURE.md", "TECHNOLOGY.md"])


def route_after_linter(state: LinterState) -> Literal["node_code_review", "__end__"]:
    return "node_code_review" if state["linter_pass"] else "__end__"


class RouterOutput(BaseModel):
    mode: Literal[
        "define_task",
        "architecture_planning",
        "technology_chooser",
        "implement_code",
        "code_review",
        "docker_manager"
    ]

    model_config = {
        "extra": "forbid"  # THIS FIXES THE ERROR
    }


router_llm = llm.with_structured_output(RouterOutput)


def node_router(state: MessagesState) -> State:
    content = state["messages"][-1]

    result = router_llm.invoke([
        SystemMessage(SYSTEM_PROMPTS["router"]),
        content
    ])

    return {
        "messages": [content],
        "mode": result.mode
    }


VALID_NODES = {
    "define_task",
    "architecture_planning",
    "technology_chooser",
    "implement_code",
    "code_review",
    "docker_manager"
}


def edge_router(state: State) -> Literal[
    "define_task",
    "architecture_planning",
    "technology_chooser",
    "implement_code",
    "code_review",
    "docker_manager",
    "__end__"
]:
    mode = state.get("mode")

    if mode not in VALID_NODES:
        return "__end__"

    return mode

_initalized_threads: set[str] = set()

def node_init(state: State, config: RunnableConfig) -> Literal["node_router"]:
    thread_id = config["configurable"]["thread_id"]

    if thread_id not in _initalized_threads:
        ingest_all(thread_id)
        _initalized_threads.add(thread_id)

    return state


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
    .add_node("node_linter", node_linter)
    .add_edge("__start__", "node_linter")
    .add_conditional_edges("node_linter", route_after_linter)
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
    .add_node("node_init", node_init)
    .add_node("node_router", node_router)
    .add_node("define_task", task_graph)
    .add_node("architecture_planning", arch_graph)
    .add_node("technology_chooser", tech_graph)
    .add_node("implement_code", impl_graph)
    .add_node("code_review", code_graph)
    .add_node("docker_manager", dock_graph)
    .add_edge("node_init", "node_router")
    .add_edge("__start__", "node_init")
    .add_conditional_edges("node_router", edge_router)
    .compile()
)
