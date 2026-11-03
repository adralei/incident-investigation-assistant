
import math
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from runbook_search import load_chunks, search_runbooks


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "text-embedding-3-small"
)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """İki vektörün kosinüs benzerliğini hesaplar."""

    if len(a) != len(b):
        raise ValueError("Vector dimensions must match")

    dot_product = sum(x * y for x, y in zip(a, b))

    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        raise ValueError("Zero-length vector cannot be compared")

    return dot_product / (norm_a * norm_b)


def semantic_search(query: str, top_k: int = 3) -> dict:
    """Runbook parçalarını anlamsal benzerliğe göre sıralar."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must be non-empty")

    if type(top_k) is not int or top_k < 1:
        raise ValueError("top_k must be a positive integer")

    chunks = load_chunks()

    if not chunks:
        return {
            "results": [],
            "embedding_tokens": 0,
            "duration": 0.0,
        }

    # Her parçanın başlığını da embedding'e dahil ediyoruz.
    chunk_texts = [
        f"{chunk['title']}\n{chunk['text']}"
        for chunk in chunks
    ]

    # Sorgu ve belgeleri tek API isteğinde gönderiyoruz.
    texts = [query] + chunk_texts

    client = OpenAI()
    started = time.perf_counter()

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
        encoding_format="float",
    )

    duration = time.perf_counter() - started

    # API'nin döndürdüğü index ile sıralamayı koruyoruz.
    ordered = sorted(response.data, key=lambda item: item.index)

    vectors = [item.embedding for item in ordered]

    if len(vectors) != len(texts):
        raise RuntimeError("Unexpected embedding response count")

    query_vector = vectors[0]
    chunk_vectors = vectors[1:]

    results = []

    for chunk, vector in zip(chunks, chunk_vectors):
        similarity = cosine_similarity(query_vector, vector)

        results.append({
            "source_id": chunk["source_id"],
            "title": chunk["title"],
            "text": chunk["text"],
            "similarity": similarity,
        })

    results.sort(
        key=lambda item: (
            -item["similarity"],
            item["source_id"],
        )
    )

    return {
        "results": results[:top_k],
        "embedding_tokens": response.usage.total_tokens,
        "duration": duration,
    }


if __name__ == "__main__":

    query = (
        "Yeni sürümü yayınladıktan sonra "
        "API istekleri başarısız olmaya başladı."
    )

    print("QUERY:", query)

    print("\n=== KEYWORD SEARCH ===")

    keyword_results = search_runbooks(query, top_k=3)

    print("Results:", len(keyword_results))

    for item in keyword_results:
        print(
            item["source_id"],
            "| Score:", item["score"]
        )

    print("\n=== SEMANTIC SEARCH ===")

    semantic_result = semantic_search(query, top_k=3)

    print("Results:", len(semantic_result["results"]))

    for item in semantic_result["results"]:
        print(
            item["source_id"],
            "| Similarity:", round(item["similarity"], 4)
        )
        print("Title:", item["title"])

    print("\n=== EMBEDDING METRICS ===")
    print("Model:", EMBEDDING_MODEL)
    print("Tokens:", semantic_result["embedding_tokens"])
    print(
        "Duration (seconds):",
        round(semantic_result["duration"], 2)
    )
