#!/usr/bin/env python3
"""
One-shot migration: convert content/resources/*.md from the site repo into
data-bibliography/sources/{id}.json.

Schema cleanups applied during migration (per the plan doc):
- Drop `claim_type` — all 67 entries are `direct`, and claim type is a
  property of *claims*, not source descriptions.
- Drop `medium` — overlaps with `source_type`; keep the latter.
- Drop `authority_tier` — overlaps with `relation_to_wheel`; keep the latter.

Run from anywhere; uses absolute paths.
"""

import json
import re
import sys
from pathlib import Path

SITE_REPO = Path("/Users/zara/Development/github.com/wheelofheaven/www.wheelofheaven.io")
RESOURCES = SITE_REPO / "content" / "resources"
OUT_DIR = Path(__file__).resolve().parent.parent / "sources"


# Fields to drop entirely (see docstring above)
DROP_FIELDS = {"claim_type", "medium", "authority_tier", "template", "slug"}

# Fields that should remain as raw scalars
SCALAR_FIELDS = {
    "title", "original_title", "publish_date", "follow_url",
    "source_type", "source_family", "relation_to_wheel",
    "stance", "licensing_status", "library_slug", "draft",
}

# Fields that are arrays of strings
ARRAY_FIELDS = {"authored_by", "topics"}


def parse_value(raw: str):
    """Parse a TOML scalar/array value into a Python value."""
    raw = raw.strip()
    # Boolean
    if raw == "true": return True
    if raw == "false": return False
    # Quoted string
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]
    # Single-quoted (uncommon in TOML, but defensive)
    if raw.startswith("'") and raw.endswith("'"):
        return raw[1:-1]
    # Array
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner: return []
        # Naïve split on commas not inside quotes — fine for our flat string arrays
        items = []
        cur = ""
        in_quote = False
        for ch in inner:
            if ch == '"' and (not cur or cur[-1] != "\\"):
                in_quote = not in_quote
                cur += ch
            elif ch == "," and not in_quote:
                items.append(cur.strip())
                cur = ""
            else:
                cur += ch
        if cur.strip():
            items.append(cur.strip())
        return [parse_value(item) for item in items]
    # Bare token
    return raw


def parse_frontmatter(md_text: str) -> dict:
    """Pull the TOML frontmatter out of a Zola markdown file."""
    m = re.match(r"\+\+\+\n(.*?)\n\+\+\+", md_text, re.DOTALL)
    if not m:
        raise ValueError("No frontmatter found")
    block = m.group(1)

    out = {}
    in_extra = False
    for line in block.split("\n"):
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        if line == "[extra]":
            in_extra = True
            continue
        # Other section headers — bail (these files don't have any in practice)
        if line.startswith("[") and line.endswith("]"):
            in_extra = False
            continue
        m = re.match(r"^([a-z_]+)\s*=\s*(.+)$", line)
        if not m:
            continue
        key, raw_val = m.group(1), m.group(2)
        out[key] = parse_value(raw_val)
    return out


def parse_body(md_text: str) -> str:
    """Pull the markdown body (everything after the frontmatter)."""
    m = re.match(r"\+\+\+\n.*?\n\+\+\+\n(.*)$", md_text, re.DOTALL)
    return m.group(1).strip() if m else ""


def md_to_record(path: Path) -> dict:
    text = path.read_text()
    fm = parse_frontmatter(text)
    body = parse_body(text)
    slug = path.stem

    # Description: prefer body if present (the rich one), fall back to frontmatter description
    description_en = body if body else fm.get("description", "")

    record = {
        "id": slug,
        "title": fm.get("title", ""),
        "description": {"en": description_en},
    }

    # Optional original_title
    if "original_title" in fm:
        record["original_title"] = fm["original_title"]

    # Arrays
    for field in ARRAY_FIELDS:
        if field in fm:
            record[field] = fm[field]

    # Scalars (after dropping the consolidated/removed ones)
    for field in SCALAR_FIELDS:
        if field in fm and field not in DROP_FIELDS:
            record[field] = fm[field]

    # Always preserve the legacy URL as an alias
    record["aliases"] = [f"/resources/{slug}/"]

    return record


def main():
    if not RESOURCES.exists():
        print(f"ERROR: resources dir not found: {RESOURCES}", file=sys.stderr)
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(p for p in RESOURCES.glob("*.md") if p.stem != "_index")
    print(f"Migrating {len(files)} files…")

    written = 0
    errors = []
    for path in files:
        try:
            record = md_to_record(path)
            out_path = OUT_DIR / f"{record['id']}.json"
            out_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
            written += 1
        except Exception as e:
            errors.append((path.name, str(e)))

    print(f"  wrote: {written}")
    if errors:
        print(f"  errors: {len(errors)}")
        for name, err in errors:
            print(f"    {name}: {err}")


if __name__ == "__main__":
    main()
