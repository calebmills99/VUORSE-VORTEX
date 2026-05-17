"""Mocked-client tests for `scripts/vast_provision.py`.

The provisioner ships as a PEP-723 script under ``scripts/`` rather than as an
importable package module, so we load it via ``importlib.util``. All tests use
in-memory stub clients — no Vast.ai SDK install, no network. Their job is to
catch SDK-shape drift (missing methods, renamed kwargs, return-type changes)
before someone reaches for `--launch` and gets a half-second-long failure.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock

import pytest
import typer
from typer.testing import CliRunner


def _load_provisioner() -> ModuleType:
    """Load ``scripts/vast_provision.py`` as the module ``vast_provision``."""
    if "vast_provision" in sys.modules:
        return sys.modules["vast_provision"]
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "vast_provision.py"
    spec = importlib.util.spec_from_file_location("vast_provision", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["vast_provision"] = module
    spec.loader.exec_module(module)
    return module


vp = _load_provisioner()


def _opts(**overrides: Any) -> Any:
    """Build a ProvisionOptions with the published VUORSE defaults."""
    defaults = {
        "min_disk": vp.MIN_DISK_GB,
        "min_vram": vp.MIN_GPU_RAM_GB,
        "min_reliability": vp.MIN_RELIABILITY,
        "min_compute_cap": vp.MIN_COMPUTE_CAP,
        "countries": list(vp.NA_GEOS),
        "tag": vp.IMAGE_TAG,
        "num_gpus": vp.DEFAULT_NUM_GPUS,
        "max_dph": vp.DEFAULT_MAX_DPH,
        "launch": False,
        "template_only": False,
        "allow_downgrade": False,
    }
    defaults.update(overrides)
    return vp.ProvisionOptions(**defaults)


# --------------------------------------------------------------------------- #
# _normalize_response                                                          #
# --------------------------------------------------------------------------- #


def test_normalize_response_passes_dict_through() -> None:
    payload = {"hash_id": "abc"}
    assert vp._normalize_response(payload) is payload


def test_normalize_response_passes_list_through() -> None:
    payload = [{"id": 1}]
    assert vp._normalize_response(payload) is payload


def test_normalize_response_parses_json_string() -> None:
    assert vp._normalize_response('{"hash_id": "abc"}') == {"hash_id": "abc"}
    assert vp._normalize_response('[{"id": 1}]') == [{"id": 1}]


def test_normalize_response_parses_json_bytes() -> None:
    assert vp._normalize_response(b'{"hash_id": "abc"}') == {"hash_id": "abc"}


def test_normalize_response_returns_malformed_string_unchanged() -> None:
    assert vp._normalize_response("{not json") == "{not json"


def test_normalize_response_ignores_plain_string() -> None:
    assert vp._normalize_response("hello") == "hello"


# --------------------------------------------------------------------------- #
# _coerce_template_list                                                        #
# --------------------------------------------------------------------------- #


def test_coerce_template_list_accepts_list() -> None:
    tpls = [{"name": "a"}, {"name": "b"}]
    assert vp._coerce_template_list(tpls) == tpls


def test_coerce_template_list_accepts_wrapped_dict() -> None:
    assert vp._coerce_template_list({"templates": [{"name": "a"}]}) == [{"name": "a"}]


def test_coerce_template_list_handles_none() -> None:
    assert vp._coerce_template_list(None) == []


def test_coerce_template_list_filters_non_dicts() -> None:
    assert vp._coerce_template_list([{"name": "a"}, "garbage", None]) == [{"name": "a"}]


# --------------------------------------------------------------------------- #
# ensure_template — reuse vs. create                                           #
# --------------------------------------------------------------------------- #


def test_ensure_template_reuses_existing_match() -> None:
    client = MagicMock()
    client.search_templates.return_value = [
        {"name": "some-other", "hash_id": "zzz"},
        {"name": vp.TEMPLATE_NAME, "hash_id": "abc123"},
    ]

    hash_id = vp.ensure_template(client, _opts())

    assert hash_id == "abc123"
    client.search_templates.assert_called_once()
    client.create_template.assert_not_called()


def test_ensure_template_creates_when_missing_with_sdk_compatible_kwargs() -> None:
    client = MagicMock()
    client.search_templates.return_value = []
    client.create_template.return_value = {"hash_id": "new-hash"}

    hash_id = vp.ensure_template(client, _opts())

    assert hash_id == "new-hash"
    client.create_template.assert_called_once()
    kwargs = client.create_template.call_args.kwargs
    # SDK-compatible parameter names
    assert kwargs["name"] == vp.TEMPLATE_NAME
    assert kwargs["image"] == vp.IMAGE
    assert kwargs["image_tag"] == vp.IMAGE_TAG
    assert kwargs["env"] == vp.ENV_FLAGS
    assert kwargs["onstart_cmd"] == vp.ONSTART_CMD
    assert kwargs["ssh"] is True
    assert kwargs["direct"] is True
    # Full template now bundles JupyterLab on top of SSH so the SDK derives
    # runtype=jupyter_direct_ssh, and the XFCE desktop is bootstrapped from the
    # onstart command. Lock the jupyter contract here.
    assert kwargs["jupyter"] is True
    assert kwargs["jupyter_lab"] is True
    assert kwargs["jupyter_dir"] == "/workspace"
    # Non-SDK kwargs must not leak through
    assert "tag" not in kwargs
    assert "runtype" not in kwargs
    assert "ssh_direct" not in kwargs
    assert "jupyter_direct" not in kwargs


def test_ensure_template_unwraps_wrapped_template_response() -> None:
    client = MagicMock()
    client.search_templates.return_value = []
    client.create_template.return_value = {"template": {"hash_id": "wrapped"}}

    assert vp.ensure_template(client, _opts()) == "wrapped"


def test_ensure_template_handles_json_string_search_response() -> None:
    client = MagicMock()
    client.search_templates.return_value = (
        f'[{{"name": "{vp.TEMPLATE_NAME}", "hash_id": "abc"}}]'
    )
    assert vp.ensure_template(client, _opts()) == "abc"
    client.create_template.assert_not_called()


def test_ensure_template_exits_when_create_template_returns_no_hash() -> None:
    client = MagicMock()
    client.search_templates.return_value = []
    client.create_template.return_value = {"other": "field"}

    with pytest.raises(typer.Exit) as exc_info:
        vp.ensure_template(client, _opts())
    assert exc_info.value.exit_code == 1


# --------------------------------------------------------------------------- #
# find_cheapest_offer — offer parsing                                          #
# --------------------------------------------------------------------------- #


def test_find_cheapest_offer_parses_list_response() -> None:
    client = MagicMock()
    client.search_offers.return_value = [
        {"id": 1, "dph_total": 0.40, "gpu_name": "A"},
        {"id": 2, "dph_total": 0.50, "gpu_name": "B"},
    ]
    offer = vp.find_cheapest_offer(client, "query", "dph_total")
    assert offer["id"] == 1


def test_find_cheapest_offer_parses_json_string_response() -> None:
    client = MagicMock()
    client.search_offers.return_value = '[{"id": 7, "dph_total": 0.30}]'
    offer = vp.find_cheapest_offer(client, "query", "dph_total")
    assert offer["id"] == 7


def test_find_cheapest_offer_parses_wrapped_dict_response() -> None:
    client = MagicMock()
    client.search_offers.return_value = {"offers": [{"id": 9, "dph_total": 0.10}]}
    offer = vp.find_cheapest_offer(client, "query", "dph_total")
    assert offer["id"] == 9


def test_find_cheapest_offer_exits_on_empty_results() -> None:
    client = MagicMock()
    client.search_offers.return_value = []
    with pytest.raises(typer.Exit):
        vp.find_cheapest_offer(client, "query", "dph_total")


# --------------------------------------------------------------------------- #
# create_instance — drops the bogus ssh kwarg, parses launch result            #
# --------------------------------------------------------------------------- #


def test_create_instance_uses_jupyter_direct_ssh_runtype_and_omits_boolean_kwargs() -> None:
    client = MagicMock()
    client.create_instance.return_value = {"success": True, "new_contract": 4242}

    offer = {"id": 11, "dph_total": 0.40, "gpu_name": "A"}
    result = vp.create_instance(client, offer, "template-hash-xyz", _opts())

    assert result == {"success": True, "new_contract": 4242}
    kwargs = client.create_instance.call_args.kwargs
    assert kwargs["id"] == 11
    assert kwargs["template_hash"] == "template-hash-xyz"
    # Combined SSH + JupyterLab + direct connect → the SDK runtype string is
    # "jupyter_direct_ssh". Anything else either drops Jupyter ("ssh"), drops
    # SSH ("jupyter_direct"), or forces traffic through the Vast proxy.
    assert kwargs["runtype"] == "jupyter_direct_ssh"
    # The SDK's instances.create_instance() does not accept ssh=/jupyter= kwargs
    # — protocols are selected purely via `runtype`. Must not leak.
    assert "ssh" not in kwargs
    assert "jupyter" not in kwargs
    assert "direct" not in kwargs


def test_create_instance_parses_json_string_launch_response() -> None:
    client = MagicMock()
    client.create_instance.return_value = '{"success": true, "new_contract": 99}'
    offer = {"id": 1, "dph_total": 0.40}
    result = vp.create_instance(client, offer, "h", _opts())
    assert result["new_contract"] == 99


def test_create_instance_exits_when_success_false() -> None:
    client = MagicMock()
    client.create_instance.return_value = {"success": False, "msg": "no capacity"}
    offer = {"id": 1, "dph_total": 0.40}
    with pytest.raises(typer.Exit) as exc_info:
        vp.create_instance(client, offer, "h", _opts())
    assert exc_info.value.exit_code == 1





# --------------------------------------------------------------------------- #
# End-to-end provision() — dry-run guarantees no spend                         #
# --------------------------------------------------------------------------- #


def _stub_client(
    *,
    templates: list[dict[str, Any]] | None = None,
    offers: list[dict[str, Any]] | None = None,
    instance_response: dict[str, Any] | None = None,
) -> MagicMock:
    client = MagicMock()
    client.search_templates.return_value = templates if templates is not None else [
        {"name": vp.TEMPLATE_NAME, "hash_id": "tpl-hash"}
    ]
    client.search_offers.return_value = (
        offers
        if offers is not None
        else [
            {
                "id": 100,
                "dph_total": 0.40,
                "gpu_name": "RTX 4090",
                "num_gpus": 1,
                "gpu_ram": 24576,
                "disk_space": 500,
                "reliability2": 0.999,
                "geolocation": "US",
            }
        ]
    )
    client.create_instance.return_value = instance_response or {
        "success": True,
        "new_contract": 12345,
    }
    return client


def test_dry_run_does_not_call_create_instance_or_prepay(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _stub_client()
    monkeypatch.setattr(vp, "make_client", lambda _key: client)
    monkeypatch.setattr(vp, "load_api_key", lambda: "fake-key")

    runner = CliRunner()
    result = runner.invoke(vp.app, [])  # no --launch → dry-run

    assert result.exit_code == 0, result.output
    assert "[DRY-RUN]" in result.output
    client.create_instance.assert_not_called()


def test_template_only_exits_after_reconciling(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _stub_client()
    monkeypatch.setattr(vp, "make_client", lambda _key: client)
    monkeypatch.setattr(vp, "load_api_key", lambda: "fake-key")

    runner = CliRunner()
    result = runner.invoke(vp.app, ["--template-only"])

    assert result.exit_code == 0, result.output
    client.search_offers.assert_not_called()
    client.create_instance.assert_not_called()


def test_launch_path_creates_instance(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _stub_client()
    monkeypatch.setattr(vp, "make_client", lambda _key: client)
    monkeypatch.setattr(vp, "load_api_key", lambda: "fake-key")

    runner = CliRunner()
    result = runner.invoke(vp.app, ["--launch"])

    assert result.exit_code == 0, result.output
    client.create_instance.assert_called_once()


# --------------------------------------------------------------------------- #
# build_query — compute capability floor                                       #
# --------------------------------------------------------------------------- #


# --------------------------------------------------------------------------- #
# Repo URL alignment + clone failure-mode (drift regression)                  #
# --------------------------------------------------------------------------- #


def test_repo_url_uses_hyphen_to_match_github_remote() -> None:
    """``GH_REPO_URL`` must match the real GitHub slug (hyphen, not underscore).

    A typo (underscore form) used to 404 silently while ``|| true`` swallowed
    the failure, so the bootstrap continued without the repo and the user only
    noticed when their first SSH landed on a box missing /workspace/VUORSE-VORTEX.
    """
    assert vp.GH_REPO_URL == "https://github.com/calebmills99/VUORSE-VORTEX.git"


def test_onstart_aborts_when_clone_does_not_produce_repo() -> None:
    """The onstart command must fail loudly if the clone leaves no .git directory.

    The contract is: a successful template bootstrap implies /workspace/VUORSE-VORTEX/.git
    exists. Anything less must terminate the onstart with a non-zero exit so the
    failure surfaces in Vast.ai instance logs instead of a half-provisioned box.
    """
    onstart = vp.ONSTART_CMD
    # `set -e` propagates failures from intermediate commands.
    assert onstart.startswith("set -e; "), "onstart must enable errexit upfront"
    # No silent `|| true` swallowing the clone.
    assert "git clone" in onstart
    assert "git clone " + vp.GH_REPO_URL + " || true" not in onstart
    # Explicit post-clone verification with a non-zero exit on failure.
    assert "test -d /workspace/VUORSE-VORTEX/.git" in onstart
    assert "exit 1" in onstart


def test_build_query_filters_below_ampere() -> None:
    """The VUORSE floor is compute_cap >= 800 (Ampere). V100 = 700 must be excluded.

    Locks the architecture floor into the query contract so a future edit
    can't silently drop us back into Volta territory and pay for a GPU we
    can't run our torch on.
    """
    query, order = vp.build_query(_opts())
    assert order == "dph_total"
    assert f"compute_cap >= {vp.MIN_COMPUTE_CAP}" in query
    assert vp.MIN_COMPUTE_CAP >= 800, "VUORSE floor must stay at Ampere or higher"


def test_build_query_honors_min_compute_cap_override() -> None:
    """`--min-compute-cap` flows through to the search filter verbatim."""
    query, _ = vp.build_query(_opts(min_compute_cap=890))
    assert "compute_cap >= 890" in query


def test_provision_refuses_compute_cap_below_floor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Passing --min-compute-cap below 800 without --allow-downgrade exits non-zero."""
    monkeypatch.setattr(vp, "load_api_key", lambda: "fake-key")
    monkeypatch.setattr(vp, "make_client", lambda _key: _stub_client())

    runner = CliRunner()
    result = runner.invoke(vp.app, ["--min-compute-cap", "700"])

    assert result.exit_code == 2
    assert "min-compute-cap" in result.output
