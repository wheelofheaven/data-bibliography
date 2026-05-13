#!/usr/bin/env python3
"""
Generate thin Zola content stubs at `content/sources/{id}.md` from the
per-source JSON records.

Each stub is just the routing artifact Zola needs to register the URL.
The sources-page.html template loads the full record from
data/sources/sources/{id}.json at render time.

Pass --content-root to point at your data-content checkout. Defaults to
the standalone clone at the conventional path.

Usage:
    python3 scripts/generate-content-stubs.py
    python3 scripts/generate-content-stubs.py --content-root /path/to/data-content
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = ROOT / "sources"


def slugify_title_for_description(text: str, max_len: int = 160) -> str:
    """Strip newlines, collapse whitespace, truncate at a word boundary, escape quotes."""
    flat = " ".join(text.split())
    if len(flat) <= max_len:
        return flat.replace('"', '\\"')
    cut = flat[:max_len].rsplit(" ", 1)[0]
    return (cut + "…").replace('"', '\\"')


def render_stub(record: dict) -> str:
    rid = record["id"]
    title = record["title"].replace('"', '\\"')
    description = record.get("description", {}).get("en", "")
    short = slugify_title_for_description(description)
    aliases = record.get("aliases", [])
    alias_lines = ", ".join(f'"{a}"' for a in aliases)

    lines = [
        "+++",
        f'title = "{title}"',
        f'slug = "{rid}"',
        f'description = "{short}"',
        'template = "sources-page.html"',
    ]
    if aliases:
        lines.append(f"aliases = [{alias_lines}]")
    lines.append("+++")
    lines.append("")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--content-root",
        default="/Users/zara/Development/github.com/wheelofheaven/data-content",
        help="Path to the data-content checkout",
    )
    parser.add_argument(
        "--include-drafts",
        action="store_true",
        help="Generate stubs for drafts too (default: skip drafts)",
    )
    args = parser.parse_args()

    content_root = Path(args.content_root)
    if not content_root.exists():
        print(f"ERROR: content root not found: {content_root}", file=sys.stderr)
        sys.exit(1)

    out_dir = content_root / "sources"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(SOURCES_DIR.glob("*.json"))
    written = 0
    skipped = 0
    for path in files:
        record = json.loads(path.read_text())
        if record.get("draft") and not args.include_drafts:
            skipped += 1
            continue
        stub_path = out_dir / f"{record['id']}.md"
        stub_path.write_text(render_stub(record))
        written += 1

    print(f"Wrote {written} stubs to {out_dir}")
    if skipped:
        print(f"  skipped {skipped} draft records (use --include-drafts to include)")


if __name__ == "__main__":
    main()
