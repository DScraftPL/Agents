import atexit
import json
import os
from pathlib import Path
import subprocess
import tempfile

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage

from src.prompts import SYSTEM_PROMPTS
from src.helpers import collect_code_files
from src.config import llm
from src.states import LinterState, State

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
