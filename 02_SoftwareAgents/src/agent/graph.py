"""LangGraph single-node graph template.

Returns a predefined response. Replace logic and configuration as needed.
"""

from __future__ import annotations
import atexit
import tempfile
from typing import Literal

import os

from langchain_core.runnables import RunnableConfig

from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional

from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage, AIMessage
from langgraph.runtime import Runtime
from openai import BaseModel
from typing_extensions import TypedDict
from pathlib import Path

from functools import partial
import json
import re
import subprocess

# from src.agent.prompts import SYSTEM_PROMPTS

SYSTEM_PROMPTS = {
    "define_task": """
You are a software engineer assistant. Your sole goal is to define a clear, actionable task definition based on the user's input.

## Input
- App idea or problem description (required)
- Conversation summary (optional — ignore if unrelated to software engineering)

## Output Format
Respond in raw Markdown with exactly these two sections:

# Problem Statement
A concise description of the core problem being solved.

# Objectives
A bullet list of clear, measurable outcomes the solution must achieve.

## Rules
- Be concise and specific
- No technologies, testing, planning, requirements, challenges, or examples
- Focus only on WHAT needs to be solved, not HOW
""",
    "system_architecture": """
You are a software engineer assistant. Your goal is to define a lean, appropriate system architecture based on the provided task definition.

## Input
- Defined task (required — if missing, ask the user before proceeding)

## Core Principle
**Match complexity to the problem.** Do not over-engineer.
- Static content → plain HTML/CSS
- Simple interactivity → vanilla JavaScript
- Simple backend → single server, no queues or brokers
- Only introduce components (frameworks, services, layers) if the task genuinely requires them

## Output Format
Respond in raw Markdown with exactly these sections:

# Description
One paragraph summarizing what the system does.

# UI/UX
Brief description of the user interface and interaction model.

# Modules
List of core modules with a one-line description each.

# Architecture
State the architecture pattern and justify it in one sentence.
Examples: Monolith, Client-Server, REST API, MVC, MVP, Microservices (only if truly needed)

## Rules
- No unnecessary frameworks, cloud services, message brokers, or infrastructure
- No technologies unless needed to describe the architecture pattern
- No testing, deployment, mobile, challenges, or examples
- Keep it brief — no diagrams
""",
    "technology_chooser": """
You are a software engineer assistant. Your goal is to select the simplest, most appropriate tech stack for the given task and architecture.

## Input
- Defined task (required)
- System architecture (required)
- If either is missing, ask the user before proceeding

## Core Principle
**Use the least powerful tool that gets the job done.**
- No frameworks if plain HTML/CSS/JS works
- No ORM if raw SQL is sufficient
- No cloud services if a local server is enough

## Output Format
Respond in raw Markdown with exactly this structure:

# Tech Stack

- **[Technology]** — [purpose, max 5 words]

Example:
- **HTML/CSS** — structure and styling
- **SQLite** — local data storage
- **Flask** — lightweight backend server

## Rules
- One choice per concern — no alternatives, no "or"
- No descriptions beyond purpose
- No testing, deployment, mobile, or implementation details
- Justify nothing — just list
""",
    "implementation_create": """
You are a software engineer. Your goal is to implement the full solution based on the provided inputs.
## Input (all required — if any missing, ask before proceeding)
- Task definition
- System architecture
- Tech stack
## Rules
- Implement every file needed to run the solution completely
- Follow the provided tech stack exactly — do not introduce new technologies
- Do not infer or assume technologies not listed in the tech stack
- No placeholders, no TODOs, no omissions — write complete, working code
- Escape all special characters properly in JSON strings
- Organize all files into 'backend/' and 'frontend/' folders as appropriate
- Use folder prefixes in filenames (e.g., "backend/app.py", "frontend/index.html")
## Required Files
- All source files needed to run the solution
- **README.md** — must include: project description, architecture summary, tech stack, and how to run
## Output
Return ONLY a valid JSON array, no explanation, no markdown fences:
[
  { "filename": "<folder/filename>", "content": "<full file content>" }
]
""",
    "implementation_update": """
You are a software engineer. Your goal is to extend or modify an existing codebase based on the provided task.
## Input
- Task definition (what to add or change)
- Existing source files
## Rules
- Only modify or add files that are strictly necessary for the task
- Preserve all existing logic and structure unless the task explicitly requires changes
- Follow the tech stack already present in the codebase — do not introduce new technologies
- No placeholders, no TODOs, no omissions — write complete, working code
- Escape all special characters properly in JSON strings
- Keep the same folder structure already used in the project
## Output
Return ONLY a valid JSON array of created or modified files, no explanation, no markdown fences:
[
  { "filename": "<folder/filename>", "content": "<full file content>" }
]
""",
    "code_review": """
You are a software engineer assistant. Your goal is to verify the implementation is correct, complete, and consistent.

## Input (all required — if any missing, ask before proceeding)
- All source files
- README.md

## Review Checklist
1. **Correctness** — will the code run without errors?
2. **Consistency** — does the code match the architecture and tech stack?
3. **Completeness** — are all files referenced in README.md present and implemented?
4. **README accuracy** — do the setup and run instructions actually work with the provided code?

## Output Format
Respond in raw Markdown with exactly these sections:

# Code Review

## Summary
One paragraph overall assessment.

## Issues
- **[filename]** — description of the problem

## Verdict
`PASS` or `FAIL` — one sentence reason.

## Rules
- Be specific — reference exact filenames and line issues when possible
- No suggestions for new features or improvements
- No testing, deployment, or mobile concerns
- If no issues found, say so explicitly
""",
    "docker": """
You are a software engineer assistant. Your goal is to create all Docker-related files needed to containerize the provided application.

## Input (all required — if any missing, ask before proceeding)
- Source files
- README.md

## Required Files
- **Dockerfile** — builds and runs the application
- **docker-compose.yml** — if the app has more than one service, otherwise omit
- **.dockerignore** — excludes unnecessary files from the build

## Rules
- Base images must match the tech stack exactly
- No unnecessary layers or dependencies
- App must be runnable with a single `docker compose up` or `docker run` command
- Follow instructions from README.md for how the app is started

## Output
Return ONLY a valid JSON array, no explanation, no markdown fences:
[
  { "filename": "Dockerfile", "content": "<full content>" },
  { "filename": ".dockerignore", "content": "<full content>" }
]
""",
    "router": """
You are a router for a software engineering agent.

## Task
Classify the user's intent and return a JSON object.

## Output format (STRICT)
{
  "mode": "<node_key>"
}

## Nodes
- "define_task"
- "architecture_planning"
- "technology_chooser"
- "implement_code"
- "code_review"
- "docker_manager"

## Rules
- Return ONLY valid JSON
- No explanations
- If unclear, use "define_task"
"""
}

llm = ChatOpenAI(model="gpt-4o")


def read_file(file_name: str, thread_id: str) -> str:
    file_name = f"static/{thread_id}/markdown/{file_name}"
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            file_content = f.read()
            return file_content
    else:
        raise RuntimeError("File cannot be read")


def save_file(file_name: str, content: str, thread_id: str):
    directory = f"static/{thread_id}/markdown/"
    os.makedirs(directory, exist_ok=True)
    file_name = os.path.join(directory, file_name)
    with open(file_name, "w") as f:
        f.write(content)


def collect_code_files(thread_id: str) -> dict:
    if not os.path.exists(f"static/{thread_id}/code/"):
        return {}
    files_in_code = {}
    allowed_ext = ('.py', '.js', '.html', '.css', '.md')
    for root, dirs, files in os.walk(f"static/{thread_id}/code/"):
        dirs[:] = [d for d in dirs if d not in (
            "__pycache__", "node_modules", ".git", ".venv", "venv")]
        for file in files:
            if not file.endswith(allowed_ext):
                continue
            if file == "graph.py":
                continue
            if file.endswith('.db'):
                continue
            if file.endswith('.txt'):
                continue
            filepath = os.path.join(root, file)
            with open(filepath, "r") as f:
                content = f.read()
                files_in_code[filepath] = content
    return files_in_code

# for input and output, MessageState


@dataclass
class State(MessagesState):
    mode: Literal["define_task", "architecture_planning",
                  "technology_chooser", "implement_code", "code_review", "docker_manager"]


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

    save_file(write_file, response.content.strip().strip(
        "```").strip("markdown").strip("\n"), thread_id)

    return {"messages": [response]}


node_define_task = partial(
    basic_node, prompt_key="define_task", write_file="TASK.md", read_files=["TASK.md"])
node_system_architecture = partial(basic_node, prompt_key="system_architecture",
                                   write_file="ARCHITECTURE.md", read_files=["TASK.md", "ARCHITECTURE.md"])
node_technology_chooser = partial(basic_node, prompt_key="technology_chooser", write_file="TECHNOLOGY.md", read_files=[
                                  "TASK.md", "ARCHITECTURE.md", "TECHNOLOGY.md"])


class LinterState(MessagesState):
    linter_output: str
    linter_pass: bool


_stylelint_cfg = tempfile.NamedTemporaryFile(
    mode="w", suffix=".json", delete=False
)
json.dump({"rules": {"block-no-empty": True}}, _stylelint_cfg)
_stylelint_cfg.close()
atexit.register(os.unlink, _stylelint_cfg.name)

_eslint_cfg = tempfile.NamedTemporaryFile(
    mode="w", suffix=".mjs", delete=False
)
_eslint_cfg.write(
    'export default [{ languageOptions: { globals: { document: true, window: true, fetch: true, localStorage: true, alert: true, console: true } }, rules: { "no-undef": "error", "no-unused-vars": "off" } }];'
)
_eslint_cfg.close()
atexit.register(os.unlink, _eslint_cfg.name)

LINTER_CMDS = {
    ".py":   ["ruff", "check", "--output-format=concise", "--ignore=D,I001,F401,T201"],
    ".js":   ["npx", "--yes", "eslint", "--no-ignore", "--config", _eslint_cfg.name],
    ".css":  ["npx", "--yes", "stylelint", "--config", _stylelint_cfg.name],
    ".html": ["npx", "--yes", "htmlhint"],
}


def node_linter(state: LinterState, config: RunnableConfig) -> LinterState:
    thread_id = config["configurable"]["thread_id"]
    base_path = f"static/{thread_id}/code/"

    if not os.path.exists(base_path):
        return {"linter_pass": True, "linter_output": "", "messages": []}

    allowed_ext = ('.py', '.js', '.html', '.css')
    all_output = []
    any_failed = False

    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in (
            "__pycache__", "node_modules", ".git")]
        for file in files:
            ext = Path(file).suffix.lower()
            if ext not in allowed_ext or file == "graph.py" or file.endswith('.db'):
                continue

            linter_cmd = LINTER_CMDS.get(ext)
            if not linter_cmd:
                continue

            filepath = os.path.join(root, file)
            try:
                result = subprocess.run(
                    linter_cmd + [filepath],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode != 0:
                    any_failed = True
                    output = (result.stdout + result.stderr).strip()
                    all_output.append(f"[{filepath}]\n{output}")
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                any_failed = True
                all_output.append(f"[{filepath}] linter error: {e}")

    combined = "\n\n".join(all_output)
    return {
        "linter_pass": not any_failed,
        "linter_output": combined,
        "messages": [] if not any_failed else [HumanMessage(f"Linter failed:\n\n{combined}")],
    }


def route_after_linter(state: LinterState) -> Literal["node_code_review", "__end__"]:
    return "node_code_review" if state["linter_pass"] else "__end__"


def node_code_review(state: LinterState, config: RunnableConfig) -> MessagesState:
    content = state["messages"][-1]
    thread_id = config["configurable"]["thread_id"]

    prompt_key = "code_review"
    write_file = "REVIEW.md"

    messages = [
        SystemMessage(SYSTEM_PROMPTS[prompt_key]),
        content
    ]

    files_in_code = collect_code_files(thread_id)

    messages.append(HumanMessage(json.dumps(files_in_code)))

    response = llm.invoke(messages)

    save_file(write_file, response.content.strip().strip(
        "```").strip("markdown").strip("\n"), thread_id)

    return {"messages": [response]}


def node_docker(state: State, config: RunnableConfig):
    content = state["messages"][-1]
    thread_id = config["configurable"]["thread_id"]

    messages = [
        SystemMessage(SYSTEM_PROMPTS["docker"]),
        content
    ]

    files_in_code = collect_code_files(thread_id)

    messages.append(HumanMessage(json.dumps(files_in_code)))

    response = llm.invoke(messages)

    return {
        "messages": [
            response,
            # AIMessage(content=f"Execution result:\n{output}")
        ]
    }


def node_implementation(state: State, config: RunnableConfig):
    content = state["messages"][-1]
    thread_id = config["configurable"]["thread_id"]
    mode = state.get("mode", "create")  # "create" | "update"

    if mode == "update":
        system_prompt = SYSTEM_PROMPTS["implementation_update"]
        messages = [SystemMessage(system_prompt), content]
        files_in_code = collect_code_files(thread_id)
        if files_in_code:
            messages.append(HumanMessage(json.dumps(files_in_code)))
    else:
        system_prompt = SYSTEM_PROMPTS["implementation_create"]
        messages = [SystemMessage(system_prompt), content]
        for filename in ["TASK.md", "ARCHITECTURE.md", "TECHNOLOGY.md"]:
            try:
                messages.append(HumanMessage(read_file(filename, thread_id)))
            except:
                pass

    response = llm.invoke(messages)
    save_file("CODE.md", response.content, thread_id)

    match = re.search(r'\[.*\]', response.content, re.DOTALL)
    raw = match.group(0) if match else response.content
    files = json.loads(raw)

    directory = f"static/{thread_id}/code/"
    for file in files:
        filepath = os.path.join(directory, file["filename"])
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(file["content"])

    return {"messages": [response]}


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

# Prompt do LLMa
# README.md podczas implementacji
# Fix docker
# Lepsze podejście do generowania kodu
# Jak zaczytać 3 duże pliki?

# re.sub(r'^```(?:markdown)?\n?', '', response.content.strip()).rstrip('`').strip()

# FROM CLAUDE:
# Summarize everything for implement node - in seperate node
# use state instead of .md file
# user_input state

# Proposed State:
# class State(TypedDict):
#     user_input: str
#     task: str
#     architecture: str
#     technology: str
#     implementation: str
#     messages: Annotated[list, add_messages]

# this should be implemented, instead of markdown files(?)

# CLAUDE IDEA:
# LLM decides if converstaion has ended
# def converse_task(state: State, config):
#     response = llm.invoke(messages)

#     # ask llm if task is sufficiently defined
#     ready = llm.invoke([
#         SystemMessage("Has the task been clearly and fully defined? Answer only YES or NO"),
#         *state["messages"],
#         AIMessage(response.content)
#     ])

#     return {
#         "messages": [response],
#         "task_ready": ready.content.strip() == "YES"
#     }

# converse_task (full history) → finalize_task (writes task.md, clears history)
# converse_arch (full history) → finalize_arch (writes arch.md, clears history)

# def converse_architecture(state: State, config):
#     messages = [
#         SystemMessage(SYSTEM_PROMPTS["architecture"]),
#         HumanMessage(f"Task definition:\n{state['task']}"),  # clean summary from state
#         *state["messages"]  # only current phase conversation
#     ]
#     response = llm.invoke(messages)
#     return {"messages": [response]}

# def finalize_task(state: State, config):
#     summary = llm.invoke([...])
#     save_file("task.md", summary.content, thread_id)
#     return {
#         "task": summary.content,
#         "messages": []  # clear for next phase
#     }


# LLM Response:
#   → write_file("index.html", ...)
#   → write_file("app.js", ...)
#   → write_file("styles.css", ...)
#   → write_file("server.py", ...)
#   → write_file("db.py", ...)

# Call 1: plan_app()
#   → returns: ["index.html", "app.js", "styles.css", "server.py", "db.py"]
#              + architecture decisions, API routes, tech stack...

# Call 2: write_file() x3  (frontend)
# Call 3: write_file() x2  (backend)

# def build_implementation_prompt(plan, architecture, tech_stack):
#     return f"""
#     You are implementing a full-stack app based on this plan:

#     ## Task
#     {plan}

#     ## Architecture
#     {architecture}

#     ## Technology Stack
#     {tech_stack}

#     Now implement all files using the write_file tool.
#     Ensure frontend and backend are consistent (API routes, data models, etc).
#     """

# response = llm.call(
#     prompt=build_implementation_prompt(plan, arch, tech),
#     tools=[write_file_tool]
# )
# ```

# ---

# ## Your Flow Becomes:
# ```
# plan_task node
#       ↓
# create_arch node
#       ↓
# choose_tech node
#       ↓
# [merge outputs into single prompt]
#       ↓
# implementation node → write_file() x5
