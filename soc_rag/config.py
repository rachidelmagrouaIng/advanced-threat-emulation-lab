"""Environment configuration. Never store credentials in source control."""
from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    data_dir: Path = Path("data")
    vector_dir: Path = Path("vector_store")
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    gemini_model: str = "gemini-2.5-flash"
    api_key: str = ""
    allow_external_llm: bool = False
    top_k: int = 4
    min_score: float = 0.25
    max_query_chars: int = 12000
    max_rows: int = 50000
    max_chunks: int = 200000
    chunk_size: int = 500
    chunk_overlap: int = 50

    @classmethod
    def from_env(cls):
        from dotenv import load_dotenv
        load_dotenv()
        settings = cls(
            data_dir=Path(os.getenv("DATA_DIR", "data")),
            vector_dir=Path(os.getenv("VECTOR_DIR", "vector_store")),
            embedding_model=os.getenv("EMBEDDING_MODEL", cls.embedding_model),
            gemini_model=os.getenv("GEMINI_MODEL", cls.gemini_model),
            api_key=os.getenv("GOOGLE_API_KEY", ""),
            allow_external_llm=os.getenv("ALLOW_EXTERNAL_LLM", "false").lower() == "true",
            top_k=int(os.getenv("TOP_K", "4")),
            min_score=float(os.getenv("MIN_RETRIEVAL_SCORE", "0.25")),
        )
        if not 1 <= settings.top_k <= 20 or not -1 <= settings.min_score <= 1:
            raise ValueError("TOP_K must be 1..20 and MIN_RETRIEVAL_SCORE must be -1..1.")
        return settings
