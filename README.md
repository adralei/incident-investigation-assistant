# Incident Investigation Assistant

**An evidence-oriented, read-only AI incident investigation prototype with RAG, structured reporting, and multi-agent orchestration.**

Built in Python, this project explores how AI agents can examine application logs, service health snapshots, deployment history, and troubleshooting runbooks to prepare source-grounded incident reports. It is designed to distinguish **observed facts**, **hypotheses**, and **recommended investigation steps**—without treating temporal correlation as proof of causation.

## Key capabilities

- **Operational evidence tools:** Read and filter synthetic application logs, service status snapshots, and deployment records by service and UTC time window.
- **Tool calling and dispatch:** OpenAI Responses API function calling, Pydantic-based input/output contracts, error handling, and tool dispatch controls.
- **Runbook RAG:** Keyword search, semantic embeddings, and hybrid retrieval using Reciprocal Rank Fusion (RRF), with source references to Markdown line ranges.
- **Two architectures:** A single-agent investigator and a multi-agent variant with a dedicated **Runbook Specialist Agent**.
- **Controlled delegation:** Structured `DelegationRequest` / `SpecialistResult` contracts; the specialist receives a limited task context rather than the main agent's full conversation.
- **Tool isolation:** A specialist-specific Python allowlist permits only `search_runbooks`, alongside the model-level tool restriction.
- **Structured reports:** Pydantic-backed OpenAI Structured Outputs with findings, hypotheses, missing information, and recommended checks.
- **Evidence checks:** Report schema validation, checks that cited source IDs were actually retrieved and used in the appropriate role, plus field-level fact checks for structured claims.
- **Evaluation and observability:** Retrieval Recall@3 experiments, human-labeled claim-review examples, 22 passing unit tests, and combined model/embedding token and end-to-end timing metrics.

## Architecture

### Single-agent investigator

```text
Incident question
      |
      v
Single Investigation Agent
      |-- get_logs ------------> Application logs
      |-- get_service_status --> Service snapshots
      |-- get_deployments -----> Deployment records
      `-- search_runbooks -----> Keyword + semantic + RRF retrieval
      |
      v
Structured IncidentReport
      |
      v
Schema validation + source reference validation
```

Run the single-agent implementation with `src/agent.py`.

### Multi-agent investigator

```text
Incident question
      |
      v
Main Investigation Agent
      |-- get_logs ------------> Application logs
      |-- get_service_status --> Service snapshots
      |-- get_deployments -----> Deployment records
      |
      `-- delegate_runbook (DelegationRequest)
                 |
                 v
         Runbook Specialist Agent
                 |
                 `-- search_runbooks only
                        |
                        v
                  Runbook passages
                 |
                 v
           SpecialistResult
                 |
                 v
Main Investigation Agent
      |
      v
Structured IncidentReport
      |
      v
Schema + source-reference checks
      |
      v
Combined multi-agent usage metrics
```

The specialist uses its own model calls, instructions, and task-specific context. It returns sourced recommendations; the main agent retains responsibility for the final report. Specialist tool execution is restricted at both the model interface and the Python dispatcher. Both implementations are **read-only**.

## Example incident: `checkout-api`

The bundled synthetic scenario covers **2026-10-20, 09:00–09:15 UTC**.

| Time (UTC) | Recorded observation | Source |
| --- | --- | --- |
| 09:02 | Service `healthy`, ready replicas **3/3** | `svc-001` |
| 09:03 | `GET /orders` completed with **HTTP 200** | `log-002` |
| 09:05 | Deployment **v1.5.1** reported `succeeded` | `dep-001` |
| 09:07 | `GET /orders` returned **HTTP 500** | `log-003` |
| 09:08 | `POST /checkout` returned **HTTP 500** | `log-004` |
| 09:12 | Service `degraded`, ready replicas **2/3** | `svc-002` |

**Interpretation:** The recorded errors followed the deployment, and a later snapshot showed reduced readiness. These observations justify further investigation; they **do not establish the root cause**, nor do a few sample requests establish the incident-wide error rate.

The agent can recommend read-only follow-up checks (such as application errors, readiness probes, rollout history, and dependency health), grounding those recommendations in retrieved runbook passages rather than presenting them as observed incident facts.

## Technology

- **Python 3.10+**, **Pydantic v2**, **unittest**
- **OpenAI Responses API** for tool calling and structured outputs
- **OpenAI Embeddings API** for semantic retrieval
- **RAG:** keyword, semantic, hybrid/RRF ranking
- **python-dotenv** for local environment configuration

## Project layout

```text
data/                        Synthetic logs, status snapshots, deployments
runbooks/                    Markdown incident-response guidance
evals/
  claim_cases.json           Human-labeled claim review examples
src/
  agent.py                   Single-agent investigator
  multi_agent.py             Main + specialist orchestration
  runbook_specialist.py      Independent runbook specialist
  delegation_contract.py     Pydantic handoff contracts
  specialist_dispatcher.py   Specialist-specific tool allowlist
  incident_tools.py          Log and deployment tools
  service_tools.py           Service status tool
  tool_contract.py           Shared tool contracts
  tool_dispatcher.py         Validated tool routing
  runbook_search.py          Keyword retrieval
  semantic_search.py         Embedding retrieval
  hybrid_search.py           RRF hybrid ranking
  runbook_tool.py            Runbook search tool
  report_schema.py           Structured incident report schema
  evidence_validator.py      Source-ID and source-type checks
  evidence_support.py        Structured field-level claim checks
  review_claims.py           Claim review packets
  evaluate_retrieval.py      Retrieval evaluation
  metrics.py                 AgentMetrics and aggregation
tests/
  test_incident_tools.py
  test_evidence_support.py
  test_specialist_dispatcher.py
  test_metrics.py
```

Additional exploratory inspection scripts are in `src/`.

## Run locally

Examples below use **Windows PowerShell** from the repository root.

### 1. Clone and create an environment

```powershell
git clone https://github.com/adralei/incident-investigation-assistant.git
cd incident-investigation-assistant
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install openai python-dotenv pydantic numpy
```

If the repository contains a dependency lockfile or `requirements.txt` in a later version, prefer that for reproducible installs.

### 3. Configure environment

Create a local `.env` file at the project root:

```dotenv
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=your_supported_model
EMBEDDING_MODEL=text-embedding-3-small
```

Choose an OpenAI model available to your account that supports the Responses API, function calling, and structured outputs. Keep `.env` and credentials **out of Git**. API-backed scripts incur token usage; unit tests below do not require API access.

### 4. Run the agents

```powershell
# Single-agent investigation
python src/agent.py

# Standalone specialist demonstration
python src/runbook_specialist.py

# Multi-agent investigation with delegation
python src/multi_agent.py
```

The demonstration entry points currently use a fixed `checkout-api` scenario rather than an interactive production CLI.

### 5. Run evaluations and tests

```powershell
# Retrieval-quality example (uses embeddings)
python src/evaluate_retrieval.py

# Print labeled claims alongside collected evidence (no LLM judge)
python src/review_claims.py

# Structured evidence field checks
python src/evidence_support.py

# Previous metrics example; does not start an agent
python src/metrics.py

# Unit tests (no OpenAI API calls)
python -m unittest discover -s tests -p "test_*.py" -v
```

**Latest verified local test run:** **22/22 passing** (incident tools, evidence support, specialist tool permissions, and metric aggregation).

## Validation and evaluation

| Layer | What it checks | Current scope |
| --- | --- | --- |
| **Schema validation** | Report and handoff structures match Pydantic contracts | Implemented |
| **Reference validation** | Cited IDs were retrieved and have the expected source type | Implemented |
| **Field-level support checks** | A record field matches a structured claim's expected value | Implemented in a separate utility; not a full free-text validator |
| **Claim review dataset** | Claims, evidence records, and preassigned labels are presented for review | 4 illustrative cases; automatic semantic accuracy not measured |
| **Retrieval evaluation** | Recall@3 on a small set of reference runbook sections | Implemented for example Turkish and English queries |
| **Usage metrics** | Input/output tokens, embedding tokens, and end-to-end elapsed time | Captured for the multi-agent run and aggregated automatically |

In the example retrieval exercise, the English query achieved **Recall@3 = 1.00** for keyword and semantic retrieval. For a Turkish paraphrase, keyword retrieval scored **0.00**, while semantic and hybrid retrieval scored **0.50**. These measurements come from a small demo dataset and should not be interpreted as production quality estimates.

A verified multi-agent demo run produced a structured report with **schema validation PASS** and **reference validation PASS**. Its automatically aggregated metrics were **11,461 input tokens**, **3,096 output tokens**, **349 embedding tokens**, and approximately **46.63 seconds** end-to-end. These values describe one run, not a benchmark or pricing estimate. The end-to-end duration already includes the specialist's execution time.

## Safety and limitations

- **Synthetic local evidence only.** No live infrastructure, monitoring integration, or production deployment management.
- **Read-only behavior.** Agents investigate and recommend checks; they do not restart services, roll back deployments, or perform remediation.
- **Correlation is not causation.** Deployment timing and reduced readiness are investigation clues, not proven root causes.
- **Source validity is not full factual correctness.** A valid citation can still fail to support the wording of a free-text claim.
- **Runbooks are untrusted inputs.** Retrieved text is not an authority to override agent instructions or execute actions.
- **Small evaluations.** Passing unit tests and example retrieval/claim cases are not evidence of production reliability or generalization.
- **Architecture trade-offs remain under evaluation.** Single-agent and multi-agent runs are not yet compared through repeated controlled experiments.

## Why this project matters

This project demonstrates **agentic tool orchestration, multi-agent handoffs, least-privilege tool access, RAG, structured outputs, source tracking, and evaluation discipline** in a realistic DevOps investigation workflow. The goal is to build auditable investigation assistance rather than automate unverified operational decisions.

**Author:** [Ege Bulut Uygur](https://github.com/adralei)
