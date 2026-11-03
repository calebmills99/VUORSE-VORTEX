from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
import uuid
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

ALLOWED_WRITE_ROOTS = (
    "worldforge/gandalphaba",
    "worldforge/worldforge/lore-index-2.0",
    "manifests/runs/gandalphaba",
    "embeddings/indexes",
)
SAFE_VISIBILITIES = frozenset({"public", "behavioral"})
MAX_TEXT_FILE_BYTES = 2 * 1024 * 1024
TEXT_EXTENSIONS = frozenset({".html", ".json", ".jsonl", ".md", ".txt", ".yaml", ".yml"})
INDEX_RELATIVE_PATH = "embeddings/indexes/vuorse_cortex.sqlite3"
PRUNE_ARCHIVE_RELATIVE_PATH = "manifests/runs/gandalphaba/.prune-archive"


def _has_repository_markers(path: Path) -> bool:
    return all(
        (path / marker).exists()
        for marker in (
            "policies/disclosure/README.md",
            "manifests/corpus/source_manifest.json",
            "vuorse_vortex",
        )
    )


def resolve_repository_root() -> Path:
    configured = os.environ.get("VUORSE_REPO_ROOT")
    if configured:
        candidate = Path(configured).expanduser()
        if not candidate.is_absolute():
            candidate = Path(__file__).resolve().parent / candidate
        candidate = candidate.resolve()
        if _has_repository_markers(candidate):
            return candidate
        raise RuntimeError("VUORSE_REPO_ROOT does not identify a VUORSE-VORTEX working tree.")

    for candidate in Path(__file__).resolve().parents:
        if _has_repository_markers(candidate):
            return candidate
    raise RuntimeError(
        "The VUORSE-VORTEX repository is not mounted. Set VUORSE_REPO_ROOT to a "
        "working tree; the cloud deployment has no repository connector configured."
    )


def _relative_parts(relative_path: str) -> tuple[str, ...]:
    if not relative_path or relative_path != relative_path.strip():
        raise ValueError("relative_path must be a non-empty repository-relative path.")
    if "\x00" in relative_path:
        raise ValueError("relative_path contains a null byte.")

    normalized = relative_path.replace("\\", "/")
    windows_path = PureWindowsPath(relative_path)
    posix_path = PurePosixPath(normalized)
    parts = normalized.split("/")
    if (
        windows_path.is_absolute()
        or windows_path.drive
        or posix_path.is_absolute()
        or any(part in {"", ".", ".."} for part in parts)
    ):
        raise ValueError("relative_path must not be absolute or contain traversal segments.")
    return tuple(parts)


def resolve_working_path(relative_path: str, repository_root: Path | None = None) -> Path:
    root = (repository_root or resolve_repository_root()).resolve()
    if not _has_repository_markers(root):
        raise RuntimeError(f"{root} is not a VUORSE-VORTEX working tree.")
    parts = _relative_parts(relative_path)
    if any(part.casefold() == ".prune-archive" for part in parts):
        raise PermissionError("Prune archives are not exposed to ordinary read/write tools.")
    target = root.joinpath(*parts).resolve(strict=False)

    for approved_root in ALLOWED_WRITE_ROOTS:
        allowed = (root / approved_root).resolve(strict=False)
        try:
            allowed.relative_to(root)
        except ValueError:
            continue
        if target == allowed or allowed in target.parents:
            return target

    raise PermissionError("The path is outside Gandalphaba's approved working areas.")


def _validate_text_path(path: Path) -> None:
    if path.suffix.casefold() not in TEXT_EXTENSIONS:
        raise ValueError("Only UTF-8 text artifacts are available through this tool.")


def _read_limited_bytes(path: Path) -> bytes:
    if path.stat().st_size > MAX_TEXT_FILE_BYTES:
        raise ValueError("Working file exceeds the 2 MiB read limit.")
    data = path.read_bytes()
    if len(data) > MAX_TEXT_FILE_BYTES:
        raise ValueError("Working file exceeds the 2 MiB read limit.")
    return data


def read_working_file(relative_path: str) -> dict[str, str]:
    target = resolve_working_path(relative_path)
    _validate_text_path(target)
    if not target.is_file():
        raise FileNotFoundError(f"Working file does not exist: {relative_path}")
    data = _read_limited_bytes(target)
    return {
        "path": relative_path.replace("\\", "/"),
        "content": data.decode("utf-8"),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def write_working_file(
    relative_path: str,
    content: str,
    *,
    expected_sha256: str | None = None,
) -> dict[str, str]:
    target = resolve_working_path(relative_path)
    _validate_text_path(target)
    data = content.encode("utf-8")
    if len(data) > MAX_TEXT_FILE_BYTES:
        raise ValueError("Working file exceeds the 2 MiB write limit.")

    exists = target.exists()
    if exists:
        if not target.is_file():
            raise IsADirectoryError(f"Working path is not a file: {relative_path}")
        if expected_sha256 is None:
            raise FileExistsError(
                "Replacing an existing file requires its current SHA-256 from a read."
            )
        current_hash = hashlib.sha256(_read_limited_bytes(target)).hexdigest()
        if current_hash != expected_sha256.casefold():
            raise RuntimeError("Working file changed since it was read; reread before retrying.")
    elif expected_sha256 is not None:
        raise FileNotFoundError("expected_sha256 was supplied for a file that does not exist.")

    target.parent.mkdir(parents=True, exist_ok=True)
    target = resolve_working_path(relative_path)
    if exists:
        current_hash = hashlib.sha256(_read_limited_bytes(target)).hexdigest()
        if current_hash != expected_sha256.casefold():
            raise RuntimeError("Working file changed before the write; reread before retrying.")

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=".gandalphaba-",
            suffix=".tmp",
            dir=target.parent,
            delete=False,
        ) as temporary_file:
            temporary_file.write(data)
            temporary_path = Path(temporary_file.name)
        os.replace(temporary_path, target)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()

    return {
        "path": relative_path.replace("\\", "/"),
        "sha256": hashlib.sha256(data).hexdigest(),
        "operation": "replaced" if exists else "created",
    }


def _resolve_repo_path(relative_path: str, repository_root: Path | None = None) -> Path:
    root = (repository_root or resolve_repository_root()).resolve()
    if not _has_repository_markers(root):
        raise RuntimeError(f"{root} is not a VUORSE-VORTEX working tree.")
    parts = _relative_parts(relative_path)
    if any(part.casefold() == ".agent-quarantine" for part in parts):
        raise PermissionError(".agent-quarantine is outside agent context.")
    if any(part.casefold() == ".prune-archive" for part in parts):
        raise PermissionError("Prune archives are managed only by the restore tool.")

    candidate = root.joinpath(*parts)
    if candidate.is_symlink():
        raise PermissionError("Access to symlinks is not supported.")
    target = candidate.resolve(strict=False)
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise PermissionError("Path must stay inside the VUORSE-VORTEX repository.") from exc
    return target


def _resolve_prune_path(relative_path: str, repository_root: Path | None = None) -> Path:
    if any(character in relative_path for character in "*?[]"):
        raise ValueError("Pruning requires one exact file path, not a wildcard.")
    target = _resolve_repo_path(relative_path, repository_root)
    if not target.is_file():
        raise FileNotFoundError(f"Prune target is not an existing regular file: {relative_path}")
    return target


def inspect_prune_target(relative_path: str) -> dict[str, str | int]:
    target = _resolve_prune_path(relative_path)
    return {
        "path": relative_path.replace("\\", "/"),
        "size_bytes": target.stat().st_size,
        "sha256": _sha256_file(target),
    }


def _sha256_file(path: Path) -> str:
    with path.open("rb") as file_handle:
        return hashlib.file_digest(file_handle, "sha256").hexdigest()


def prune_exact_file(relative_path: str, *, expected_sha256: str) -> dict[str, str]:
    target = _resolve_prune_path(relative_path)
    current_hash = _sha256_file(target)
    if current_hash != expected_sha256.casefold():
        raise RuntimeError(
            "Prune target changed since inspection; inspect it again before retrying."
        )

    root = resolve_repository_root()
    archive_id = uuid.uuid4().hex
    archive_dir = root / PRUNE_ARCHIVE_RELATIVE_PATH / archive_id
    archive_dir.mkdir(parents=True, exist_ok=False)
    backup_path = archive_dir / "payload"
    with target.open("rb") as source_file, backup_path.open("wb") as backup_file:
        shutil.copyfileobj(source_file, backup_file)
    if _sha256_file(backup_path) != current_hash:
        raise RuntimeError("Prune archive verification failed; original file was not removed.")
    if _sha256_file(target) != current_hash:
        raise RuntimeError(
            f"Prune target changed during archiving; original was kept. Archive: {archive_id}"
        )

    receipt = {
        "source_path": relative_path.replace("\\", "/"),
        "archive_id": archive_id,
        "archive_path": f"{PRUNE_ARCHIVE_RELATIVE_PATH}/{archive_id}/payload",
        "sha256": current_hash,
        "size_bytes": str(backup_path.stat().st_size),
        "created_at": datetime.now(UTC).isoformat(),
    }
    (archive_dir / "receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    target.unlink()
    return {**receipt, "operation": "pruned"}


def restore_pruned_file(archive_id: str) -> dict[str, str]:
    if len(archive_id) != 32 or any(char not in "0123456789abcdef" for char in archive_id):
        raise ValueError("archive_id must be the 32-character id returned by a prune operation.")

    root = resolve_repository_root()
    archive_dir = root / PRUNE_ARCHIVE_RELATIVE_PATH / archive_id
    receipt_path = archive_dir / "receipt.json"
    backup_path = archive_dir / "payload"
    if not receipt_path.is_file() or not backup_path.is_file():
        raise FileNotFoundError(f"Prune archive not found: {archive_id}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    relative_path = str(receipt["source_path"])
    target = _resolve_repo_path(relative_path, root)
    if target.exists():
        raise FileExistsError(f"Cannot restore over an existing file: {relative_path}")
    if _sha256_file(backup_path) != str(receipt["sha256"]):
        raise RuntimeError(f"Prune archive failed its SHA-256 check: {archive_id}")

    target.parent.mkdir(parents=True, exist_ok=True)
    target = _resolve_repo_path(relative_path, root)
    temporary_path: Path | None = None
    try:
        with (
            tempfile.NamedTemporaryFile(
                mode="wb",
                prefix=".gandalphaba-restore-",
                suffix=".tmp",
                dir=target.parent,
                delete=False,
            ) as temporary_file,
            backup_path.open("rb") as backup_file,
        ):
            shutil.copyfileobj(backup_file, temporary_file)
            temporary_path = Path(temporary_file.name)
        os.replace(temporary_path, target)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()

    return {
        "path": relative_path,
        "sha256": str(receipt["sha256"]),
        "operation": "restored",
        "archive_id": archive_id,
    }


def visible_hit_payloads(hits: list[Any], sealed_layers: set[str]) -> list[dict[str, Any]]:
    visible: list[dict[str, Any]] = []
    for hit in hits:
        payload = asdict(hit) if is_dataclass(hit) else dict(hit)
        if payload.get("visibility") not in SAFE_VISIBILITIES:
            continue
        if payload.get("layer") in sealed_layers:
            continue
        visible.append(payload)
    return visible


def _load_cortex(repository_root: Path) -> tuple[type[Any], set[str]]:
    root_string = str(repository_root)
    if root_string not in sys.path:
        sys.path.insert(0, root_string)

    from vuorse_vortex.cortex import CortexSatellite
    from vuorse_vortex.settings import get_settings

    return CortexSatellite, set(get_settings().sealed_categories)


def search_vuorse_corpus(query: str, *, num_results: int = 8) -> list[dict[str, Any]]:
    if not query.strip():
        raise ValueError("query must not be empty.")
    if not 1 <= num_results <= 20:
        raise ValueError("num_results must be between 1 and 20.")

    root = resolve_repository_root()
    index_path = root / INDEX_RELATIVE_PATH
    if not index_path.is_file():
        raise FileNotFoundError(
            "The local VUORSE corpus index is missing. Explicitly request an index rebuild "
            "before asking for corpus search."
        )

    satellite_type, sealed_layers = _load_cortex(root)
    with satellite_type(index_path) as satellite:
        metadata = satellite.stats().get("meta", {})
        if not metadata.get("fingerprint"):
            raise RuntimeError(
                "The local VUORSE corpus index has no build fingerprint; rebuild it explicitly."
            )
        hits = satellite.search(query, top_k=50)
    return visible_hit_payloads(hits, sealed_layers)[:num_results]


def build_vuorse_index() -> dict[str, str]:
    root = resolve_repository_root()
    satellite_type, _ = _load_cortex(root)
    index_path = root / INDEX_RELATIVE_PATH
    with satellite_type(index_path) as satellite:
        result = satellite.build(base=root)
    return {
        "status": "rebuilt",
        "path": INDEX_RELATIVE_PATH,
        "fingerprint": str(result["fingerprint"]),
    }
