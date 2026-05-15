"""Canon Firewall Validator.

The canon firewall enforces strict separation between memory categories.
roadmap_manifest units are NEVER exposed via public query interfaces.

This validator runs at ingest time and on demand, ensuring that:
1. roadmap_manifest units are always SEALED.
2. Synthetic memories are never passed off as canon.
3. No erased memory is inadvertently made public.
4. Visibility and behavioral permissions are consistent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from vuorse_vortex.logging_utils import get_logger
from vuorse_vortex.models.memory_unit import (
    CanonStatus,
    MemoryCategory,
    MemoryUnit,
    VisibilityRule,
)

logger = get_logger(__name__)


@dataclass
class FirewallViolation:
    """A single canon firewall violation record."""

    unit_id: str
    rule: str
    severity: str  # "critical" | "warning"
    detail: str
    suggested_fix: str = ""

    def is_critical(self) -> bool:
        return self.severity == "critical"


@dataclass
class FirewallReport:
    """Full validation report from a canon firewall run."""

    total_units: int = 0
    violations: list[FirewallViolation] = field(default_factory=list)
    passed: list[str] = field(default_factory=list)

    @property
    def critical_count(self) -> int:
        return sum(1 for v in self.violations if v.is_critical())

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if not v.is_critical())

    @property
    def is_clean(self) -> bool:
        return self.critical_count == 0


class CanonFirewallValidator:
    """Validates memory units against canon firewall rules.

    Rules enforced:
    - RULE-001: roadmap_manifest units must be SEALED or VOID.
    - RULE-002: synthetic memories must not have PUBLIC visibility.
    - RULE-003: erased memories must not be retrievable.
    - RULE-004: PUBLIC units must have retrievable=True behavioral permission.
    - RULE-005: roadmap_manifest units must not be retrievable via public interfaces.
    """

    RULES = [
        "RULE-001",
        "RULE-002",
        "RULE-003",
        "RULE-004",
        "RULE-005",
    ]

    def __init__(self, strict_mode: bool = True) -> None:
        """
        Args:
            strict_mode: If True, critical violations cause validate() to raise.
        """
        self.strict_mode = strict_mode

    def _check_unit(self, unit: MemoryUnit) -> list[FirewallViolation]:
        """Run all firewall rules against a single MemoryUnit."""
        violations: list[FirewallViolation] = []

        # RULE-001: roadmap_manifest must be SEALED or VOID
        if unit.category == MemoryCategory.ROADMAP_MANIFEST:
            if unit.visibility_rules not in (VisibilityRule.SEALED, VisibilityRule.VOID):
                violations.append(
                    FirewallViolation(
                        unit_id=unit.id,
                        rule="RULE-001",
                        severity="critical",
                        detail=(
                            f"roadmap_manifest unit {unit.id!r} has visibility "
                            f"{unit.visibility_rules!r} — must be SEALED or VOID"
                        ),
                        suggested_fix="Set visibility_rules to 'sealed'",
                    )
                )

        # RULE-002: synthetic memories must not be PUBLIC
        if unit.canon_status == CanonStatus.SYNTHETIC:
            if unit.visibility_rules == VisibilityRule.PUBLIC:
                violations.append(
                    FirewallViolation(
                        unit_id=unit.id,
                        rule="RULE-002",
                        severity="critical",
                        detail=(
                            f"Synthetic unit {unit.id!r} has PUBLIC visibility — "
                            "synthetic memories must be RESTRICTED or lower"
                        ),
                        suggested_fix="Set visibility_rules to 'restricted'",
                    )
                )

        # RULE-003: erased memories must not be retrievable
        if unit.canon_status == CanonStatus.ERASED:
            if unit.behavioral_permissions.retrievable:
                violations.append(
                    FirewallViolation(
                        unit_id=unit.id,
                        rule="RULE-003",
                        severity="critical",
                        detail=(
                            f"Erased unit {unit.id!r} has retrievable=True — "
                            "erased memories must not be returned via queries"
                        ),
                        suggested_fix="Set behavioral_permissions.retrievable to False",
                    )
                )

        # RULE-004: PUBLIC units should be retrievable
        if unit.visibility_rules == VisibilityRule.PUBLIC:
            if not unit.behavioral_permissions.retrievable:
                violations.append(
                    FirewallViolation(
                        unit_id=unit.id,
                        rule="RULE-004",
                        severity="warning",
                        detail=(
                            f"PUBLIC unit {unit.id!r} has retrievable=False — "
                            "public units are expected to be retrievable"
                        ),
                        suggested_fix="Set behavioral_permissions.retrievable to True or reduce visibility",
                    )
                )

        # RULE-005: roadmap_manifest must not be publicly retrievable
        if unit.category == MemoryCategory.ROADMAP_MANIFEST:
            if unit.behavioral_permissions.retrievable and unit.is_publicly_queryable():
                violations.append(
                    FirewallViolation(
                        unit_id=unit.id,
                        rule="RULE-005",
                        severity="critical",
                        detail=(
                            f"roadmap_manifest unit {unit.id!r} is publicly queryable — "
                            "this category must never be accessible via public interfaces"
                        ),
                        suggested_fix="Set visibility_rules to 'sealed' and retrievable to False",
                    )
                )

        return violations

    def validate(self, units: list[MemoryUnit]) -> FirewallReport:
        """Validate a list of MemoryUnit objects against canon firewall rules.

        Args:
            units: Memory units to validate.

        Returns:
            FirewallReport with all violations and pass/fail status.

        Raises:
            ValueError: If strict_mode=True and critical violations are found.
        """
        report = FirewallReport(total_units=len(units))

        for unit in units:
            unit_violations = self._check_unit(unit)
            if unit_violations:
                report.violations.extend(unit_violations)
                for v in unit_violations:
                    log_fn = logger.error if v.is_critical() else logger.warning
                    log_fn(
                        "Canon firewall violation",
                        rule=v.rule,
                        severity=v.severity,
                        unit_id=v.unit_id,
                        detail=v.detail,
                    )
            else:
                report.passed.append(unit.id)

        logger.info(
            "Canon firewall validation complete",
            total=report.total_units,
            passed=len(report.passed),
            critical=report.critical_count,
            warnings=report.warning_count,
        )

        if self.strict_mode and not report.is_clean:
            raise ValueError(
                f"Canon firewall: {report.critical_count} critical violation(s) detected. "
                "Ingest aborted."
            )

        return report

    def validate_jsonl_records(self, records: list[dict[str, Any]]) -> FirewallReport:
        """Parse and validate JSONL records.

        Args:
            records: List of dicts (from a JSONL file) to validate.

        Returns:
            FirewallReport.
        """
        units = [MemoryUnit.model_validate(r) for r in records]
        return self.validate(units)
