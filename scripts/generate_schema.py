"""Regenerate the published JSON Schema from the Pydantic source of truth.

The Pydantic ``MemoryRecord`` model in ``src/vuorse_vortex/schemas.py`` is the
canonical contract for VUORSE memory records. The JSON Schema file at
``schemas/vuorse_cloud_memory_record.schema.json`` is consumed by external
validators and must stay byte-identical to what Pydantic would emit.

Run this script whenever the Pydantic models change. The test suite enforces
alignment via ``tests/test_jsonl_contract.py::test_published_schema_matches_pydantic_source``
— it will fail loudly if the on-disk schema drifts away from Pydantic.

Usage:
    uv run scripts/generate_schema.py            # write the schema file
    uv run scripts/generate_schema.py --check    # exit non-zero if drifted
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from vuorse_vortex.schemas import MemoryRecord

SCHEMA_ID = "https://vuorse-vortex.local/schemas/vuorse_cloud_memory_record.schema.json"
SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"
SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent
    / "schemas"
    / "vuorse_cloud_memory_record.schema.json"
)


def build_schema() -> dict[str, Any]:
    """Return the JSON Schema dict generated from the Pydantic source of truth.

    Pydantic emits Draft 2020-12-compatible schemas but does not set ``$schema``
    or ``$id``. We prepend both so the published file is a complete standalone
    schema, then merge in everything Pydantic produced verbatim.
    """
    pyd_schema = MemoryRecord.model_json_schema()
    return {
        "$schema": SCHEMA_DIALECT,
        "$id": SCHEMA_ID,
        **pyd_schema,
    }


def serialize(schema: dict[str, Any]) -> str:
    """Format the schema for on-disk storage. Trailing newline keeps POSIX tools happy."""
    return json.dumps(schema, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if the on-disk schema would change; do not write.",
    )
    args = parser.parse_args(argv)

    generated = serialize(build_schema())

    if args.check:
        existing = SCHEMA_PATH.read_text(encoding="utf-8") if SCHEMA_PATH.exists() else ""
        if existing != generated:
            sys.stderr.write(
                f"Schema drift detected at {SCHEMA_PATH}. "
                "Re-run scripts/generate_schema.py to regenerate.\n"
            )
            return 1
        return 0

    SCHEMA_PATH.write_text(generated, encoding="utf-8")
    print(f"Wrote {SCHEMA_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
