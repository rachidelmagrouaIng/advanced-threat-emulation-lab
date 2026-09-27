"""Deterministic component/integration tests. No network or LLM calls."""
import json
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import numpy as np
from fastapi.testclient import TestClient
from main import create_app
from soc_rag.config import Settings
from soc_rag.ingestion import Chunk, load_documents, chunk_documents
from soc_rag.retrieval import create_vector_store, load_vector_store
from soc_rag.service import get_answer, ExternalLLMDisabled, ProviderError


class Encoder:
    """Controlled vectors test mechanics; they do not measure model quality."""
    def encode(self, texts, **kwargs):
        return np.array([[1, 0] if "ssh" in t.lower() else [0, 1] for t in texts], dtype="float32")


class IngestionTests(unittest.TestCase):
    def test_schema_and_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / "sample.csv").write_text('text,ignored\n"SSH failure",private\n,unused\n', encoding="utf-8")
            docs = list(load_documents(path))
            self.assertEqual(len(docs), 1)
            self.assertEqual(docs[0], Chunk("sample.csv", 2, 0, "SSH failure"))

    def test_missing_text_column(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / "bad.csv").write_text("token\nprivate\n")
            with self.assertRaisesRegex(ValueError, "required column"):
                list(load_documents(path))

    def test_row_limit_fails_instead_of_truncating(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / "sample.csv").write_text("text\none\ntwo\n")
            with self.assertRaisesRegex(ValueError, "row limit"):
                list(load_documents(path, max_rows=1))

    def test_empty_corpus(self):
        with self.assertRaises(ValueError):
            chunk_documents([])

    def test_overlap_and_source(self):
        chunks = chunk_documents([Chunk("a.csv", 2, 0, "abcdefghij")], 6, 2)
        self.assertEqual([c.text for c in chunks], ["abcdef", "efghij"])
        self.assertEqual([c.chunk for c in chunks], [0, 1])

    def test_bad_overlap_and_chunk_cap(self):
        doc = [Chunk("a.csv", 2, 0, "abcdefghij")]
        with self.assertRaises(ValueError):
            chunk_documents(doc, 4, 4)
        with self.assertRaises(ValueError):
            chunk_documents(doc, 4, 1, max_chunks=1)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.settings = Settings(vector_dir=Path(self.temp.name) / "index", min_score=0.5)
        self.chunks = [Chunk("demo.csv", 2, 0, "SSH failures"), Chunk("demo.csv", 3, 0, "Web upload")]
        create_vector_store(self.chunks, self.settings, Encoder())
        self.retriever = load_vector_store(self.settings, Encoder())

    def tearDown(self):
        self.temp.cleanup()

    def test_roundtrip_ranking_and_threshold(self):
        result = self.retriever.search("SSH password failures")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["row"], 2)
        self.assertAlmostEqual(result[0]["score"], 1)

    def test_existing_index_not_overwritten(self):
        with self.assertRaises(ValueError):
            create_vector_store(self.chunks, self.settings, Encoder())

    def test_corruption_rejected(self):
        (self.settings.vector_dir / "chunks.json").write_text("[]")
        with self.assertRaisesRegex(ValueError, "integrity"):
            load_vector_store(self.settings, Encoder())

    def test_model_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, "mismatch"):
            load_vector_store(replace(self.settings, embedding_model="other"), Encoder())

    def test_local_mode_never_calls_generator(self):
        generator = Mock(side_effect=AssertionError("must not run"))
        result = get_answer("SSH", self.retriever, self.settings, True, generator)
        self.assertEqual(result["status"], "retrieval_only")
        self.assertEqual(result["sources"][0]["id"], "S1")
        generator.assert_not_called()

    def test_external_disabled_even_with_key(self):
        settings = replace(self.settings, api_key="test-placeholder")
        with self.assertRaises(ExternalLLMDisabled):
            get_answer("SSH", self.retriever, settings)

    def test_external_enabled_without_key(self):
        with self.assertRaises(ExternalLLMDisabled):
            get_answer("SSH", self.retriever, replace(self.settings, allow_external_llm=True))

    def test_generation_receives_sources(self):
        settings = replace(self.settings, api_key="test-placeholder", allow_external_llm=True)
        generator = Mock(return_value="Review SSH evidence [S1].")
        result = get_answer("SSH", self.retriever, settings, generator=generator)
        self.assertEqual(result["status"], "generated")
        self.assertEqual(generator.call_args.args[1][0]["id"], "S1")

    def test_no_matches_abstains_without_generation(self):
        retriever = Mock()
        retriever.search.return_value = []
        generator = Mock()
        result = get_answer("unknown", retriever, self.settings, generator=generator)
        self.assertEqual(result["status"], "insufficient_evidence")
        generator.assert_not_called()

    def test_blank_and_overlong_requests(self):
        for query in ["   ", "a" * 12001]:
            with self.assertRaises(ValueError):
                get_answer(query, self.retriever, self.settings)

    def test_api_local_request_and_limits(self):
        with TestClient(create_app(self.settings, lambda _: self.retriever)) as client:
            self.assertTrue(client.get("/health").json()["index_ready"])
            result = client.post("/ask", json={"query": "SSH", "retrieve_only": True})
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result.json()["sources"][0]["row"], 2)
            for query in ["", "   ", "x" * 12001]:
                self.assertEqual(client.post("/ask", json={"query": query}).status_code, 422)
            self.assertEqual(client.post("/ask", json={"query": "SSH"}).status_code, 503)

    def test_unavailable_index_health_and_error(self):
        def fail(_):
            raise ValueError("private filesystem detail")
        with TestClient(create_app(self.settings, fail)) as client:
            self.assertFalse(client.get("/health").json()["index_ready"])
            response = client.post("/ask", json={"query": "SSH"})
            self.assertEqual(response.status_code, 503)
            self.assertNotIn("private", response.text)

    def test_provider_error_is_generic(self):
        settings = replace(self.settings, api_key="test-placeholder", allow_external_llm=True)
        with TestClient(create_app(settings, lambda _: self.retriever)) as client:
            with patch("soc_rag.service.generate_response", side_effect=ProviderError("private details")):
                response = client.post("/ask", json={"query": "SSH"})
                self.assertEqual(response.status_code, 502)
                self.assertNotIn("private details", response.text)


if __name__ == "__main__":
    unittest.main()
