# Local setup and API contract

Follow the root README quick start with Python 3.11. Install inside a virtual environment. Dependency ranges express intended compatibility; they are not a lockfile. Pin a resolved environment after testing on your target OS and hardware.

## Data

Place reviewed CSV files under `data/` (ignored by Git) or use `--data-dir examples/knowledge`. The required column is `text`; choose another explicitly with `--text-column`. Empty records are skipped. There is a maximum of 50,000 records per file and 200,000 chunks per build. Exceeding limits stops the build.

Synthetic examples are demonstration material, not an evaluation corpus or real incident evidence. Remove secrets, identifiers, internal hostnames and proprietary content before ingestion. Filenames also appear in retrieval results and generation requests.

## Rebuilding

The builder refuses an existing output directory. Stop the application, build into a new directory with `--vector-dir vector_store_v2`, then set `VECTOR_DIR=vector_store_v2` in `.env` and restart. This avoids serving a partially rebuilt index. Keep the old version until the new corpus passes checks. Do not load indexes from untrusted sources.

Changing the embedding model requires a new index. The manifest records the model name but does not pin a model revision; pin downloaded model artifacts separately for strict reproducibility.

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `GOOGLE_API_KEY` | empty | Local secret, required only for generation |
| `ALLOW_EXTERNAL_LLM` | `false` | Operator opt-in to hosted generation |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Provider model name; confirm access in your account |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Corpus and query encoder |
| `DATA_DIR` | `data` | Build input directory |
| `VECTOR_DIR` | `vector_store` | Local persisted vectors and metadata |
| `TOP_K` | `4` | 1–20 retrieved chunks |
| `MIN_RETRIEVAL_SCORE` | `0.25` | Cosine threshold, -1 to 1; tune with held-out examples |

## API

`GET /health` returns a readiness payload. HTTP 200 means the process responded; use the `index_ready` field to decide whether retrieval is available. `external_llm_enabled` reports the operator switch, not provider availability or key validity.

`POST /ask` accepts:

```json
{"query":"Short sanitized security question or log excerpt","retrieve_only":true}
```

The response contains `status`, `answer` and `sources`. Status values are `retrieval_only`, `insufficient_evidence` and `generated`. Every returned source contains `id`, `source`, `row`, `chunk`, `text` and `score`. An empty match set returns `insufficient_evidence` without contacting Gemini.

Errors: 422 for invalid input; 503 for unavailable index or disabled/unconfigured generation; 502 for a provider failure; 500 for an unexpected analysis failure. The API uses a synchronous handler so blocking inference runs in FastAPI's worker thread pool. It has no built-in multi-user queue or admission control.

## Troubleshooting

- **Index unavailable:** run the index builder and check `VECTOR_DIR`. Integrity/model mismatch requires a rebuild. The API intentionally avoids exposing raw startup errors to clients; run `python -c "from soc_rag.config import Settings; from soc_rag.retrieval import load_vector_store; load_vector_store(Settings.from_env())"` locally to diagnose.
- **Model download failure:** allow access to the model provider or use a trusted local model path. Retrieval is local once weights are cached.
- **No retrieved evidence:** inspect the corpus and question. Tune thresholds with labeled examples instead of lowering the threshold until any answer appears.
- **Generation disabled:** configure the key and opt-in flag, then restart. Streamlit also requests confirmation before generation.
- **Provider failure:** check account model access, quota and network. The repository does not include a key or guarantee a model's continued availability.
- **PDF rejected:** paste a sanitized excerpt. Maximum 2 MB, 20 pages and 12,000 extracted characters. Encrypted and image-only PDFs are not supported. PDF parsing is not sandboxed; accept only trusted local files.
