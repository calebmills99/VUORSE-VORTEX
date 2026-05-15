"""Canon firewall validation using centralized settings."""

from __future__ import annotations

from vuorse_vortex.schemas import MemoryRecord
from vuorse_vortex.settings import Settings, get_settings


class CanonFirewallValidator:
    """Validates that records in sealed layers respect canon firewall rules.

    Sealed categories are sourced from Settings.sealed_categories so that
    changes are centralized and consistently enforced across ingest and query.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    @property
    def sealed_categories(self) -> list[str]:
        return self._settings.sealed_categories

    def validate_record(self, record: MemoryRecord) -> list[str]:
        """Return a list of firewall violation messages for a single record."""
        errors: list[str] = []
        if record.layer in set(self.sealed_categories):
            if record.behavior.may_state_as_fact:
                errors.append("private layer may_state_as_fact must be false")
            if record.behavior.may_reveal_to_user:
                errors.append("private layer may_reveal_to_user must be false")
        return errors
