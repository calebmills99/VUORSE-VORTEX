from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_WORKSPACE = Path(r"C:\Users\caleb\Documents\Codex\2026-08-09\new-chat")
sys.path.insert(0, str(ORIGINAL_WORKSPACE / "work" / "python-packages"))
os.environ.setdefault(
    "AZURE_EXTENSION_DIR", str(ORIGINAL_WORKSPACE / "work" / "az-cli-extensions")
)

from azure.ai.projects import AIProjectClient  # noqa: E402
from azure.identity import AzureCliCredential  # noqa: E402


PROJECT_ENDPOINT = (
    "https://ai-account-gm3ycgiiyeaz4.services.ai.azure.com/"
    "api/projects/ai-project-ai-project-pt02msod"
)
BLOCKED_KEY_PARTS = ("credential", "secret", "token", "api_key", "apikey", "password")


def serialize(value):
    if hasattr(value, "as_dict"):
        value = value.as_dict()
    elif hasattr(value, "model_dump"):
        value = value.model_dump()
    if isinstance(value, dict):
        return {
            str(key): (
                "[OMITTED]"
                if any(part in str(key).casefold() for part in BLOCKED_KEY_PARTS)
                else serialize(item)
            )
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [serialize(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def collect(operation, **kwargs):
    try:
        return {"status": "ok", "items": [serialize(item) for item in operation(**kwargs)]}
    except Exception as exc:
        return {"status": "error", "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    project = AIProjectClient(
        endpoint=PROJECT_ENDPOINT, credential=AzureCliCredential()
    )
    inventory = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_endpoint": PROJECT_ENDPOINT,
        "credentials_included": False,
        "connections": collect(project.connections.list),
        "datasets": collect(project.datasets.list),
        "deployments": collect(project.deployments.list),
        "indexes": collect(project.indexes.list),
        "agents": collect(project.agents.list, limit=100),
        "toolboxes": collect(project.toolboxes.list, limit=100),
    }
    destination = PACKAGE_ROOT / "evidence" / "azure" / "project-inventory.json"
    destination.write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    summary = {
        key: (
            len(value.get("items", [])) if isinstance(value, dict) else value
        )
        for key, value in inventory.items()
        if key not in {"generated_at", "project_endpoint", "credentials_included"}
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
