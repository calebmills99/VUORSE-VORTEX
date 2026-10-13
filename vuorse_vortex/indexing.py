"""Corpus indexing: source manifests, entity indexes, relationship indexes.

The entity layer is borrowed from ``slay-cortex/src/gazetteer.py``, which was
already reading this repository's ``canon/slayverse_index.json`` from across
the drive. The matching policy travels with it and is not negotiable:

**Exact surface forms only.** No stemming, no fuzzy matching, no edit distance.
Miss Slaytonia *Verse* was lost in the Fifth Summit of Splat; Miss Slaytonia
*VUORSE* is the sixth iteration. They share the token "Slaytonia", so any fuzzy
matcher merges them and the dead one starts answering the living one's mail.
``NON_MERGEABLE`` documents the requirement and :func:`build_entity_index`
asserts it.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CANON_INDEX = Path("canon/slayverse_index.json")
SOURCE_MANIFEST_OUT = Path("manifests/corpus/source_manifest.json")
ENTITY_INDEX_OUT = Path("manifests/corpus/entity_index.json")
RELATIONSHIP_INDEX_OUT = Path("manifests/corpus/relationship_index.json")
# Hand-audited fields the disk walk cannot re-derive. Read, never written,
# by build_source_manifest -- see the "Curation overlay" section below.
SOURCE_CURATION_IN = Path("manifests/corpus/source_curation.json")


class IndexingError(Exception):
    """Raised when an index cannot be built from the sources on disk."""


class CanonIndexMissingError(IndexingError):
    """The canon index file does not exist."""


class NonMergeableCollapseError(IndexingError):
    """Two entities that must stay distinct acquired identical surface forms."""


class DuplicateSourceIdError(IndexingError):
    """Two manifest sources ended up claiming the same ``id``."""


class CurationFileError(IndexingError):
    """The curation overlay is present but cannot be read as curation."""


# ---------------------------------------------------------------------------
# Borrowed from slay-cortex: alias repairs and matching policy
# ---------------------------------------------------------------------------

# The canon index was generated from the Slayverse Canon Seed PDF and its
# generator truncated at least one alias at the first whitespace. The break is
# inherited by every regenerated copy (v1.0 / 53 entities, v1.1 / 72, v1.2 / 62),
# so it cannot be fixed by picking a newer index -- it has to be repaired here.
# Left uncorrected, the bare token "Grand" claims every "grand poetic tones"
# and "Grand Drag Queen Theory of Existence" in the corpus.
ALIAS_REPAIRS: dict[tuple[str, str], str] = {
    ("miss-slaytonia-vuorse", "Grand"): "Grand Oracle of the Velvet Archive",
}

# Surface forms that are also ordinary words. Matched case-sensitively and on
# whole-word boundaries so "Pop" (the Last of the Veincallers) does not swallow
# "pop", "popular" and "popped".
CASE_SENSITIVE_FORMS: set[str] = {
    "Pop",
    "Rolf",
    "Splat",
    "Grand",
    "Verse",
    "Thread",
    "Brand",
    "Seam",
}

# Canon-critical: these entity pairs must never be collapsed into each other.
NON_MERGEABLE: Sequence[tuple[str, str]] = (
    ("miss-slaytonia-vuorse", "miss-slaytonia-verse"),
)

# Tokens too generic to identify an entity on their own. A multi-word name that
# contains them still matches in full; this only governs the derived
# single-token layer.
TOKEN_STOPLIST: set[str] = {
    # grammar and honorifics
    "the", "of", "and", "a", "an", "in", "to", "for", "von", "der", "de", "van",
    "miss", "mister", "mrs", "ms", "dr", "doctor", "professor", "prof", "sir",
    "lord", "lady", "count", "countess", "baroness", "baron", "patroness",
    "prince", "bishop", "prince-bishop", "matriarch", "mother", "father", "widow", "sage",
    # collective nouns
    "order", "league", "institute", "society", "research", "club", "house",
    # ordinals and scale
    "first", "second", "third", "last", "new", "old", "great", "grand",
    "secret", "lower", "upper", "three", "twenty", "years", "year",
    # colours and materials
    "black", "golden", "silk", "silken", "painted", "velvet", "satin", "mink",
    "crystal", "quartz", "parchment", "paper", "powder", "dust", "ash",
    # structural and cosmological common nouns
    "book", "one", "two", "words", "concerning", "crown", "wound", "returning",
    "line", "energy", "force", "field", "state", "event", "protocol", "rite",
    "ritual", "cycle", "law", "mode", "theory", "particles", "archive",
    "cavern", "chamber", "ranch", "basin", "rift", "see", "hall", "cosmology",
    "lattice", "incident", "fracture", "burnings", "transmission",
    "persistence", "convergence", "collapse", "activation", "matrix",
    # objects and roles
    "copyist", "cat", "ring", "brand", "thread", "shard", "sigil", "codex",
    "expert", "composer", "mystic", "markswoman", "alchemist", "whisperer",
    "vessel", "steward", "weaver", "oracle", "snake", "swan", "mirror", "mask",
    "masks", "mirrors", "flame", "buttons", "arts", "seam", "veil",
    "reflection", "banshee", "bassline", "veincallers", "eleganza", "wingers",
    # texture words
    "writing", "digital", "drag", "automatic", "victorian", "faced", "born",
    "poor", "sleep", "snap", "elusive", "glam", "gothic", "quantum",
    "narrative", "truth", "post", "remembers", "handshake", "hello",
    "children", "shrouded", "patriarch", "chromatic", "echo", "reverb",
    "frequency", "intergalactic", "cosmic",
    # derived tokens that are ordinary words in a software corpus
    "architect", "archivist", "broken", "chapter", "glitch", "goddess",
    "exodus", "euphoria", "mistress", "fractures", "bookend", "weaving",
    "unmaking", "parallax", "elijah",
}


def is_distinctive(token: str) -> bool:
    """True if a bare token is rare enough to identify an entity on its own.

    All-caps coined names (VUORSE) qualify at 5 characters; everything else
    needs 6, which admits Slayton, McCullen and Hooplehopper while rejecting
    the ordinary vocabulary the stoplist does not already name.
    """
    if token.lower() in TOKEN_STOPLIST:
        return False
    if not token[:1].isalpha():
        return False
    if token.isupper() and len(token) >= 5:
        return True
    return len(token) >= 6


def tokenize_name(name: str) -> list[str]:
    """Split a canon name into candidate word tokens."""
    return re.findall(r"[A-Za-z][A-Za-z'\-]*", name)


def slugify(value: str) -> str:
    """Derive a stable, deterministic id fragment from a name or heading.

    Matches the hyphen-slug convention the canon index already uses
    (``hildebrand-von-hooplehopper``). Deterministic across reruns: the same
    input always yields the same id.
    """
    lowered = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return lowered.strip("-")


# ---------------------------------------------------------------------------
# Source routing
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Route:
    """Layer, visibility and canon status implied by a corpus location."""

    layer: str
    visibility: str
    canon_status: str
    sealed: bool = False


# Longest prefix wins. Values come from the enums in
# schemas/vuorse_cloud_memory_record.schema.json; sealed layers come from
# Settings.sealed_categories.
ROUTES: tuple[tuple[str, Route], ...] = (
    (
        "synthetic_enrichment/validated",
        Route("apocrypha", "private_to_vuorse", "synthetic_behavioral", sealed=True),
    ),
    (
        "hooplehopper_totality",
        Route("hooplehopper_totality", "weaver_only", "roadmap_private", sealed=True),
    ),
    ("roadmap", Route("roadmap_manifest", "private_to_vuorse", "roadmap_private", sealed=True)),
    ("canon", Route("canon", "public", "unknown")),
    ("schemas", Route("rule", "internal", "system_rule")),
    # Agent charters are behavioural rules, not lore. They are internal: they
    # describe how the machinery behaves, which is not a public canon fact.
    ("agents", Route("rule", "internal", "system_rule")),
    # Voice and performance direction. Usable for voice, never quotable as
    # canon fact -- hence layer 'persona' with 'behavioral' visibility.
    ("persona", Route("persona", "behavioral", "unknown")),
)

DEFAULT_ROOTS: tuple[str, ...] = (
    "canon",
    "schemas",
    "agents",
    "persona",
    "synthetic_enrichment/validated",
    "hooplehopper_totality",
    "roadmap",
)

# Never walked unless the caller explicitly opts in.
FINALE_PREFIX = "roadmap/finale"

SOURCE_TYPES: dict[str, str] = {
    ".md": "markdown",
    ".txt": "text",
    ".json": "json",
    ".jsonl": "jsonl",
    ".pdf": "pdf",
    ".yaml": "yaml",
    ".yml": "yaml",
}

_SKIP_NAMES = {".gitkeep", ".DS_Store"}
_SKIP_SUFFIXES = {".bak", ".pyc"}
_SKIP_DIR_PARTS = {"__pycache__", ".git", ".venv"}


def route_for(rel_path: str) -> Route | None:
    """Return the routing rule for a repo-relative path, longest prefix first."""
    posix = rel_path.replace("\\", "/")
    best: Route | None = None
    best_len = -1
    for prefix, route in ROUTES:
        if (posix == prefix or posix.startswith(prefix + "/")) and len(prefix) > best_len:
            best, best_len = route, len(prefix)
    return best


def iter_source_files(
    roots: Sequence[str] = DEFAULT_ROOTS,
    *,
    base: Path = Path("."),
    include_pdf: bool = False,
    include_finale: bool = False,
) -> Iterator[Path]:
    """Yield indexable files under ``roots``, in deterministic order.

    ``roadmap/finale/`` is withheld unless ``include_finale`` is set. PDFs are
    withheld unless ``include_pdf`` is set, because every markdown source in
    this repo has a derived PDF sibling and indexing both doubles the manifest
    for no retrieval gain.
    """
    for root in roots:
        root_path = base / root
        if not root_path.exists():
            continue
        for path in sorted(root_path.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(base).as_posix()
            if not include_finale and (
                rel == FINALE_PREFIX or rel.startswith(FINALE_PREFIX + "/")
            ):
                continue
            # Suffixes are compared case-folded. Book One ships as
            # `Words_of_Weaver_BOOK_ONE.MD`, and a case-sensitive check drops
            # the supreme doctrine itself out of the corpus.
            suffix = path.suffix.lower()
            if path.name in _SKIP_NAMES or suffix in _SKIP_SUFFIXES:
                continue
            if _SKIP_DIR_PARTS.intersection(path.parts):
                continue
            if suffix not in SOURCE_TYPES:
                continue
            if suffix == ".pdf" and not include_pdf:
                continue
            yield path


_MIXED_POSTURE_PREFIX = "MIXED privacy posture"


def _read_jsonl_metadata(path: Path) -> tuple[Route | None, list[str], list[str]]:
    """Read layer/visibility/canon_status off a JSONL file's own records.

    Metadata carried by the records outranks the routing table: the indexer
    preserves what a record declares rather than re-deriving it from location.

    Returns ``(route, notes, warnings)``. Warnings are kept apart from notes
    because they must outlive curation: a hand-written note may replace the
    informational ``"16 records"``, but nothing may replace a
    ``"MIXED privacy posture"`` warning.
    """
    from vuorse_vortex.settings import get_settings

    layers: set[str] = set()
    visibilities: set[str] = set()
    statuses: set[str] = set()
    count = 0
    try:
        with path.open(encoding="utf-8") as fh:
            for lineno, raw_line in enumerate(fh, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as exc:
                    return (
                        None,
                        [],
                        [
                            f"unreadable as JSONL: {path.as_posix()} line {lineno}: "
                            f"{exc.msg}; routed by location instead. Repair the line "
                            "or move the file out of the corpus roots."
                        ],
                    )
                if not isinstance(obj, dict):
                    return (
                        None,
                        [],
                        [
                            f"unreadable as JSONL: {path.as_posix()} line {lineno} is a "
                            f"{type(obj).__name__}, not a JSON object; routed by "
                            "location instead. Every JSONL record must be an object."
                        ],
                    )
                count += 1
                if isinstance(obj.get("layer"), str):
                    layers.add(obj["layer"])
                meta = obj.get("metadata")
                if isinstance(meta, dict):
                    if isinstance(meta.get("visibility"), str):
                        visibilities.add(meta["visibility"])
                    if isinstance(meta.get("canon_status"), str):
                        statuses.add(meta["canon_status"])
    except OSError as exc:
        return (
            None,
            [],
            [
                f"unreadable as JSONL: {path.as_posix()}: {exc.strerror or exc}; "
                "routed by location instead. Check the file's permissions."
            ],
        )

    notes = [f"{count} records"]
    warnings: list[str] = []
    if len(layers) > 1 or len(visibilities) > 1 or len(statuses) > 1:
        warnings.append(
            f"{_MIXED_POSTURE_PREFIX}: "
            f"layers={sorted(layers)} visibility={sorted(visibilities)} "
            f"canon_status={sorted(statuses)} -- split this file"
        )
    if len(layers) != 1 or len(visibilities) != 1 or len(statuses) != 1:
        return None, notes, warnings

    layer = layers.pop()
    sealed = layer in get_settings().sealed_categories
    return (
        Route(layer, visibilities.pop(), statuses.pop(), sealed=sealed),
        notes,
        warnings,
    )


# ---------------------------------------------------------------------------
# Curation overlay
# ---------------------------------------------------------------------------
#
# The routing table can only say what a *location* implies. It cannot know that
# `canon/artifacts/artifacts.md` is locked canon rather than a draft, and it
# cannot re-derive the provenance sentences an audit wrote into `notes`. Those
# are human judgements, so they live in their own file --
# `manifests/corpus/source_curation.json` -- keyed by repo-relative path, and
# the generated manifest is the join of the walk and that overlay.
#
# Keyed by path, not by id: an id is derived and may change; a path is the
# source's identity. Held in a separate file, not merged out of the previous
# manifest, so that curated judgement is inspectable on its own and a
# regeneration cannot quietly launder generated output into curated state.


@dataclass(frozen=True)
class Curation:
    """Hand-audited manifest fields for one source, keyed by repo-relative path."""

    canon_status: str | None = None
    notes: str | None = None


CURATION_FIELDS: tuple[str, ...] = ("canon_status", "notes")


def load_source_curation(
    curation_path: Path = SOURCE_CURATION_IN,
    *,
    base: Path = Path("."),
) -> dict[str, Curation]:
    """Load the curation overlay as ``{repo-relative path: Curation}``.

    A missing overlay is not an error -- a corpus that has never been audited
    has nothing to preserve. A *malformed* overlay is an error, because the
    failure mode this whole file exists to prevent is curated state vanishing
    without anyone being told.

    Raises:
        CurationFileError: the overlay exists but cannot be read or does not
            have the expected ``{"sources": {path: {...}}}`` shape.
    """
    target = base / curation_path
    if not target.exists():
        return {}
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CurationFileError(
            f"curation overlay unreadable: {target.as_posix()}: "
            f"{exc.strerror or exc}. Fix the file's permissions, or move it "
            "aside to regenerate the manifest without curation."
        ) from exc
    except json.JSONDecodeError as exc:
        raise CurationFileError(
            f"curation overlay is not valid JSON: {target.as_posix()} "
            f"line {exc.lineno} column {exc.colno}: {exc.msg}. "
            "Repair the JSON; the manifest is not regenerated from a file "
            "whose curated fields cannot be read."
        ) from exc

    entries = raw.get("sources") if isinstance(raw, dict) else None
    if not isinstance(entries, dict):
        raise CurationFileError(
            f"curation overlay {target.as_posix()} must be a JSON object with a "
            "'sources' object mapping repo-relative path -> "
            f"{{{', '.join(CURATION_FIELDS)}}}; found "
            f"{type(entries).__name__} for 'sources'."
        )

    curation: dict[str, Curation] = {}
    for rel, fields in entries.items():
        curation[rel] = _curation_entry(rel, fields, target)
    return curation


def _curation_entry(rel: str, fields: Any, target: Path) -> Curation:
    """Validate one overlay entry, naming the file, the key and the defect."""
    if not isinstance(fields, dict):
        raise CurationFileError(
            f"curation overlay {target.as_posix()} entry {rel!r} must be an "
            f"object of {{{', '.join(CURATION_FIELDS)}}}; found "
            f"{type(fields).__name__}."
        )
    unsupported = sorted(set(fields) - set(CURATION_FIELDS))
    if unsupported:
        raise CurationFileError(
            f"curation overlay {target.as_posix()} entry {rel!r} carries "
            f"unsupported fields {unsupported}; only {list(CURATION_FIELDS)} "
            "survive regeneration. Remove them, or the curation they hold will "
            "be silently lost on the next build."
        )
    for name in CURATION_FIELDS:
        value = fields.get(name)
        if value is not None and not isinstance(value, str):
            raise CurationFileError(
                f"curation overlay {target.as_posix()} entry {rel!r} field "
                f"{name!r} must be a string or absent; found "
                f"{type(value).__name__} ({value!r})."
            )
    return Curation(canon_status=fields.get("canon_status"), notes=fields.get("notes"))


def _mint_source_id(rel: str, claims: dict[str, list[str]]) -> tuple[str, str | None]:
    """Mint a manifest id for ``rel`` that no earlier source can already hold.

    The base id is the slugified path with its suffix removed, which is not
    injective: ``x.jsonl`` and ``x.md`` reduce to the same base. Disambiguation
    follows the convention already proven in ``walled._build_jsonl_text`` (see
    ``tests/test_walled_build.py::test_build_disambiguates_duplicate_concept_ids``):
    the first claimant keeps the base id and every later claimant takes an
    ordinal suffix starting at 2. ``iter_source_files`` walks in sorted order,
    so a given file set always yields the same ids.

    ``claims`` is mutated: it maps base id -> the paths that claimed it, in
    walk order, which is what lets the returned message name the incumbent.

    Returns ``(entry_id, collision_message)``; the message is ``None`` when the
    base id was free.

    Raises:
        IndexingError: the path carries no slug-able characters at all.
    """
    base_id = slugify(rel.rsplit(".", 1)[0])
    if not base_id:
        raise IndexingError(
            f"source path {rel!r} slugifies to an empty manifest id; a source "
            "id is the disclosure key used to build cortex chunk ids and "
            "cannot be blank. Rename the file to contain at least one "
            "alphanumeric character."
        )
    claimed = claims.setdefault(base_id, [])
    claimed.append(rel)
    if len(claimed) == 1:
        return base_id, None
    entry_id = f"{base_id}-{len(claimed)}"
    return entry_id, (
        f"{rel}: base id {base_id!r} was already claimed by {claimed[0]}; "
        f"minted {entry_id} instead"
    )


def _resolve_canon_status(
    route: Route, curated: Curation | None, *, self_declared: bool
) -> str:
    """Pick the ``canon_status`` that reaches the manifest.

    A source that declares its own status inside its records outranks the
    overlay: the overlay corrects the routing table's guesses, it does not get
    to overrule what the data says about itself. Everywhere else the overlay
    wins, because the routing table's ``"unknown"`` is a placeholder awaiting
    triage, not a classification.
    """
    if self_declared or curated is None or curated.canon_status is None:
        return route.canon_status
    return curated.canon_status


def _merge_notes(
    curated: Curation | None,
    generated: Sequence[str],
    warnings: Sequence[str],
) -> str:
    """Compose the manifest ``notes`` string for one source.

    Curated prose replaces the generated commentary -- generated notes are
    re-derivable on every build, curated provenance is not. Warnings are
    appended either way, so a curation entry can never hide the fact that a
    file mixes privacy postures or will not parse.
    """
    curated_notes = curated.notes if curated is not None else None
    body = [curated_notes] if curated_notes else list(generated)
    return "; ".join([*(note for note in body if note), *warnings])


def _assert_unique_ids(sources: Sequence[dict[str, Any]], out_path: Path | None) -> None:
    """Fail the build if two emitted sources share an ``id``.

    ``_mint_source_id`` already guarantees this. The check stays because the
    guarantee is load-bearing: ``cortex`` derives chunk ids as
    ``f"{source['id']}:{index:05d}"``, so a duplicate source id merges two
    sources into one retrieval key, and the two sources that collided in
    practice sat on opposite sides of the disclosure boundary.
    """
    by_id: dict[str, list[str]] = {}
    for source in sources:
        by_id.setdefault(str(source["id"]), []).append(str(source["path"]))
    collisions = {key: paths for key, paths in by_id.items() if len(paths) > 1}
    if not collisions:
        return
    destination = out_path.as_posix() if out_path is not None else "<in-memory manifest>"
    raise DuplicateSourceIdError(
        f"build_source_manifest minted duplicate source ids while building "
        f"{destination}: {collisions}. A duplicate id collapses the disclosure "
        "boundary, because cortex chunk ids are '<source id>:<index>'. This is "
        "a defect in _mint_source_id, not something to patch out by hand in "
        "the manifest."
    )


@dataclass
class ManifestReport:
    """What a source-manifest pass scanned, wrote, and refused to guess at."""

    scanned: int = 0
    entries: int = 0
    sealed_entries: int = 0
    unrouted: list[str] = field(default_factory=list)
    stale_paths: list[str] = field(default_factory=list)
    mixed_files: list[str] = field(default_factory=list)
    disambiguated_ids: list[str] = field(default_factory=list)
    curated_paths: list[str] = field(default_factory=list)
    orphaned_curation: list[str] = field(default_factory=list)


def build_source_manifest(
    roots: Sequence[str] = DEFAULT_ROOTS,
    out_path: Path | None = SOURCE_MANIFEST_OUT,
    *,
    base: Path = Path("."),
    include_pdf: bool = False,
    include_finale: bool = False,
    curation_path: Path | None = SOURCE_CURATION_IN,
) -> tuple[dict[str, Any], ManifestReport]:
    """Walk the corpus and emit ``manifests/corpus/source_manifest.json``.

    Each entry carries the eight fields the indexer agent contract names:
    ``id``, ``path``, ``title``, ``layer``, ``visibility``, ``canon_status``,
    ``source_type``, ``notes``. Nothing is invented: a file whose location does
    not match a known route is reported in ``unrouted`` rather than guessed at.

    The walk decides which sources exist; the curation overlay at
    ``curation_path`` decides what the audited ``canon_status`` and ``notes``
    are for the ones that do. New files therefore appear, deleted files drop,
    and hand-triaged judgement survives -- overlay entries whose path no longer
    exists are reported in ``ManifestReport.orphaned_curation`` rather than
    dropped in silence. Pass ``curation_path=None`` to see the raw walk.

    Raises:
        CurationFileError: the curation overlay is present but malformed.
        DuplicateSourceIdError: two sources ended up sharing an id.
        IndexingError: a source path cannot produce a non-empty id.
    """
    report = ManifestReport()
    sources: list[dict[str, Any]] = []
    id_claims: dict[str, list[str]] = {}
    curation = (
        load_source_curation(curation_path, base=base) if curation_path is not None else {}
    )

    for root in roots:
        if not (base / root).exists():
            report.stale_paths.append(f"{root} (declared root does not exist)")

    for path in iter_source_files(
        roots, base=base, include_pdf=include_pdf, include_finale=include_finale
    ):
        report.scanned += 1
        rel = path.relative_to(base).as_posix()
        notes: list[str] = []
        warnings: list[str] = []

        suffix = path.suffix.lower()
        route: Route | None = None
        self_declared = False
        if suffix == ".jsonl":
            route, jsonl_notes, jsonl_warnings = _read_jsonl_metadata(path)
            notes.extend(jsonl_notes)
            warnings.extend(jsonl_warnings)
            self_declared = route is not None
            if route is None and any(
                warning.startswith(_MIXED_POSTURE_PREFIX) for warning in jsonl_warnings
            ):
                report.mixed_files.append(rel)
        if route is None:
            route = route_for(rel)
        if route is None:
            report.unrouted.append(rel)
            continue

        entry_id, collision = _mint_source_id(rel, id_claims)
        if collision is not None:
            report.disambiguated_ids.append(collision)

        curated = curation.get(rel)
        if curated is not None:
            report.curated_paths.append(rel)

        sources.append(
            {
                "id": entry_id,
                "path": rel,
                "title": path.stem.replace("_", " ").strip(),
                "layer": route.layer,
                "visibility": route.visibility,
                "canon_status": _resolve_canon_status(
                    route, curated, self_declared=self_declared
                ),
                "source_type": SOURCE_TYPES[suffix],
                "notes": _merge_notes(curated, notes, warnings),
            }
        )
        report.entries += 1
        if route.sealed:
            report.sealed_entries += 1

    _assert_unique_ids(sources, out_path)
    emitted = {str(source["path"]) for source in sources}
    report.orphaned_curation = sorted(set(curation) - emitted)

    # Stale paths the original agent spec called out, verified against disk.
    for suspect in ("canon/timeline", "canon/places", "policies"):
        target = base / suspect
        if not target.exists():
            report.stale_paths.append(f"{suspect} (referenced by agent spec, not on disk)")
        elif target.is_dir() and not any(p.is_dir() for p in target.iterdir()):
            files = [
                p.name
                for p in target.iterdir()
                if p.is_file() and p.name not in _SKIP_NAMES and p.suffix not in _SKIP_SUFFIXES
            ]
            if len(files) <= 2:
                report.stale_paths.append(
                    f"{suspect} (flat directory holding only {files}; "
                    "the top-level markdown is the real source)"
                )

    manifest: dict[str, Any] = {
        "name": "VUORSE-VORTEX Source Corpus",
        "description": (
            "Manifest for Slayverse lore, canon, roadmap-private material, "
            "and synthetic enrichment sources."
        ),
        "roots": list(roots),
        "includes_pdf": include_pdf,
        "includes_finale": include_finale,
        "source_count": len(sources),
        "sealed_source_count": report.sealed_entries,
        "sources": sources,
        "notes": [
            "Generated by vuorse_vortex.indexing.build_source_manifest.",
            "canon_status 'unknown' means the source does not declare one. Do not guess.",
            "Keep Memory Cortex separate.",
            "Do not invent Jake's mother's name prematurely.",
        ],
    }

    if out_path is not None:
        _write_json(base / out_path, manifest)
    return manifest, report


# ---------------------------------------------------------------------------
# Entity index (borrowed from slay-cortex gazetteer)
# ---------------------------------------------------------------------------


def _load_canon_index(index_path: Path) -> dict[str, Any]:
    if not index_path.exists():
        raise CanonIndexMissingError(f"Canon index not found: {index_path}")
    try:
        with index_path.open(encoding="utf-8") as fh:
            data: dict[str, Any] = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise IndexingError(f"Canon index will not parse: {index_path}: {exc}") from exc
    return data


def build_entity_index(
    index_path: Path = CANON_INDEX,
    out_path: Path | None = ENTITY_INDEX_OUT,
    *,
    base: Path = Path("."),
) -> dict[str, Any]:
    """Build the entity index and its surface-form / distinctive-token layers.

    The surface-form layer doubles as retrieval query hints: asking for
    "VUORSE" also searches "The Banshee of Bassline" and "Grand Oracle of the
    Velvet Archive" -- query expansion driven by scripture rather than by a
    model guessing at synonyms.

    Raises:
        CanonIndexMissingError: the canon index is not on disk.
        NonMergeableCollapseError: a NON_MERGEABLE pair became indistinguishable.
    """
    raw = _load_canon_index(base / index_path)

    entities: dict[str, dict[str, Any]] = {}
    repairs_applied: list[str] = []

    for record in raw.get("entities", []):
        eid = record["id"]
        forms: list[str] = [record["name"]]
        for alias in record.get("aliases") or []:
            repaired = ALIAS_REPAIRS.get((eid, alias))
            if repaired:
                repairs_applied.append(f"{eid}: {alias!r} -> {repaired!r}")
                forms.append(repaired)
            else:
                forms.append(alias)

        seen: set[str] = set()
        forms = [f for f in forms if not (f in seen or seen.add(f))]

        entities[eid] = {
            "id": eid,
            "name": record["name"],
            "type": record.get("type", "unknown"),
            "status": record.get("status", "unknown"),
            "era": record.get("era"),
            "surface_forms": forms,
            "related": record.get("related") or [],
            "tags": record.get("tags") or [],
            "source_pages": record.get("source_pages") or [],
            "summary": record.get("summary", ""),
        }

    token_map: dict[str, set[str]] = {}
    for eid, ent in entities.items():
        for form in ent["surface_forms"]:
            for token in tokenize_name(form):
                if is_distinctive(token):
                    token_map.setdefault(token, set()).add(eid)

    form_map: dict[str, set[str]] = {}
    for eid, ent in entities.items():
        for form in ent["surface_forms"]:
            form_map.setdefault(form, set()).add(eid)

    _assert_non_mergeable(entities)

    index: dict[str, Any] = {
        "generated_from": (base / index_path).as_posix(),
        "canon_version": raw.get("version"),
        "canon_generated": raw.get("generated"),
        "canon_amended": raw.get("amended"),
        "entity_count": len(entities),
        "surface_form_count": len(form_map),
        "distinctive_token_count": len(token_map),
        "ambiguous_tokens": sorted(t for t, ids in token_map.items() if len(ids) > 1),
        "repairs_applied": repairs_applied,
        "entities": entities,
        "surface_forms": {k: sorted(v) for k, v in sorted(form_map.items())},
        "distinctive_tokens": {k: sorted(v) for k, v in sorted(token_map.items())},
        "case_sensitive_forms": sorted(CASE_SENSITIVE_FORMS),
    }

    if out_path is not None:
        _write_json(base / out_path, index)
    return index


def _assert_non_mergeable(entities: dict[str, dict[str, Any]]) -> None:
    """Fail the build if two entities that must stay distinct became identical."""
    for left, right in NON_MERGEABLE:
        if left not in entities or right not in entities:
            continue
        if set(entities[left]["surface_forms"]) == set(entities[right]["surface_forms"]):
            raise NonMergeableCollapseError(
                f"NON_MERGEABLE entities {left} and {right} have identical "
                "surface forms; exact matching can no longer separate them."
            )


# ---------------------------------------------------------------------------
# Relationship index
# ---------------------------------------------------------------------------


def build_relationship_index(
    index_path: Path = CANON_INDEX,
    out_path: Path | None = RELATIONSHIP_INDEX_OUT,
    *,
    base: Path = Path("."),
) -> dict[str, Any]:
    """Build the relationship index and report edges pointing at nothing.

    Dangling edges are reported, never silently dropped: an edge naming an
    entity the index does not carry is a gap in the canon index, and the
    indexer's job is to say so.
    """
    raw = _load_canon_index(base / index_path)
    known = {e["id"] for e in raw.get("entities", [])}

    edges: list[dict[str, Any]] = []
    dangling: list[dict[str, Any]] = []
    adjacency: dict[str, list[str]] = {}

    for rel in raw.get("relationships", []):
        src, dst = rel.get("from"), rel.get("to")
        edge = {"from": src, "to": dst, "type": rel.get("type", "unknown")}
        missing = [side for side, val in (("from", src), ("to", dst)) if val not in known]
        if missing:
            dangling.append({**edge, "missing": missing})
            continue
        edges.append(edge)
        adjacency.setdefault(src, []).append(dst)
        adjacency.setdefault(dst, []).append(src)

    timeline = [
        {
            "year": event.get("year"),
            "event": event.get("event"),
            "entities": event.get("entities") or [],
            "unknown_entities": sorted(set(event.get("entities") or []) - known),
        }
        for event in raw.get("timeline", [])
    ]

    # Entity `related` arrays are a second, quieter edge set. Validating only the
    # `relationships` array reports a clean graph while these point at nothing.
    dangling_related: dict[str, list[str]] = {}
    for entity in raw.get("entities", []):
        missing = sorted({r for r in (entity.get("related") or []) if r not in known})
        if missing:
            dangling_related[entity["id"]] = missing

    index: dict[str, Any] = {
        "generated_from": (base / index_path).as_posix(),
        "canon_version": raw.get("version"),
        "edge_count": len(edges),
        "dangling_count": len(dangling),
        "dangling_related_count": sum(len(v) for v in dangling_related.values()),
        "relationship_types": sorted({e["type"] for e in edges}),
        "edges": edges,
        "dangling_edges": dangling,
        "dangling_related": dict(sorted(dangling_related.items())),
        "adjacency": {k: sorted(set(v)) for k, v in sorted(adjacency.items())},
        "timeline": timeline,
    }

    if out_path is not None:
        _write_json(base / out_path, index)
    return index


# ---------------------------------------------------------------------------
# Shared IO
# ---------------------------------------------------------------------------


def rendered(payload: dict[str, Any]) -> str:
    """Return the exact on-disk form of an index, for drift checks."""
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered(payload), encoding="utf-8")


def is_current(path: Path, payload: dict[str, Any]) -> bool:
    """True if ``path`` already holds exactly what ``payload`` would write."""
    if not path.exists():
        return False
    try:
        return path.read_text(encoding="utf-8") == rendered(payload)
    except OSError:
        return False
