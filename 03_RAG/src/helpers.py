import os

BASE_PATH = "projects"
CODE_SUBPATH = "code"
MARKDOWN_SUBPATH = "markdown"


def _thread_folder(thread_id: str) -> str:
    return os.path.join(BASE_PATH, thread_id)


def _markdown_folder(thread_id: str) -> str:
    return os.path.join(_thread_folder(thread_id), MARKDOWN_SUBPATH)


def _code_folder(thread_id: str) -> str:
    return os.path.join(_thread_folder(thread_id), CODE_SUBPATH)


def read_file(file_name: str, thread_id: str) -> str:
    file_path = os.path.join(_markdown_folder(thread_id), file_name)
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            file_content = f.read()
            return file_content
    else:
        raise RuntimeError("File cannot be read")


def save_file(file_name: str, content: str, thread_id: str):
    directory = _markdown_folder(thread_id)
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, file_name)
    with open(file_path, "w") as f:
        f.write(content)


def collect_code_files(thread_id: str) -> dict:
    code_dir = _code_folder(thread_id)
    if not os.path.exists(code_dir):
        return {}
    files_in_code = {}
    allowed_ext = ('.py', '.js', '.html', '.css', '.md')
    for root, dirs, files in os.walk(code_dir):
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
