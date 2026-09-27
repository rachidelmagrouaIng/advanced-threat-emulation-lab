# Security and data handling

This is a local research prototype for an authorized lab. Bind services to loopback. There is no authentication, tenant isolation or rate limiter; do not expose the API or UI directly to the internet.

## Data flow

CSV processing, embeddings and vector search run locally. Initial model weights may be downloaded. Generation is disabled by default. When enabled, Google Gemini receives the submitted input and retrieved source excerpts, including source filenames. Review provider data handling and organizational requirements before opting in.

Do not submit API keys, passwords, captured NTLM responses, session tokens, customer logs or personal information. Sanitization is a manual responsibility in this release. There is no claim that an automatic redactor protects every record.

`.env`, local datasets, vector stores, captures, private keys and model artifacts are excluded through `.gitignore`. Ignore rules do not remove files already tracked by Git. Run the hygiene check and inspect the staged diff before publishing.

## Trust boundaries

Only build indexes from trusted local CSVs. Numeric-array persistence avoids pickle and native FAISS file loading; manifest hashes detect accidental modification, not malicious authorship. Treat stored vectors, JSON metadata and model artifacts as private runtime data. Model code uses `trust_remote_code=False`.

PDF parsing is local and bounded by byte/page/text limits but is not sandboxed. Use trusted files. A malicious corpus may contain prompt injection. System instructions reduce ambiguity, but do not eliminate the risk. No generated instructions execute automatically.

## Reporting

Do not put secrets or exploit details affecting real systems in public issues. Contact Rachid EL MAGROUA through the LinkedIn profile linked in the README to arrange a private reporting channel. For exposed credentials, revoke or rotate them with the provider and remove them from repository history as appropriate.
