# RAG engineering design

## Pipeline

1. Read UTF-8 CSV records from an explicit `text` column. Fail on absent schema, empty corpus or row-limit overflow rather than silently concatenating unrelated fields.
2. Split text into 500-character chunks with 50-character overlap. Preserve filename, CSV record number and chunk number. For multiline CSV, the record number is logical, not a physical file line.
3. Encode chunks with `sentence-transformers/all-MiniLM-L6-v2`; normalize vectors.
4. Persist `vectors.npy`, `chunks.json` and an integrity manifest. Reconstruct an in-memory FAISS `IndexFlatIP` when loading. No pickle or serialized native FAISS index is loaded.
5. Encode the query and retrieve up to four records above the configured cosine threshold.
6. Return evidence locally, abstain if no record meets the threshold, or send the query and evidence to Gemini when enabled.
7. Return source identifiers with the generated answer for analyst inspection.

## Key decisions and limits

| Mechanism | Benefit | Remaining limit |
| --- | --- | --- |
| Normalized inner-product search | Interpretable cosine similarity | Not a threat probability or calibrated confidence |
| JSON + numeric arrays | Avoids pickle loading and native-index deserialization | Local files must still be trusted; hashes do not authenticate the author |
| Manifest hashes and shape checks | Detect accidental index corruption and model mismatch | An attacker able to replace the manifest can replace checksums |
| Similarity threshold (default 0.25) | Can abstain on weak matches | A heuristic, not a calibrated operating point |
| Source/row/chunk IDs | Enables review of retrieved evidence | The model can still miscite or misinterpret a source |
| Separate system instruction | Tells the model to treat corpus text as data | Does not guarantee prompt-injection resistance |
| Local mode by default | No LLM data transfer for retrieval | Embedding weights may need an initial download |
| 12,000-character request limit | Bounds accepted query size | Long PDFs must be curated; no full-document batching |

The corpus loads into memory for embedding and exact FAISS search. Row and chunk caps fail explicitly; this is not a streaming billion-vector architecture. Retain only reviewed, useful security context. Chunking can separate an event from its explanation, and nearest neighbors do not establish a temporal or causal relationship.

## Generation boundary

The hosted model receives the query and the retrieved text, filenames, row references and similarity scores. It does not receive the API key as prompt text. Prompts ask for observations, hypotheses, missing telemetry, validation steps and defensive proposals. Numerical confidence claims are discouraged. No tools or command execution are attached to the model.

Errors returned to API/UI clients suppress raw provider exception details. The API has no authentication or rate limiting; keep it on loopback. A production gateway, request quotas, tenant isolation, privacy controls and provider-backed evaluation would be separate work.

## Evolution from the initial implementation

| Initial implementation | Current repository |
| --- | --- |
| Four scripts with shared global configuration | Four entry points plus a modular service package |
| LangChain FAISS persistence requiring pickle deserialization | Numpy arrays + JSON; FAISS rebuilt in memory |
| CSV text-column fallback over arbitrary object columns | Required explicit text column |
| Legacy Google generative SDK | Google Gen AI SDK |
| Similarity-only retrieval without source visibility | Source metadata, exposed scores and abstention threshold |
| Index load at API import time | Lifecycle load and readiness state |
| PDF extraction without input bounds | Byte, page and extracted-text limits |
| Provider error text surfaced directly | Generic provider failures |

`rag_utils.py` retains function names as re-exports; signatures now require explicit settings. Existing callers must be updated accordingly.

## References

- [Sentence Transformers model API](https://www.sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html)
- [Google Gen AI Python SDK](https://googleapis.github.io/python-genai/)
- [FAISS index I/O cautions](https://github.com/facebookresearch/faiss/wiki/Index-IO%2C-cloning-and-hyper-parameter-tuning)
