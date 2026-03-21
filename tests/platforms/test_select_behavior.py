"""Behavior tests for Lipro select platform entities."""

from __future__ import annotations

from collections.abc import Iterable
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, patch

import pytest


class TestSelectEntityBehavior:
    """Behavior tests for select entities."""

    @pytest.mark.asyncio
    async def test_async_setup_entry_creates_expected_entities(
        self, hass, make_device
    ) -> None:
        """Setup should create heater selects and gear select for eligible lights."""
        from custom_components.lipro.select import (
            LiproHeaterLightModeSelect,
            LiproHeaterWindDirectionSelect,
            LiproLightGearSelect,
            async_setup_entry,
        )

        coordinator = SimpleNamespace(
            devices={
                "heater": make_device("heater"),
                "gear_light": make_device(
                    "light",
                    properties={"gearList": '[{"temperature":50,"brightness":100}]'},
                ),
                "plain_light": make_device("light"),
            }
        )
        entry = SimpleNamespace(runtime_data=coordinator)
        from custom_components.lipro import LiproConfigEntry
        from homeassistant.helpers.entity import Entity
        from homeassistant.helpers.entity_platform import AddEntitiesCallback

        captured: list[Entity] = []

        def _add_entities(
            entities: Iterable[Entity],
            update_before_add: bool = False,
        ) -> None:
            captured.extend(entities)

        await async_setup_entry(
            hass,
            cast(LiproConfigEntry, entry),
            cast(AddEntitiesCallback, _add_entities),
        )

        assert any(isinstance(e, LiproHeaterWindDirectionSelect) for e in captured)
        assert any(isinstance(e, LiproHeaterLightModeSelect) for e in captured)
        assert any(isinstance(e, LiproLightGearSelect) for e in captured)
        assert len(captured) == 3

    @pytest.mark.asyncio
    async def test_mapped_select_invalid_option_returns_early(
        self, mock_coordinator, make_device
    ) -> None:
        """Mapped select should ignore unsupported options instead of forcing defaults."""
        from custom_components.lipro.select import LiproHeaterLightModeSelect

        device = make_device("heater", properties={"lightMode": "1"})
        mock_coordinator.devices = {device.serial: device}
        mock_coordinator.get_device = lambda serial: mock_coordinator.devices.get(
            serial
        )
        select = LiproHeaterLightModeSelect(mock_coordinator, device)

        with patch.object(select, "async_write_ha_state"):
            await select.async_select_option("invalid")

        mock_coordinator.async_send_command.assert_not_called()

    def test_mapped_select_current_option_unknown_value_is_observable(
        self, mock_coordinator, make_device
    ) -> None:
        """Mapped select current option should surface unknown raw values."""
        from custom_components.lipro.select import LiproHeaterLightModeSelect

        device = make_device("heater", properties={"lightMode": "99"})
        mock_coordinator.devices = {device.serial: device}
        mock_coordinator.get_device = lambda serial: mock_coordinator.devices.get(
            serial
        )
        select = LiproHeaterLightModeSelect(mock_coordinator, device)

        assert select.current_option is None
        assert select.extra_state_attributes == {
            "property_key": "lightMode",
            "raw_value": "99",
        }

    @pytest.mark.asyncio
    async def test_light_gear_select_options_are_trimmed(
        self, mock_coordinator, make_device
    ) -> None:
        """Options should be trimmed to actual gear count when less than 3."""
        from custom_components.lipro.select import LiproLightGearSelect

        device = make_device(
            "light",
            properties={
                "gearList": '[{"temperature":50,"brightness":100},{"temperature":40,"brightness":80}]'
            },
        )
        mock_coordinator.devices = {device.serial: device}
        mock_coordinator.get_device = lambda serial: mock_coordinator.devices.get(
            serial
        )
        select = LiproLightGearSelect(mock_coordinator, device)
        assert select.options == ["gear_1", "gear_2"]

    @pytest.mark.asyncio
    async def test_light_gear_select_options_empty_without_presets(
        self, mock_coordinator, make_device
    ) -> None:
        """Options should be empty when device has no gear presets."""
        from custom_components.lipro.select import LiproLightGearSelect

        device = make_device("light", properties={})
        mock_coordinator.devices = {device.serial: device}
        mock_coordinator.get_device = lambda serial: mock_coordinator.devices.get(
            serial
        )
        select = LiproLightGearSelect(mock_coordinator, device)
        assert select.options == []

    @pytest.mark.asyncio
    async def test_light_gear_select_options_cap_to_max_presets(
        self, mock_coordinator, make_device
    ) -> None:
        """Options should cap to supported max when device exposes more presets."""
        from custom_components.lipro.select import GEAR_OPTIONS, LiproLightGearSelect

        device = make_device(
            "light",
            properties={
                "gearList": '[{"temperature":50,"brightness":100},{"temperature":40,"brightness":80},{"temperature":30,"brightness":60},{"temperature":20,"brightness":40}]'
            },
        )
        mock_coordinator.devices = {device.serial: device}
        mock_coordinator.get_device = lambda serial: mock_coordinator.devices.get(
            serial
        )
        select = LiproLightGearSelect(mock_coordinator, device)

        assert select.options == GEAR_OPTIONS

    @pytest.mark.asyncio
    async def test_light_gear_select_current_option_none_without_presets(
        self, mock_coordinator, make_device
    ) -> None:
        """Current option should be None when no gear presets exist."""
        from custom_components.lipro.select import LiproLightGearSelect

        device = make_device("light", properties={})
        mock_coordinator.devices = {device.serial: device}
        mock_coordinator.get_device = lambda serial: mock_coordinator.devices.get(
            serial
        )
        select = LiproLightGearSelect(mock_coordinator, device)

        assert select.current_option is None

    def test_light_gear_select_coerce_none_value(self):
        """None gear values should coerce to None instead of raising."""
        from custom_components.lipro.select import LiproLightGearSelect

        assert LiproLightGearSelect._coerce_gear_int(None) is None

    @pytest.mark.asyncio
    async def test_light_gear_select_extra_state_attributes_include_presets_and_range(
        self, mock_coordinator, make_device
    ) -> None:
        """Extra attributes should include preset summaries and color-temp range."""
        from custom_components.lipro.select import LiproLightGearSelect

        device = make_device(
            "light",
            properties={
                "gearList": '[{"temperature":50,"brightness":100},{"temperature":40,"brightness":80}]'
            },
        )
        mock_coordinator.devices = {device.serial: device}
        mock_coordinator.get_device = lambda serial: mock_coordinator.devices.get(
            serial
        )
        select = LiproLightGearSelect(mock_coordinator, device)

        attrs = select.extra_state_attributes

        assert "preset_warm" in attrs
        assert "preset_neutral" in attrs
        preset_warm = attrs["preset_warm"]
        assert isinstance(preset_warm, str)
        assert preset_warm.startswith("100% / ")
        assert "color_temp_range" in attrs

    @pytest.mark.asyncio
    async def test_light_gear_select_extra_state_attributes_skip_invalid_rows(
        self, mock_coordinator, make_device
    ) -> None:
        """Invalid gear rows should be ignored when building extra attributes."""
        from custom_components.lipro.select import LiproLightGearSelect

        device = make_device(
            "light",
            properties={
                "gearList": '[{"temperature":null,"brightness":100},{"temperature":40,"brightness":80}]'
            },
        )
        mock_coordinator.devices = {device.serial: device}
        mock_coordinator.get_device = lambda serial: mock_coordinator.devices.get(
            serial
        )
        select = LiproLightGearSelect(mock_coordinator, device)

        attrs = select.extra_state_attributes

        assert "preset_warm" not in attrs
        assert "preset_neutral" in attrs

    @pytest.mark.asyncio
    async def test_light_gear_select_no_presets_returns_early(
        self, mock_coordinator, make_device
    ) -> None:
        """Selecting gear with no presets should return without sending commands."""
        from custom_components.lipro.select import LiproLightGearSelect

        device = make_device("light", properties={})
        mock_coordinator.devices = {device.serial: device}
        mock_coordinator.get_device = lambda serial: mock_coordinator.devices.get(
            serial
        )
        mock_coordinator.async_send_command = AsyncMock(return_value=True)
        select = LiproLightGearSelect(mock_coordinator, device)

        with patch.object(select, "async_write_ha_state"):
            await select.async_select_option("gear_1")

        mock_coordinator.async_send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_light_gear_select_current_option_no_match_returns_none(
        self, mock_coordinator, make_device
    ) -> None:
        """Current option should be None when state does not match any gear."""
        from custom_components.lipro.select import LiproLightGearSelect

        device = make_device(
            "light",
            properties={
                "brightness": "1",
                "temperature": "99",
                "gearList": '[{"temperature":50,"brightness":100}]',
            },
        )
        mock_coordinator.devices = {device.serial: device}
        mock_coordinator.get_device = lambda serial: mock_coordinator.devices.get(
            serial
        )
        select = LiproLightGearSelect(mock_coordinator, device)
        assert select.current_option is None

    @pytest.mark.asyncio
    async def test_light_gear_select_invalid_option_returns_early(
        self, mock_coordinator, make_device
    ) -> None:
        """Invalid gear option should return without sending command."""
        from custom_components.lipro.select import LiproLightGearSelect

        device = make_device(
            "light", properties={"gearList": '[{"temperature":50,"brightness":100}]'}
        )
        mock_coordinator.devices = {device.serial: device}
        mock_coordinator.get_device = lambda serial: mock_coordinator.devices.get(
            serial
        )
        mock_coordinator.async_send_command = AsyncMock(return_value=True)
        select = LiproLightGearSelect(mock_coordinator, device)

        with patch.object(select, "async_write_ha_state"):
            await select.async_select_option("invalid")
        mock_coordinator.async_send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_light_gear_select_index_out_of_range_returns_early(
        self, mock_coordinator, make_device
    ) -> None:
        """Out-of-range gear index should return without sending command."""
        from custom_components.lipro.select import LiproLightGearSelect

        device = make_device(
            "light", properties={"gearList": '[{"temperature":50,"brightness":100}]'}
        )
        mock_coordinator.devices = {device.serial: device}
        mock_coordinator.get_device = lambda serial: mock_coordinator.devices.get(
            serial
        )
        mock_coordinator.async_send_command = AsyncMock(return_value=True)
        select = LiproLightGearSelect(mock_coordinator, device)

        with patch.object(select, "async_write_ha_state"):
            await select.async_select_option("gear_3")
        mock_coordinator.async_send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_light_gear_select_invalid_gear_payload_returns_early(
        self, mock_coordinator, make_device
    ) -> None:
        """Non-dict gear payload should return without sending command."""
        from custom_components.lipro.select import LiproLightGearSelect

        device = make_device("light", properties={"gearList": "[1]"})
        mock_coordinator.devices = {device.serial: device}
        mock_coordinator.get_device = lambda serial: mock_coordinator.devices.get(
            serial
        )
        mock_coordinator.async_send_command = AsyncMock(return_value=True)
        select = LiproLightGearSelect(mock_coordinator, device)

        with patch.object(select, "async_write_ha_state"):
            await select.async_select_option("gear_1")
        mock_coordinator.async_send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_light_gear_select_string_numeric_payload_supported(
        self, mock_coordinator, make_device
    ) -> None:
        """String numeric gear values should be parsed and applied correctly."""
        from custom_components.lipro.select import LiproLightGearSelect

        device = make_device(
            "light",
            properties={
                "brightness": "100",
                "temperature": "50",
                "gearList": '[{"temperature":"50","brightness":"100"}]',
            },
        )
        mock_coordinator.devices = {device.serial: device}
        mock_coordinator.get_device = lambda serial: mock_coordinator.devices.get(
            serial
        )
        mock_coordinator.async_send_command = AsyncMock(return_value=True)
        mock_coordinator.async_request_refresh = AsyncMock()
        select = LiproLightGearSelect(mock_coordinator, device)

        assert select.current_option == "gear_1"
        with patch.object(select, "async_write_ha_state"):
            await select.async_select_option("gear_1")
        mock_coordinator.async_send_command.assert_called_once()
        mock_coordinator.async_request_refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_light_gear_select_invalid_numeric_payload_returns_early(
        self, mock_coordinator, make_device
    ) -> None:
        """Non-numeric gear fields should return early without sending command."""
        from custom_components.lipro.select import LiproLightGearSelect

        device = make_device(
            "light",
            properties={"gearList": '[{"temperature":"bad","brightness":"100"}]'},
        )
        mock_coordinator.devices = {device.serial: device}
        mock_coordinator.get_device = lambda serial: mock_coordinator.devices.get(
            serial
        )
        mock_coordinator.async_send_command = AsyncMock(return_value=True)
        select = LiproLightGearSelect(mock_coordinator, device)

        assert select.current_option is None
        with patch.object(select, "async_write_ha_state"):
            await select.async_select_option("gear_1")
        mock_coordinator.async_send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_light_gear_select_valid_option_updates_and_requests_refresh(
        self, mock_coordinator, make_device
    ) -> None:
        """Valid gear option should send state change and request formal refresh."""
        from custom_components.lipro.select import LiproLightGearSelect

        device = make_device(
            "light", properties={"gearList": '[{"temperature":50,"brightness":100}]'}
        )
        mock_coordinator.devices = {device.serial: device}
        mock_coordinator.get_device = lambda serial: mock_coordinator.devices.get(
            serial
        )
        mock_coordinator.async_send_command = AsyncMock(return_value=True)
        mock_coordinator.async_request_refresh = AsyncMock()
        select = LiproLightGearSelect(mock_coordinator, device)

        with patch.object(select, "async_write_ha_state"):
            await select.async_select_option("gear_1")

        mock_coordinator.async_send_command.assert_called_once()
        mock_coordinator.async_request_refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_light_gear_select_failed_command_requests_refresh(
        self, mock_coordinator, make_device
    ) -> None:
        """Failed optimistic gear command should request refresh to restore truth."""
        from custom_components.lipro.select import LiproLightGearSelect

        device = make_device(
            "light", properties={"gearList": '[{"temperature":50,"brightness":100}]'}
        )
        mock_coordinator.devices = {device.serial: device}
        mock_coordinator.get_device = lambda serial: mock_coordinator.devices.get(
            serial
        )
        mock_coordinator.async_send_command = AsyncMock(return_value=False)
        mock_coordinator.async_request_refresh = AsyncMock()
        select = LiproLightGearSelect(mock_coordinator, device)

        with patch.object(select, "async_write_ha_state"):
            await select.async_select_option("gear_1")

        mock_coordinator.async_send_command.assert_called_once()
        mock_coordinator.async_request_refresh.assert_awaited_once()
