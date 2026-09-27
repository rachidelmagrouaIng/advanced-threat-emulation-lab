# Synthetic demonstration data

All records in this directory are newly authored examples. Addresses use documentation ranges; names are placeholders. They are not real incident evidence or a measured detection benchmark.

Build the sample corpus with `python build_index.py --data-dir examples/knowledge`. Paste a short excerpt from `logs/ssh-example.txt` or `logs/windows-example.json` into the UI, or submit it to `/ask` with `retrieve_only=true`.

Expected analyst reasoning for the SSH example: repeated authentication failures justify investigation, but do not establish a successful compromise. Review subsequent successful logons, account context, normal administration patterns and host activity before assigning severity or blocking.

The knowledge corpus is intentionally small. It supports workflow demonstrations and may yield irrelevant neighbors. Generated output will vary by model and prompt; no fabricated response screenshot is included.
