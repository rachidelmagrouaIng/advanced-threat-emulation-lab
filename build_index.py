"""Build a local corpus index without making an LLM request."""
import argparse
from dataclasses import replace
from pathlib import Path
from soc_rag.config import Settings
from rag_utils import load_documents, chunk_documents, create_vector_store


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--vector-dir", type=Path)
    parser.add_argument("--text-column", default="text")
    args = parser.parse_args()
    settings = Settings.from_env()
    settings = replace(settings, data_dir=args.data_dir or settings.data_dir,
                       vector_dir=args.vector_dir or settings.vector_dir)
    docs = load_documents(settings.data_dir, args.text_column, settings.max_rows)
    chunks = chunk_documents(docs, settings.chunk_size, settings.chunk_overlap, settings.max_chunks)
    manifest = create_vector_store(chunks, settings)
    print(f"Created {manifest['count']} chunks ({manifest['dimension']} dimensions).")


if __name__ == "__main__":
    main()
