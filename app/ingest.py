"""Reusable ingestion helpers for PDFs: extract, chunk, embed, upsert to Chroma."""
from pathlib import Path
from typing import List
from .vectorstore import ChromaClientWrapper
from .llm import get_embeddings
import tempfile
import os
import requests


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    chunks = []
    if not text:
        return chunks
    start = 0
    L = len(text)
    while start < L:
        end = min(L, start + chunk_size)
        chunks.append(text[start:end])
        if end >= L:
            break
        start = end - overlap
        if start >= end: # safety check
            start = end
    return chunks


def ingest_pdf_file(pdf_path: Path, persist_directory: str = "./chroma_db", source_name: str = None) -> int:
    display_name = source_name or pdf_path.name
    print(f"Starting ingestion for {display_name} (local: {pdf_path})")
    # extract text using pdftomd.py's helper
    import importlib.util
    spec = importlib.util.spec_from_file_location("pdftomd", Path("pdftomd.py"))
    pdftomd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pdftomd)

    print(f"Extracting text from {pdf_path}...")
    pages = pdftomd.extract_pdf_text(pdf_path)
    full_text = "\n\n".join(pages)
    print(f"Extracted {len(pages)} pages. Splitting into chunks...")
    chunks = chunk_text(full_text)
    print(f"Created {len(chunks)} chunks. Generating embeddings...")

    embeddings = get_embeddings(chunks)
    print(f"Generated embeddings for {len(chunks)} chunks. Upserting to vector store...")

    docs = []
    for i, (c, emb) in enumerate(zip(chunks, embeddings)):
        docs.append({"id": f"{display_name}-{i}", "text": c, "metadata": {"source": display_name, "chunk": i}})

    db = ChromaClientWrapper(persist_directory=persist_directory)
    db.upsert_documents(docs, embeddings=embeddings)
    print(f"Successfully upserted {len(docs)} chunks.")
    return len(docs)


def ingest_pdf_from_url(url: str, persist_directory: str = "./chroma_db") -> int:
    # download to temp file
    # support file:// URLs or local absolute paths
    if url.startswith("file://"):
        local = url[len("file://"):]
        # normalize leading slash on Windows file:// (e.g. file:///C:/...)
        if local.startswith('/') and len(local) > 2 and local[2] == ':':
            local = local[1:]
        local_path = Path(local)
        return ingest_pdf_file(local_path, persist_directory=persist_directory)

    # Windows absolute path (e.g. C:\... or D:/...)
    if Path(url).exists():
        return ingest_pdf_file(Path(url), persist_directory=persist_directory)

    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()
    suffix = ".pdf" if url.lower().endswith('.pdf') else ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        for chunk in resp.iter_content(8192):
            tmp.write(chunk)
        tmp_path = Path(tmp.name)

    try:
        count = ingest_pdf_file(tmp_path, persist_directory=persist_directory)
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
    return count
