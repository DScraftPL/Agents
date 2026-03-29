import json
import os
import re

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage

from src.prompts import SYSTEM_PROMPTS
from src.helpers import collect_code_files, read_file, save_file
from src.config import llm
from src.states import State
from src.rag import format_context, retrieve, ingest_code_file, save_snapshot


def node_implementation(state: State, config: RunnableConfig):
    content = state["messages"][-1]
    thread_id = config["configurable"]["thread_id"]
    files_in_code = collect_code_files(thread_id)
    is_update = bool(files_in_code)

    messages = [content]

    if is_update:
        system_prompt = SYSTEM_PROMPTS["implementation_update"]
        rag_query = content.content
        rag_data = retrieve(rag_query, thread_id)

        existing = ""
        for filepath, file_content in files_in_code.items():
            rel_path = filepath.replace(f"projects/{thread_id}/code/", "")
            existing += f"\n### {rel_path}\n```\n{file_content}\n```\n"
        messages.append(HumanMessage(f"## Existing codebase:\n{existing}"))
    else:
        system_prompt = SYSTEM_PROMPTS["implementation_create"]
        rag_data = retrieve(content.content, thread_id, source_type="markdown")

    messages.append(SystemMessage(system_prompt))
    if rag_data:
        messages.append(HumanMessage(format_context(rag_data)))

        file_path = f"projects/{thread_id}/data.txt"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as f:
            f.write(format_context(rag_data))

    response = llm.invoke(messages)
    save_file("CODE.md", response.content, thread_id)

    match = re.search(r'\[.*\]', response.content, re.DOTALL)
    raw = match.group(0) if match else response.content
    files = json.loads(raw)

    directory = f"projects/{thread_id}/code/"
    for file in files:
        filename = file["filename"]

        # Normalize to relative path
        if filename.startswith(directory):
            filename = filename[len(directory):]
        elif filename.startswith("projects/"):
            filename = re.sub(r"^projects/[^/]+/code/", "", filename)

        # Use normalized filename, not file["filename"]
        filepath = os.path.join(directory, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(file["content"])
        ingest_code_file(filepath, file["content"], thread_id)

    save_snapshot(thread_id, f"projects/{thread_id}/snapshot.txt")
    return {"messages": [response]}
