"""Offline installer checks use temporary fixtures, never a live HA instance."""

import hashlib
import os
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest


@pytest.mark.parametrize("valid_checksum", [True, False])
def test_relative_local_archive_is_verified_before_activation(tmp_path, valid_checksum):
    config = tmp_path / "config"
    config.mkdir()
    (config / "home-assistant.log").touch()
    installed = config / "custom_components" / "lipro"
    installed.mkdir(parents=True)
    (installed / "manifest.json").write_text('{"version":"old"}')
    archive = tmp_path / "release.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr(
            "release/custom_components/lipro/manifest.json", '{"version":"new"}'
        )
    digest = (
        hashlib.sha256(archive.read_bytes()).hexdigest() if valid_checksum else "0" * 64
    )
    (tmp_path / "SHA256SUMS").write_text(f"{digest}  release.zip\n")
    script = Path(__file__).resolve().parents[2] / "install.sh"
    env = os.environ.copy()
    env["PATH"] = f"{Path(sys.executable).parent}:{env['PATH']}"
    for variable in ("ARCHIVE_TAG", "ARCHIVE_FILE", "CHECKSUM_FILE", "HUB_DOMAIN"):
        env.pop(variable, None)
    result = subprocess.run(  # noqa: S603 - fixed repository script and generated local fixtures
        [
            "/bin/bash",
            str(script),
            "--archive-file",
            "./release.zip",
            "--checksum-file",
            "./SHA256SUMS",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if valid_checksum:
        assert result.returncode == 0, result.stdout + result.stderr
        assert (installed / "manifest.json").read_text() == '{"version":"new"}'
    else:
        assert result.returncode != 0
        assert "Checksum mismatch" in result.stderr
        assert (installed / "manifest.json").read_text() == '{"version":"old"}'
