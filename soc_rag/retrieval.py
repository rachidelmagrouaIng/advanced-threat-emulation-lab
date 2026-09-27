"""FAISS cosine retrieval; persist numeric arrays and JSON, never pickle."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

import numpy as np


def _hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def make_encoder(model_name):
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(model_name, trust_remote_code=False)


def _encode(encoder, texts):
    vectors = np.asarray(encoder.encode(texts, normalize_embeddings=True), dtype="float32")
    if vectors.ndim != 2 or not np.isfinite(vectors).all():
        raise ValueError("Encoder returned invalid vectors.")
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    if np.any(norms == 0):
        raise ValueError("Encoder returned a zero vector.")
    return np.ascontiguousarray(vectors / norms)


def create_vector_store(chunks, settings, encoder=None):
    directory = Path(settings.vector_dir)
    if directory.exists():
        raise ValueError("Index directory already exists. Use a new VECTOR_DIR to rebuild safely.")
    encoder = encoder or make_encoder(settings.embedding_model)
    vectors = _encode(encoder, [chunk.text for chunk in chunks])
    if len(vectors) != len(chunks):
        raise ValueError("Vector count does not match the corpus.")
    directory.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".rag-build-", dir=directory.parent))
    try:
        np.save(staging / "vectors.npy", vectors, allow_pickle=False)
        (staging / "chunks.json").write_text(json.dumps([c.to_dict() for c in chunks]), encoding="utf-8")
        manifest = {"format": 1, "embedding_model": settings.embedding_model,
                    "count": len(chunks), "dimension": vectors.shape[1],
                    "files": {name: _hash(staging / name) for name in ("vectors.npy", "chunks.json")}}
        (staging / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        os.rename(staging, directory)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return manifest


class Retriever:
    def __init__(self, index, chunks, encoder, settings):
        self.index, self.chunks, self.encoder, self.settings = index, chunks, encoder, settings

    def search(self, query):
        vectors = _encode(self.encoder, [query])
        if vectors.shape[1] != self.index.d:
            raise ValueError("Embedding dimensions changed. Rebuild the index.")
        scores, ids = self.index.search(vectors, min(self.settings.top_k, len(self.chunks)))
        return [{**self.chunks[int(i)], "score": round(float(score), 6)}
                for score, i in zip(scores[0], ids[0])
                if i >= 0 and score >= self.settings.min_score]


def load_vector_store(settings, encoder=None):
    import faiss
    directory = Path(settings.vector_dir)
    manifest_path = directory / "manifest.json"
    if manifest_path.stat().st_size > 16384:
        raise ValueError("Invalid index manifest size.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("format") != 1 or manifest.get("embedding_model") != settings.embedding_model:
        raise ValueError("Index format or embedding model mismatch. Rebuild the index.")
    for name, limit in [("vectors.npy", 1024**3), ("chunks.json", 256 * 1024**2)]:
        path = directory / name
        if path.stat().st_size > limit or _hash(path) != manifest["files"].get(name):
            raise ValueError("Index integrity or size check failed. Rebuild from trusted CSV files.")
    vectors = np.load(directory / "vectors.npy", allow_pickle=False, mmap_mode="r")
    chunks = json.loads((directory / "chunks.json").read_text(encoding="utf-8"))
    if (vectors.dtype != np.float32 or vectors.ndim != 2 or
            vectors.shape != (manifest["count"], manifest["dimension"]) or
            not 0 < len(chunks) <= settings.max_chunks or len(chunks) != len(vectors) or
            not np.isfinite(vectors).all() or
            not np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-4)):
        raise ValueError("Invalid vector data.")
    for chunk in chunks:
        if (not isinstance(chunk, dict) or not isinstance(chunk.get("text"), str) or
                not isinstance(chunk.get("source"), str) or not isinstance(chunk.get("row"), int) or
                not isinstance(chunk.get("chunk"), int)):
            raise ValueError("Invalid source metadata.")
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(np.ascontiguousarray(vectors))
    return Retriever(index, chunks, encoder or make_encoder(settings.embedding_model), settings)
