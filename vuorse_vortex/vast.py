"""Vast.ai billing insurance: status, cost accounting, and fail-closed teardown.

Borrowed from slay-cortex, which learned these lessons the expensive way:

* ``resolve_vastai`` / ``list_instances`` / ``is_dead_instance`` / ``destroy_ids``
  come from ``slay-cortex/scripts/vast_insurance.py``.
* ``api_key_source`` / ``fetch_vast_user`` / ``assert_expected_account`` come from
  ``slay-cortex/get_instance.py``.

Two rules travel with the code and are not negotiable:

**Ambient auth only.** The key is read from ``VASTAI_API_KEY`` or
``~/.config/vastai/vast_api_key`` — never from a repo ``.env``. This repo's
``.env.example`` ships a live-looking ``VAST_API_KEY``; a provisioner that
reads secrets out of the tree is how that happens. Nothing here prints a key.

**A rented box that exited is still billing.** ``exited`` means the container
died, not that the meter stopped. :func:`dead_instances` finds exactly those.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

VASTAI_KEYFILE = Path.home() / ".config" / "vastai" / "vast_api_key"

# Keep means "I am still using this box." A container that already died is not that.
DEAD_STATUSES = frozenset({"exited", "offline", "stopped", "error"})

# Environment variable naming the account this repo is allowed to bill.
ACCOUNT_ENV = "VUORSE_VAST_ACCOUNT"


class VastError(Exception):
    """Raised when the Vast CLI is missing, unauthenticated, or unparseable."""


class VastCliMissingError(VastError):
    """The vastai CLI is not installed or not on PATH."""


class WrongAccountError(VastError):
    """The authenticated Vast account is not the one this repo bills to."""


def resolve_vastai() -> str:
    """Locate the vastai CLI, preferring the repo venv over a stripped PATH.

    Hooks and agent shells frequently run without the user's PATH, so the
    venv shims are checked first.
    """
    base = Path(__file__).resolve().parent.parent
    candidates = (
        base / ".venv" / "Scripts" / "vastai.exe",
        base / ".venv" / "Scripts" / "vastai",
        base / ".venv" / "bin" / "vastai",
    )
    for path in candidates:
        if path.is_file():
            return str(path)
    found = shutil.which("vastai")
    if found:
        return found
    raise VastCliMissingError(
        "vastai CLI not found. Expected a repo venv shim at "
        f"{base / '.venv' / 'Scripts' / 'vastai.exe'} or `vastai` on PATH. "
        "Install with: curl -fsSL https://vast.ai/install.sh | bash"
    )


def _run_vastai(args: list[str]) -> str:
    """Run a vastai subcommand and return stdout, raising with stderr on failure."""
    vastai = resolve_vastai()
    result = subprocess.run(
        [vastai, *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip() or "no output"
        raise VastError(f"`vastai {' '.join(args)}` failed (exit {result.returncode}): {detail}")
    return (result.stdout or "").strip()


def api_key_source() -> str:
    """Where vastai will authenticate from. Never returns the key itself."""
    env_key = (os.environ.get("VASTAI_API_KEY") or "").strip()
    if env_key:
        return f"env:VASTAI_API_KEY (len={len(env_key)})"
    if VASTAI_KEYFILE.is_file():
        return f"keyfile:{VASTAI_KEYFILE}"
    return "NONE (no VASTAI_API_KEY and no ~/.config/vastai/vast_api_key)"


def fetch_vast_user() -> dict[str, Any]:
    """Return the account attached to the ambient vastai CLI key."""
    raw = _run_vastai(["show", "user", "--raw"])
    try:
        user = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise VastError(f"Unable to parse `vastai show user --raw`: {raw[:300]}") from exc
    if not isinstance(user, dict):
        raise VastError(f"Unexpected user payload type: {type(user).__name__}")
    return user


def assert_expected_account(expect_email: str | None = None) -> dict[str, Any]:
    """Fail closed if the CLI is not logged into the expected account.

    ``expect_email`` falls back to ``$VUORSE_VAST_ACCOUNT``. When neither is
    set the account is returned unguarded — this repo does not hardcode whose
    Gmail is allowed to be billed.

    Raises:
        VastError: no API key is configured at all.
        WrongAccountError: the CLI is logged into a different account.
    """
    source = api_key_source()
    if source.startswith("NONE"):
        raise VastError(
            f"No Vast API key configured ({source}). Set VASTAI_API_KEY or write "
            "~/.config/vastai/vast_api_key. Do not put the key in a repo .env."
        )
    user = fetch_vast_user()
    expect = (expect_email or os.environ.get(ACCOUNT_ENV) or "").strip().lower()
    if not expect:
        return user
    email = str(user.get("email") or "").strip().lower()
    if email != expect:
        raise WrongAccountError(
            f"Refusing to act: vastai is authenticated as "
            f"'{email or '<missing>'}' but {ACCOUNT_ENV} expects '{expect}'. "
            "Fix VASTAI_API_KEY / ~/.config/vastai/vast_api_key, or pass --any-account."
        )
    return user


@dataclass(frozen=True)
class Instance:
    """One rented Vast box, with the part that costs money made explicit."""

    id: str
    status: str
    label: str
    gpu: str
    dph: float
    age_hours: float
    host: str
    ssh_port: str
    image: str

    @property
    def is_dead(self) -> bool:
        """True when the box is still rented but the workload is gone."""
        return self.status in DEAD_STATUSES

    @property
    def accrued(self) -> float:
        """Dollars this instance has burned since it started, best estimate."""
        return self.dph * self.age_hours

    def describe(self) -> str:
        flag = "  <-- DEAD BUT BILLING" if self.is_dead else ""
        return (
            f"  id={self.id} status={self.status} gpu={self.gpu} "
            f"${self.dph:.4f}/hr age={self.age_hours:.1f}h "
            f"accrued=~${self.accrued:.2f} label={self.label}{flag}"
        )


def _as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _to_instance(raw: dict[str, Any], *, now: float) -> Instance:
    started = _as_float(raw.get("start_date"))
    age_hours = max((now - started) / 3600.0, 0.0) if started else 0.0
    return Instance(
        id=str(raw.get("id") or "").strip(),
        status=str(raw.get("actual_status") or raw.get("cur_state") or "").strip().lower(),
        label=str(raw.get("label") or ""),
        gpu=f"{raw.get('num_gpus') or '?'}x {raw.get('gpu_name') or 'unknown'}",
        dph=_as_float(raw.get("dph_total") or raw.get("dph") or raw.get("cost_per_hour")),
        age_hours=age_hours,
        host=str(raw.get("public_ipaddr") or raw.get("ssh_host") or ""),
        ssh_port=str(raw.get("ssh_port") or ""),
        image=str(raw.get("image_uuid") or ""),
    )


def list_instances(*, now: float | None = None) -> list[Instance]:
    """Return every instance on the authenticated account.

    An empty list is a real answer -- it means nothing is billing -- and is
    distinct from a failure, which raises.
    """
    text = _run_vastai(["show", "instances", "--raw"])
    if not text:
        return []
    try:
        decoded: Any = json.loads(text)
    except json.JSONDecodeError as exc:
        raise VastError(f"Unexpected JSON from `vastai show instances --raw`: {exc}") from exc

    rows: list[dict[str, Any]] | None = None
    if isinstance(decoded, list):
        rows = [r for r in decoded if isinstance(r, dict)]
    elif isinstance(decoded, dict):
        for key in ("instances", "rows", "results"):
            value = decoded.get(key)
            if isinstance(value, list):
                rows = [r for r in value if isinstance(r, dict)]
                break
    if rows is None:
        raise VastError(
            "Unexpected payload shape from `vastai show instances --raw`: "
            f"{type(decoded).__name__}"
        )

    stamp = time.time() if now is None else now
    return [_to_instance(row, now=stamp) for row in rows]


def dead_instances(instances: list[Instance]) -> list[Instance]:
    """Instances whose container has died while the rental keeps billing."""
    return [inst for inst in instances if inst.is_dead]


def total_burn_rate(instances: list[Instance]) -> float:
    """Combined dollars-per-hour across every instance still on the account."""
    return sum(inst.dph for inst in instances)


def destroy_ids(ids: list[str], *, dry_run: bool = True) -> list[str]:
    """Destroy instances by id. Dry-run by default; returns the ids acted on.

    Nothing is destroyed unless ``dry_run=False`` is passed explicitly. The
    caller is responsible for having confirmed with a human first.
    """
    vastai = resolve_vastai()
    acted: list[str] = []
    failures: list[str] = []

    for raw_id in ids:
        iid = str(raw_id).strip()
        if not iid:
            continue
        if dry_run:
            acted.append(iid)
            continue
        result = subprocess.run(
            [vastai, "destroy", "instance", iid, "-y"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "").strip() or "no output"
            failures.append(f"{iid}: exit {result.returncode}: {detail}")
        else:
            acted.append(iid)

    if failures:
        raise VastError(
            "Some instances were not destroyed and may still be billing:\n  "
            + "\n  ".join(failures)
        )
    return acted
