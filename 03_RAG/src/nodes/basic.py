from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import MessagesState

from src.prompts import SYSTEM_PROMPTS
from src.helpers import read_file, save_file
from src.config import llm
from src.states import State


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
