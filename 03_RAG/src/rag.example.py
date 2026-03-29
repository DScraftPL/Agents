import os
import re
import hashlib

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# ---------------------------------------------------------------------------
# One InMemoryVectorStore per thread, lazily created
# ---------------------------------------------------------------------------

_stores: dict[str, InMemoryVectorStore] = {}

def _embeddings():
    return OpenAIEmbeddings(model="text-embedding-3-small")

def _get_store(thread_id: str) -> InMemoryVectorStore:
    if thread_id not in _stores:
        _stores[thread_id] = InMemoryVectorStore(embedding=_embeddings())
    return _stores[thread_id]

def clear_thread(thread_id: str):
    """Drop RAG memory for a thread (e.g. on reset)."""
    _stores.pop(thread_id, None)


# ---------------------------------------------------------------------------
# Chunking helpers
# ---------------------------------------------------------------------------

def _chunk_markdown(content: str, file_name: str) -> list[Document]:
    chunks, current_heading, current_lines = [], "top", []

    for line in content.splitlines():
        if re.match(r"^#{1,3} ", line):
            if current_lines:
                chunks.append((current_heading, "\n".join(current_lines).strip()))
            current_heading = line.lstrip("#").strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        chunks.append((current_heading, "\n".join(current_lines).strip()))

    return [
        Document(
            page_content=text,
            metadata={"file": file_name, "heading": heading, "source_type": "markdown"},
            id=_chunk_id(file_name, i),
        )
        for i, (heading, text) in enumerate(chunks)
        if text
    ]


def _chunk_code(content: str, file_path: str) -> list[Document]:
    ext = os.path.splitext(file_path)[1]
    language = {".py": "python", ".js": "javascript"}.get(ext, ext.lstrip("."))
    base_meta = {"file": file_path, "source_type": "code", "language": language}

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


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ingest_markdown(file_name: str, content: str, thread_id: str):
    """Call right after save_file(). Safe to call multiple times — upserts by ID."""
    docs = _chunk_markdown(content, file_name)
    if docs:
        _get_store(thread_id).add_documents(documents=docs, ids=[d.id for d in docs])


def ingest_code_file(file_path: str, content: str, thread_id: str):
    """Call right after writing/updating a code file."""
    docs = _chunk_code(content, file_path)
    if docs:
        _get_store(thread_id).add_documents(documents=docs, ids=[d.id for d in docs])


def ingest_all(thread_id: str, markdown_files: dict, code_files: dict):
    """
    Bulk re-hydrate from disk at graph startup.
    markdown_files: {file_name: content}
    code_files:     {file_path: content}  (output of collect_code_files())
    """
    for file_name, content in markdown_files.items():
        ingest_markdown(file_name, content, thread_id)
    for file_path, content in code_files.items():
        ingest_code_file(file_path, content, thread_id)


def retrieve(
    query: str,
    thread_id: str,
    k: int = 5,
    source_type: str | None = None,   # "markdown" | "code" | None
) -> list[Document]:
    """
    Returns LangChain Documents ranked by similarity.
    Pass source_type to restrict to markdown or code chunks.
    """
    store = _get_store(thread_id)

    if source_type:
        return store.similarity_search(
            query, k=k, filter={"source_type": source_type}
        )
    return store.similarity_search(query, k=k)


def format_context(docs: list[Document]) -> str:
    """Format retrieved docs into a prompt-ready string."""
    if not docs:
        return ""
    parts = []
    for doc in docs:
        m = doc.metadata
        label = f"[{m.get('source_type')}] {m.get('file')}"
        if m.get("heading"):
            label += f" › {m['heading']}"
        parts.append(f"### {label}\n{doc.page_content}")
    return "\n\n".join(parts)