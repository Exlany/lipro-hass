"""Guardrails for the installer script (static checks)."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root


def test_install_sh_has_preflight_and_symlink_guards() -> None:
    root = repo_root(Path(__file__))
    install_sh = (root / "install.sh").read_text(encoding="utf-8")

    # Preflight scan (symlink/size/path) should exist.
    assert "python_preflight_scan_zip" in install_sh
    assert "LIPRO_INSTALL_MAX_FILES" in install_sh
    assert "LIPRO_INSTALL_MAX_UNCOMPRESSED_BYTES" in install_sh
    assert "Unsafe path traversal in archive" in install_sh
    assert "Python not found; cannot safely validate archive" in install_sh

    # Staged component should be rejected if it contains symlinks.
    assert "Symlinks detected in staged component" in install_sh

    # Mirror installs should require an explicit dangerous override.
    assert "LIPRO_ALLOW_MIRROR" in install_sh
    assert "Refusing to install from non-default HUB_DOMAIN" in install_sh

    # latest resolution should not silently fall back to main.
    assert "Could not resolve latest release tag" in install_sh
    assert "ARCHIVE_TAG=main explicitly" in install_sh

    # Version-like tags should not silently fall back to branch archives.
    assert "LIPRO_ALLOW_BRANCH_FALLBACK" in install_sh
    assert "Tag-only install mode" in install_sh

    # Optional checksum verification (Release assets).
    assert "LIPRO_REQUIRE_CHECKSUM" in install_sh
    assert "SHA256SUMS" in install_sh
    assert "Checksum verified" in install_sh
