"""Tests for refactor validation helpers."""

from __future__ import annotations

import json
from pathlib import Path

from scripts import check_translations as translation_checker
from scripts.coverage_diff import (
    load_file_percents,
    load_percent,
    main as coverage_main,
)
from scripts.refactor_tools import RefactorValidator


def _write_translation_fixture(
    tmp_path: Path,
    *,
    code_key: str,
    en_switch_keys: list[str],
    zh_switch_keys: list[str],
) -> Path:
    repo = tmp_path / "repo"
    script_path = repo / "scripts" / "check_translations.py"
    script_path.parent.mkdir(parents=True)
    script_path.write_text("# fixture script anchor\n", encoding="utf-8")

    src_dir = repo / "custom_components" / "lipro"
    src_dir.mkdir(parents=True)
    (src_dir / "switch.py").write_text(
        "\n".join(
            [
                "class DemoSwitch:",
                f'    _attr_translation_key = "{code_key}"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    translations_dir = src_dir / "translations"
    translations_dir.mkdir(parents=True)
    en_payload = {"entity": {"switch": {key: {"name": key} for key in en_switch_keys}}}
    zh_payload = {"entity": {"switch": {key: {"name": key} for key in zh_switch_keys}}}
    (translations_dir / "en.json").write_text(
        json.dumps(en_payload, ensure_ascii=False),
        encoding="utf-8",
    )
    (translations_dir / "zh-Hans.json").write_text(
        json.dumps(zh_payload, ensure_ascii=False),
        encoding="utf-8",
    )
    return script_path


def test_load_percent_reads_pytest_cov_json(tmp_path: Path) -> None:
    report = tmp_path / "coverage.json"
    report.write_text(json.dumps({"totals": {"percent_covered": 97.25}}))

    assert load_percent(report) == 97.25


def test_load_file_percents_reads_pytest_cov_json(tmp_path: Path) -> None:
    report = tmp_path / "coverage.json"
    report.write_text(
        json.dumps(
            {
                "files": {
                    "custom_components/lipro/demo.py": {
                        "summary": {"percent_covered": 91.5}
                    }
                }
            }
        )
    )

    assert load_file_percents(report) == {"custom_components/lipro/demo.py": 91.5}


def test_refactor_validator_checks_minimum_coverage(tmp_path: Path) -> None:
    report = tmp_path / "coverage.json"
    report.write_text(json.dumps({"totals": {"percent_covered": 96.0}}))
    validator = RefactorValidator(minimum_coverage=95.0)

    assert validator.validate_coverage(report) == (True, 96.0)


def test_refactor_validator_summarizes_paths(tmp_path: Path) -> None:
    existing = tmp_path / "exists.txt"
    existing.write_text("ok")
    missing = tmp_path / "missing.txt"
    validator = RefactorValidator()

    assert validator.summarize_paths(existing, missing) == {
        str(existing): True,
        str(missing): False,
    }


def test_coverage_main_fails_when_below_minimum(tmp_path: Path, monkeypatch) -> None:
    report = tmp_path / "coverage.json"
    report.write_text(json.dumps({"totals": {"percent_covered": 90.0}}))
    monkeypatch.setattr(
        "sys.argv",
        ["coverage_diff.py", str(report), "--minimum", "95"],
    )

    assert coverage_main() == 1


def test_coverage_main_fails_when_changed_surface_is_below_floor(
    tmp_path: Path, monkeypatch
) -> None:
    report = tmp_path / "coverage.json"
    report.write_text(
        json.dumps(
            {
                "totals": {"percent_covered": 96.0},
                "files": {
                    "custom_components/lipro/demo.py": {
                        "summary": {"percent_covered": 82.0}
                    }
                },
            }
        )
    )
    changed = tmp_path / "changed.txt"
    changed.write_text("custom_components/lipro/demo.py\nREADME.md\n", encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "coverage_diff.py",
            str(report),
            "--minimum",
            "95",
            "--changed-files",
            str(changed),
            "--changed-minimum",
            "95",
        ],
    )

    assert coverage_main() == 1


def test_coverage_main_skips_changed_surface_without_measured_files(
    tmp_path: Path, monkeypatch
) -> None:
    report = tmp_path / "coverage.json"
    report.write_text(
        json.dumps(
            {
                "totals": {"percent_covered": 96.0},
                "files": {
                    "custom_components/lipro/demo.py": {
                        "summary": {"percent_covered": 100.0}
                    }
                },
            }
        )
    )
    changed = tmp_path / "changed.txt"
    changed.write_text("README.md\nCONTRIBUTING.md\n", encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "coverage_diff.py",
            str(report),
            "--minimum",
            "95",
            "--changed-files",
            str(changed),
            "--changed-minimum",
            "95",
        ],
    )

    assert coverage_main() == 0


def test_check_translations_main_passes_for_consistent_translation_tree(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    script_path = _write_translation_fixture(
        tmp_path,
        code_key="demo_switch",
        en_switch_keys=["demo_switch"],
        zh_switch_keys=["demo_switch"],
    )
    monkeypatch.setattr(translation_checker, "__file__", str(script_path))

    assert translation_checker.main() == 0
    output = capsys.readouterr().out
    assert "demo_switch" in output
    assert "All translation checks passed" in output


def test_check_translations_main_fails_when_translation_key_is_missing(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    script_path = _write_translation_fixture(
        tmp_path,
        code_key="demo_switch",
        en_switch_keys=["demo_switch"],
        zh_switch_keys=[],
    )
    monkeypatch.setattr(translation_checker, "__file__", str(script_path))

    assert translation_checker.main() == 1
    output = capsys.readouterr().out
    assert "Missing keys: demo_switch" in output


def test_check_translations_main_fails_when_translation_files_drift(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    script_path = _write_translation_fixture(
        tmp_path,
        code_key="demo_switch",
        en_switch_keys=["demo_switch"],
        zh_switch_keys=["demo_switch", "extra_switch"],
    )
    monkeypatch.setattr(translation_checker, "__file__", str(script_path))

    assert translation_checker.main() == 1
    output = capsys.readouterr().out
    assert "keys differ from en.json" in output
