from __future__ import annotations

import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_WORKSPACE = Path(r"C:\Users\caleb\Documents\Codex\2026-08-09\new-chat")
PYTHON_PACKAGES = ORIGINAL_WORKSPACE / "work" / "python-packages"
sys.path.insert(0, str(PYTHON_PACKAGES))
os.environ.setdefault(
    "AZURE_EXTENSION_DIR", str(ORIGINAL_WORKSPACE / "work" / "az-cli-extensions")
)

from azure.ai.projects import AIProjectClient  # noqa: E402
from azure.identity import AzureCliCredential  # noqa: E402


PROJECT_ENDPOINT = (
    "https://ai-account-gm3ycgiiyeaz4.services.ai.azure.com/"
    "api/projects/ai-project-ai-project-pt02msod"
)
RESPONSES_ROOT = PACKAGE_ROOT / "evidence" / "azure" / "responses"
OUTPUTS_ROOT = PACKAGE_ROOT / "evidence" / "competition" / "outputs"


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def response_index() -> list[dict]:
    records: list[dict] = []
    phases = (
        ("charter", OUTPUTS_ROOT / "charter-exposure" / "receipts.jsonl"),
        ("identity", OUTPUTS_ROOT / "identity-ceremony" / "receipts.jsonl"),
    )
    for phase, path in phases:
        for row in read_jsonl(path):
            if row.get("response_id"):
                records.append(
                    {
                        "phase": phase,
                        "contestant_number": row.get("contestant_number"),
                        "model": row.get("model"),
                        "version": row.get("version"),
                        "response_id": row["response_id"],
                    }
                )

    registry = json.loads(
        (OUTPUTS_ROOT / "identity-ceremony" / "identity-registry.json").read_text(
            encoding="utf-8"
        )
    )
    for row in registry.get("tiebreaks", []):
        if row.get("response_id"):
            records.append(
                {
                    "phase": "tiebreak",
                    "contestant_number": row.get("contestant_number"),
                    "model": "gpt-chat-latest",
                    "version": "2026-06-24",
                    "response_id": row["response_id"],
                }
            )
    return records


def main() -> int:
    client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT, credential=AzureCliCredential()
    ).get_openai_client()

    index = response_index()
    audits: list[dict] = []
    for record in index:
        response = client.responses.retrieve(record["response_id"])
        payload = response.model_dump()
        output = payload.get("output") or []
        output_types = [
            item.get("type") for item in output if isinstance(item, dict)
        ]
        tool_events = [
            item
            for item in output
            if isinstance(item, dict)
            and item.get("type") not in {"message", "reasoning"}
        ]
        reasoning = [
            item
            for item in output
            if isinstance(item, dict) and item.get("type") == "reasoning"
        ]

        filename = (
            f"contestant-{int(record['contestant_number']):02d}-"
            f"{record['model'].replace('.', '_')}-{record['response_id']}.json"
        )
        destination = RESPONSES_ROOT / record["phase"] / filename
        destination.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n",
            encoding="utf-8",
        )

        audits.append(
            {
                **record,
                "saved_as": str(destination.relative_to(PACKAGE_ROOT)),
                "output_types": output_types,
                "tool_event_types": [item.get("type") for item in tool_events],
                "declared_tools": payload.get("tools"),
                "previous_response_id": payload.get("previous_response_id"),
                "instructions": payload.get("instructions"),
                "metadata": payload.get("metadata"),
                "reasoning_item_count": len(reasoning),
                "reasoning_summaries": [item.get("summary") for item in reasoning],
                "reasoning_content": [item.get("content") for item in reasoning],
                "reasoning_encrypted_content_present": any(
                    bool(item.get("encrypted_content")) for item in reasoning
                ),
            }
        )

    type_counts = Counter(
        output_type for audit in audits for output_type in audit["output_types"]
    )
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_endpoint": PROJECT_ENDPOINT,
        "responses_expected": len(index),
        "responses_retrieved": len(audits),
        "phase_counts": dict(Counter(audit["phase"] for audit in audits)),
        "output_type_counts": dict(type_counts),
        "responses_with_tool_events": sum(
            bool(audit["tool_event_types"]) for audit in audits
        ),
        "responses_with_declared_tools": sum(
            bool(audit["declared_tools"]) for audit in audits
        ),
        "responses_with_previous_response_id": sum(
            bool(audit["previous_response_id"]) for audit in audits
        ),
        "responses_with_hidden_instructions": sum(
            bool(audit["instructions"]) for audit in audits
        ),
        "responses_with_metadata": sum(bool(audit["metadata"]) for audit in audits),
        "identity_reasoning_item_count": sum(
            audit["reasoning_item_count"]
            for audit in audits
            if audit["phase"] == "identity"
        ),
        "identity_reasoning_items_with_visible_summary": sum(
            any(summary for summary in audit["reasoning_summaries"])
            for audit in audits
            if audit["phase"] == "identity"
        ),
        "identity_reasoning_items_with_visible_content": sum(
            any(content for content in audit["reasoning_content"])
            for audit in audits
            if audit["phase"] == "identity"
        ),
        "identity_reasoning_items_with_encrypted_content": sum(
            audit["reasoning_encrypted_content_present"]
            for audit in audits
            if audit["phase"] == "identity"
        ),
        "responses": audits,
    }
    (PACKAGE_ROOT / "evidence" / "azure" / "audit-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: value for key, value in summary.items() if key != "responses"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
