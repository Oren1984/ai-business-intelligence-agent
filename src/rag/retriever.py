# src/rag/retriever.py — NeuroOps Insight Engine
# Keyword-based RAG retriever: loads knowledge base docs and scores them against queries.

from pathlib import Path
import re

KB_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_base"

def _tokenize(text: str):
    return set(re.findall(r"[a-zA-Z0-9_]+", text.lower()))

def load_documents():
    docs = []
    if not KB_DIR.exists():
        return docs

    for file_path in KB_DIR.glob("*"):
        if file_path.is_file() and file_path.suffix.lower() in [".md", ".txt"]:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            docs.append({
                "source": file_path.name,
                "content": content
            })
    return docs

def retrieve_context(query: str, top_k: int = 3):
    query_tokens = _tokenize(query)
    docs = load_documents()
    scored = []

    for doc in docs:
        doc_tokens = _tokenize(doc["content"])
        score = len(query_tokens.intersection(doc_tokens))
        scored.append({
            "source": doc["source"],
            "content": doc["content"],
            "score": score
        })

    scored = sorted(scored, key=lambda x: x["score"], reverse=True)
    top_docs = [doc for doc in scored[:top_k] if doc["score"] > 0]

    if not top_docs:
        top_docs = scored[:1] if scored else []

    context = "\n\n".join(
        [f"[Source: {doc['source']}]\n{doc['content'][:1600]}" for doc in top_docs]
    )

    return {
        "documents": top_docs,
        "context": context
    }
