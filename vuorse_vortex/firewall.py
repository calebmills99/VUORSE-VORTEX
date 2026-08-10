"""Canon firewall validation using centralized settings."""

from __future__ import annotations

from vuorse_vortex.schemas import MemoryRecord
from vuorse_vortex.settings import Settings, get_settings


class CanonFirewallViolation(Exception):
    """Raised when a sealed-layer record violates the canon firewall invariant.

    The premise of VUORSE-VORTEX is that records in sealed layers (apocrypha,
    roadmap_manifest, hooplehopper_totality, ...) must never be stated as fact
    or revealed to users. Anything that loosens that invariant — including a
    caller that tries to push such a record into an embedding store, a notebook
    that constructs a record by hand, or a future backend that forgets to call
    validate_jsonl — should fail loudly here rather than silently corrupting
    the canon boundary.
    """


class CanonFirewallValidator:
    """Validates that records in sealed layers respect canon firewall rules.

    Sealed categories are sourced from Settings.sealed_categories so that
    changes are centralized and consistently enforced across ingest and query.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._sealed_categories = set(self._settings.sealed_categories)

    @property
    def sealed_categories(self) -> list[str]:
        return self._settings.sealed_categories

    def validate_record(self, record: MemoryRecord) -> list[str]:
        """Return a list of firewall violation messages for a single record."""
        errors: list[str] = []
        if record.layer in self._sealed_categories:
            if record.behavior.may_state_as_fact:
                errors.append("private layer may_state_as_fact must be false")
            if record.behavior.may_reveal_to_user:
                errors.append("private layer may_reveal_to_user must be false")
        return errors

    def enforce(self, record: MemoryRecord, *, context: str = "") -> None:
        """Raise CanonFirewallViolation if the record violates the firewall.

        ``context`` is a free-form label (e.g. "chromadb ingest record #3 id='foo'")
        that shows up in the exception message so the call site is identifiable
        without a traceback.
        """
        violations = self.validate_record(record)
        if violations:
            prefix = f"{context}: " if context else ""
            raise CanonFirewallViolation(
                f"{prefix}canon firewall violation "
                f"(layer={record.layer!r}, id={record.id!r}): {'; '.join(violations)}"
            )
