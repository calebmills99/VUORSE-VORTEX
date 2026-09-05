from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
COMPETITION_ROOT = PACKAGE_ROOT / "evidence" / "competition"
WORK_ROOT = COMPETITION_ROOT / "work"
OUTPUTS_ROOT = COMPETITION_ROOT / "outputs"
PROMPTS_ROOT = COMPETITION_ROOT / "prompts"
ORIGINAL_WORKSPACE = Path(r"C:\Users\caleb\Documents\Codex\2026-08-09\new-chat")
sys.path.insert(0, str(ORIGINAL_WORKSPACE / "work" / "python-packages"))
sys.path.insert(
    0,
    str(
        Path(
            r"C:\Users\caleb\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\Lib\site-packages"
        )
    ),
)
sys.path.insert(0, str(WORK_ROOT))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def sha256_text(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def slug(model: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", model)


def main() -> int:
    exposure_module = load_module(
        "run_charter_exposure", WORK_ROOT / "run_charter_exposure.py"
    )
    identity_module = load_module(
        "run_identity_ceremony", WORK_ROOT / "run_identity_ceremony.py"
    )

    exposure_rows = read_jsonl(
        OUTPUTS_ROOT / "charter-exposure" / "receipts.jsonl"
    )
    identity_rows = read_jsonl(
        OUTPUTS_ROOT / "identity-ceremony" / "receipts.jsonl"
    )
    registry = json.loads(
        (OUTPUTS_ROOT / "identity-ceremony" / "identity-registry.json").read_text(
            encoding="utf-8"
        )
    )
    charter = (
        OUTPUTS_ROOT / "charter-exposure" / "charter-extracted.txt"
    ).read_text(encoding="utf-8")

    charter_prompt_audits = []
    identity_prompt_audits = []
    for directory in (PROMPTS_ROOT / "charter", PROMPTS_ROOT / "identity"):
        directory.mkdir(parents=True, exist_ok=True)

    for row in exposure_rows:
        if not row.get("prompt_sha256"):
            continue
        prompt = exposure_module.make_prompt(
            int(row["contestant_number"]), row["model"], row["version"], charter
        )
        calculated = sha256_text(prompt)
        name = f"contestant-{int(row['contestant_number']):02d}-{slug(row['model'])}.txt"
        destination = PROMPTS_ROOT / "charter" / name
        destination.write_text(prompt, encoding="utf-8")
        charter_prompt_audits.append(
            {
                "contestant_number": row["contestant_number"],
                "model": row["model"],
                "logged_sha256": row["prompt_sha256"],
                "reconstructed_sha256": calculated,
                "hash_matches": calculated == row["prompt_sha256"],
                "contains_velvet": "velvet" in prompt.casefold(),
                "contains_github": "github" in prompt.casefold(),
                "contains_repo_name": "vuorse-vortex" in prompt.casefold(),
                "saved_as": str(destination.relative_to(PACKAGE_ROOT)),
            }
        )

    exposure_by_number = {
        int(row["contestant_number"]): row
        for row in exposure_rows
        if row.get("status") == "exposed"
    }
    for row in identity_rows:
        number = int(row["contestant_number"])
        contestant = exposure_by_number[number]
        prompt = identity_module.identity_prompt(contestant)
        calculated = sha256_text(prompt)
        name = f"contestant-{number:02d}-{slug(row['model'])}.txt"
        destination = PROMPTS_ROOT / "identity" / name
        destination.write_text(prompt, encoding="utf-8")
        identity_prompt_audits.append(
            {
                "contestant_number": number,
                "model": row["model"],
                "logged_sha256": row["prompt_sha256"],
                "reconstructed_sha256": calculated,
                "hash_matches": calculated == row["prompt_sha256"],
                "contains_velvet": "velvet" in prompt.casefold(),
                "contains_github": "github" in prompt.casefold(),
                "contains_repo_name": "vuorse-vortex" in prompt.casefold(),
                "saved_as": str(destination.relative_to(PACKAGE_ROOT)),
            }
        )

    tiebreaks = registry.get("tiebreaks", [])
    for row in tiebreaks:
        prompt = identity_module.tiebreak_prompt(
            int(row["contestant_number"]), row["previous_drag_name"]
        )
        (PROMPTS_ROOT / "tiebreak-contestant-23.txt").write_text(
            prompt, encoding="utf-8"
        )

    original_identities = [
        row.get("parsed_identity", {})
        for row in identity_rows
        if row.get("status") == "identity_received"
    ]
    original_names = [row.get("drag_name", "") for row in original_identities]
    canonical_names = [row.get("drag_name", "") for row in registry.get("queens", [])]
    response_corpus = "\n".join(row.get("raw_response", "") for row in identity_rows)
    terms = [
        "velvet",
        "archive",
        "vuorse",
        "hooplehopper",
        "federstahl",
        "slayton",
        "thread",
        "mirror",
        "cosmic",
        "golden",
        "winger",
        "dust",
        "seam",
        "charter",
        "neon",
        "cathedral",
        "chrome",
        "hex",
        "mirage",
        "voltage",
        "siren",
    ]
    name_tokens = Counter(
        token.casefold()
        for name in original_names
        for token in re.findall(r"[A-Za-z0-9]+", name)
    )

    clean_md = (PACKAGE_ROOT / "evidence" / "source-files" / "Charter.md").read_text(
        encoding="utf-8-sig"
    )
    dirty_md = (
        PACKAGE_ROOT / "evidence" / "source-files" / "TheCharter.md"
    ).read_text(encoding="utf-8-sig")
    normalize = lambda text: text.replace("\r\n", "\n").strip()

    analysis = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "charter_prompt_count": len(charter_prompt_audits),
        "charter_prompt_hash_matches": sum(
            row["hash_matches"] for row in charter_prompt_audits
        ),
        "identity_prompt_count": len(identity_prompt_audits),
        "identity_prompt_hash_matches": sum(
            row["hash_matches"] for row in identity_prompt_audits
        ),
        "prompt_audits": {
            "charter": charter_prompt_audits,
            "identity": identity_prompt_audits,
        },
        "original_identity_count": len(original_names),
        "original_names": original_names,
        "original_velvet_names": [
            name for name in original_names if "velvet" in name.casefold()
        ],
        "original_velvet_name_count": sum(
            "velvet" in name.casefold() for name in original_names
        ),
        "canonical_names": canonical_names,
        "canonical_velvet_names": [
            name for name in canonical_names if "velvet" in name.casefold()
        ],
        "canonical_velvet_name_count": sum(
            "velvet" in name.casefold() for name in canonical_names
        ),
        "duplicate_original_names": [
            name for name, count in Counter(original_names).items() if count > 1
        ],
        "name_token_counts": dict(name_tokens.most_common()),
        "identity_response_term_counts": {
            term: response_corpus.casefold().count(term) for term in terms
        },
        "source_comparison": {
            "clean_characters": len(normalize(clean_md)),
            "the_charter_characters": len(normalize(dirty_md)),
            "the_charter_starts_with_clean_charter": normalize(dirty_md).startswith(
                normalize(clean_md)
            ),
            "clean_velvet_count": normalize(clean_md).casefold().count("velvet"),
            "the_charter_velvet_count": normalize(dirty_md).casefold().count(
                "velvet"
            ),
        },
    }
    (COMPETITION_ROOT / "analysis.json").write_text(
        json.dumps(analysis, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {key: value for key, value in analysis.items() if key != "prompt_audits"},
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
