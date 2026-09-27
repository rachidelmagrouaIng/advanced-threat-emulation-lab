# Engineering case study

## Problem

A domain environment can expose several connected attack surfaces: fallback name resolution, legacy authentication, administrative remote access, vulnerable web endpoints and weak SSH authentication. A successful exploit alone gives an incomplete security assessment. I wanted to understand the enabling conditions, the useful evidence and the effect of a defensive change.

## My approach

I worked through Windows and Linux scenarios in a simulated enterprise, paired offensive tests with defensive controls, and added a retrieval-based assistant for security log interpretation. The project combines hands-on network and system security with Python application engineering.

The Windows work examines authentication redirection and relay, name-resolution hardening and remote administration exposure. The Ubuntu work examines SQL injection, executable uploads and SSH access controls. CALDERA adds an emulation platform with agents on lab endpoints. The RAG component brings relevant security records into the analyst's investigation instead of relying exclusively on a model's general knowledge.

## Design decisions

| Decision | Rationale | Trade-off |
| --- | --- | --- |
| CSV knowledge corpus | Straightforward ingestion and inspection | Quality, labeling and provenance must be curated |
| MiniLM embeddings | A compact local embedding model | Short chunks can lose relationships between events |
| FAISS similarity retrieval | Direct local vector search | No temporal correlation or semantic reranking |
| Hosted Gemini model | Flexible natural-language analysis | External data transfer, quotas and provider dependency |
| Two interfaces, one service | UI and API reuse the same behavior | No built-in multi-user isolation |
| Analyst reviews actions | Preserve operational control | Recommendations do not provide autonomous containment |

## What the work demonstrates

- Connecting a weakness to its protocol or application preconditions.
- Translating an attack path into a targeted hardening decision.
- Considering authentication dependencies and service availability before a change.
- Building an inspectable retrieval pipeline with evidence references.
- Separating an observed event, a hypothesis and a proposed response.

## Public implementation improvements

The current implementation preserves the four original entry-point filenames while separating ingestion, configuration, retrieval and generation. It adds explicit text-column validation, source/row/chunk metadata, JSON and numeric-array persistence, local retrieval mode, input limits, generic provider errors and testable service boundaries.

These are repository engineering improvements. They should not be read as historical measurements or as a claim that the entire lab has been redeployed by this code. A full emulation-to-response integration, calibrated retrieval thresholds and provider-backed evaluation remain future work.
