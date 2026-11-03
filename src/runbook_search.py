
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNBOOK_DIR = PROJECT_ROOT / "runbooks"


def tokenize(text: str) -> set[str]:
    """Metni küçük harfli, benzersiz kelimelere ayırır."""
    return set(re.findall(r"\w+", text.casefold()))


def load_chunks() -> list[dict]:
    """Markdown belgelerini başlıklarına göre parçalara ayırır."""

    chunks = []

    for file_path in sorted(RUNBOOK_DIR.glob("*.md")):
        lines = file_path.read_text(encoding="utf-8").splitlines()

        current_title = None
        current_lines = []
        start_line = 1

        def save_chunk(end_line: int):
            if not current_lines:
                return

            text = "\n".join(current_lines).strip()

            if not text:
                return

            chunks.append({
                "source_id": (
                    f"{file_path.name}:"
                    f"L{start_line}-L{end_line}"
                ),
                "title": current_title,
                "text": text,
            })

        for line_number, line in enumerate(lines, start=1):
            if line.startswith("## "):
                save_chunk(line_number - 1)

                current_title = line[3:].strip()
                current_lines = [line]
                start_line = line_number
            elif current_title is not None:
                current_lines.append(line)

        save_chunk(len(lines))

    return chunks


def search_runbooks(
    query: str,
    top_k: int = 3,
) -> list[dict]:
    """Sorgudaki kelimelerle eşleşen parçaları getirir."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must be a non-empty string")

    if not isinstance(top_k, int) or isinstance(top_k, bool):
        raise ValueError("top_k must be an integer")

    if top_k < 1:
        raise ValueError("top_k must be positive")

    query_terms = tokenize(query)
    results = []

    for chunk in load_chunks():
        chunk_terms = tokenize(chunk["text"])

        matching_terms = query_terms & chunk_terms
        score = len(matching_terms)

        if score > 0:
            results.append({
                **chunk,
                "score": score,
                "matched_terms": sorted(matching_terms),
            })

    results.sort(
        key=lambda item: (
            -item["score"],
            item["source_id"],
        )
    )

    return results[:top_k]


if __name__ == "__main__":
    query = "HTTP 500 errors after deployment"

    print("Query:", query)

    chunks = load_chunks()
    print("Total chunks:", len(chunks))

    results = search_runbooks(query, top_k=3)

    print("Matching results:", len(results))

    for result in results:
        print("\n--- RESULT ---")
        print("Source:", result["source_id"])
        print("Title:", result["title"])
        print("Score:", result["score"])
        print("Matched:", result["matched_terms"])
        print("Text:")
        print(result["text"])
