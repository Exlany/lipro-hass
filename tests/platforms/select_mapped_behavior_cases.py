"""Mapped-property behavior cases for the Lipro select platform."""

from __future__ import annotations

from unittest.mock import patch

import pytest


def _build_heater_light_mode_select(mock_coordinator, make_device, raw_value: object):
    from custom_components.lipro.select import LiproHeaterLightModeSelect

    device = make_device("heater", properties={"lightMode": raw_value})
    mock_coordinator.devices = {device.serial: device}
    mock_coordinator.get_device = lambda serial: mock_coordinator.devices.get(serial)
    return LiproHeaterLightModeSelect(mock_coordinator, device), device


class TestSelectMappedBehavior:
    """Focused behavior cases for mapped-property selects."""

    @pytest.mark.asyncio
    async def test_mapped_select_invalid_option_returns_early(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        """Mapped select should ignore unsupported options instead of forcing defaults."""
        select, _device = _build_heater_light_mode_select(
            mock_coordinator,
            make_device,
            "1",
        )

        with patch.object(select, "async_write_ha_state"):
            await select.async_select_option("invalid")

        mock_coordinator.async_send_command.assert_not_called()

    def test_mapped_select_current_option_unknown_value_is_observable(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        """Mapped select current option should surface unknown raw values."""
        select, _device = _build_heater_light_mode_select(
            mock_coordinator,
            make_device,
            "99",
        )

        assert select.current_option is None
        assert select.extra_state_attributes == {
            "property_key": "lightMode",
            "raw_value": "99",
        }

    def test_mapped_select_unknown_value_recovery_clears_debug_attributes(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        """Known values should clear the temporary unknown-value observability payload."""
        select, device = _build_heater_light_mode_select(
            mock_coordinator,
            make_device,
            "99",
        )

        assert select.current_option is None
        assert select.extra_state_attributes == {
            "property_key": "lightMode",
            "raw_value": "99",
        }

        device.properties["lightMode"] = "1"

        assert select.current_option == "main"
        assert select.extra_state_attributes == {}

    def test_mapped_select_blank_string_value_stays_observable(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        """Blank string payloads should stay visible instead of collapsing into defaults."""
        select, _device = _build_heater_light_mode_select(
            mock_coordinator,
            make_device,
            "   ",
        )

        assert select.current_option is None
        assert select.extra_state_attributes == {
            "property_key": "lightMode",
            "raw_value": "   ",
        }
