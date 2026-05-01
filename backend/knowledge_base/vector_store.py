"""
FAISS Vector Store
Embeds mortgage knowledge-base documents using sentence-transformers
and builds a FAISS index for RAG retrieval.
"""

import os
import pickle

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from knowledge_base.documents import (
    ESCROW_HOW_IT_WORKS,
    ESCROW_SHORTAGE,
    INSURANCE_PREMIUM_INCREASE,
    PAYMENT_INCREASE_OVERVIEW,
    PROPERTY_TAX_INCREASE,
)

# ── Config ─────────────────────────────────────────────────────────────────────
EMBED_MODEL   = "all-MiniLM-L6-v2"
CHUNK_SIZE    = 400   # characters per chunk
CHUNK_OVERLAP = 80
INDEX_PATH    = os.path.join(os.path.dirname(__file__), "faiss_index.bin")
META_PATH     = os.path.join(os.path.dirname(__file__), "faiss_meta.pkl")

RAW_DOCS = {
    "Escrow Shortage Explanation":    ESCROW_SHORTAGE,
    "Property Tax Increase Rules":    PROPERTY_TAX_INCREASE,
    "Insurance Premium Adjustments":  INSURANCE_PREMIUM_INCREASE,
    "How Escrow Works":               ESCROW_HOW_IT_WORKS,
    "Why Mortgage Payment Increases": PAYMENT_INCREASE_OVERVIEW,
}

# ── Singletons ─────────────────────────────────────────────────────────────────
_embedder: SentenceTransformer | None = None
_index:    faiss.IndexFlatIP   | None = None
_metadata: list[dict]          | None = None


def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL)
    return _embedder


def _chunk(text: str, source: str) -> list[dict]:
    chunks, start = [], 0
    while start < len(text):
        chunk = text[start : start + CHUNK_SIZE].strip()
        if chunk:
            chunks.append({"text": chunk, "source": source})
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def build_index(force: bool = False) -> None:
    """Embed all documents and persist a FAISS index to disk."""
    global _index, _metadata

    if not force and os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
        _load_index()
        return

    print("  Building FAISS index …")
    embedder   = _get_embedder()
    all_chunks = [c for src, txt in RAW_DOCS.items() for c in _chunk(txt, src)]
    texts      = [c["text"] for c in all_chunks]

    vecs = embedder.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    vecs = np.array(vecs, dtype="float32")

    index = faiss.IndexFlatIP(vecs.shape[1])
    index.add(vecs)

    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "wb") as f:
        pickle.dump(all_chunks, f)

    _index, _metadata = index, all_chunks
    print(f"  → {len(all_chunks)} chunks indexed across {len(RAW_DOCS)} documents.")


def _load_index() -> None:
    global _index, _metadata
    _index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "rb") as f:
        _metadata = pickle.load(f)


def retrieve(query: str, top_k: int = 4) -> list[dict]:
    """Return top-k relevant chunks for the query."""
    global _index, _metadata
    if _index is None:
        build_index()

    embedder = _get_embedder()
    q_vec    = np.array(
        embedder.encode([query], normalize_embeddings=True), dtype="float32"
    )
    scores, indices = _index.search(q_vec, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx != -1:
            results.append({**_metadata[idx], "score": float(score)})
    return results
