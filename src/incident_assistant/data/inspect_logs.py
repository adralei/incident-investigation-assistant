
import json
from datetime import datetime
from pathlib import Path


# Proje klasörünün içindeki log dosyası
from incident_assistant.core.paths import PROJECT_ROOT
LOG_FILE = PROJECT_ROOT / "data" / "logs.jsonl"


def parse_timestamp(value: str) -> datetime:
    """UTC zaman damgasını datetime nesnesine dönüştürür."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def read_logs(
    service: str,
    start_time: str,
    end_time: str,
) -> list[dict]:
    """Belirli servis ve zaman aralığındaki logları getirir."""

    start = parse_timestamp(start_time)
    end = parse_timestamp(end_time)

    matching_logs = []

    with LOG_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            log = json.loads(line)

            log_time = parse_timestamp(log["timestamp"])

            if (
                log["service"] == service
                and start <= log_time < end
            ):
                matching_logs.append(log)

    return matching_logs


if __name__ == "__main__":

    service = "checkout-api"
    start_time = "2026-10-20T09:00:00Z"
    end_time = "2026-10-20T09:15:00Z"

    logs = read_logs(service, start_time, end_time)

    error_count = sum(
        1 for log in logs if log["status_code"] >= 500
    )

    print(f"Service: {service}")
    print(f"Time range: {start_time} - {end_time}")
    print(f"Total logs: {len(logs)}")
    print(f"HTTP 5xx errors: {error_count}")

    print("\nMatching logs:")

    for log in logs:
        print(
            f"[{log['log_id']}] "
            f"{log['timestamp']} "
            f"HTTP {log['status_code']} "
            f"- {log['message']}"
        )
