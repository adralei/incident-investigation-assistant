
from incident_assistant.retrieval.runbook_search import search_runbooks
from incident_assistant.retrieval.semantic_search import semantic_search


# Bu beklentileri arama algoritması değil,
# incelemeyi yapan geliştirici belirliyor.
EXPECTED_SECTIONS = {
    "Initial Investigation",
    "Deployment Correlation",
}

TEST_QUERIES = [
    {
        "name": "Turkish query",
        "query": (
            "Yeni sürümü yayınladıktan sonra "
            "API istekleri başarısız olmaya başladı."
        ),
    },
    {
        "name": "English query",
        "query": "HTTP 500 errors started after a deployment.",
    },
]


def evaluate_results(results: list[dict]) -> float:
    """İlk sonuçlarda beklenen bölümlerin oranını hesaplar."""

    found_titles = {
        item["title"]
        for item in results
    }

    matched = EXPECTED_SECTIONS & found_titles

    return len(matched) / len(EXPECTED_SECTIONS)


def print_results(results: list[dict], method: str) -> None:
    print(f"\n{method}")

    for index, item in enumerate(results, start=1):
        print(f"{index}. {item['title']}")

    recall = evaluate_results(results)

    print(f"Recall@3: {recall:.2f}")


if __name__ == "__main__":

    for case in TEST_QUERIES:

        print("\n" + "=" * 50)
        print(case["name"])
        print("Query:", case["query"])

        keyword_results = search_runbooks(
            case["query"],
            top_k=3,
        )

        print_results(keyword_results, "KEYWORD SEARCH")

        semantic_output = semantic_search(
            case["query"],
            top_k=3,
        )

        print_results(
            semantic_output["results"],
            "SEMANTIC SEARCH",
        )

        print(
            "Embedding tokens:",
            semantic_output["embedding_tokens"],
        )
