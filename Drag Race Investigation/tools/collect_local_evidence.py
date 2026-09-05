from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parent
ENV_ROOT = PACKAGE_ROOT / "evidence" / "environment"
SOURCE_ROOT = PACKAGE_ROOT / "evidence" / "source-files"
GITHUB_ROOT = PACKAGE_ROOT / "evidence" / "github"
PS_HISTORY = Path(
    r"C:\Users\caleb\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def command(*args: str) -> dict:
    completed = subprocess.run(
        args,
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    return {
        "command": list(args),
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def main() -> int:
    file_metadata = []
    for path in sorted(PACKAGE_ROOT.rglob("*")):
        if path.is_file() and path.name != "MANIFEST.sha256":
            stat = path.stat()
            file_metadata.append(
                {
                    "path": str(path.relative_to(PACKAGE_ROOT)),
                    "size": stat.st_size,
                    "created_local": datetime.fromtimestamp(
                        stat.st_ctime, timezone.utc
                    ).isoformat(),
                    "modified_local": datetime.fromtimestamp(
                        stat.st_mtime, timezone.utc
                    ).isoformat(),
                    "sha256": sha256(path),
                }
            )
    (ENV_ROOT / "file-metadata.json").write_text(
        json.dumps(file_metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    history_hits = []
    if PS_HISTORY.exists():
        for number, line in enumerate(
            PS_HISTORY.read_text(encoding="utf-8", errors="replace").splitlines(), 1
        ):
            folded = line.casefold()
            if any(
                term in folded
                for term in (
                    "thecharter.md",
                    "charter.md",
                    "charter.pdf",
                    "cosmic_md_to_pdf",
                )
            ):
                history_hits.append({"line_number": number, "line": line})
    (ENV_ROOT / "powershell-history-charter-matches.json").write_text(
        json.dumps(history_hits, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    git_snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(REPO_ROOT),
        "remote": command("git", "remote", "-v"),
        "status": command("git", "status", "--short"),
        "head": command("git", "rev-parse", "HEAD"),
        "branch": command("git", "branch", "--show-current"),
    }
    (ENV_ROOT / "git-snapshot.json").write_text(
        json.dumps(git_snapshot, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    searches = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": {},
    }
    for path in sorted(SOURCE_ROOT.iterdir()):
        if path.suffix.casefold() == ".md":
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            matches = [
                {"line_number": number, "line": line}
                for number, line in enumerate(text.splitlines(), 1)
                if "velvet" in line.casefold()
            ]
            searches["source_files"][path.name] = {
                "match_count_by_line": len(matches),
                "occurrence_count": text.casefold().count("velvet"),
                "matches": matches,
            }
    (ENV_ROOT / "velvet-search-results.json").write_text(
        json.dumps(searches, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    repo_hits = []
    allowed_suffixes = {
        ".md",
        ".txt",
        ".json",
        ".jsonl",
        ".py",
        ".toml",
        ".yaml",
        ".yml",
        ".html",
    }
    skipped_parts = {".git", ".venv", "Drag Race Investigation"}
    for path in sorted(REPO_ROOT.rglob("*")):
        if (
            not path.is_file()
            or path.suffix.casefold() not in allowed_suffixes
            or any(part in skipped_parts for part in path.parts)
            or path.stat().st_size > 10_000_000
        ):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), 1):
            folded = line.casefold()
            if "velvet" in folded or "golden wingers" in folded:
                repo_hits.append(
                    {
                        "path": str(path.relative_to(REPO_ROOT)),
                        "line_number": number,
                        "contains_velvet": "velvet" in folded,
                        "contains_golden_wingers": "golden wingers" in folded,
                        "line": line,
                    }
                )
    (GITHUB_ROOT / "local-repo-corpus-hits.json").write_text(
        json.dumps(repo_hits, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
