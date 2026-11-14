from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
RUNBOOK_DIR = PROJECT_ROOT / "runbooks"
EVALS_DIR = PROJECT_ROOT / "evals"
RESULTS_DIR = EVALS_DIR / "results"
ENV_FILE = PROJECT_ROOT / ".env"
CLAIM_CASES_FILE = EVALS_DIR / "claim_cases.json"
BENCHMARK_FILE = EVALS_DIR / "benchmark_runs.json"
