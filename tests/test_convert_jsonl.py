"""Unit tests for legacy JSONL conversion utility."""
import json
from pathlib import Path
from vuorse_vortex.convert_jsonl import convert_jsonl, normalize_record
from vuorse_vortex.schemas import MemoryRecord

def test_normalize_record_legacy_mapping() -> None:
    """Test that legacy fields are correctly converted and Pydantic-compliant."""
    legacy_raw = {
        "id": "test-id-123",
        "source_path": "canon/1_words_of_weaver_book_one/Words_of_Weaver_BOOK_ONE.MD",
        "source_anchor": "Chapter I",
        "canon_tier": "locked",
        "canon_status_label": "FULL",
        "title": "Weaver Decrees",
        "text": "Save the prairie mother, save the universe.",
    }
    
    normalized = normalize_record(legacy_raw)
    
    # Assert top-level fields
    assert normalized["id"] == "test-id-123"
    assert normalized["layer"] == "canon"
    assert normalized["title"] == "Weaver Decrees"
    assert normalized["text"] == "Save the prairie mother, save the universe."
    
    # Assert mapped metadata fields
    assert normalized["metadata"]["source_file"] == "canon/1_words_of_weaver_book_one/Words_of_Weaver_BOOK_ONE.MD"
    assert normalized["metadata"]["section"] == "Chapter I"
    
    # Assert that invalid literal 'FULL' was mapped to 'unknown' and appended to tags
    assert normalized["metadata"]["canon_status"] == "unknown"
    assert "FULL" in normalized["metadata"]["tags"]
    assert "locked" in normalized["metadata"]["tags"]
    
    # Assert full validation
    record = MemoryRecord(**normalized)
    assert record.id == "test-id-123"

def test_convert_jsonl_file(tmp_path: Path) -> None:
    """Test full file-based conversion pipeline."""
    input_file = tmp_path / "legacy.jsonl"
    output_file = tmp_path / "cleaned.jsonl"
    
    legacy_lines = [
        {"id": "id-1", "canon_status_label": "LOCKED", "title": "Record 1", "text": "First"},
        {"id": "id-2", "canon_status_label": "MODERATE", "title": "Record 2", "text": "Second"},
    ]
    
    with input_file.open("w", encoding="utf-8") as f:
        for item in legacy_lines:
            f.write(json.dumps(item) + "\n")
            
    convert_jsonl(input_file, output_file)
    
    assert output_file.exists()
    
    # Parse and validate the output lines
    with output_file.open("r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f if line.strip()]
        
    assert len(lines) == 2
    
    # Line 1: 'LOCKED' should map cleanly to 'locked'
    rec1 = MemoryRecord(**lines[0])
    assert rec1.metadata.canon_status == "locked"
    
    # Line 2: 'MODERATE' should map to 'unknown' and have 'MODERATE' in tags
    rec2 = MemoryRecord(**lines[1])
    assert rec2.metadata.canon_status == "unknown"
    assert "MODERATE" in rec2.metadata.tags
