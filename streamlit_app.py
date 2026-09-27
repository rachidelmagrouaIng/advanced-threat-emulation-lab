"""Local analyst UI. Shares the retrieval service with the independent API."""
import io
import streamlit as st
from pypdf import PdfReader
from soc_rag.config import Settings
from soc_rag.retrieval import load_vector_store
from soc_rag.service import get_answer, ExternalLLMDisabled, ProviderError

st.set_page_config(page_title="SOC RAG Assistant", page_icon="🛡️", layout="wide")
st.title("SOC RAG Assistant")
st.caption("Advanced Threat Emulation & Security Lab · Rachid EL MAGROUA")
st.write("Inspect security logs against a local knowledge base and review proposed defensive actions.")
settings = Settings.from_env()


@st.cache_resource
def init_retriever(model, directory):
    return load_vector_store(settings)


try:
    retriever = init_retriever(settings.embedding_model, str(settings.vector_dir))
except Exception:
    st.error("Index unavailable. Run python build_index.py and restart the application.")
    st.stop()

query = st.text_area("Question or sanitized log excerpt", max_chars=settings.max_query_chars, height=170)
upload = st.file_uploader("Or select a text PDF (maximum 2 MB and 20 pages)", type=["pdf"])
if upload:
    try:
        if upload.size > 2 * 1024**2:
            raise ValueError()
        reader = PdfReader(io.BytesIO(upload.getvalue()))
        if reader.is_encrypted or len(reader.pages) > 20:
            raise ValueError()
        query = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        if not query or len(query) > settings.max_query_chars:
            raise ValueError()
        st.caption("The PDF text replaces the text box input. OCR is not supported.")
        with st.expander("Review extracted text"):
            st.text(query)
    except Exception:
        st.error("PDF unreadable or exceeds limits. Paste a short, sanitized text excerpt instead.")
        st.stop()

retrieve_only = st.checkbox("Retrieve evidence only (no LLM call)", value=True)
consent = False
if not retrieve_only:
    st.info("Generation sends your input and retrieved excerpts to Google Gemini. Remove secrets and personal data first.")
    consent = st.checkbox("I have reviewed the data and authorize this request to Gemini.")
if st.button("Analyze", type="primary", disabled=not retrieve_only and not consent):
    try:
        with st.spinner("Analyzing..."):
            result = get_answer(query, retriever, settings, retrieve_only)
        if result["answer"]:
            st.markdown(result["answer"])
        for source in result["sources"]:
            with st.expander(f"[{source['id']}] {source['source']} · row {source['row']} · similarity {source['score']:.3f}"):
                st.text(source["text"])
        st.caption("Similarity is not confidence. Validate all model-generated rules before applying them.")
    except (ValueError, ExternalLLMDisabled, ProviderError) as exc:
        st.error(str(exc))
    except Exception:
        st.error("Analysis failed. Check the local index and configuration.")
