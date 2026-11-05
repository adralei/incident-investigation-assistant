# Incident Investigation Assistant

**An evidence-oriented AI assistant for investigating software incidents using operational data and runbook retrieval.**

This Python project explores how an agent can connect logs, deployment events, service health, and internal runbooks to produce grounded incident reports without treating correlation as proven causation.

## What it does

- Collects evidence through structured tools for **application logs**, **service status**, and **deployments**.
- Retrieves relevant runbook passages with **keyword search**, **semantic embeddings**, and **hybrid ranking (Reciprocal Rank Fusion)**.
- Uses agent tool-calling to organize investigation and generate findings from available records.
- Evaluates retrieval quality with **Recall@3** and compares Turkish and English queries.
- Exercises error contracts and validation through unit tests.
- Includes claim-review evaluation cases to distinguish supported findings from assertions that lack adequate evidence.

## Architecture

```text
Incident question
       |
       v
    AI Agent
       |
       +-- get_logs ----------> Log records
       +-- get_service_status -> Service snapshots
       +-- get_deployments ---> Deployment history
       +-- search_runbooks ---> Keyword + semantic retrieval
                                      |
                                      v
                                Runbook passages
       |
       v
Evidence-based incident report + claim review / evaluations
```

## Example investigation

The included `checkout-api` scenario uses a 15-minute UTC window on **2026-10-20**:

| Time (UTC) | Observation |
| --- | --- |
| 09:02 | Service healthy; ready replicas **3/3** |
| 09:05 | Deployment of **v1.5.1** reported successful |
| 09:07 | `GET /orders` returned **HTTP 500** |
| 09:08 | `POST /checkout` returned **HTTP 500** |
| 09:12 | Service degraded; ready replicas **2/3** |

**Interpretation:** The error spike followed the deployment and coincided with degraded readiness. The timeline supports *temporal correlation*, not definitive proof that the deployment caused the failures.

## Tech stack

`Python` · `OpenAI API` · `RAG` · `Embeddings` · `Keyword search` · `Hybrid search / RRF` · `unittest`

## Repository guide

```text
data/       Synthetic incident records
runbooks/   Operational troubleshooting documents
evals/      Evaluation examples and reference claims
src/        Data tools, retrieval, agent, and evaluation modules
tests/      Unit and contract tests
```

Notable modules include `src/agent.py`, `src/incident_tools.py`, `src/tool_dispatcher.py`, `src/runbook_tool.py`, `src/hybrid_search.py`, `src/evaluate_retrieval.py`, and `src/review_claims.py`.

## Run locally

Requires Python 3.10+. Model-backed and embedding-based features require an OpenAI API key.

```bash
git clone https://github.com/adralei/incident-investigation-assistant.git
cd incident-investigation-assistant
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the relevant dependencies for your selected modules. For the OpenAI-based agent and retrieval experiments:

```bash
python -m pip install openai python-dotenv numpy
```

Set `OPENAI_API_KEY` in your local environment. Run the reference cases from the repository root:

```bash
python src/agent.py
python src/evaluate_retrieval.py
python src/review_claims.py
python -m unittest discover -s tests
```

Some scripts are exploratory entry points rather than a unified CLI; consult their code for expected local inputs.

## Evaluation highlights

In the documented retrieval examples, English keyword and semantic search both reached **Recall@3 = 1.00**; for a Turkish paraphrase, keyword search reached **0.00** and semantic/hybrid search **0.50**. These are results from a **small demo evaluation**, not production performance benchmarks.

## Scope and limitations

- Uses **synthetic, local incident evidence**, not live monitoring or production infrastructure.
- Produces investigative findings and recommendations; **does not execute remediation**.
- Retrieval scores depend on a small set of runbooks, queries, and reference judgments.
- Root-cause hypotheses must remain distinguishable from directly supported observations.

## Why this project matters

It demonstrates AI agent orchestration, tool contracts, RAG evaluation, and evidence discipline in a DevOps incident-response use case.

**Author:** [Ege Bulut Uygur](https://github.com/adralei)
