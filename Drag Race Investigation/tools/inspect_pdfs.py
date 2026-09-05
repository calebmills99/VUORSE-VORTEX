from __future__ import annotations

import hashlib
import json
import re
import sys
import zlib
from datetime import datetime, timezone
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
CODEX_PYTHON_PACKAGES = Path(
    r"C:\Users\caleb\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\Lib\site-packages"
)
sys.path.insert(0, str(CODEX_PYTHON_PACKAGES))

from pypdf import PdfReader  # noqa: E402


SOURCE_ROOT = PACKAGE_ROOT / "evidence" / "source-files"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def inspect(path: Path) -> dict:
    data = path.read_bytes()
    reader = PdfReader(str(path))
    pages = [(page.extract_text() or "") for page in reader.pages]
    extracted = "\n\n".join(pages)
    stream_results = []
    for match in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.DOTALL):
        raw = match.group(1)
        decompressed = None
        try:
            decompressed = zlib.decompress(raw)
        except zlib.error:
            pass
        stream_results.append(
            {
                "raw_length": len(raw),
                "raw_sha256": sha256(raw),
                "raw_contains_velvet": b"velvet" in raw.lower(),
                "decompressed_length": len(decompressed) if decompressed else None,
                "decompressed_sha256": sha256(decompressed) if decompressed else None,
                "decompressed_contains_velvet": (
                    b"velvet" in decompressed.lower() if decompressed else False
                ),
            }
        )

    root = reader.trailer.get("/Root")
    root_keys = sorted(str(key) for key in root.keys()) if root else []
    attachments = sorted((reader.attachments or {}).keys())
    try:
        outline_count = len(reader.outline)
    except Exception:
        outline_count = None

    return {
        "file": path.name,
        "size": len(data),
        "sha256": sha256(data),
        "page_count": len(reader.pages),
        "pdf_object_count": len(re.findall(rb"\n\d+\s+\d+\s+obj\b", data)),
        "metadata": dict(reader.metadata or {}),
        "catalog_keys": root_keys,
        "attachment_names": attachments,
        "outline_count": outline_count,
        "raw_contains_velvet": b"velvet" in data.lower(),
        "extracted_text_length": len(extracted),
        "extracted_text_sha256": sha256(extracted.encode("utf-8")),
        "extracted_text_contains_velvet": "velvet" in extracted.casefold(),
        "extracted_text_velvet_count": extracted.casefold().count("velvet"),
        "page_text_sha256": [sha256(page.encode("utf-8")) for page in pages],
        "streams": stream_results,
    }


def main() -> int:
    reports = [inspect(SOURCE_ROOT / name) for name in ("charter.pdf", "TheCharter.pdf")]
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reports": reports,
    }
    destination = PACKAGE_ROOT / "evidence" / "pdf" / "pdf-deep-audit.json"
    destination.write_text(
        json.dumps(output, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
