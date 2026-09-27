# Evaluation and evidence

## What is established

The lab work covers authentication interception/relay, remote WMI execution, SQL injection, unsafe upload execution and SSH password attacks, paired with hardening steps. CALDERA architecture and agent deployment form the emulation component. The Python workflow implements CSV retrieval and analyst-facing generation.

The public repository includes architecture images and qualitative scenario documentation. It does not include a timestamped, sanitized evidence bundle proving every post-hardening outcome. Do not infer a detection rate, latency improvement or complete ATT&CK coverage from the scenario list.

## Automated checks

`tests/test_pipeline.py` uses a deterministic two-dimensional encoder with real NumPy/FAISS operations. It tests CSV schema handling, chunk boundaries, limits, vector persistence, corruption rejection, ranking, metadata, generation opt-in, abstention, API readiness, input validation and generic errors.

These checks validate implementation mechanics. They do not test MiniLM semantic quality, live Gemini behavior, Streamlit browser interactions, PDF exploit resistance, production load or actual security-device rule enforcement.

## Lab retest record

For each scenario, record privately:

| Field | Required content |
| --- | --- |
| Baseline | Host roles, software versions, relevant configuration |
| Authorization | Lab target set and permitted time window |
| Procedure | Scenario identifier and preconditions |
| Before | Observable result with sanitized evidence |
| Change | Exact defensive control and rollback plan |
| After | Same test repeated, including normal-use regression |
| Detection | Sensor, event/query, time window and analyst interpretation |
| Outcome | Verified, inconclusive or not run |

## RAG evaluation plan

Build a held-out set with benign activity, malicious activity, ambiguous logs, unrelated queries and prompt-injection attempts. Keep it separate from indexed records. Include questions requiring multiple event sources.

Measure retrieval recall@k against manually labeled relevant chunks, evidence citation correctness, unsupported-claim rate, abstention behavior and analyst acceptance of proposed next steps. Record corpus version, model revision, prompt version, provider model, threshold, timings and failure counts. Evaluate generated rule syntax in the target product and check operational impact before deployment.

The default 0.25 similarity threshold is a starting heuristic. Tune it from held-out evidence and report the resulting trade-off. Do not use similarity scores as attack confidence percentages.

## Roadmap

- Curated and labeled retrieval evaluation set.
- Model/version pinning and a reproducible dependency lock.
- Hybrid search or reranking if error analysis justifies it.
- Structured generation output and citation validation.
- Offline LLM provider option for sensitive environments.
- Authenticated, rate-limited service deployment.
- Explicit, tested adapters for telemetry ingestion; no autonomous blocking by default.
