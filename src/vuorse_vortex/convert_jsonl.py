"""Utility to convert legacy JSONL records to the current MemoryRecord schema.

- Drops unknown fields.
- Fills missing required fields with sensible defaults.
- Writes a cleaned JSONL file that can be passed to `vuorse-vortex firewall`.
"""
import json
from pathlib import Path
from typing import Any, Dict

from .schemas import (
    MemoryRecord,
    MemoryMetadata,
    RetrievalMetadata,
    BehaviorPolicy,
    CanonStatus,
    Visibility,
    Layer,
)

DEFAULTS = {
    "layer": "canon",
    "record_type": "generic",
    "title": "Untitled",
    "text": "",
    "metadata": {
        "canon_status": "unknown",
        "visibility": "private_to_vuorse",
        "tags": [],
        "source_file": None,
        "section": None,
        "source_confidence": None,
        "layer_affinity": None,
    },
    "retrieval": {
        "priority": 5,
        "embedding_weight": "medium",
        "query_hints": [],
    },
    "behavior": {
        "may_state_as_fact": False,
        "may_use_for_voice": False,
        "may_reveal_to_user": False,
        "allowed_surface_form": None,
        "promotion_authority": None,
    },
}

import copy
import uuid

def normalize_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Return a dict that matches the MemoryRecord schema.
    Unknown keys are dropped; missing keys are filled from `DEFAULTS`.
    """
    normalized: Dict[str, Any] = copy.deepcopy(DEFAULTS)
    
    # Ensure ID exists
    if "id" in raw and raw["id"] is not None:
        normalized["id"] = str(raw["id"])
    else:
        normalized["id"] = str(uuid.uuid4())

    # Direct mapping for known top-level fields
    for key in ["layer", "record_type", "title", "text"]:
        if key in raw and raw[key] is not None:
            normalized[key] = raw[key]

    # Deep copy / merge dicts for nested fields if present in raw
    for key in ["metadata", "retrieval", "behavior"]:
        if key in raw and isinstance(raw[key], dict):
            for sub_k, sub_v in raw[key].items():
                if sub_v is not None:
                    normalized[key][sub_k] = sub_v

    # Map legacy fields to new schema where possible
    if "source_path" in raw and raw["source_path"] is not None:
        normalized["metadata"]["source_file"] = raw["source_path"]
    if "source_anchor" in raw and raw["source_anchor"] is not None:
        normalized["metadata"]["section"] = raw["source_anchor"]
    if "canon_tier" in raw and raw["canon_tier"] is not None:
        if raw["canon_tier"] not in normalized["metadata"]["tags"]:
            normalized["metadata"]["tags"].append(raw["canon_tier"])

    # Safely handle canon status to keep within Pydantic literals
    valid_statuses = {
        "locked",
        "draft",
        "roadmap_private",
        "synthetic_behavioral",
        "non_canon_private",
        "poetic_private",
        "system_rule",
        "unknown",
    }
    
    lbl = raw.get("canon_status_label")
    if lbl is not None:
        lbl_str = str(lbl).strip()
        lbl_lower = lbl_str.lower()
        if lbl_lower in valid_statuses:
            normalized["metadata"]["canon_status"] = lbl_lower
        else:
            normalized["metadata"]["canon_status"] = "unknown"
            if lbl_str not in normalized["metadata"]["tags"]:
                normalized["metadata"]["tags"].append(lbl_str)

    return normalized

def convert_jsonl(input_path: Path, output_path: Path) -> None:
    """Read `input_path`, normalize each line, and write to `output_path`.
    Invalid lines are logged and skipped.
    """
    with input_path.open("r", encoding="utf-8") as src, output_path.open("w", encoding="utf-8") as dst:
        for line_no, raw_line in enumerate(src, start=1):
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                data = json.loads(raw_line)
                normalized = normalize_record(data)
                MemoryRecord(**normalized)  # validate
                dst.write(json.dumps(normalized, ensure_ascii=False) + "\n")
            except Exception as exc:
                print(f"[WARN] Line {line_no} could not be converted: {exc}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert legacy VUORSE JSONL to current schema")
    parser.add_argument("input", type=Path, help="Path to the legacy JSONL file")
    parser.add_argument("output", type=Path, help="Path where the cleaned JSONL will be written")
    args = parser.parse_args()
    convert_jsonl(args.input, args.output)
    print(f"Conversion complete: {args.output}")
