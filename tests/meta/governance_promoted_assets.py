"""Shared helpers for promoted phase-asset manifest guards."""

from __future__ import annotations

from functools import lru_cache

from .conftest import _ROOT, _load_frontmatter

_PROMOTED_PHASE_ASSETS = _ROOT / ".planning" / "reviews" / "PROMOTED_PHASE_ASSETS.md"


@lru_cache(maxsize=1)
def _load_promoted_phase_assets() -> dict[str, frozenset[str]]:
    manifest = _load_frontmatter(_PROMOTED_PHASE_ASSETS)
    phases = manifest["phases"]
    assert isinstance(phases, dict)

    promoted_assets: dict[str, frozenset[str]] = {}
    for phase_dir_name, filenames in phases.items():
        assert isinstance(phase_dir_name, str)
        assert isinstance(filenames, list)
        assert filenames
        promoted_assets[phase_dir_name] = frozenset(filenames)

    return promoted_assets


def _assert_promoted_phase_assets(phase_dir_name: str, *filenames: str) -> None:
    promoted_assets = _load_promoted_phase_assets()
    assert phase_dir_name in promoted_assets

    phase_root = _ROOT / ".planning" / "phases" / phase_dir_name
    for filename in filenames:
        assert filename in promoted_assets[phase_dir_name]
        assert (phase_root / filename).exists()


def _assert_exact_promoted_phase_assets(phase_dir_name: str, *filenames: str) -> None:
    promoted_assets = _load_promoted_phase_assets()
    assert phase_dir_name in promoted_assets
    assert promoted_assets[phase_dir_name] == frozenset(filenames)

    phase_root = _ROOT / ".planning" / "phases" / phase_dir_name
    for filename in filenames:
        assert (phase_root / filename).exists()


def _assert_phase_assets_not_promoted(phase_dir_name: str, *filenames: str) -> None:
    promoted_assets = _load_promoted_phase_assets().get(phase_dir_name, frozenset())
    for filename in filenames:
        assert filename not in promoted_assets


def _assert_promoted_closeout_package(roadmap_text: str, *filenames: str) -> None:
    package_listing = ", ".join(f"`{filename}`" for filename in filenames)
    assert f"**Promoted closeout package**: {package_listing}" in roadmap_text


__all__ = [
    '_PROMOTED_PHASE_ASSETS',
    '_ROOT',
    '_assert_exact_promoted_phase_assets',
    '_assert_phase_assets_not_promoted',
    '_assert_promoted_closeout_package',
    '_assert_promoted_phase_assets',
    '_load_promoted_phase_assets',
]
