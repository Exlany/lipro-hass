"""Phase 62 naming and discoverability guards."""

from __future__ import annotations

from pathlib import Path

from scripts.check_file_matrix import repo_root

_ROOT = repo_root(Path(__file__))
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
_VERIFICATION_MATRIX = _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"


def test_phase62_device_extras_support_path_is_family_aligned() -> None:
    old_path = _ROOT / "custom_components" / "lipro" / "core" / "device" / "extra_support.py"
    new_path = _ROOT / "custom_components" / "lipro" / "core" / "device" / "extras_support.py"

    assert not old_path.exists()
    assert new_path.exists()
    text = new_path.read_text(encoding="utf-8")
    assert "DeviceExtras" in text
    assert "Support helpers" in text


def test_phase62_active_truth_uses_extras_support_not_extra_support() -> None:
    file_matrix_text = _FILE_MATRIX.read_text(encoding="utf-8")
    verification_text = _VERIFICATION_MATRIX.read_text(encoding="utf-8")

    assert "custom_components/lipro/core/device/extras_support.py" in file_matrix_text
    assert "custom_components/lipro/core/device/extras_support.py" in verification_text
    assert "custom_components/lipro/core/device/extra_support.py" not in file_matrix_text
    assert "custom_components/lipro/core/device/extra_support.py" not in verification_text


def test_phase62_public_fast_path_keeps_maintainer_boundary_explicit() -> None:
    readme_text = (_ROOT / "README.md").read_text(encoding="utf-8")
    readme_zh_text = (_ROOT / "README_zh.md").read_text(encoding="utf-8")
    contributing_text = (_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    support_text = (_ROOT / "SUPPORT.md").read_text(encoding="utf-8")
    docs_text = (_ROOT / "docs" / "README.md").read_text(encoding="utf-8")

    for text in (readme_text, readme_zh_text, contributing_text, support_text, docs_text):
        assert "docs/README.md" in text
        assert "docs/MAINTAINER_RELEASE_RUNBOOK.md" in text

    assert "maintainer-only" in readme_text
    assert "maintainer-only" in contributing_text
    assert "unsupported" in contributing_text.lower()
    assert "unsupported" in docs_text.lower()
