import json

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import MessagesState

from src.prompts import SYSTEM_PROMPTS
from src.helpers import collect_code_files, read_file, save_file
from src.config import llm
from src.states import LinterState, State


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
