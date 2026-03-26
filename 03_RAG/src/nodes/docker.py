import json

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage

from src.prompts import SYSTEM_PROMPTS
from src.helpers import collect_code_files
from src.config import llm
from src.states import State


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
        ]
    }
