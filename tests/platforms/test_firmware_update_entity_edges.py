"""Edge-branch tests for firmware update entity runtime paths."""

from __future__ import annotations

from unittest.mock import patch

from custom_components.lipro.entities.firmware_update import LiproFirmwareUpdateEntity


def test_handle_coordinator_update_refreshes_installed_version_and_schedules(
    mock_coordinator, make_device
) -> None:
    device = make_device(
        "light",
        serial="03ab5ccd7c303030",
        properties={"version": "1.0.0"},
    )
    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)

    with (
        patch(
            "custom_components.lipro.entities.firmware_update.LiproEntity._handle_coordinator_update"
        ) as super_update,
        patch.object(entity, "_schedule_ota_refresh") as schedule_refresh,
    ):
        device.properties["version"] = "1.2.3"
        entity._handle_coordinator_update()

    assert entity.installed_version == "1.2.3"
    schedule_refresh.assert_called_once_with(force=False)
    super_update.assert_called_once()


def test_apply_ota_candidate_clears_release_attributes_when_candidate_missing(
    mock_coordinator, make_device
) -> None:
    entity = LiproFirmwareUpdateEntity(mock_coordinator, make_device("light"))
    entity._ota_candidate = None
    entity._attr_release_summary = "old summary"
    entity._attr_release_url = "https://example.com/release"

    entity._apply_ota_candidate()

    assert entity.release_summary is None
    assert entity.release_url is None
