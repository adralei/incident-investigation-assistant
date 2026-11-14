
from incident_assistant.retrieval.runbook_search import load_chunks, search_runbooks
from incident_assistant.retrieval.semantic_search import semantic_search


RRF_K = 60


def hybrid_search(query: str, top_k: int = 3) -> dict:
    """Keyword ve semantic sonuçlarını RRF ile birleştirir."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must be non-empty")

    if type(top_k) is not int or top_k < 1:
        raise ValueError("top_k must be a positive integer")

    # Bütün chunk'lar arasında arama yap.
    total_chunks = len(load_chunks())

    if total_chunks == 0:
        return {
            "results": [],
            "embedding_tokens": 0,
        }

    keyword_results = search_runbooks(
        query,
        top_k=total_chunks,
    )

    semantic_output = semantic_search(
        query,
        top_k=total_chunks,
    )

    semantic_results = semantic_output["results"]

    # Kaynak kimlikleri üzerinden ortak puan tablosu.
    scores = {}
    documents = {}

    for rank, item in enumerate(keyword_results, start=1):
        source_id = item["source_id"]

        scores[source_id] = (
            scores.get(source_id, 0) + 1 / (RRF_K + rank)
        )

        documents[source_id] = item

    for rank, item in enumerate(semantic_results, start=1):
        source_id = item["source_id"]

        scores[source_id] = (
            scores.get(source_id, 0) + 1 / (RRF_K + rank)
        )

        documents[source_id] = item

    # RRF puanlarına göre sıralama.
    ranked_ids = sorted(
        scores,
        key=lambda source_id: (
            -scores[source_id],
            source_id,
        ),
    )

    results = []

    for source_id in ranked_ids[:top_k]:
        document = documents[source_id]

        results.append({
            "source_id": source_id,
            "title": document["title"],
            "text": document["text"],
            "rrf_score": scores[source_id],
        })

    return {
        "results": results,
        "embedding_tokens": semantic_output["embedding_tokens"],
    }


if __name__ == "__main__":
    from incident_assistant.evaluation.evaluate_retrieval import evaluate_results

    queries = [
        (
            "Turkish query",
            "Yeni sürümü yayınladıktan sonra "
            "API istekleri başarısız olmaya başladı.",
        ),
        (
            "English query",
            "HTTP 500 errors started after a deployment.",
        ),
    ]

    for name, query in queries:
        print("\n" + "=" * 50)
        print(name)
        print("Query:", query)

        result = hybrid_search(query, top_k=3)

        print("\nHYBRID SEARCH")

        for index, item in enumerate(result["results"], start=1):
            print(
                f"{index}. {item['title']} "
                f"| RRF: {item['rrf_score']:.5f}"
            )
            print("Source:", item["source_id"])

        recall = evaluate_results(result["results"])

        print(f"\nRecall@3: {recall:.2f}")
        print(
            "Embedding tokens:",
            result["embedding_tokens"],
        )
