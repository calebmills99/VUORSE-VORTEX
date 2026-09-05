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
    lines = []
    for path in sorted(PACKAGE_ROOT.rglob("*")):
        if path.is_file() and path != MANIFEST:
            relative = path.relative_to(PACKAGE_ROOT).as_posix()
            lines.append(f"{sha256(path)}  {relative}")
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {len(lines)} hashes to {MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
