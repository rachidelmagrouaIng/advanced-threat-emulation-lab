"""Check publishable files for common credentials and accidental large artifacts.

A heuristic check, not a guarantee that all sensitive information is absent.
Uses tracked files in Git and skips local runtime directories in an unpacked copy.
"""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


def main():
    result = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True)
    paths = ([ROOT / p for p in result.stdout.decode().split("\0") if p] if result.returncode == 0
             else [p for p in ROOT.rglob("*") if p.is_file() and
                   not any(part in {".git", ".venv", "venv", "__pycache__", "data"} or
                           part.startswith("vector_store") for part in p.relative_to(ROOT).parts)])
    errors = []
    for path in paths:
        rel = path.relative_to(ROOT)
        if path.name == ".env" or (path.name.startswith(".env.") and path.name != ".env.example"):
            errors.append(f"{rel}: environment secret file")
            continue
        if path.stat().st_size > 5 * 1024**2:
            errors.append(f"{rel}: file exceeds 5 MB")
        if path.suffix in {".pem", ".key", ".pfx", ".p12", ".pcap", ".pcapng", ".pkl", ".pickle"}:
            errors.append(f"{rel}: sensitive or generated artifact type")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if any(pattern.search(text) for pattern in PATTERNS):
            errors.append(f"{rel}: possible credential (value suppressed)")
    if errors:
        print("\n".join(errors))
        return 1
    print(f"Checked {len(paths)} publishable files; no configured-pattern matches or oversized artifacts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
