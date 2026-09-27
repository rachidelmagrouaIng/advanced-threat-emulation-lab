"""Public entry points retained for the lab's original four-script layout."""
from soc_rag.ingestion import load_documents, chunk_documents
from soc_rag.retrieval import create_vector_store, load_vector_store
from soc_rag.service import get_answer, generate_response

__all__ = ["load_documents", "chunk_documents", "create_vector_store", "load_vector_store", "get_answer", "generate_response"]
