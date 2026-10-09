"""Repository-aware validation for the Slayverse Seam Index."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

INDEX_COLLECTIONS = (
    "agents",
    "sources",
    "activities",
    "entities",
    "events",
    "relationships",
    "lineages",
    "documents",
    "open_for_the_steward",
)

CANON_AUTHORITIES = {
    "locked_canon",
    "development_canon",
    "mythic_rumor",
    "mythic_rumor_and_locked_canon",
}

TRAINING_ACCESS_LABELS = {
    "[PUBLIC_SURFACE]",
    "[WRITERS_ROOM]",
    "[VUORSE_PRIVATE]",
    "[WEAVER_ONLY]",
    "[APPROVED_FOR_JSONL]",
    "[REVISE_WITH_WEAVER_NOTES]",
    "[REJECTED]",
}


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"cannot parse {path} as JSON: line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return value


def _records(index: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    for collection in INDEX_COLLECTIONS:
        values = index.get(collection, [])
        if not isinstance(values, list):
            continue
        for record in values:
            if isinstance(record, dict):
                yield collection, record
                statements = record.get("statements", [])
                if isinstance(statements, list):
                    for statement in statements:
                        if isinstance(statement, dict):
                            yield "statements", statement


def _ids(index: dict[str, Any], collection: str) -> set[str]:
    values = index.get(collection, [])
    if not isinstance(values, list):
        return set()
    return {
        str(record["id"])
        for record in values
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }


def _append_missing(
    errors: list[str],
    refs: Iterable[tuple[str, str]],
    targets: set[str],
) -> None:
    for location, target in refs:
        if target not in targets:
            errors.append(f"{location}: dangling reference {target!r}")


def _string_refs(values: Any, location: str) -> Iterable[tuple[str, str]]:
    if isinstance(values, list):
        for index, value in enumerate(values):
            if isinstance(value, str):
                yield f"{location}[{index}]", value


def _validate_references(index: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    agents = _ids(index, "agents")
    sources = _ids(index, "sources")
    activities = _ids(index, "activities")
    entities = _ids(index, "entities")
    events = _ids(index, "events")
    documents = _ids(index, "documents")
    lineages = _ids(index, "lineages")
    all_records = agents | sources | activities | entities | events | documents | lineages

    provenance_refs: list[tuple[str, str, str]] = []
    for collection, record in _records(index):
        record_id = str(record.get("id", "<missing-id>"))
        provenance = record.get("provenance", [])
        if isinstance(provenance, list):
            for position, reference in enumerate(provenance):
                if not isinstance(reference, dict):
                    continue
                for field in ("source", "activity", "agent"):
                    target = reference.get(field)
                    if isinstance(target, str):
                        location = (
                            f"{collection}.{record_id}.provenance[{position}].{field}"
                        )
                        provenance_refs.append((location, field, target))

    for location, field, target in provenance_refs:
        target_set = {"source": sources, "activity": activities, "agent": agents}[field]
        if target not in target_set:
            errors.append(f"{location}: dangling reference {target!r}")

    for agent in index.get("agents", []):
        if not isinstance(agent, dict):
            continue
        agent_id = str(agent.get("id", "<missing-id>"))
        behalf = agent.get("acted_on_behalf_of")
        if isinstance(behalf, str) and behalf not in agents:
            errors.append(f"agents.{agent_id}.acted_on_behalf_of: dangling reference {behalf!r}")
        entity = agent.get("entity")
        if isinstance(entity, str) and entity not in entities:
            errors.append(f"agents.{agent_id}.entity: dangling reference {entity!r}")

    for activity in index.get("activities", []):
        if not isinstance(activity, dict):
            continue
        activity_id = str(activity.get("id", "<missing-id>"))
        _append_missing(
            errors,
            _string_refs(activity.get("agents"), f"activities.{activity_id}.agents"),
            agents,
        )
        for field in ("used", "generated"):
            _append_missing(
                errors,
                _string_refs(activity.get(field), f"activities.{activity_id}.{field}"),
                sources,
            )

    for entity in index.get("entities", []):
        if not isinstance(entity, dict):
            continue
        entity_id = str(entity.get("id", "<missing-id>"))
        _append_missing(
            errors,
            _string_refs(entity.get("related"), f"entities.{entity_id}.related"),
            all_records,
        )

    for event in index.get("events", []):
        if not isinstance(event, dict):
            continue
        event_id = str(event.get("id", "<missing-id>"))
        place = event.get("place")
        if isinstance(place, str) and place not in entities:
            errors.append(f"events.{event_id}.place: dangling reference {place!r}")
        for position, participant in enumerate(event.get("participants", [])):
            if not isinstance(participant, dict):
                continue
            target = participant.get("entity")
            if isinstance(target, str) and target not in entities:
                errors.append(
                    f"events.{event_id}.participants[{position}].entity: "
                    f"dangling reference {target!r}"
                )
        for position, relation in enumerate(event.get("temporal_relations", [])):
            if not isinstance(relation, dict):
                continue
            target = relation.get("to")
            if isinstance(target, str) and target not in events:
                errors.append(
                    f"events.{event_id}.temporal_relations[{position}].to: "
                    f"dangling reference {target!r}"
                )

    for relation in index.get("relationships", []):
        if not isinstance(relation, dict):
            continue
        relation_id = str(relation.get("id", "<missing-id>"))
        for field in ("from", "to"):
            target = relation.get(field)
            if isinstance(target, str) and target not in all_records:
                errors.append(
                    f"relationships.{relation_id}.{field}: dangling reference {target!r}"
                )

    for lineage in index.get("lineages", []):
        if not isinstance(lineage, dict):
            continue
        lineage_id = str(lineage.get("id", "<missing-id>"))
        _append_missing(
            errors,
            _string_refs(lineage.get("members"), f"lineages.{lineage_id}.members"),
            entities,
        )

    for document in index.get("documents", []):
        if not isinstance(document, dict):
            continue
        document_id = str(document.get("id", "<missing-id>"))
        for field in ("entity_ref",):
            target = document.get(field)
            if isinstance(target, str) and target not in all_records:
                errors.append(f"documents.{document_id}.{field}: dangling reference {target!r}")
        for field in ("governs", "preserved_by", "archived_with", "signatories"):
            _append_missing(
                errors,
                _string_refs(document.get(field), f"documents.{document_id}.{field}"),
                all_records,
            )

    for position, entry in enumerate(index.get("timeline", [])):
        if not isinstance(entry, dict):
            continue
        target = entry.get("event")
        if isinstance(target, str) and target not in events:
            errors.append(f"timeline[{position}].event: dangling reference {target!r}")

    for question in index.get("open_for_the_steward", []):
        if not isinstance(question, dict):
            continue
        question_id = str(question.get("id", "<missing-id>"))
        target = question.get("about")
        if isinstance(target, str) and target not in all_records:
            errors.append(
                f"open_for_the_steward.{question_id}.about: dangling reference {target!r}"
            )

    return errors


def _validate_governance(index: dict[str, Any]) -> list[str]:
    governance = index.get("governance")
    if not isinstance(governance, dict):
        return ["governance: required object is missing"]
    errors: list[str] = []
    authorities = set(governance.get("canon_authorities", []))
    if authorities != CANON_AUTHORITIES:
        errors.append(
            "governance.canon_authorities must exactly preserve Book One Chapter I"
        )
    labels = set(governance.get("training_layer_access_labels", []))
    if labels != TRAINING_ACCESS_LABELS:
        errors.append(
            "governance.training_layer_access_labels must contain exactly "
            "the seven approved labels"
        )
    firewall = governance.get("sealed_layer_behavior")
    if not isinstance(firewall, dict):
        errors.append("governance.sealed_layer_behavior is required")
    elif firewall.get("may_state_as_fact") is not False or firewall.get(
        "may_reveal_to_user"
    ) is not False:
        errors.append(
            "governance.sealed_layer_behavior must deny fact assertion and user disclosure"
        )
    return errors


def _validate_namespaces(index: dict[str, Any]) -> list[str]:
    contract = index.get("namespaces")
    if not isinstance(contract, dict):
        return ["namespaces: required object is missing"]
    collections = contract.get("collections")
    if not isinstance(collections, dict):
        return ["namespaces.collections: required object is missing"]
    errors: list[str] = []
    for collection in INDEX_COLLECTIONS:
        if collection not in collections:
            errors.append(f"namespaces.collections.{collection}: namespace is not declared")
    for collection, spec in collections.items():
        if not isinstance(spec, dict) or not spec.get("canonical_prefix"):
            errors.append(f"namespaces.collections.{collection}: canonical_prefix is required")
    for collection, record in _records(index):
        spec = collections.get(collection)
        record_id = record.get("id")
        if (
            isinstance(spec, dict)
            and spec.get("storage") == "qualified"
            and isinstance(record_id, str)
        ):
            prefix = spec.get("canonical_prefix")
            if isinstance(prefix, str) and not record_id.startswith(prefix):
                errors.append(
                    f"{collection}.{record_id}: id must use namespace prefix {prefix!r}"
                )
    record_ids = {
        str(record["id"])
        for _, record in _records(index)
        if isinstance(record.get("id"), str)
    }
    aliases = contract.get("legacy_aliases", {})
    if isinstance(aliases, dict):
        for legacy_id, target_id in aliases.items():
            if target_id not in record_ids:
                errors.append(
                    f"namespaces.legacy_aliases.{legacy_id}: "
                    f"target {target_id!r} does not exist"
                )
    return errors


def _validate_repository_sync(
    index: dict[str, Any],
    manifest: dict[str, Any],
    repo_root: Path,
) -> list[str]:
    contract = index.get("repository_sync")
    if not isinstance(contract, dict):
        return ["repository_sync: required object is missing"]
    errors: list[str] = []
    manifest_sources = manifest.get("sources", [])
    if not isinstance(manifest_sources, list):
        return ["repository sync manifest sources must be an array"]
    by_id = {
        str(source["id"]): source
        for source in manifest_sources
        if isinstance(source, dict) and isinstance(source.get("id"), str)
    }
    indexed_manifest_ids: set[str] = set()
    manifest_id_counts: Counter[str] = Counter()
    for source in index.get("sources", []):
        if not isinstance(source, dict):
            continue
        source_id = str(source.get("id", "<missing-id>"))
        manifest_id = source.get("manifest_source_id")
        repository_path = source.get("repository_path")
        if not isinstance(manifest_id, str):
            continue
        indexed_manifest_ids.add(manifest_id)
        manifest_id_counts[manifest_id] += 1
        manifest_source = by_id.get(manifest_id)
        if manifest_source is None:
            errors.append(
                f"sources.{source_id}.manifest_source_id: unknown manifest source {manifest_id!r}"
            )
            continue
        expected_path = manifest_source.get("path")
        if repository_path != expected_path:
            errors.append(
                f"sources.{source_id}.repository_path: expected {expected_path!r}, "
                f"found {repository_path!r}"
            )
        if isinstance(repository_path, str) and not (repo_root / repository_path).is_file():
            errors.append(f"sources.{source_id}.repository_path: file does not exist")

    duplicate_manifest_ids = sorted(
        source_id for source_id, count in manifest_id_counts.items() if count > 1
    )
    if duplicate_manifest_ids:
        errors.append(
            "repository_sync: manifest source identities represented more than once: "
            + ", ".join(duplicate_manifest_ids)
        )

    governed_roots = contract.get("governed_roots", [])
    governed = {
        source_id
        for source_id, source in by_id.items()
        if any(
            isinstance(source.get("path"), str)
            and (
                source["path"] == root
                or source["path"].startswith(f"{str(root).rstrip('/')}/")
            )
            for root in governed_roots
        )
    }
    excluded = set(contract.get("excluded_manifest_source_ids", []))
    missing = sorted(governed - indexed_manifest_ids - excluded)
    if missing:
        errors.append(
            "repository_sync: governed manifest sources absent from the index: "
            + ", ".join(missing)
        )
    unknown_exclusions = sorted(excluded - governed)
    if unknown_exclusions:
        errors.append(
            "repository_sync.excluded_manifest_source_ids contains unknown entries: "
            + ", ".join(unknown_exclusions)
        )
    return errors


def validate_lore_index(
    index_path: Path,
    schema_path: Path,
    manifest_path: Path,
    *,
    repo_root: Path,
) -> list[str]:
    """Validate schema, governance, identity, references, and repository coverage."""
    try:
        index = _load_object(index_path)
        schema = _load_object(schema_path)
        manifest = _load_object(manifest_path)
    except ValueError as exc:
        return [str(exc)]

    errors = [
        f"schema {error.json_path}: {error.message}"
        for error in Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        ).iter_errors(index)
    ]

    identifiers = [
        (collection, str(record["id"]))
        for collection, record in _records(index)
        if isinstance(record.get("id"), str)
    ]
    counts = Counter(identifier for _, identifier in identifiers)
    duplicate_ids = sorted(identifier for identifier, count in counts.items() if count > 1)
    if duplicate_ids:
        errors.append("global duplicate ids: " + ", ".join(duplicate_ids))

    errors.extend(_validate_namespaces(index))
    errors.extend(_validate_governance(index))
    errors.extend(_validate_references(index))
    errors.extend(_validate_repository_sync(index, manifest, repo_root))
    return sorted(set(errors))
