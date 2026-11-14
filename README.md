# Incident Investigation Assistant

A read-only, evidence-grounded assistant for investigating synthetic DevOps incidents. It inspects local application logs, service snapshots, deployment records, and runbooks, then produces findings and recommended checks. It does not restart services, roll back deployments, mutate Kubernetes resources, or perform other remediation.

The project distinguishes recorded observations from model-generated hypotheses and recommendations. A source citation establishes provenance, not factual support by itself; claims must still be checked against the cited evidence. Temporal sequence alone does not establish deployment causation.

## Investigation workflows

### Single agent

`agent.py` is the current single-agent workflow. It dispatches read-only operational and runbook tools, creates a structured incident report, validates its evidence references, and saves the report.

`agent_rag_v1.py` is an earlier single-agent RAG version and remains available for comparison. It is not replaced by the structured workflow.

### Multi-agent

`multi_agent.py` delegates runbook research to the Runbook Specialist. The specialist receives task-specific context and is restricted to the `search_runbooks` tool. Its cited recommendations are returned to the main agent; the main agent remains responsible for the final structured report. The restriction is enforced in both the model tool configuration and Python dispatch.

Both workflows are demonstrations with fixed prompts, not interactive production CLIs. Their inputs and retrieved content are untrusted data and cannot grant tools additional permissions.

## Data and retrieval

Operational tools read the synthetic records in `data/`. The retrieval pipeline supports keyword search, embedding-based semantic search, and hybrid search using Reciprocal Rank Fusion. Runbook source IDs include filenames and line ranges, for example `http-500.md:L10-L17`. Keep the Markdown runbooks' line structure unchanged when source IDs are used in reports or evaluation cases.

Runbook instructions are reference material, not agent instructions. Retrieved operational records remain distinct from runbook recommendations, and the specialist has no operational mutation tools.

## Evidence, reports, and evaluation

Evidence validation checks registered source IDs and source types for report fields. It does not treat the existence of a citation as proof that a claim is true. The report schema keeps observed findings, hypotheses, missing information, and recommended checks distinct.

Reports are stored at the existing paths:

- `evals/results/single_agent.json`
- `evals/results/multi_agent.json`

The results directory is created when a report is saved and is ignored by Git. Existing historical benchmark inputs under `evals/` are not modified by the workflows.

Available evaluation and analysis scripts include:

- `evaluate_retrieval.py`: Recall@3 over a small set of expected runbook sections and example English/Turkish queries. Semantic retrieval uses the embeddings API.
- `review_claims.py` and `evidence_support.py`: local claim-case and evidence inspection.
- `evaluate_claims.py`: asks an LLM to label predefined claims as `supported`, `contradicted`, or `insufficient_evidence`; this makes API calls and may incur costs.
- `compare_reports.py`: compares citation coverage for saved reports. Coverage is not a measure of semantic correctness.
- `compare_architectures.py`: compares saved benchmark measurements, including token and timing data. Historical single-run comparisons are not statistically significant performance conclusions.
- `metrics.py`: reports the project's token and execution-time measurements.

The claim cases and retrieval examples are illustrative, not comprehensive benchmarks. LLM judgments are evaluation outputs, not ground truth. These tools do not establish incident-wide error rates or causation from a handful of synthetic records.

## Project layout

```text
.
├── data/                         Synthetic operational records
├── evals/                        Claim cases and historical benchmark inputs
├── runbooks/                     Reference runbooks
├── src/
│   ├── incident_assistant/
│   │   ├── agents/               Single-agent and delegated workflows
│   │   ├── contracts/            Tool, report, and delegation models
│   │   ├── core/                 Shared paths and metrics
│   │   ├── data/                 Read-only record readers
│   │   ├── evaluation/           Claim, retrieval, and report comparisons
│   │   ├── evidence/             Source validation and claim support
│   │   ├── reports/              Report persistence
│   │   ├── retrieval/            Keyword, semantic, and hybrid search
│   │   └── tools/                Read-only investigation tools and dispatch
│   └── *.py                      Compatibility launchers for existing commands
└── tests/                        unittest suite
```

The installable `incident_assistant` package uses absolute imports. Shared path configuration resolves resources from the repository root; the `data/`, `runbooks/`, `evals/`, and `.env` locations remain unchanged.

## Setup

Python 3.10 or newer is required. From the repository root, in Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
Copy-Item .env.example .env
```

Set `OPENAI_API_KEY`, `OPENAI_MODEL`, and `EMBEDDING_MODEL` in `.env` for workflows that call OpenAI. Keep real credentials out of version control. The local review tools and unit tests do not require API calls.

## Run workflows

Compatibility launchers preserve the existing script paths. Run commands from the repository root:

```powershell
python src/agent.py
python src/agent_rag_v1.py
python src/multi_agent.py
python src/runbook_specialist.py
```

Additional utilities:

```powershell
python src/evaluate_retrieval.py
python src/review_claims.py
python src/evidence_support.py
python src/evaluate_claims.py
python src/compare_reports.py
python src/compare_architectures.py
python src/metrics.py
```

Retrieval evaluation and claim evaluation use OpenAI APIs and may incur costs. Other commands that read or compare local data do not require an API unless their implementation invokes one.

## Tests

Run the unit tests from the repository root:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

The unit tests use the standard-library `unittest` framework and do not run API-backed demonstrations or evaluations.

## Limitations

The data, runbooks, query set, and claim cases are small synthetic examples. Results should not be treated as production incident conclusions. In particular, temporal correlation does not prove causation, citation coverage does not prove factual accuracy, and the architecture comparison does not support general performance claims.
