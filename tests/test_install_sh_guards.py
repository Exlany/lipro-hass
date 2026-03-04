"""Guardrails for the installer script (static checks)."""

from __future__ import annotations

from pathlib import Path


def test_install_sh_has_preflight_and_symlink_guards() -> None:
    install_sh = (Path(__file__).resolve().parents[1] / "install.sh").read_text(
        encoding="utf-8"
    )

    # Preflight scan (symlink/size/path) should exist.
    assert "python_preflight_scan_zip" in install_sh
    assert "LIPRO_INSTALL_MAX_FILES" in install_sh
    assert "LIPRO_INSTALL_MAX_UNCOMPRESSED_BYTES" in install_sh
    assert "Unsafe path traversal in archive" in install_sh

    # Staged component should be rejected if it contains symlinks.
    assert "Symlinks detected in staged component" in install_sh
