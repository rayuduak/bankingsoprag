"""Ingest PDFs (using existing pdftomd.py) into Chroma with embeddings."""
from pathlib import Path
import argparse
from dotenv import load_dotenv
load_dotenv()
from app.ingest import ingest_pdf_file


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
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
        if start >= end:
            start = end
    return chunks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", "-p", required=True)
    parser.add_argument("--persist", "-d", default="./chroma_db")
    args = parser.parse_args()

    pdf = Path(args.pdf)
    if not pdf.exists():
        print("PDF not found", pdf)
        return 2

    # reuse existing pdftomd.py to extract text
    import importlib.util
    spec = importlib.util.spec_from_file_location("pdftomd", Path("pdftomd.py"))
    pdftomd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pdftomd)

    pages = pdftomd.extract_pdf_text(Path(pdf))
    full_text = "\n\n".join(pages)
    chunks = chunk_text(full_text)

    # Try to get embeddings via Ollama; optional fallback controlled by ENABLE_EMBEDDING_FALLBACK
    count = ingest_pdf_file(pdf, persist_directory=args.persist)
    print(f"Upserted {count} chunks into {args.persist}")


if __name__ == "__main__":
    raise SystemExit(main())
