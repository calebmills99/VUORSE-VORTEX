from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_WORKSPACE = Path(r"C:\Users\caleb\Documents\Codex\2026-08-09\new-chat")
sys.path.insert(0, str(ORIGINAL_WORKSPACE / "work" / "python-packages"))
os.environ.setdefault(
    "AZURE_EXTENSION_DIR", str(ORIGINAL_WORKSPACE / "work" / "az-cli-extensions")
)

from azure.identity import AzureCliCredential  # noqa: E402


WORKSPACE_RESOURCE_ID = (
    "/subscriptions/e0c48bb6-1d7f-4859-ac27-f4a15129eb98/"
    "resourceGroups/rg-ai-project-pt02msod/providers/"
    "Microsoft.OperationalInsights/workspaces/logs-gm3ycgiiyeaz4"
)
QUERY_URL = (
    f"https://management.azure.com{WORKSPACE_RESOURCE_ID}/query?api-version=2017-10-01"
)
WINDOW = "2026-08-10T17:00:00Z/2026-08-10T19:00:00Z"
TABLES = ["AppRequests", "AppTraces", "AppDependencies", "AppEvents", "AppExceptions"]


def query(token: str, kusto: str) -> dict:
    body = json.dumps({"query": kusto, "timespan": WINDOW}).encode("utf-8")
    request = urllib.request.Request(
        QUERY_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return {
                "status": response.status,
                "body": json.loads(response.read().decode("utf-8")),
            }
    except urllib.error.HTTPError as exc:
        return {
            "status": exc.code,
            "body": json.loads(exc.read().decode("utf-8", errors="replace")),
        }


def main() -> int:
    token = AzureCliCredential().get_token(
        "https://management.azure.com/.default"
    ).token
    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace_resource_id": WORKSPACE_RESOURCE_ID,
        "timespan": WINDOW,
        "queries": {},
    }
    for table in TABLES:
        kusto = f"{table} | order by TimeGenerated asc | take 10000"
        results["queries"][table] = {"query": kusto, **query(token, kusto)}
    destination = (
        PACKAGE_ROOT / "evidence" / "azure" / "application-insights-competition-window.json"
    )
    destination.write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    summary = {}
    for table, result in results["queries"].items():
        tables = result.get("body", {}).get("tables", [])
        summary[table] = sum(len(item.get("rows", [])) for item in tables)
        if result.get("status") != 200:
            summary[table] = {"status": result.get("status"), "body": result.get("body")}
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
