#!/usr/bin/env python3
"""
Regenerate index.json from the per-source JSON files in sources/.

Each entry is a thin pointer with the fields needed to render a list view
(/sources/ overview, citation chips, etc.) without loading the full record.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = ROOT / "sources"
INDEX_PATH = ROOT / "index.json"

INDEX_FIELDS = (
    "id",
    "title",
    "source_type",
    "source_family",
    "relation_to_wheel",
    "stance",
    "library_slug",
)


def main():
    files = sorted(SOURCES_DIR.glob("*.json"))
    index = []
    for path in files:
        record = json.loads(path.read_text())
        if record.get("draft"):
            continue
        entry = {k: record.get(k) for k in INDEX_FIELDS if k in record}
        index.append(entry)

    INDEX_PATH.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {len(index)} entries to {INDEX_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
