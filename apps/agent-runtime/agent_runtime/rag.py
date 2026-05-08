"""RAG module for arch-assistant — TF-IDF retrieval with jieba tokenization.
Self-contained: builds index on first load, no pickle dependencies."""
import json, os
import jieba
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

INDEX_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "rag_index")
CHUNKS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "rag_chunks", "chunks.json")

# Lazy-load globals
_vectorizer = None
_tfidf_matrix = None
_chunks = None

def _build_index():
    """Build TF-IDF index from chunks on first load."""
    global _vectorizer, _tfidf_matrix, _chunks
    
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        _chunks = json.load(f)
    
    texts = [c["text"] for c in _chunks]
    
    _vectorizer = TfidfVectorizer(
        tokenizer=lambda x: list(jieba.cut(x)),
        max_features=5000,
        ngram_range=(1, 2),
        min_df=1,
    )
    _tfidf_matrix = _vectorizer.fit_transform(texts)

def _ensure_index():
    if _vectorizer is None:
        _build_index()

def retrieve(query: str, top_k: int = 5) -> list[str]:
    """Search RAG index and return top-k relevant text chunks."""
    _ensure_index()
    q_vec = _vectorizer.transform([query])
    scores = cosine_similarity(q_vec, _tfidf_matrix).flatten()
    top_indices = scores.argsort()[-top_k:][::-1]
    
    results = []
    for idx in top_indices:
        if scores[idx] > 0.01:
            results.append(_chunks[idx]["text"])
    return results

def retrieve_context(query: str, max_chars: int = 1500, top_k: int = 5) -> str:
    """Retrieve and format context for LLM prompt."""
    chunks = retrieve(query, top_k)
    if not chunks:
        return ""
    
    context = "【参考资料（来自课程讲义）】\n"
    total = 0
    for i, chunk in enumerate(chunks):
        truncated = chunk[:400]
        context += f"\n--- 参考资料 {i+1} ---\n{truncated}\n"
        total += len(truncated)
        if total > max_chars:
            break
    return context
