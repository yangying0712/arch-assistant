#!/usr/bin/env python3
"""Build TF-IDF index with Chinese word segmentation (jieba)."""
import json, pickle, os
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import save_npz

CHUNKS_FILE = "/mnt/e/workspace/UserRegister/arch-assistant/data/rag_chunks/chunks.json"
INDEX_DIR = "/mnt/e/workspace/UserRegister/arch-assistant/data/rag_index"
os.makedirs(INDEX_DIR, exist_ok=True)

with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

# jieba tokenizer for scikit-learn
def jieba_tokenizer(text):
    return list(jieba.cut(text))

texts = [c["text"] for c in chunks]
print(f"Building jieba+TF-IDF index for {len(texts)} chunks...")

vectorizer = TfidfVectorizer(
    tokenizer=jieba_tokenizer,
    max_features=8000,
    ngram_range=(1, 2),
    min_df=1,
)
tfidf_matrix = vectorizer.fit_transform(texts)

# Save
with open(os.path.join(INDEX_DIR, "vectorizer.pkl"), "wb") as f:
    pickle.dump(vectorizer, f)
with open(os.path.join(INDEX_DIR, "chunks.pkl"), "wb") as f:
    pickle.dump(chunks, f)
save_npz(os.path.join(INDEX_DIR, "tfidf_matrix.npz"), tfidf_matrix)

print(f"Index: {tfidf_matrix.shape[1]} features, {tfidf_matrix.shape[0]} docs")

# Test
from sklearn.metrics.pairwise import cosine_similarity
tests = ["事件驱动架构风格", "管道过滤器数据流", "P2P去中心化对等架构", "MVC模型视图控制器", "软件体系结构评估方法"]
for q in tests:
    q_vec = vectorizer.transform([q])
    scores = cosine_similarity(q_vec, tfidf_matrix).flatten()
    top3 = scores.argsort()[-3:][::-1]
    print(f"\n'{q}':")
    for idx in top3:
        print(f"  [{scores[idx]:.3f}] {chunks[idx]['source']}: {chunks[idx]['text'][:100]}...")
