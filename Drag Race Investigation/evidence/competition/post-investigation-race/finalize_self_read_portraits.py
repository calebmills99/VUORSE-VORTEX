from __future__ import annotations

import hashlib
import json
from pathlib import Path


WORKSPACE = Path(r"C:\Users\caleb\Documents\Codex\2026-08-09\new-chat")
DIR = WORKSPACE / "outputs" / "reading-challenge" / "cp-17r-self-read"
REFLECTIONS = DIR / "reflections.json"
PORTRAIT_DIR = DIR / "portraits"
MANIFEST = DIR / "portrait-manifest.json"

FILES = {
    "Ophelia Overclock": "01-ophelia-overclock.png",
    "Velvet Vespers": "02-velvet-vespers.png",
    "Opaline Riot": "03-opaline-riot.png",
    "Saint Static": "04-saint-static.png",
    "Mercy Misdemeanor": "05-mercy-misdemeanor.png",
}


def main() -> int:
    if MANIFEST.exists():
        raise RuntimeError("Refusing to overwrite the portrait manifest")
    doc = json.loads(REFLECTIONS.read_text(encoding="utf-8"))
    portraits = []
    for row in doc["reflections"]:
        name = row["drag_name"]
        filename = FILES[name]
        path = PORTRAIT_DIR / filename
        digest = hashlib.sha256(path.read_bytes()).hexdigest().upper()
        entry = {
            "contestant_number": row["contestant_number"],
            "drag_name": name,
            "file": filename,
            "sha256": digest,
            "self_read": row["parsed"]["self_read"],
            "what_i_failed_to_accomplish": row["parsed"]["what_i_failed_to_accomplish"],
            "self_caption": row["parsed"]["self_caption"],
            "portrait_concept": row["parsed"]["portrait_concept"],
        }
        portraits.append(entry)
        row["portrait_file"] = f"portraits/{filename}"
        row["portrait_sha256"] = digest

    manifest = {
        "status": "complete",
        "checkpoint": "CP-17R",
        "name": "Read Yourself: Self-Portrait",
        "replaces": "CP-17 The Latency Library Is Open",
        "generation_mode": "built-in imagegen",
        "style_direction": "Original caricatures using classic irreverent American satirical humor-magazine visual language",
        "portrait_count": len(portraits),
        "portraits": portraits,
        "judging_status": "reserved_for_CP-18R",
        "winner": None,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    doc["status"] = "complete"
    doc["portraits_complete"] = True
    doc["judging_status"] = "reserved_for_CP-18R"
    doc["winner"] = None
    REFLECTIONS.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "complete", "portrait_count": len(portraits), "judging_status": "reserved_for_CP-18R"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
