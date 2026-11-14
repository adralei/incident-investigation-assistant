
import json
from pathlib import Path

from incident_assistant.data.inspect_logs import parse_timestamp


from incident_assistant.core.paths import PROJECT_ROOT

STATUS_FILE = PROJECT_ROOT / "data" / "status_snapshots.jsonl"
DEPLOYMENT_FILE = PROJECT_ROOT / "data" / "deployments.jsonl"


def read_records(
    file_path: Path,
    service: str,
    start_time: str,
    end_time: str,
) -> list[dict]:
    """Servis ve zaman aralığına göre kayıtları filtreler."""

    start = parse_timestamp(start_time)
    end = parse_timestamp(end_time)

    results = []

    with file_path.open("r", encoding="utf-8") as file:

        for line in file:
            if not line.strip():
                continue

            record = json.loads(line)
            record_time = parse_timestamp(record["timestamp"])

            if (
                record["service"] == service
                and start <= record_time < end
            ):
                results.append(record)

    results.sort(
        key=lambda record: parse_timestamp(record["timestamp"])
    )

    return results


if __name__ == "__main__":

    service = "checkout-api"
    start_time = "2026-10-20T09:00:00Z"
    end_time = "2026-10-20T09:15:00Z"

    statuses = read_records(
        STATUS_FILE, service, start_time, end_time
    )

    deployments = read_records(
        DEPLOYMENT_FILE, service, start_time, end_time
    )

    print(f"Service: {service}")

    print("\n--- SERVICE STATUS ---")
    print(f"Snapshots found: {len(statuses)}")

    for status in statuses:
        print(
            f"[{status['snapshot_id']}] "
            f"{status['timestamp']} | "
            f"{status['state']} | "
            f"Ready: {status['ready_replicas']}/"
            f"{status['desired_replicas']}"
        )

    print("\n--- DEPLOYMENTS ---")
    print(f"Deployments found: {len(deployments)}")

    for deployment in deployments:
        print(
            f"[{deployment['deployment_id']}] "
            f"{deployment['timestamp']} | "
            f"{deployment['version']} | "
            f"{deployment['status']}"
        )
