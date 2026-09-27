"""Local API: uvicorn main:app --host 127.0.0.1 --port 8000."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from soc_rag.config import Settings
from soc_rag.retrieval import load_vector_store
from soc_rag.service import get_answer, ExternalLLMDisabled, ProviderError


class Question(BaseModel):
    query: str = Field(min_length=1, max_length=12000)
    retrieve_only: bool = False


def create_app(settings=None, loader=load_vector_store):
    settings = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(app):
        try:
            app.state.retriever = loader(settings)
        except Exception:
            # Keep health available without leaking paths, request data or provider errors.
            app.state.retriever = None
        yield

    app = FastAPI(title="SOC RAG Assistant", version="0.1.0", lifespan=lifespan)

    @app.get("/health")
    def health():
        ready = app.state.retriever is not None
        return {"status": "ready" if ready else "index_unavailable", "index_ready": ready,
                "external_llm_enabled": settings.allow_external_llm}

    @app.post("/ask")
    def ask(question: Question):
        if app.state.retriever is None:
            raise HTTPException(503, "Index unavailable. Build or validate the local index.")
        try:
            return get_answer(question.query, app.state.retriever, settings, question.retrieve_only)
        except ValueError:
            raise HTTPException(422, "Invalid query or incompatible index.") from None
        except ExternalLLMDisabled:
            raise HTTPException(503, "Generation disabled or unconfigured. Use retrieve_only=true.") from None
        except ProviderError:
            raise HTTPException(502, "LLM request failed. Check model access, quota and connectivity.") from None
        except Exception:
            raise HTTPException(500, "Analysis failed. Review local configuration.") from None

    return app


app = create_app()
