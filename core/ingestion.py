"""
Document ingestion: PDF, Markdown, plain text, and web URLs.
Chunks at ~600 tokens (2400 chars) with 100-token (400 char) overlap.
Stores embeddings in ChromaDB and builds/updates a BM25 keyword index.
"""

import os
import pickle
import hashlib
import requests
import time
from pathlib import Path
from typing import Optional

import chromadb
import yaml
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rank_bm25 import BM25Okapi

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = str(DATA_DIR / "chroma_db")
BM25_PATH = str(DATA_DIR / "bm25_index.pkl")

with open(BASE_DIR / "config" / "prompts.yaml") as f:
    _config = yaml.safe_load(f)

EMBEDDING_MODEL = _config["thresholds"]["embedding_model"]
CHUNK_SIZE = _config["thresholds"]["chunk_size_chars"]
CHUNK_OVERLAP = _config["thresholds"]["chunk_overlap_chars"]


import chromadb

CHROMA_CLIENT = chromadb.PersistentClient(path=CHROMA_DIR)

def _get_chroma_collection():
    return CHROMA_CLIENT.get_or_create_collection("rag_documents")

def _get_embeddings(texts: list[str]) -> list[list[float]]:
    """Call Ollama embedding endpoint directly (no extra deps)."""
    from langchain_ollama import OllamaEmbeddings
    model = OllamaEmbeddings(model=EMBEDDING_MODEL)
    return model.embed_documents(texts)


def _load_bm25() -> tuple:
    if os.path.exists(BM25_PATH):
        with open(BM25_PATH, "rb") as f:
            return pickle.load(f)
    return None, []


def _save_bm25(index, chunks: list[dict]):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(BM25_PATH, "wb") as f:
        pickle.dump((index, chunks), f)


def _chunk_text(text: str, source: str) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    raw_chunks = splitter.split_text(text)
    return [
        {
            "id": hashlib.md5(f"{source}:{i}:{c[:40]}".encode()).hexdigest(),
            "text": c,
            "metadata": {"source": source, "chunk_id": i, "char_count": len(c)},
        }
        for i, c in enumerate(raw_chunks)
    ]


def ingest_text(text: str, source_name: str) -> dict:
    """Ingest a raw string into ChromaDB + BM25."""
    chunks = _chunk_text(text, source_name)
    if not chunks:
        return {"status": "error", "message": "No text extracted", "chunks": 0}

    ids = [c["id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    metas = [c["metadata"] for c in chunks]

    collection = _get_chroma_collection()
    existing_ids = set(collection.get(ids=ids)["ids"])
    new = [(i, t, m) for i, t, m in zip(ids, texts, metas) if i not in existing_ids]

    if new:
        new_ids, new_texts, new_metas = zip(*new)
        embeds = _get_embeddings(list(new_texts))
        collection.add(
            ids=list(new_ids),
            embeddings=embeds,
            documents=list(new_texts),
            metadatas=list(new_metas),
        )

    _, existing_chunks = _load_bm25()
    existing_ids_set = {c["id"] for c in existing_chunks}
    fresh = [c for c in chunks if c["id"] not in existing_ids_set]
    all_chunks = existing_chunks + fresh
    tokenized = [c["text"].lower().split() for c in all_chunks]
    new_bm25 = BM25Okapi(tokenized)
    _save_bm25(new_bm25, all_chunks)

    print("Chunks created:", len(chunks))
    print("Collection count:", collection.count())
    return {
        "status": "ok",
        "source": source_name,
        "chunks": len(chunks),
        "new_chunks": len(new) if new else 0,
    }


def ingest_file(filepath: str) -> dict:
    """Ingest a PDF, Markdown, or plain text file."""
    path = Path(filepath)
    suffix = path.suffix.lower()
    source_name = path.name

    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(filepath)
            text = "\n\n".join(
                page.extract_text() or "" for page in reader.pages
            )
        except Exception as e:
            return {"status": "error", "message": f"PDF read error: {e}", "chunks": 0}
    elif suffix in (".md", ".markdown"):
        from markdown import markdown
        from bs4 import BeautifulSoup as BS
        raw = path.read_text(encoding="utf-8", errors="ignore")
        html = markdown(raw)
        text = BS(html, "html.parser").get_text(separator=" ")
    else:
        text = path.read_text(encoding="utf-8", errors="ignore")

    if not text.strip():
        return {"status": "error", "message": "Empty document", "chunks": 0}

    return ingest_text(text, source_name)


def ingest_url(url: str) -> dict:
    """Fetch a web page and ingest its text."""
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "RAGBot/1.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        source_name = url.split("//")[-1].split("/")[0]
        return ingest_text(text, source_name)
    except Exception as e:
        return {"status": "error", "message": f"URL fetch error: {e}", "chunks": 0}


def get_collection_stats() -> dict:
    try:
        collection = _get_chroma_collection()
        count = collection.count()
        _, bm25_chunks = _load_bm25()
        sources = {}
        if bm25_chunks:
            for c in bm25_chunks:
                src = c["metadata"].get("source", "unknown")
                sources[src] = sources.get(src, 0) + 1
        return {
            "total_chunks": count,
            "bm25_chunks": len(bm25_chunks),
            "sources": sources,
        }
    except Exception as e:
        return {"total_chunks": 0, "bm25_chunks": 0, "sources": {}, "error": str(e)}


def clear_all_data():
    """Wipe ChromaDB collection and BM25 index."""
    try:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        client.delete_collection("rag_documents")
    except Exception:
        pass
    if os.path.exists(BM25_PATH):
        os.remove(BM25_PATH)
