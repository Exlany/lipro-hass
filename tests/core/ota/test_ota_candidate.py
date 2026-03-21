"""Tests for core.ota.candidate helper branches."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.lipro.core.ota.candidate import (
    OtaManifestTruth,
    _InstallCommand,
    _OtaCandidate,
    evaluate_install,
    has_pending_confirmation,
    resolve_certification,
    resolve_inline_certification,
    resolve_latest_version,
    resolve_update_available,
)


def _is_version_newer(latest: str, installed: str) -> bool:
    """Simple semantic compare helper for numeric dot versions."""
    return tuple(int(part) for part in latest.split(".")) > tuple(
        int(part) for part in installed.split(".")
    )


def test_resolve_latest_version_falls_back_to_installed_when_common_missing() -> None:
    assert resolve_latest_version({}, "1.0.0") == "1.0.0"


def test_resolve_latest_version_keeps_installed_when_common_equals_installed() -> None:
    assert resolve_latest_version({"version": "1.0.0"}, "1.0.0") == "1.0.0"


def test_resolve_update_available_returns_false_when_latest_none() -> None:
    comparator = MagicMock(return_value=True)

    result = resolve_update_available(
        {},
        installed="1.0.0",
        latest=None,
        is_version_newer=comparator,
    )

    assert result is False
    comparator.assert_not_called()


def test_resolve_update_available_returns_true_when_installed_none() -> None:
    assert (
        resolve_update_available(
            {},
            installed=None,
            latest="1.1.0",
            is_version_newer=_is_version_newer,
        )
        is True
    )


def test_resolve_update_available_returns_false_when_versions_equal() -> None:
    assert (
        resolve_update_available(
            {},
            installed="1.1.0",
            latest="1.1.0",
            is_version_newer=_is_version_newer,
        )
        is False
    )


def test_resolve_update_available_returns_false_on_compare_error() -> None:
    def _broken_compare(_latest: str, _installed: str) -> bool:
        msg = "compare failed"
        raise ValueError(msg)

    assert (
        resolve_update_available(
            {},
            installed="1.0.0",
            latest="1.1.0",
            is_version_newer=_broken_compare,
        )
        is False
    )


def test_resolve_certification_returns_false_when_latest_missing() -> None:
    assert (
        resolve_certification(
            {},
            installed="1.0.0",
            latest=None,
            device_iot_name="21P3",
            manifest_truth=OtaManifestTruth(
                verified_versions=frozenset({"1.1.0"}),
                versions_by_type={"21p3": frozenset({"1.1.0"})},
            ),
            is_version_newer=_is_version_newer,
        )
        is False
    )


def test_resolve_inline_certification_uses_nested_certification_flag() -> None:
    row = {"certification": {"certified": True}}
    assert (
        resolve_inline_certification(
            row,
            installed="1.0.0",
            latest="1.1.0",
            is_version_newer=_is_version_newer,
        )
        is True
    )


def test_resolve_inline_certification_uses_nested_certified_versions() -> None:
    row = {"certification": {"certifiedVersions": ["1.1.0"]}}
    assert (
        resolve_inline_certification(
            row,
            installed="1.0.0",
            latest="1.1.0",
            is_version_newer=_is_version_newer,
        )
        is True
    )


def test_resolve_inline_certification_returns_none_when_nested_versions_no_match() -> (
    None
):
    row = {"certification": {"certifiedVersions": ["1.1.0"]}}
    assert (
        resolve_inline_certification(
            row,
            installed="2.0.0",
            latest="1.2.0",
            is_version_newer=_is_version_newer,
        )
        is None
    )



def test_evaluate_install_requires_confirmation_before_unverified_install() -> None:
    """Unverified install policy should open a confirmation window before execution."""
    evaluation = evaluate_install(
        _OtaCandidate(
            installed_version="1.0.0",
            latest_version="1.1.0",
            update_available=True,
            certified=False,
            release_summary=None,
            release_url=None,
            install_command=_InstallCommand(
                command="CHANGE_STATE",
                properties=[{"key": "version", "value": "1.1.0"}],
            ),
        ),
        requested_version=None,
        confirm_until=0.0,
        now_monotonic=100.0,
        confirmation_window_seconds=120,
    )

    assert evaluation.error_key == "firmware_unverified_confirm_required"
    assert evaluation.confirm_until == 220.0
    assert has_pending_confirmation(evaluation.confirm_until, now_monotonic=101.0) is True


def test_resolve_local_manifest_certification_ignores_remote_advisory_truth() -> None:
    assert resolve_certification(
        {"latestVersion": "8.0.0"},
        installed="7.0.0",
        latest="8.0.0",
        device_iot_name="21P3",
        manifest_truth=OtaManifestTruth(
            verified_versions=frozenset(),
            versions_by_type={},
        ),
        is_version_newer=lambda candidate, current: candidate > current,
    ) is False
