from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import MessagesState

from src.prompts import SYSTEM_PROMPTS
from src.helpers import read_file, save_file
from src.config import llm
from src.states import State
from src.rag import format_context, ingest_markdown, retrieve, save_snapshot


def basic_node(state: State, config: RunnableConfig,  prompt_key: str, read_files: list[str], write_file: str) -> MessagesState:
    content = state["messages"][-1]
    thread_id = config["configurable"]["thread_id"]

    messages = [
        SystemMessage(SYSTEM_PROMPTS[prompt_key]),
        content
    ]

    rag_data = retrieve(content.content, thread_id)
    if rag_data:
        messages.append(HumanMessage(format_context(rag_data)))
    save_snapshot(thread_id, ".snapshots/temp.txt")

    response = llm.invoke(messages)
    content = response.content.strip().strip(
        "```").strip("markdown").strip("\n")

    save_file(write_file, content, thread_id)
    ingest_markdown(write_file, content, thread_id)

    return {"messages": [response]}
