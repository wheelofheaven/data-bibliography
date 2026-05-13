#!/usr/bin/env python3
"""
Validate every record in sources/*.json against schema/source.schema.json.

Uses the `jsonschema` package if available; falls back to a minimal
hand-rolled check otherwise so the validator runs even in a bare environment.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = ROOT / "sources"
SCHEMA_PATH = ROOT / "schema" / "source.schema.json"


def validate_with_jsonschema(schema, record, name):
    import jsonschema  # type: ignore
    try:
        jsonschema.validate(instance=record, schema=schema)
        return []
    except jsonschema.exceptions.ValidationError as e:
        return [f"{name}: {e.message} (at {'.'.join(map(str, e.absolute_path))})"]


def validate_basic(schema, record, name):
    """Minimal fallback: required fields + enum membership + id pattern."""
    errs = []
    # required
    for field in schema.get("required", []):
        if field not in record:
            errs.append(f"{name}: missing required field '{field}'")

    # id pattern
    if "id" in record:
        import re
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", record["id"]):
            errs.append(f"{name}: id '{record['id']}' does not match kebab-case pattern")

    # enums
    for field, prop in schema.get("properties", {}).items():
        if field in record and "enum" in prop:
            if record[field] not in prop["enum"]:
                errs.append(
                    f"{name}: {field}='{record[field]}' not in enum {prop['enum']}"
                )

    # filename matches id
    expected = record.get("id", "") + ".json"
    if name != expected:
        errs.append(f"{name}: filename does not match id (expected {expected})")

    return errs


def main():
    schema = json.loads(SCHEMA_PATH.read_text())
    try:
        import jsonschema  # noqa: F401
        validator = validate_with_jsonschema
        backend = "jsonschema"
    except ImportError:
        validator = validate_basic
        backend = "fallback"

    files = sorted(SOURCES_DIR.glob("*.json"))
    print(f"Validating {len(files)} records (backend: {backend})…")

    all_errs = []
    for path in files:
        record = json.loads(path.read_text())
        errs = validator(schema, record, path.name)
        all_errs.extend(errs)

    if all_errs:
        print(f"  FAIL: {len(all_errs)} error(s)")
        for e in all_errs:
            print(f"  - {e}")
        sys.exit(1)
    print(f"  OK")


if __name__ == "__main__":
    main()
