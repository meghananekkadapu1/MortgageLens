"""
Chain 3 — RAG Retrieval
Runs all queries from the detection chain against FAISS and returns
deduplicated, ranked context chunks for the LLM prompt.
"""

from chains.detection import DetectedCauses
from knowledge_base.vector_store import retrieve


def build_context(causes: DetectedCauses, top_k: int = 3) -> tuple[str, list[str]]:
    """
    Returns:
        context_text  — formatted numbered chunks for the LLM
        sources       — deduplicated list of source document titles
    """
    seen:   set[str] = set()
    chunks: list[dict] = []

    for query in causes.rag_queries:
        for r in retrieve(query, top_k=top_k):
            key = r["text"][:120]
            if key not in seen:
                seen.add(key)
                chunks.append(r)

    chunks.sort(key=lambda x: x["score"], reverse=True)
    top = chunks[:8]

    parts:   list[str] = []
    sources: list[str] = []
    for i, chunk in enumerate(top, 1):
        parts.append(f"[{i}] Source: {chunk['source']}\n{chunk['text']}")
        if chunk["source"] not in sources:
            sources.append(chunk["source"])

    return "\n\n---\n\n".join(parts), sources
