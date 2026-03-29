import os
import re
import hashlib

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from src.helpers import collect_code_files, _markdown_folder

_stores: dict[str, InMemoryVectorStore] = {}

_SEP = "=" * 72

_META_KEYS = ("id", "file", "source_type", "language", "heading")


def _embeddings():
    return OpenAIEmbeddings(model="text-embedding-3-small")


def _get_store(thread_id: str) -> InMemoryVectorStore:
    if thread_id not in _stores:
        _stores[thread_id] = InMemoryVectorStore(embedding=_embeddings())
    return _stores[thread_id]


def clear_thread(thread_id: str):
    _stores.pop(thread_id, None)


def _chunk_markdown(content: str, file_name: str) -> list[Document]:
    chunks, current_heading, current_lines = [], "top", []

    for line in content.splitlines():
        if re.match(r"^#{1,3} ", line):
            if current_lines:
                chunks.append(
                    (current_heading, "\n".join(current_lines).strip()))
            current_heading = line.lstrip("#").strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        chunks.append((current_heading, "\n".join(current_lines).strip()))

    return [
        Document(
            page_content=text,
            metadata={"file": file_name, "heading": heading,
                      "source_type": "markdown"},
            id=_chunk_id(file_name, i),
        )
        for i, (heading, text) in enumerate(chunks)
        if text
    ]


def _chunk_code(content: str, file_path: str) -> list[Document]:
    ext = os.path.splitext(file_path)[1]
    language = {".py": "python", ".js": "javascript"}.get(ext, ext.lstrip("."))
    base_meta = {"file": file_path,
                 "source_type": "code", "language": language}

    if ext not in (".py", ".js"):
        return [Document(
            page_content=content,
            metadata={**base_meta, "heading": os.path.basename(file_path)},
            id=_chunk_id(file_path, 0),
        )]

    pattern = (
        re.compile(r"^(def |class )", re.MULTILINE) if ext == ".py"
        else re.compile(r"^(function |class |const \w+ = (?:async )?\()", re.MULTILINE)
    )

    splits = list(pattern.finditer(content))
    if not splits:
        return [Document(
            page_content=content,
            metadata={**base_meta, "heading": "module"},
            id=_chunk_id(file_path, 0),
        )]

    boundaries = [m.start() for m in splits]
    ranges = list(zip([0] + boundaries, boundaries + [len(content)]))

    docs = []
    for i, (start, end) in enumerate(ranges):
        text = content[start:end].strip()
        if not text:
            continue
        docs.append(Document(
            page_content=text,
            metadata={**base_meta, "heading": text.splitlines()[0][:80]},
            id=_chunk_id(file_path, i),
        ))
    return docs


def _chunk_id(file: str, index: int) -> str:
    return hashlib.md5(f"{file}::{index}".encode()).hexdigest()


def ingest_markdown(file_name: str, content: str, thread_id: str):
    purge_file(file_name, thread_id)
    docs = _chunk_markdown(content, file_name)
    if docs:
        _get_store(thread_id).add_documents(
            documents=docs, ids=[d.id for d in docs])


def ingest_code_file(file_path: str, content: str, thread_id: str):
    prefix = f"projects/{thread_id}/code/"
    relative_path = file_path[len(prefix):] if file_path.startswith(
        prefix) else file_path

    purge_file(file_path, thread_id)
    docs = _chunk_code(content, relative_path)
    if docs:
        _get_store(thread_id).add_documents(
            documents=docs, ids=[d.id for d in docs])


def ingest_all(thread_id: str, markdown_files: dict | None = None, code_files: dict | None = None):
    if markdown_files is None:
        markdown_files = {}
        md_folder = _markdown_folder(thread_id)
        if os.path.exists(md_folder):
            for file_name in os.listdir(md_folder):
                if file_name.endswith(".md"):
                    file_path = os.path.join(md_folder, file_name)
                    with open(file_path, "r") as f:
                        markdown_files[file_name] = f.read()

    if code_files is None:
        code_files = collect_code_files(thread_id)

    for file_name, content in markdown_files.items():
        ingest_markdown(file_name, content, thread_id)
    for file_path, content in code_files.items():
        ingest_code_file(file_path, content, thread_id)


def retrieve(
    query: str,
    thread_id: str,
    k: int = 5,
    source_type: str | None = None,
) -> list[Document]:
    store = _get_store(thread_id)

    if source_type:
        return store.similarity_search(
            query, k=k, filter=lambda doc: doc.metadata.get(
                "source_type") == source_type
        )
    return store.similarity_search(query, k=k)


def format_context(docs: list[Document]) -> str:
    if not docs:
        return ""
    parts = []
    for doc in docs:
        m = doc.metadata
        label = f"[{m.get('source_type')}] {m.get('file')}"
        if m.get("heading"):
            label += f" > {m['heading']}"
        parts.append(f"### {label}\n{doc.page_content}")
    return "\n\n".join(parts)


def save_snapshot(thread_id: str, path: str) -> int:
    store = _get_store(thread_id)
    docs: list[Document] = [
        Document(
            page_content=entry["text"],
            metadata=entry["metadata"],
            id=entry["id"],
        )
        for entry in store.store.values()
    ]

    if not docs:
        return 0

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    with open(path, "w", encoding="utf-8") as fh:
        for doc in docs:
            fh.write(_SEP + "\n")
            # -- metadata header --
            for key in _META_KEYS:
                value = doc.metadata.get(key, "")
                if isinstance(value, str):
                    # escape newlines so the header stays single-line
                    value = value.replace("\\", "\\\\").replace("\n", "\\n")
                fh.write(f"{key}: {value}\n")
            # doc.id lives on the object, not in metadata
            fh.write(f"doc_id: {doc.id or ''}\n")
            fh.write("---\n")
            fh.write(doc.page_content)
            fh.write("\n")

    return len(docs)


# def load_snapshot(thread_id: str, path: str) -> int:
#     if not os.path.exists(path):
#         raise FileNotFoundError(f"Snapshot not found: {path}")

#     docs = _parse_snapshot(path)
#     if not docs:
#         return 0

#     store = _get_store(thread_id)
#     store.add_documents(documents=docs, ids=[d.id for d in docs if d.id])
#     return len(docs)


# def _parse_snapshot(path: str) -> list[Document]:
#     with open(path, encoding="utf-8") as fh:
#         raw = fh.read()

#     chunks = [c for c in raw.split(_SEP) if c.strip()]
#     docs: list[Document] = []

#     for chunk in chunks:
#         if "\n---\n" not in chunk:
#             continue
#         header_part, content = chunk.split("\n---\n", 1)

#         metadata: dict = {}
#         doc_id: str = ""

#         for line in header_part.strip().splitlines():
#             if ": " not in line:
#                 continue
#             key, _, raw_val = line.partition(": ")
#             key = key.strip()
#             # unescape
#             val = raw_val.replace("\\n", "\n").replace("\\\\", "\\")
#             if key == "doc_id":
#                 doc_id = val
#             elif key in _META_KEYS:
#                 metadata[key] = val

#         page_content = content.lstrip("\n").rstrip("\n")
#         if not page_content:
#             continue

#         docs.append(Document(
#             page_content=page_content,
#             metadata=metadata,
#             id=doc_id or None,
#         ))

#     return docs


def snapshot_path(thread_id: str, base_dir: str = ".snapshots") -> str:
    safe = re.sub(r"[^\w\-]", "_", thread_id)
    return os.path.join(base_dir, f"{safe}.txt")


def purge_file(file_path: str, thread_id: str):
    store = _get_store(thread_id)
    stale_ids = [
        entry["id"]
        for entry in store.store.values()
        if entry["metadata"].get("file") == file_path
    ]
    if stale_ids:
        store.delete(ids=stale_ids)
