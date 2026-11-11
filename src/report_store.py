
import json
from pathlib import Path

from report_schema import IncidentReport


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "evals" / "results"

ALLOWED_ARCHITECTURES = {
    "single_agent",
    "multi_agent",
}


def save_report(
    report: IncidentReport,
    architecture: str,
    output_dir: Path | None = None,
) -> Path:
    """Doğrulanmış raporu JSON dosyasına kaydeder."""

    if architecture not in ALLOWED_ARCHITECTURES:
        raise ValueError("Unknown architecture")

    # Şema kontrolü.
    validated = IncidentReport.model_validate(
        report.model_dump()
    )

    target_dir = (
        output_dir
        if output_dir is not None
        else DEFAULT_OUTPUT_DIR
    )

    target_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    target_file = target_dir / f"{architecture}.json"

    target_file.write_text(
        json.dumps(
            validated.model_dump(),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return target_file
