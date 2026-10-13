"""Tests for Vast.ai billing insurance.

Nothing here talks to Vast. The subprocess boundary is stubbed, because the
behaviour worth pinning down is exactly the behaviour that costs money if it
regresses: a dead-but-rented box must be recognised, and destroy must not
destroy anything unless it was told to twice.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from vuorse_vortex import vast as vast_mod
from vuorse_vortex.vast import (
    ACCOUNT_ENV,
    Instance,
    VastError,
    WrongAccountError,
    api_key_source,
    assert_expected_account,
    dead_instances,
    destroy_ids,
    list_instances,
    total_burn_rate,
)


@pytest.fixture(autouse=True)
def _fake_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pretend the vastai CLI exists so tests never depend on the machine."""
    monkeypatch.setattr(vast_mod, "resolve_vastai", lambda: "vastai")


def _instance(**overrides: Any) -> Instance:
    base = {
        "id": "480962",
        "status": "running",
        "label": "susie-training",
        "gpu": "1x B200",
        "dph": 6.9792,
        "age_hours": 2.0,
        "host": "162.192.107.46",
        "ssh_port": "14580",
        "image": "pytorch/pytorch",
    }
    base.update(overrides)
    return Instance(**base)  # type: ignore[arg-type]


class TestApiKeySource:
    def test_env_key_wins_and_key_is_never_returned(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("VASTAI_API_KEY", "supersecretvalue")
        source = api_key_source()
        assert source.startswith("env:VASTAI_API_KEY")
        assert "supersecretvalue" not in source

    def test_reports_none_when_unconfigured(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.delenv("VASTAI_API_KEY", raising=False)
        monkeypatch.setattr(vast_mod, "VASTAI_KEYFILE", tmp_path / "absent")
        assert api_key_source().startswith("NONE")


class TestAccountGuard:
    def test_refuses_when_no_key_configured(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.delenv("VASTAI_API_KEY", raising=False)
        monkeypatch.setattr(vast_mod, "VASTAI_KEYFILE", tmp_path / "absent")
        with pytest.raises(VastError, match="No Vast API key"):
            assert_expected_account()

    def test_refuses_on_wrong_account(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("VASTAI_API_KEY", "k")
        monkeypatch.setenv(ACCOUNT_ENV, "expected@example.com")
        monkeypatch.setattr(vast_mod, "fetch_vast_user", lambda: {"email": "other@example.com"})
        with pytest.raises(WrongAccountError, match="other@example.com"):
            assert_expected_account()

    def test_passes_on_matching_account_case_insensitively(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("VASTAI_API_KEY", "k")
        monkeypatch.setenv(ACCOUNT_ENV, "Expected@Example.com")
        monkeypatch.setattr(vast_mod, "fetch_vast_user", lambda: {"email": "expected@example.com"})
        assert assert_expected_account()["email"] == "expected@example.com"

    def test_unguarded_when_no_expectation_is_declared(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("VASTAI_API_KEY", "k")
        monkeypatch.delenv(ACCOUNT_ENV, raising=False)
        monkeypatch.setattr(vast_mod, "fetch_vast_user", lambda: {"email": "whoever@example.com"})
        assert assert_expected_account()["email"] == "whoever@example.com"


class TestListInstances:
    def _stub(self, monkeypatch: pytest.MonkeyPatch, payload: str, code: int = 0) -> None:
        def fake_run(*_args: Any, **_kwargs: Any) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(args=[], returncode=code, stdout=payload, stderr="")

        monkeypatch.setattr(vast_mod.subprocess, "run", fake_run)

    def test_empty_account_is_a_real_answer_not_an_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._stub(monkeypatch, "[]")
        assert list_instances() == []

    def test_parses_dph_and_age_into_accrued_cost(self, monkeypatch: pytest.MonkeyPatch) -> None:
        now = 1_000_000.0
        rows = [
            {
                "id": 480962,
                "actual_status": "running",
                "gpu_name": "B200",
                "num_gpus": 1,
                "dph_total": 6.9792,
                "start_date": now - 7200,  # two hours
            }
        ]
        self._stub(monkeypatch, json.dumps(rows))
        [inst] = list_instances(now=now)
        assert inst.age_hours == pytest.approx(2.0)
        assert inst.accrued == pytest.approx(13.9584)

    def test_cur_state_is_accepted_when_actual_status_is_absent(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._stub(monkeypatch, json.dumps([{"id": 1, "cur_state": "EXITED"}]))
        [inst] = list_instances()
        assert inst.status == "exited"
        assert inst.is_dead

    def test_wrapped_payload_shape_is_unwrapped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._stub(monkeypatch, json.dumps({"instances": [{"id": 7, "actual_status": "running"}]}))
        assert [i.id for i in list_instances()] == ["7"]

    def test_cli_failure_raises_with_stderr(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def fake_run(*_args: Any, **_kwargs: Any) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(
                args=[], returncode=1, stdout="", stderr="401 unauthorized"
            )

        monkeypatch.setattr(vast_mod.subprocess, "run", fake_run)
        with pytest.raises(VastError, match="401 unauthorized"):
            list_instances()

    def test_garbage_payload_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._stub(monkeypatch, "not json at all")
        with pytest.raises(VastError, match="Unexpected JSON"):
            list_instances()


class TestDeadDetection:
    @pytest.mark.parametrize("status", ["exited", "offline", "stopped", "error"])
    def test_dead_statuses_are_still_billing(self, status: str) -> None:
        assert _instance(status=status).is_dead

    def test_running_is_not_dead(self) -> None:
        assert not _instance(status="running").is_dead

    def test_dead_instances_filters(self) -> None:
        live = _instance(id="1", status="running")
        gone = _instance(id="2", status="exited")
        assert dead_instances([live, gone]) == [gone]

    def test_burn_rate_sums_across_the_account(self) -> None:
        rate = total_burn_rate([_instance(dph=6.9792), _instance(dph=11.3056)])
        assert rate == pytest.approx(18.2848)


class TestDestroy:
    def test_dry_run_is_the_default_and_spawns_nothing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def explode(*_args: Any, **_kwargs: Any) -> None:
            raise AssertionError("destroy must not shell out during a dry run")

        monkeypatch.setattr(vast_mod.subprocess, "run", explode)
        assert destroy_ids(["480962"]) == ["480962"]

    def test_commit_calls_the_cli_once_per_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        calls: list[list[str]] = []

        def fake_run(cmd: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
            calls.append(cmd)
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="ok", stderr="")

        monkeypatch.setattr(vast_mod.subprocess, "run", fake_run)
        assert destroy_ids(["1", "2"], dry_run=False) == ["1", "2"]
        assert [c[1:4] for c in calls] == [
            ["destroy", "instance", "1"],
            ["destroy", "instance", "2"],
        ]

    def test_a_failed_destroy_raises_because_the_box_may_still_bill(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def fake_run(cmd: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(
                args=cmd, returncode=1, stdout="", stderr="instance not found"
            )

        monkeypatch.setattr(vast_mod.subprocess, "run", fake_run)
        with pytest.raises(VastError, match="may still be billing"):
            destroy_ids(["480962"], dry_run=False)

    def test_blank_ids_are_skipped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def explode(*_args: Any, **_kwargs: Any) -> None:
            raise AssertionError("blank ids must never reach the CLI")

        monkeypatch.setattr(vast_mod.subprocess, "run", explode)
        assert destroy_ids(["", "  "], dry_run=False) == []
