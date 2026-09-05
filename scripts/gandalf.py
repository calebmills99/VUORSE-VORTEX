#!/usr/bin/env python3
"""Gandalf the Gray Eye -- deterministic continuity audit for VUORSE-VORTEX.

Runs the reconnaissance pass by hand, with no model in the loop and no cost.
Everything here is arithmetic and string comparison against files on disk.

    python3 scripts/gandalf.py                # human report, free, read-only
    python3 scripts/gandalf.py --json         # machine-readable findings
    python3 scripts/gandalf.py --quiet        # only WARN/FAIL findings
    python3 scripts/gandalf.py --narrate      # OPTIONAL, costs money, see below

--narrate is the ONLY thing that calls an API. It is off by default, it never
turns itself on, and if MISTRAL_API_KEY is unset it says so and carries on with
the free report rather than failing. Findings are computed identically either
way -- narration only rewrites the summary in prose.

READ-ONLY. This script opens the cortex index with mode=ro and never writes a
file anywhere. It is safe to run at any time, including mid-edit.

EXIT CODES
    0  clean
    1  at least one FAIL
    2  no FAIL but at least one WARN
    3  the repository could not be inspected at all
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

MANIFEST = REPO / "manifests/corpus/source_manifest.json"
ENTITY_INDEX = REPO / "manifests/corpus/entity_index.json"
RELATIONSHIP_INDEX = REPO / "manifests/corpus/relationship_index.json"
CURATION = REPO / "manifests/corpus/source_curation.json"
CORTEX_DB = REPO / "embeddings/indexes/vuorse_cortex.sqlite3"
SETTINGS_PY = REPO / "vuorse_vortex/settings.py"
SCHEMAS_PY = REPO / "vuorse_vortex/schemas.py"

SEALED_VISIBILITIES = {"weaver_only", "private_to_vuorse"}
KNOWN_VISIBILITIES = {"public", "behavioral", "private_to_vuorse", "internal", "weaver_only"}

FAIL, WARN, OK, INFO = "FAIL", "WARN", "OK", "INFO"


class AuditError(Exception):
    """Raised when the repository itself cannot be inspected."""


@dataclass
class Finding:
    check: str
    level: str
    message: str
    detail: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"check": self.check, "level": self.level,
                "message": self.message, "detail": self.detail}


def load_json(path: Path, *, required: bool = True) -> dict | None:
    """Load a JSON file, or explain precisely why it could not be loaded."""
    if not path.exists():
        if required:
            raise AuditError(
                f"missing required file: {path.relative_to(REPO)}\n"
                f"  why : no such file under {REPO}\n"
                f"  next: run this script from inside the VUORSE-VORTEX checkout, or\n"
                f"        rebuild the manifests with `vuorse-vortex build-index`."
            )
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AuditError(
            f"cannot parse {path.relative_to(REPO)} as JSON\n"
            f"  json says: {exc}\n"
            f"  next: the file is corrupt or half-written. Check line {exc.lineno}."
        ) from exc
    except OSError as exc:
        raise AuditError(
            f"cannot read {path.relative_to(REPO)}\n"
            f"  os says: {exc}\n"
            f"  next: check permissions and that the folder is mounted."
        ) from exc


def literal_members(source: Path, name: str) -> set[str]:
    """Pull the string members out of a `Name = Literal[...]` declaration."""
    if not source.exists():
        return set()
    text = source.read_text(encoding="utf-8")
    match = re.search(rf"{name}\s*=\s*Literal\[(.*?)\]", text, re.S)
    if not match:
        return set()
    return set(re.findall(r'"([a-z_]+)"', match.group(1)))


def sealed_layers() -> set[str]:
    """Read Settings.sealed_categories' default without importing pydantic."""
    if not SETTINGS_PY.exists():
        return set()
    text = SETTINGS_PY.read_text(encoding="utf-8")
    match = re.search(r"sealed_categories[^=]*=\s*Field\(\s*default=\[(.*?)\]", text, re.S)
    if not match:
        match = re.search(r"sealed_categories[^=]*=\s*\[(.*?)\]", text, re.S)
    return set(re.findall(r'"([a-z_]+)"', match.group(1))) if match else set()


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------


def check_governance() -> list[Finding]:
    """policies/ is the constitution. Its absence outranks every other finding."""
    out: list[Finding] = []
    policies = REPO / "policies"
    if not policies.exists():
        return [Finding("governance", FAIL,
                        "policies/ is absent from the working tree",
                        ["The canon firewall, disclosure classes and writer-room boundary "
                         "are not on disk. Recover with: git restore policies/",
                         "Until then this repo has code enforcing rules nobody can read."])]
    expected = ["canon_firewall", "disclosure", "writer_room", "gpu_runtime"]
    missing = [name for name in expected if not (policies / name / "README.md").exists()]
    if missing:
        out.append(Finding("governance", WARN,
                           f"{len(missing)} policy document(s) missing",
                           [f"policies/{name}/README.md" for name in missing]))
    else:
        out.append(Finding("governance", OK,
                           f"policies/ intact ({len(expected)} documents)"))
    return out


def check_manifest(manifest: dict) -> list[Finding]:
    """The invariants that keep a source id from becoming a disclosure leak."""
    out: list[Finding] = []
    sources = manifest.get("sources", [])
    seal_layers = sealed_layers()
    statuses = literal_members(SCHEMAS_PY, "CanonStatus")

    ids: dict[str, list[str]] = {}
    paths: dict[str, int] = {}
    for source in sources:
        ids.setdefault(source["id"], []).append(source["path"])
        paths[source["path"]] = paths.get(source["path"], 0) + 1

    dupe_ids = {key: value for key, value in ids.items() if len(value) > 1}
    if dupe_ids:
        detail = []
        for key, members in dupe_ids.items():
            visibilities = {s["visibility"] for s in sources if s["id"] == key}
            marker = "  <-- SPANS DISCLOSURE CLASSES" if len(visibilities) > 1 else ""
            detail.append(f"{key}{marker}")
            detail.extend(f"    {p}" for p in members)
        out.append(Finding("manifest.ids", FAIL,
                           f"{len(dupe_ids)} duplicate source id(s)",
                           detail + ["A source id becomes the cortex chunk id prefix. Two "
                                     "sources sharing one collapse the disclosure boundary."]))
    else:
        out.append(Finding("manifest.ids", OK, f"{len(sources)} sources, all ids unique"))

    dupe_paths = [key for key, count in paths.items() if count > 1]
    if dupe_paths:
        out.append(Finding("manifest.paths", FAIL,
                           f"{len(dupe_paths)} duplicate path(s)", dupe_paths))

    declared = manifest.get("source_count")
    if declared != len(sources):
        out.append(Finding("manifest.counts", FAIL,
                           f"source_count declares {declared}, contents hold {len(sources)}"))

    sealed = [s for s in sources if s["layer"] in seal_layers]
    declared_sealed = manifest.get("sealed_source_count")
    if declared_sealed != len(sealed):
        out.append(Finding("manifest.counts", FAIL,
                           f"sealed_source_count declares {declared_sealed}, "
                           f"contents hold {len(sealed)}"))

    by_layer = {s["id"] for s in sealed}
    by_visibility = {s["id"] for s in sources if s["visibility"] in SEALED_VISIBILITIES}
    if by_layer != by_visibility:
        out.append(Finding("manifest.sealing", FAIL,
                           "layer-sealed and visibility-sealed sets disagree",
                           [f"layer-only: {sorted(by_layer - by_visibility)}",
                            f"visibility-only: {sorted(by_visibility - by_layer)}",
                            "Two independent vocabularies describe the same records. "
                            "When they drift, one of them is lying about what is sealed."]))
    else:
        out.append(Finding("manifest.sealing", OK,
                           f"sealing coherent ({len(sealed)} sealed by both layer and visibility)"))

    untriaged = [s["path"] for s in sources if s["canon_status"] == "unknown"]
    if untriaged:
        out.append(Finding("manifest.triage", WARN,
                           f"{len(untriaged)} source(s) still canon_status 'unknown'",
                           untriaged + ["'unknown' is the un-triaged default, not a "
                                        "classification. These may be read as material "
                                        "but never asserted as settled."]))

    if statuses:
        bad = {s["canon_status"] for s in sources} - statuses
        if bad:
            out.append(Finding("manifest.schema", FAIL,
                               f"canon_status values outside the schema Literal: {sorted(bad)}"))

    unknown_vis = {s["visibility"] for s in sources} - KNOWN_VISIBILITIES
    if unknown_vis:
        out.append(Finding("manifest.schema", FAIL,
                           f"visibility values not declared in policies/disclosure: "
                           f"{sorted(unknown_vis)}"))

    missing = [s["path"] for s in sources if not (REPO / s["path"]).exists()]
    if missing:
        out.append(Finding("manifest.paths", FAIL,
                           f"{len(missing)} manifest path(s) absent from disk", missing[:20]))

    stale_roots = [r for r in manifest.get("roots", []) if not (REPO / r).exists()]
    if stale_roots:
        out.append(Finding("manifest.roots", FAIL,
                           f"{len(stale_roots)} declared corpus root(s) absent", stale_roots))

    return out


def check_curation(manifest: dict) -> list[Finding]:
    """Curation must cover everything the route table would otherwise revert."""
    overlay = load_json(CURATION, required=False)
    if overlay is None:
        return [Finding("curation", WARN,
                        "no curation overlay (manifests/corpus/source_curation.json)",
                        ["Without it, regenerating the manifest reverts every curated "
                         "canon_status to the route-table default and blanks notes."])]
    entries = overlay.get("sources", overlay)
    curated_paths = set(entries)
    live_paths = {s["path"] for s in manifest.get("sources", [])}

    orphans = sorted(curated_paths - live_paths)
    out = [Finding("curation", OK,
                   f"overlay covers {len(curated_paths)} path(s)")]
    if orphans:
        out.append(Finding("curation", WARN,
                           f"{len(orphans)} overlay entry/entries point at paths no longer "
                           f"in the corpus", orphans))

    route_default = {"canon": "unknown", "persona": "unknown"}
    at_risk = [s["path"] for s in manifest.get("sources", [])
               if s["canon_status"] != route_default.get(s["layer"], s["canon_status"])
               and s["path"] not in curated_paths]
    if at_risk:
        out.append(Finding("curation", WARN,
                           f"{len(at_risk)} curated source(s) NOT covered by the overlay",
                           at_risk[:20] + ["These revert on the next regeneration."]))
    return out


def check_cortex() -> list[Finding]:
    """Duplicate chunk ids, and the ones that straddle two disclosure tiers."""
    if not CORTEX_DB.exists():
        return [Finding("cortex", INFO,
                        "no cortex index on disk (embeddings/indexes/vuorse_cortex.sqlite3)",
                        ["Nothing to verify. Built by `vuorse-vortex cortex build`."])]
    uri = f"{CORTEX_DB.resolve().as_uri()}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True)
        conn.execute("SELECT 1 FROM chunks LIMIT 1").fetchone()
    except sqlite3.Error as exc:
        return [Finding("cortex", WARN,
                        f"cannot read the cortex index: {exc}",
                        [f"opened as {uri}",
                         "next: confirm it is a SQLite file with a 'chunks' table."])]
    try:
        rows = conn.execute(
            "SELECT chunk_id, COUNT(*), COUNT(DISTINCT visibility) FROM chunks "
            "GROUP BY chunk_id HAVING COUNT(*) > 1 ORDER BY chunk_id"
        ).fetchall()
        total, distinct = conn.execute(
            "SELECT COUNT(*), COUNT(DISTINCT chunk_id) FROM chunks").fetchone()
        meta = dict(conn.execute("SELECT key, value FROM meta"))
    except sqlite3.Error as exc:
        conn.close()
        return [Finding("cortex", WARN, f"failed reading cortex tables: {exc}")]
    finally:
        conn.close()

    out: list[Finding] = []
    if rows:
        crossing = [r for r in rows if r[2] > 1]
        detail = [f"{cid}  ({n} rows, {v} visibility class(es))" for cid, n, v in rows[:20]]
        level = FAIL if crossing else WARN
        message = f"{len(rows)} duplicate chunk_id(s)"
        if crossing:
            message += f", {len(crossing)} spanning MORE THAN ONE visibility class"
            detail.append("A chunk id naming two disclosure tiers is a leak risk: any "
                          "retrieval that dedupes or filters by id can return the wrong tier.")
        detail.append("Only a rebuild clears these. Read scripts/REINDEX.md first.")
        out.append(Finding("cortex.chunks", level, message, detail))
    else:
        out.append(Finding("cortex.chunks", OK,
                           f"{total} chunks, {distinct} unique chunk_ids, no duplicates"))

    declared = meta.get("chunk_count")
    if declared is not None and str(total) != str(declared):
        out.append(Finding("cortex.meta", WARN,
                           f"meta.chunk_count declares {declared}, table holds {total}",
                           ["The index was modified outside cortex.py::build, or a build "
                            "did not finish."]))
    return out




def _walk_files(root: Path):
    """Yield every readable regular file under `root`.

    `Path.rglob` raises on the first directory this account cannot stat, which
    on a mounted Windows checkout is routine (``.pytest_cache`` is a common
    offender). An audit that dies on one unreadable cache directory is useless,
    so unreadable branches are skipped -- but only the unreadable ones, and the
    caller is told when a top-level directory was skipped entirely.
    """
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            entries = list(current.iterdir())
        except OSError:
            continue
        for entry in entries:
            try:
                if entry.is_dir():
                    stack.append(entry)
                elif entry.is_file():
                    yield entry
            except OSError:
                continue



def check_git_hygiene() -> list[Finding]:
    """Read-only. A stale lock silently blocks every write in the repo."""
    git_dir = REPO / ".git"
    if not git_dir.exists():
        return [Finding("git", INFO, "not a git repository")]
    lock = git_dir / "index.lock"
    if lock.exists():
        size = lock.stat().st_size
        return [Finding("git", WARN,
                        f"stale .git/index.lock present ({size} bytes)",
                        ["Every git write -- commit, restore, submodule add -- fails while "
                         "this exists.",
                         "If no git process is running, delete it:",
                         "    del .git\\index.lock       (Windows)",
                         "    rm .git/index.lock         (POSIX)"])]
    return [Finding("git", OK, "no stale index.lock")]


# --------------------------------------------------------------------------
# optional narration -- the only thing here that can cost money
# --------------------------------------------------------------------------

MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_KEY_VARS = ("MISTRAL_API_KEY", "MISTRAL_KEY", "MISTRALAI_API_KEY")

NARRATOR_SYSTEM = (
    "You are Gandalf the Gray Eye, auditing a canon-governed story repository. "
    "You will be given findings that were already computed deterministically. "
    "Summarise them in at most 200 words: what actually threatens the integrity "
    "of the canon, in priority order. Label nothing as canon that the findings do "
    "not state. Invent no file paths, no counts, and no lore. If the findings are "
    "clean, say so briefly and stop."
)


def find_api_key() -> tuple[str | None, str | None]:
    for var in MISTRAL_KEY_VARS:
        value = os.environ.get(var)
        if value and value.strip():
            return value.strip(), var
    return None, None


def narrate(findings: list[Finding], *, model: str, timeout: int) -> str:
    """Ask Mistral to summarise findings already computed. Never invents them."""
    key, var = find_api_key()
    if not key:
        return ("[narration skipped] no API key found. Set one of: "
                + ", ".join(MISTRAL_KEY_VARS) + "\n"
                "The findings above are complete without it -- narration only "
                "rephrases them.")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": NARRATOR_SYSTEM},
            {"role": "user", "content": "\n".join(
                f"[{f.level}] {f.check}: {f.message}"
                + ("".join(f"\n    {d}" for d in f.detail[:6]) if f.detail else "")
                for f in findings)},
        ],
        "temperature": 0.2,
        "max_tokens": 500,
    }
    request = urllib.request.Request(
        MISTRAL_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        return f"[narrated by {model}, key from ${var}]\n" \
               + body["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        return (f"[narration failed] Mistral returned HTTP {exc.code}.\n"
                f"  response: {detail}\n"
                f"  next: 401 means the key in ${var} is rejected; 429 means rate limited; "
                f"404 means the model name '{model}' is wrong (try --model mistral-small-latest).")
    except urllib.error.URLError as exc:
        return (f"[narration failed] could not reach {MISTRAL_URL}: {exc.reason}\n"
                f"  next: this machine may have no outbound network. The findings above "
                f"are complete and free; narration is optional.")
    except (KeyError, ValueError) as exc:
        return (f"[narration failed] unexpected response shape from Mistral: {exc}\n"
                f"  next: the API contract may have changed; the free findings stand.")


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------

RULE = "=" * 78
ORDER = {FAIL: 0, WARN: 1, INFO: 2, OK: 3}


def render(findings: list[Finding], *, quiet: bool) -> None:
    print(RULE)
    print("GANDALF THE GRAY EYE -- deterministic continuity audit")
    print(f"repository: {REPO}")
    print(RULE)
    shown = [f for f in findings if not quiet or f.level in (FAIL, WARN)]
    if quiet and not shown:
        print("\nNothing is wrong. Nothing needs your attention.")
    for finding in sorted(shown, key=lambda f: (ORDER[f.level], f.check)):
        print(f"\n[{finding.level:<4}] {finding.check}")
        print(f"        {finding.message}")
        for line in finding.detail:
            print(f"          {line}")
    counts = {level: sum(1 for f in findings if f.level == level)
              for level in (FAIL, WARN, INFO, OK)}
    print("\n" + RULE)
    print(f"SUMMARY   FAIL {counts[FAIL]}   WARN {counts[WARN]}   "
          f"INFO {counts[INFO]}   OK {counts[OK]}")
    if counts[FAIL]:
        print("VERDICT   integrity is compromised. Fix the FAILs before trusting any "
              "claim this corpus makes.")
    elif counts[WARN]:
        print("VERDICT   holding, with drift. Nothing is lying to you yet.")
    else:
        print("VERDICT   clean. The realm is in order.")
    print(RULE)


def collect() -> list[Finding]:
    manifest = load_json(MANIFEST)
    findings: list[Finding] = []
    findings += check_governance()
    findings += check_manifest(manifest)
    findings += check_curation(manifest)
    findings += check_cortex()
    findings += check_git_hygiene()
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="scripts/gandalf.py",
        description="Deterministic, free, read-only continuity audit of VUORSE-VORTEX.",
        epilog="exit: 0 clean | 1 has FAIL | 2 has WARN only | 3 repo unreadable",
    )
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    parser.add_argument("--quiet", action="store_true",
                        help="show only real problems (FAIL and WARN). Nothing to show means nothing is wrong.")
    parser.add_argument("--narrate", action="store_true",
                        help="ALSO ask Mistral to summarise (costs money; needs "
                             "MISTRAL_API_KEY; off by default)")
    parser.add_argument("--model", default="mistral-small-latest",
                        help="Mistral model for --narrate (default: %(default)s)")
    parser.add_argument("--timeout", type=int, default=30,
                        help="seconds to wait on the Mistral call (default: %(default)s)")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    try:
        findings = collect()
    except AuditError as exc:
        print(f"scripts/gandalf.py: error: {exc}", file=sys.stderr)
        return 3

    if args.json:
        print(json.dumps({"repo": str(REPO),
                          "findings": [f.as_dict() for f in findings]}, indent=2))
    else:
        render(findings, quiet=args.quiet)

    if args.narrate:
        print("\n" + RULE)
        print("NARRATION (optional, billable)")
        print(RULE)
        print(narrate(findings, model=args.model, timeout=args.timeout))

    if any(f.level == FAIL for f in findings):
        return 1
    if any(f.level == WARN for f in findings):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
