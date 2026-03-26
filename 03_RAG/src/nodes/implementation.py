import json
import os
import re

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage

from src.prompts import SYSTEM_PROMPTS
from src.helpers import collect_code_files, read_file, save_file
from src.config import llm
from src.states import State


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
