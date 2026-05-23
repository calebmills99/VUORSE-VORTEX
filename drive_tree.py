#!/usr/bin/env python3
"""
drive_tree.py - Walk a Google Drive and emit an LLM-friendly catalog.

WHY: Claude's Drive search only reads native Google Docs and chokes on
folders, .ps1, .md, .txt, and every binary. This walks the *whole* tree via
the Drive API and writes a compact, annotated map Claude can actually read,
including the Google-Doc IDs so it can fetch and read those next.

OUTPUTS (written next to this script, or --output-dir):
  drive_tree.txt   annotated indented tree  <- hand THIS to Claude
  drive_tree.json  full structured tree for anything programmatic

ONE-TIME SETUP (the only manual part):
  1. Google Cloud Console -> APIs & Services -> Library -> enable "Google Drive API".
  2. -> Credentials -> Create Credentials -> OAuth client ID -> type "Desktop app".
  3. Download it as  credentials.json  and drop it next to this script.
  First run opens a browser for consent; the token caches to token.json after.

  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

SCOPE is metadata-readonly. This script reads the catalog only (names, types,
sizes, dates, ids). It never touches file contents. Re-runnable, idempotent,
read-only by design.

USAGE:
  python drive_tree.py                      # My Drive, no trash
  python drive_tree.py --include-trashed
  python drive_tree.py --shared-drives      # also walk Shared/Team drives
  python drive_tree.py --max-depth 4
  python drive_tree.py --ids-all            # print id on every line, not just gdocs
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    sys.exit(
        "Missing deps. Run:\n"
        "  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
    )

SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDER_MIME = "application/vnd.google-apps.folder"
SHORTCUT_MIME = "application/vnd.google-apps.shortcut"

# mimeType -> short label, for fast scanning. Anything not here gets bucketed
# by prefix or filename extension in label_for().
TYPE_LABELS = {
    FOLDER_MIME: "folder",
    "application/vnd.google-apps.document": "gdoc",
    "application/vnd.google-apps.spreadsheet": "gsheet",
    "application/vnd.google-apps.presentation": "gslides",
    "application/vnd.google-apps.form": "gform",
    "application/vnd.google-apps.drawing": "gdrawing",
    "application/vnd.google-apps.script": "gscript",
    SHORTCUT_MIME: "shortcut",
    "application/pdf": "pdf",
    "text/plain": "txt",
    "text/markdown": "md",
    "text/x-markdown": "md",
    "application/json": "json",
    "application/zip": "zip",
    "application/x-zip-compressed": "zip",
    "application/x-7z-compressed": "7z",
    "application/gzip": "gz",
    "application/msword": "doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
}

# Native Google editable types Claude can fetch and read -> always show id.
FETCHABLE = {"gdoc", "gsheet", "gslides", "gform", "gdrawing", "gscript"}

# Quick filename-extension fallbacks for code/config that mimeType often
# reports as octet-stream or text/plain.
EXT_LABELS = {
    ".ps1": "ps1", ".psm1": "ps1", ".psd1": "ps1",
    ".py": "py", ".rs": "rust", ".toml": "toml", ".yaml": "yaml", ".yml": "yaml",
    ".js": "js", ".ts": "ts", ".sh": "sh", ".zsh": "zsh", ".bat": "bat",
    ".md": "md", ".json": "json", ".env": "env", ".cfg": "cfg", ".ini": "ini",
    ".sql": "sql", ".dockerfile": "docker", ".exe": "exe", ".msi": "msi",
    ".mp4": "video", ".mov": "video", ".mkv": "video", ".braw": "video",
    ".wav": "audio", ".mp3": "audio", ".aif": "audio",
    ".png": "image", ".jpg": "image", ".jpeg": "image", ".tif": "image",
    ".tiff": "image", ".exr": "image", ".dpx": "image", ".webp": "image",
    ".drp": "resolve-proj", ".drx": "resolve-grade", ".aep": "ae-proj",
    ".prproj": "premiere-proj", ".nk": "nuke-script", ".cube": "lut",
}


def label_for(name, mime):
    if mime in TYPE_LABELS:
        return TYPE_LABELS[mime]
    ext = os.path.splitext(name)[1].lower()
    if ext in EXT_LABELS:
        return EXT_LABELS[ext]
    for prefix, lbl in (("image/", "image"), ("video/", "video"),
                        ("audio/", "audio"), ("text/", "text")):
        if mime.startswith(prefix):
            return lbl
    return mime.split(".")[-1].split("/")[-1] or "file"


def human_size(n):
    if n is None:
        return "-"
    n = int(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f}{unit}" if unit == "B" else f"{n/1.0:.1f}{unit}"
        n /= 1024.0


def human_size_clean(n):
    if n is None:
        return "-"
    n = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{int(n)}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024.0


def authenticate():
    creds = None
    token_path = os.path.join(SCRIPT_DIR, "token.json")
    cred_path = os.path.join(SCRIPT_DIR, "credentials.json")
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(cred_path):
                sys.exit(
                    f"No credentials.json found at {cred_path}\n"
                    "Create an OAuth Desktop client in Google Cloud Console, "
                    "download it as credentials.json, and put it next to this script."
                )
            flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())
    return build("drive", "v3", credentials=creds)


def fetch_all(service, include_trashed, shared_drives):
    """Pull every file's metadata with pagination. Returns list of dicts."""
    files = []
    page_token = None
    q = None if include_trashed else "trashed = false"
    fields = ("nextPageToken, files(id, name, mimeType, parents, size, "
              "modifiedTime, trashed, shortcutDetails)")
    extra = {}
    if shared_drives:
        extra = dict(includeItemsFromAllDrives=True, supportsAllDrives=True,
                     corpora="allDrives")
    import time
    while True:
        retries = 5
        delay = 1.0
        while retries > 0:
            try:
                resp = service.files().list(
                    q=q, fields=fields, pageSize=1000, pageToken=page_token,
                    **extra
                ).execute()
                break
            except HttpError as e:
                status = getattr(e.resp, "status", None) or getattr(e, "status_code", None)
                try:
                    status = int(status)
                except (ValueError, TypeError):
                    pass
                if status in [500, 502, 503, 504] and retries > 1:
                    sys.stderr.write(f"\n  API error {status}, retrying in {delay:.1f}s...")
                    sys.stderr.flush()
                    time.sleep(delay)
                    delay *= 2
                    retries -= 1
                else:
                    raise
        files.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        sys.stderr.write(f"\r  fetched {len(files)} items...")
        sys.stderr.flush()
        if not page_token:
            break
    sys.stderr.write("\n")
    return files


def build_tree(files, root_id):
    nodes = {f["id"]: f for f in files}
    # Synthetic root so My Drive top-level items have a home.
    nodes.setdefault(root_id, {"id": root_id, "name": "My Drive",
                               "mimeType": FOLDER_MIME, "parents": []})
    children = {}
    other = []  # shared-with-me / orphaned (parent not in our set)
    for f in files:
        parents = f.get("parents") or []
        if not parents:
            if f["id"] != root_id:
                other.append(f["id"])
            continue
        placed = False
        for p in parents:
            if p in nodes or p == root_id:
                children.setdefault(p, []).append(f["id"])
                placed = True
                break
        if not placed:
            other.append(f["id"])
    return nodes, children, other


def sort_children(ids, nodes):
    return sorted(
        ids,
        key=lambda i: (nodes[i]["mimeType"] != FOLDER_MIME,
                       nodes[i]["name"].lower()),
    )


def render_txt(nodes, children, root_id, other, ids_all, max_depth):
    lines = []
    stats = {"folders": 0, "files": 0, "bytes": 0, "by_type": {}}

    def walk(node_id, depth, visited):
        if node_id in visited:
            return
        visited.add(node_id)
        if max_depth is not None and depth > max_depth:
            return
        for cid in sort_children(children.get(node_id, []), nodes):
            n = nodes[cid]
            indent = "  " * depth
            lbl = label_for(n["name"], n["mimeType"])
            if n["mimeType"] == FOLDER_MIME:
                stats["folders"] += 1
                kids = len(children.get(cid, []))
                lines.append(f"{indent}{n['name']}/  ({kids})")
                walk(cid, depth + 1, visited)
            else:
                stats["files"] += 1
                stats["by_type"][lbl] = stats["by_type"].get(lbl, 0) + 1
                size = n.get("size")
                if size:
                    stats["bytes"] += int(size)
                date = (n.get("modifiedTime") or "")[:10]
                tail = ""
                if ids_all or lbl in FETCHABLE:
                    tail = f"  id={n['id']}"
                lines.append(
                    f"{indent}{n['name']}  [{lbl}, {human_size_clean(size)}, {date}]{tail}"
                )

    visited = set()
    lines.append("My Drive/")
    walk(root_id, 1, visited)

    if other:
        lines.append("")
        lines.append("Shared-with-me / orphaned (parent outside My Drive):")
        for cid in sort_children(other, nodes):
            n = nodes[cid]
            lbl = label_for(n["name"], n["mimeType"])
            slash = "/" if n["mimeType"] == FOLDER_MIME else ""
            date = (n.get("modifiedTime") or "")[:10]
            tail = f"  id={n['id']}" if (ids_all or lbl in FETCHABLE) else ""
            lines.append(f"  {n['name']}{slash}  [{lbl}, {date}]{tail}")

    header = [
        "GOOGLE DRIVE TREE",
        f"generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"folders: {stats['folders']}   files: {stats['files']}   "
        f"total file size: {human_size_clean(stats['bytes'])}",
        "top types: " + ", ".join(
            f"{k}:{v}" for k, v in sorted(
                stats["by_type"].items(), key=lambda x: -x[1])[:12]
        ),
        "legend: name/  (N children) = folder.  "
        "files show [type, size, modified].  id= shown for Claude-readable "
        "Google docs (and all items with --ids-all).",
        "=" * 70,
        "",
    ]
    return "\n".join(header + lines) + "\n", stats


def build_json(nodes, children, root_id, max_depth):
    def node_dict(node_id, depth, visited):
        if node_id in visited:
            return None
        visited.add(node_id)
        n = nodes[node_id]
        d = {
            "id": n["id"],
            "name": n["name"],
            "type": label_for(n["name"], n["mimeType"]),
            "mimeType": n["mimeType"],
            "modified": n.get("modifiedTime"),
            "size": int(n["size"]) if n.get("size") else None,
        }
        if n["mimeType"] == FOLDER_MIME:
            if max_depth is None or depth < max_depth:
                kids = [node_dict(c, depth + 1, visited)
                        for c in sort_children(children.get(node_id, []), nodes)]
                d["children"] = [k for k in kids if k]
            else:
                d["children"] = []
        return d

    return node_dict(root_id, 0, set())


def main():
    ap = argparse.ArgumentParser(description="Walk Google Drive into an LLM-friendly tree.")
    ap.add_argument("--output-dir", default=SCRIPT_DIR)
    ap.add_argument("--include-trashed", action="store_true")
    ap.add_argument("--shared-drives", action="store_true",
                    help="also include Shared/Team drives")
    ap.add_argument("--max-depth", type=int, default=None)
    ap.add_argument("--ids-all", action="store_true",
                    help="print id on every line, not just Google docs")
    args = ap.parse_args()

    service = authenticate()
    try:
        root_id = service.files().get(fileId="root", fields="id").execute()["id"]
    except HttpError as e:
        sys.exit(f"Drive API error getting root: {e}")

    sys.stderr.write("Fetching Drive metadata...\n")
    files = fetch_all(service, args.include_trashed, args.shared_drives)
    nodes, children, other = build_tree(files, root_id)

    txt, stats = render_txt(nodes, children, root_id, other,
                            args.ids_all, args.max_depth)
    tree_json = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "stats": stats,
        "root": build_json(nodes, children, root_id, args.max_depth),
        "other_count": len(other),
    }

    os.makedirs(args.output_dir, exist_ok=True)
    txt_path = os.path.join(args.output_dir, "drive_tree.txt")
    json_path = os.path.join(args.output_dir, "drive_tree.json")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(txt)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(tree_json, f, indent=2, ensure_ascii=False)

    print(f"\nWrote:\n  {txt_path}  <- hand this one to Claude\n  {json_path}")
    print(f"folders: {stats['folders']}   files: {stats['files']}   "
          f"size: {human_size_clean(stats['bytes'])}")


if __name__ == "__main__":
    main()
