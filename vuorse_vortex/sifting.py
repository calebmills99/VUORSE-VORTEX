"""Sifting and sanitization helpers for Slayverse concepts."""

import re

def clean_concept_name(name: str) -> str:
    if not name:
        return ""
    # Remove bracketed statuses
    name = re.sub(r'\[[A-Z_ ]+\]', '', name)
    # Strip outline numbering (e.g. "2. Series Overview" -> "Series Overview")
    name = re.sub(r'^\s*(\d+(\.\d+)*\s*[-–—:.]*\s*)', '', name)
    # Strip trailing hashes and indices
    name = re.sub(r'_(?:[0-9]+_[0-9a-fA-F]{8,12})$', '', name)
    name = re.sub(r'_(?:[0-9a-fA-F]{8,12}|(?=.*[0-9])[a-zA-Z0-9]{8,12})$', '', name)
    name = re.sub(r'_(?:[0-9a-fA-F]{8,12})$', '', name)
    name = re.sub(r'_(?:[0-9]+)$', '', name)
    # Strip canon path prefixes
    name = re.sub(r'^canon_[a-zA-Z0-9_]*_md_(?:character|place|artifact|ritual|organization|cosmology|story_arc|relationship|timeline)_(?:record|note|preface|fact|graph_block)_', '', name, flags=re.IGNORECASE)
    name = re.sub(r'^canon_[a-zA-Z0-9_]*_md_(?:character|place|artifact|ritual|organization|cosmology|story_arc|relationship|timeline)s?_', '', name, flags=re.IGNORECASE)
    name = re.sub(r'^canon_[a-zA-Z0-9_]*_md_', '', name, flags=re.IGNORECASE)
    name = re.sub(r'^canon_', '', name, flags=re.IGNORECASE)
    # Replace underscores with spaces
    name = name.replace("_", " ").strip()
    # Normalize whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def is_valid_concept_name(name: str) -> bool:
    if not name:
        return False
    if name.isdigit():
        return False
    if re.match(r'^[0-9a-fA-F]{8,12}$', name):
        return False
    lower_name = name.lower()
    generic_exclusions = {
        "document preamble",
        "markdown",
        "chatgpt said:",
        "prompt:",
        "key features include:",
        "issue recap:",
        "thought for 7s",
        "thought for a second",
        "thought for a few seconds",
        "thought for a couple of seconds",
        "updated memory",
        "stopped talking to app",
        "image content",
        "positive prompt",
        "negative prompt",
        "chatgpt said",
        "you said",
        "you said:",
        "preamble",
        "untitled",
        "skip",
        "provenance skip",
        "key features",
        "thought for",
        "thought",
        "session",
        "digest",
        "preface",
        "notes",
        "note",
        "summary",
        "body",
        "content",
        "entities",
        "tags",
        "id",
        "title",
        "concept",
        "layer",
        "record type",
        "record_type",
        "canon rank",
        "canon_rank",
        "training layer access",
        "training_layer_access",
        "semantic class",
        "semantic_class",
        "dominant noun phrase",
        "dominant_noun_phrase",
    }
    if lower_name in generic_exclusions:
        return False
    if len(lower_name) <= 2:
        if lower_name not in {"eli", "pop", "cat"}:
            return False
    if re.match(r'^[a-fA-F0-9]{8,12}$', name):
        return False
    return True
