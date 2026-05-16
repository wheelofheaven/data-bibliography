# Wheel of Heaven Bibliography

Structured bibliography records for [Wheel of Heaven](https://www.wheelofheaven.world) — every source used or cited across the project, with the source-program metadata that travels with it (authority, stance, relation to the canon, licensing).

Powers `/sources/` on the site and inline citations from `data-content/` wiki and article entries.

## Repo layout

```
data-bibliography/
├── README.md
├── LICENSE                       (CC0-1.0)
├── schema/
│   └── source.schema.json        # JSON Schema for source records
├── sources/                      # one JSON file per source, keyed by id
│   ├── book-of-enoch.json
│   ├── book-of-mormon.json
│   └── …
└── index.json                    # generated; lists every source with id + title + family for fast lookup
```

## Naming context — three repos, three roles

- **`data-sources`** — raw upstream material: PDFs, EPUBs, scans
- **`data-library`** — processed digitized texts, ready to read on the site
- **`data-bibliography`** *(this repo)* — citation records / source-program metadata

A book can appear in all three: its scan in `data-sources`, its digitized text in `data-library`, and its bibliographic record in `data-bibliography` (with a `library_slug` cross-link).

## Source record schema

See [`schema/source.schema.json`](schema/source.schema.json) for the full JSON Schema. A typical record:

```json
{
  "id": "book-of-enoch",
  "title": "Book of Enoch",
  "original_title": "1 Enoch",
  "description": {
    "en": "The Book of Enoch is an ancient Hebrew apocalyptic religious text…"
  },
  "authored_by": ["Enoch (ascribed to)"],
  "publish_date": "-300?",
  "follow_url": "https://sacred-texts.com/bib/boe/index.htm",
  "source_type": "scripture",
  "source_family": "second_temple",
  "relation_to_wheel": "comparative_primary",
  "stance": "neutral",
  "licensing_status": "public_domain",
  "topics": ["Religion", "Mythology", "The Tradition"],
  "library_slug": "book-of-enoch",
  "aliases": ["/resources/book-of-enoch/"]
}
```

### Field reference

| Field | Type | Notes |
|---|---|---|
| `id` | string | Stable kebab-case slug; used in citations. Matches the filename (`{id}.json`). |
| `title` | string | Display title in the project's primary language (English). |
| `original_title` | string · optional | Native-language title for translated works. |
| `description` | object | Keyed by language code (`en`, `de`, …); `en` is required. |
| `authored_by` | array of strings | Author / attribution list. |
| `publish_date` | string · optional | Freeform; supports BCE notation and approximations (`-300?`, `1974`, `c. 1850`). |
| `follow_url` | string · optional | Canonical external URL for the source. |
| `source_type` | enum | See enum list below. |
| `source_family` | enum | Tradition or domain. See enum list below. |
| `relation_to_wheel` | enum | How the project uses this source. See enum list below. |
| `stance` | enum | `neutral` · `supportive` · `critical` |
| `licensing_status` | enum | `public_domain` · `licensed` · `unknown` |
| `topics` | array of strings | Freeform tag list. |
| `library_slug` | string · optional | Slug in `data-library` for digitized texts (bidirectional). |
| `aliases` | array of strings · optional | Legacy URLs preserved for reference. Redirects themselves live in `static/_redirects` in the site repo. |
| `draft` | boolean · optional | `true` hides from public surfaces. |

### Enums

**`source_type`**
`academic_monograph` · `academic_article` · `scripture` · `myth_text` ·
`encyclopedia` · `commentary` · `documentary` · `official_document` ·
`fiction` · `lecture` · `web_resource` · `podcast` · `manifesto`

**`source_family`**
`raelian` · `abrahamic` · `mesopotamian` · `second_temple` · `mormon` ·
`bahai` · `caodaist` · `oomoto` · `iranian` · `western_esoteric` ·
`archaeoastronomy` · `neo_euhemerism` · `criticism` · `science` ·
`supplementary`

**`relation_to_wheel`**
`foundational` · `comparative_primary` · `scholarly_context` ·
`scientific_context` · `critical_context` · `supplementary`

## index.json

Generated from the per-source files. Each entry is a thin pointer:

```json
[
  {"id": "book-of-enoch", "title": "Book of Enoch", "source_family": "second_temple", "relation_to_wheel": "comparative_primary"},
  …
]
```

Regenerate with:

```bash
python3 scripts/build-index.py
```

## How records get edited

- Hand-edit a `sources/{id}.json` file directly.
- New record: copy an existing file, change `id`, `title`, `description`, etc., update `index.json`.
- Validate with the JSON Schema (any IDE that understands `$schema` will type-check).

## License

CC0-1.0 — public domain dedication.
