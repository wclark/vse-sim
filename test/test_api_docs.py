from __future__ import annotations

import runpy
import shutil
import sys
from pathlib import Path

import pytest

import tools.build_api_docs as api_docs


def test_build_docs_recreates_output_and_runs_pdoc(monkeypatch, tmp_path):
    calls = []

    def fake_run(command, cwd, check):
        calls.append((command, cwd, check))

    monkeypatch.setattr(api_docs.subprocess, "run", fake_run)

    existing_output = tmp_path / "existing"
    existing_output.mkdir()
    (existing_output / "stale.html").write_text("old", encoding="utf-8")

    api_docs.build_docs(existing_output)

    assert existing_output.exists()
    assert not (existing_output / "stale.html").exists()
    assert calls[0][0][0] == sys.executable
    assert calls[0][0][calls[0][0].index("--output-directory") + 1] == str(existing_output)
    assert calls[0][1] == api_docs.ROOT
    assert calls[0][2] is True

    fresh_output = tmp_path / "fresh"
    api_docs.build_docs(fresh_output)

    assert fresh_output.exists()
    assert calls[1][0][calls[1][0].index("--output-directory") + 1] == str(fresh_output)


def test_relative_files_and_changed_files(tmp_path):
    expected = tmp_path / "expected"
    actual = tmp_path / "actual"
    expected.mkdir()
    actual.mkdir()

    (expected / "same.html").write_text("same", encoding="utf-8")
    (actual / "same.html").write_text("same", encoding="utf-8")
    (expected / "changed.html").write_text("old", encoding="utf-8")
    (actual / "changed.html").write_text("new", encoding="utf-8")
    (expected / "committed-only.html").write_text("committed", encoding="utf-8")
    (actual / "generated-only.html").write_text("generated", encoding="utf-8")

    assert api_docs.relative_files(tmp_path / "missing") == set()
    assert api_docs.relative_files(expected) == {
        Path("changed.html"),
        Path("committed-only.html"),
        Path("same.html"),
    }
    assert api_docs.changed_files(expected, actual) == [
        "missing from generated docs: committed-only.html",
        "missing from committed docs: generated-only.html",
        "changed: changed.html",
    ]


def test_check_docs_reports_current_docs(monkeypatch, tmp_path, capsys):
    committed = tmp_path / "committed"
    committed.mkdir()
    (committed / "vse_sim.html").write_text("current", encoding="utf-8")

    def fake_build_docs(output):
        output.mkdir()
        (output / "vse_sim.html").write_text("current", encoding="utf-8")

    monkeypatch.setattr(api_docs, "API_DOCS", committed)
    monkeypatch.setattr(api_docs, "build_docs", fake_build_docs)

    assert api_docs.check_docs() == 0
    assert "Generated API docs are current." in capsys.readouterr().out


def test_check_docs_reports_stale_docs(monkeypatch, tmp_path, capsys):
    committed = tmp_path / "committed"
    committed.mkdir()
    (committed / "vse_sim.html").write_text("old", encoding="utf-8")

    def fake_build_docs(output):
        output.mkdir()
        (output / "vse_sim.html").write_text("new", encoding="utf-8")

    monkeypatch.setattr(api_docs, "API_DOCS", committed)
    monkeypatch.setattr(api_docs, "build_docs", fake_build_docs)

    assert api_docs.check_docs() == 1
    output = capsys.readouterr().out
    assert "Generated API docs are not current." in output
    assert "changed: vse_sim.html" in output


def test_main_checks_or_builds_docs(monkeypatch, capsys):
    monkeypatch.setattr(api_docs.sys, "argv", ["build_api_docs.py", "--check"])
    monkeypatch.setattr(api_docs, "check_docs", lambda: 3)

    assert api_docs.main() == 3

    generated = api_docs.ROOT / "docs" / "api-test-generated"
    if generated.exists():
        shutil.rmtree(generated)

    def fake_build_docs(output):
        output.mkdir()

    monkeypatch.setattr(api_docs.sys, "argv", ["build_api_docs.py"])
    monkeypatch.setattr(api_docs, "API_DOCS", generated)
    monkeypatch.setattr(api_docs, "build_docs", fake_build_docs)

    try:
        assert api_docs.main() == 0
        assert "Generated API docs in" in capsys.readouterr().out
    finally:
        if generated.exists():
            shutil.rmtree(generated)


def test_script_help_entrypoint(monkeypatch):
    monkeypatch.setattr(sys, "argv", [str(Path(api_docs.__file__)), "--help"])

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(api_docs.__file__, run_name="__main__")

    assert excinfo.value.code == 0
