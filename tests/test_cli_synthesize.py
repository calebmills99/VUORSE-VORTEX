"""CPU-safe tests for synthesis CLI workflow commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from vuorse_vortex import cli
from vuorse_vortex.jsonl import validate_jsonl


def _count_records(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def test_synthesize_command_supports_quickstart_flags(
    tmp_path: Path, patch_walled_pool: Path
) -> None:
    output = tmp_path / "batch.jsonl"
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        [
            "synthesize",
            "--seed",
            "42",
            "--n",
            "8",
            "--chaos",
            "0.2",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0, result.output
    assert output.is_file()
    assert _count_records(output) == 8
    assert validate_jsonl(output) == []


def test_synthesize_interactive_can_edit_then_accept(
    tmp_path: Path, patch_walled_pool: Path
) -> None:
    output = tmp_path / "reviewed.jsonl"
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        [
            "synthesize-interactive",
            "--seed",
            "42",
            "--output",
            str(output),
        ],
        input=(
            "e\n"
            "Edited Thesis\n"
            "edited, human-reviewed\n"
            "Edited premise.\n"
            "Edited synthesis.\n"
            "a\n"
            "q\n"
        ),
    )

    assert result.exit_code == 0, result.output
    assert _count_records(output) == 1
    assert validate_jsonl(output) == []
    text = output.read_text(encoding="utf-8")
    assert "Edited Thesis" in text
    assert "Edited premise." in text
    assert "Edited synthesis." in text


@pytest.mark.parametrize("flag", ["--n", "--output"])
def test_synthesize_help_documents_quickstart_flags(flag: str) -> None:
    runner = CliRunner()
    result = runner.invoke(cli.app, ["synthesize", "--help"])

    assert result.exit_code == 0
    assert flag in result.output
