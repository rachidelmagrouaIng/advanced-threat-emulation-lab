# Repository validation record

Checked on 2026-09-27 in Linux with Python 3.12.

| Check | Result |
| --- | --- |
| Unit/integration suite | 19 tests passed |
| Retrieval persistence and search | Real FAISS and NumPy, deterministic test encoder |
| API tests | Local TestClient, including invalid input and generic errors |
| Python compilation | All application modules compiled |
| Internal Markdown links | No missing local targets |
| Repository hygiene | No configured credential-pattern matches or oversized files |
| Gemini SDK setup | Client/context manager and generation configuration constructed; no API request |

Installed components used for these checks: FastAPI 0.141.1, httpx 0.28.1, NumPy 2.5.3, faiss-cpu 1.15.1, google-genai 2.25.0, pypdf 6.19.0 and python-dotenv 1.2.3. The test runtime emitted a Starlette notice about a future HTTP test-client transition; the tests passed. The sandbox's SOCKS proxy required the optional httpx SOCKS extra for SDK construction; that is an environment-specific requirement.

The full application dependency set, MiniLM model download, live provider generation, interactive Streamlit/PDF behavior and target-device hardening were not exercised in this validation. Python 3.11 is configured in CI alongside 3.12, but no remote CI run is claimed. The hygiene check is heuristic and is supplemented by manual review of the included text and architecture images.

These results establish a tested local service core, not a production certification or model-performance benchmark.
