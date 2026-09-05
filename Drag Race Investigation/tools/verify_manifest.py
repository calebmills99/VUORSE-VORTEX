from __future__ import annotations

import hashlib
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = PACKAGE_ROOT / "MANIFEST.sha256"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> int:
    errors = []
    checked = 0
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        path = PACKAGE_ROOT / Path(relative)
        if not path.is_file():
            errors.append(f"missing: {relative}")
            continue
        actual = sha256(path)
        if actual != expected:
            errors.append(f"hash mismatch: {relative}")
        checked += 1
    print(f"checked={checked} errors={len(errors)}")
    for error in errors:
        print(error)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
