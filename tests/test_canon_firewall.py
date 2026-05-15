"""Tests for the Canon Firewall Validator."""

from __future__ import annotations

import pytest

from vuorse_vortex.agents.canon_firewall import CanonFirewallValidator, FirewallViolation
from vuorse_vortex.models.memory_unit import (
    BehavioralPermissions,
    CanonStatus,
    MemoryCategory,
    MemoryUnit,
    VisibilityRule,
)


def make_unit(**kwargs) -> MemoryUnit:
    """Helper to create a MemoryUnit with defaults."""
    defaults = {
        "category": MemoryCategory.CANON,
        "content": "Test memory content.",
    }
    defaults.update(kwargs)
    return MemoryUnit(**defaults)


class TestCanonFirewallValidator:
    def setup_method(self):
        self.validator = CanonFirewallValidator(strict_mode=False)

    def test_clean_canon_unit_passes(self):
        units = [make_unit(category=MemoryCategory.CANON, visibility_rules=VisibilityRule.PUBLIC)]
        report = self.validator.validate(units)
        assert report.is_clean
        assert report.critical_count == 0

    def test_rule_001_roadmap_must_be_sealed(self):
        """RULE-001: roadmap_manifest with non-sealed visibility is a critical violation."""
        # The model auto-seals roadmap_manifest, so we need to test via raw dict
        # and validate_jsonl_records to simulate a bad record bypassing model validation.
        # We test the validator rule itself by directly calling _check_unit on a
        # unit that has been constructed to bypass the model validator.
        unit = make_unit(category=MemoryCategory.ROADMAP_MANIFEST)
        # The model auto-seals it; verify the model enforcement works
        assert unit.visibility_rules == VisibilityRule.SEALED
        # Now manually set to restricted to test the firewall rule
        unit.visibility_rules = VisibilityRule.RESTRICTED
        violations = self.validator._check_unit(unit)
        rule_ids = [v.rule for v in violations]
        assert "RULE-001" in rule_ids
        critical = [v for v in violations if v.rule == "RULE-001"]
        assert all(v.is_critical() for v in critical)

    def test_rule_002_synthetic_not_public(self):
        """RULE-002: synthetic memories must not be PUBLIC."""
        unit = make_unit(
            category=MemoryCategory.APOCRYPHA,
            canon_status=CanonStatus.SYNTHETIC,
        )
        # Model auto-demotes synthetic public → restricted, so manually set it back
        unit.visibility_rules = VisibilityRule.PUBLIC
        violations = self.validator._check_unit(unit)
        rule_ids = [v.rule for v in violations]
        assert "RULE-002" in rule_ids

    def test_rule_003_erased_not_retrievable(self):
        """RULE-003: erased memories must not be retrievable."""
        unit = make_unit(
            canon_status=CanonStatus.ERASED,
            behavioral_permissions=BehavioralPermissions(retrievable=True),
        )
        violations = self.validator._check_unit(unit)
        rule_ids = [v.rule for v in violations]
        assert "RULE-003" in rule_ids
        critical = [v for v in violations if v.rule == "RULE-003"]
        assert all(v.is_critical() for v in critical)

    def test_rule_004_public_should_be_retrievable(self):
        """RULE-004: PUBLIC units with retrievable=False get a warning."""
        unit = make_unit(
            visibility_rules=VisibilityRule.PUBLIC,
            behavioral_permissions=BehavioralPermissions(retrievable=False),
        )
        violations = self.validator._check_unit(unit)
        rule_ids = [v.rule for v in violations]
        assert "RULE-004" in rule_ids
        warnings = [v for v in violations if v.rule == "RULE-004"]
        assert all(not v.is_critical() for v in warnings)

    def test_clean_erased_not_retrievable_passes(self):
        """No RULE-003 when erased + not retrievable."""
        unit = make_unit(
            canon_status=CanonStatus.ERASED,
            behavioral_permissions=BehavioralPermissions(retrievable=False),
        )
        violations = self.validator._check_unit(unit)
        rule_ids = [v.rule for v in violations]
        assert "RULE-003" not in rule_ids

    def test_validate_list_passes(self):
        units = [
            make_unit(category=MemoryCategory.CANON),
            make_unit(category=MemoryCategory.APOCRYPHA),
            make_unit(category=MemoryCategory.HOOPLEHOPPER_TOTALITY),
        ]
        report = self.validator.validate(units)
        assert report.total_units == 3
        assert report.is_clean

    def test_strict_mode_raises_on_critical(self):
        """Strict mode should raise ValueError on critical violations."""
        strict_validator = CanonFirewallValidator(strict_mode=True)
        unit = make_unit(
            canon_status=CanonStatus.ERASED,
            behavioral_permissions=BehavioralPermissions(retrievable=True),
        )
        with pytest.raises(ValueError, match="critical violation"):
            strict_validator.validate([unit])

    def test_validate_jsonl_records(self):
        """validate_jsonl_records accepts raw dicts."""
        records = [
            {
                "category": "canon",
                "content": "Valid canon memory.",
                "visibility_rules": "public",
                "canon_status": "verified",
            }
        ]
        report = self.validator.validate_jsonl_records(records)
        assert report.total_units == 1
        assert report.is_clean

    def test_firewall_violation_is_critical(self):
        v_critical = FirewallViolation(unit_id="x", rule="RULE-001", severity="critical", detail="test")
        v_warning = FirewallViolation(unit_id="x", rule="RULE-004", severity="warning", detail="test")
        assert v_critical.is_critical() is True
        assert v_warning.is_critical() is False

    def test_report_counts(self):
        units = [
            make_unit(
                canon_status=CanonStatus.ERASED,
                behavioral_permissions=BehavioralPermissions(retrievable=True),
            ),
            make_unit(category=MemoryCategory.CANON),
        ]
        report = self.validator.validate(units)
        assert report.total_units == 2
        assert report.critical_count >= 1
        assert len(report.passed) == 1
