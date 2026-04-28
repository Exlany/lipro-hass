"""Load authority-indexed replay manifests for protocol replay scenarios."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from tests.harness.protocol.replay_models import (
    ASSERTION_FAMILY_VALUES,
    REPLAY_CHANNEL_VALUES,
    REPLAY_OPERATION_VALUES,
    AssertionFamily,
    DeterministicReplayControls,
    LoadedReplayFixture,
    ReplayChannel,
    ReplayManifest,
    ReplayOperation,
)
from tests.helpers.repo_root import repo_root

_REPO_ROOT = repo_root(Path(__file__))
_REPLAY_ROOT = _REPO_ROOT / "tests" / "fixtures" / "protocol_replay"
_ALLOWED_AUTHORITY_PREFIXES = (
    "tests/fixtures/api_contracts/",
    "tests/fixtures/protocol_boundary/",
)


def _require_mapping(payload: object, *, source: Path) -> dict[str, Any]:
    if not isinstance(payload, dict):
        msg = f"Replay file must contain one object mapping: {source}"
        raise TypeError(msg)
    return cast(dict[str, Any], payload)


def _require_channel(value: object, *, source: Path) -> ReplayChannel:
    if not isinstance(value, str):
        msg = f"Replay manifest channel must be a string: {source}"
        raise TypeError(msg)
    try:
        return REPLAY_CHANNEL_VALUES[value]
    except KeyError as err:
        msg = f"Replay manifest channel must be one of {tuple(REPLAY_CHANNEL_VALUES)}: {source}"
        raise ValueError(msg) from err


def _require_operation(value: object, *, source: Path) -> ReplayOperation:
    if not isinstance(value, str):
        msg = f"Replay manifest operation must be a string: {source}"
        raise TypeError(msg)
    try:
        return REPLAY_OPERATION_VALUES[value]
    except KeyError as err:
        msg = (
            "Replay manifest operation must be one of "
            f"{tuple(REPLAY_OPERATION_VALUES)}: {source}"
        )
        raise ValueError(msg) from err


def _require_assertion_families(
    value: object, *, source: Path
) -> tuple[AssertionFamily, ...]:
    if not isinstance(value, list) or not value:
        msg = f"Replay manifest assertion_families must be a non-empty list: {source}"
        raise ValueError(msg)

    families: list[AssertionFamily] = []
    for item in value:
        if not isinstance(item, str):
            msg = (
                f"Replay manifest assertion_families entries must be strings: {source}"
            )
            raise TypeError(msg)
        try:
            families.append(ASSERTION_FAMILY_VALUES[item])
        except KeyError as err:
            msg = (
                "Replay manifest assertion_families entries must be one of "
                f"{tuple(ASSERTION_FAMILY_VALUES)}: {source}"
            )
            raise ValueError(msg) from err

    return tuple(families)


def replay_fixture_root() -> Path:
    """Return the formal replay manifest fixture root."""
    return _REPLAY_ROOT


def load_replay_manifest(path: Path) -> ReplayManifest:
    """Load one replay manifest JSON file into a typed manifest."""
    data = _require_mapping(json.loads(path.read_text(encoding="utf-8")), source=path)
    authority_relpath = data["authority_path"]
    if not isinstance(authority_relpath, str) or not authority_relpath.startswith(
        _ALLOWED_AUTHORITY_PREFIXES
    ):
        msg = f"Replay manifest authority_path must point to registered fixture truth: {path}"
        raise ValueError(msg)
    return ReplayManifest(
        scenario_id=str(data["scenario_id"]),
        channel=_require_channel(data["channel"], source=path),
        family=str(data["family"]),
        version=str(data["version"]),
        operation=_require_operation(data["operation"], source=path),
        authority_path=_REPO_ROOT / authority_relpath,
        assertion_families=_require_assertion_families(
            data["assertion_families"], source=path
        ),
        controls=DeterministicReplayControls(
            seed=int(data["seed"]),
            clock_baseline=str(data["clock_baseline"]),
        ),
        manifest_path=path,
        notes=str(data["notes"]) if isinstance(data.get("notes"), str) else None,
    )


def iter_replay_manifests(
    *, channel: ReplayChannel | None = None
) -> list[ReplayManifest]:
    """Return replay manifests in deterministic path order."""
    manifests: list[ReplayManifest] = []
    for path in sorted(_REPLAY_ROOT.rglob("*.json")):
        manifest = load_replay_manifest(path)
        if channel is None or manifest.channel == channel:
            manifests.append(manifest)
    return manifests


def load_replay_fixture(manifest: ReplayManifest) -> LoadedReplayFixture:
    """Load the authority payload referenced by one replay manifest."""
    authority_payload = json.loads(manifest.authority_path.read_text(encoding="utf-8"))
    authority_metadata = (
        cast(dict[str, Any], authority_payload)
        if isinstance(authority_payload, dict)
        else {}
    )
    return LoadedReplayFixture(
        manifest=manifest,
        authority_payload=authority_payload,
        authority_metadata=authority_metadata,
    )
