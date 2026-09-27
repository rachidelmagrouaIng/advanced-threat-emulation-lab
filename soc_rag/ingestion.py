"""CSV ingestion with explicit text columns and traceable chunks."""
import csv
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Chunk:
    source: str
    row: int
    chunk: int
    text: str

    def to_dict(self):
        return asdict(self)


def load_documents(data_dir: Path, text_column="text", max_rows=50000):
    files = sorted(Path(data_dir).glob("*.csv"))
    if not files:
        raise ValueError("No CSV files found. See examples/knowledge for the required schema.")
    for path in files:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if text_column not in (reader.fieldnames or []):
                raise ValueError(f"{path.name}: required column {text_column!r} is missing.")
            for row_number, row in enumerate(reader, 2):
                if row_number - 2 >= max_rows:
                    raise ValueError(f"{path.name}: row limit exceeded; split or curate the corpus.")
                text = (row.get(text_column) or "").strip()
                if text:
                    yield Chunk(path.name, row_number, 0, text)


def chunk_documents(documents, chunk_size=500, chunk_overlap=50, max_chunks=200000):
    if not 0 <= chunk_overlap < chunk_size:
        raise ValueError("Chunk overlap must be nonnegative and smaller than chunk size.")
    result = []
    for doc in documents:
        for number, start in enumerate(range(0, len(doc.text), chunk_size - chunk_overlap)):
            result.append(Chunk(doc.source, doc.row, number, doc.text[start:start + chunk_size]))
            if len(result) > max_chunks:
                raise ValueError("Chunk limit exceeded; reduce the corpus.")
            if start + chunk_size >= len(doc.text):
                break
    if not result:
        raise ValueError("No nonempty text was available to index.")
    return result
