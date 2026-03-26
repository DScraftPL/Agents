from dataclasses import dataclass
from typing import Literal

from langgraph.graph import MessagesState

@dataclass
class LinterState(MessagesState):
    linter_output: str
    linter_pass: bool


@dataclass
class State(MessagesState):
    mode: Literal["define_task", "architecture_planning",
                  "technology_chooser", "implement_code", "code_review", "docker_manager"]
