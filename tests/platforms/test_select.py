"""Tests for Lipro select platform."""

from __future__ import annotations

from collections.abc import Iterable
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, patch

import pytest

from custom_components.lipro.core.device import LiproDevice


class TestLiproHeaterWindDirectionSelect:
    """Tests for LiproHeaterWindDirectionSelect entity."""

    def test_wind_direction_auto(self, make_device):
        """Test wind direction mode is auto."""
        from custom_components.lipro.const.properties import WIND_DIRECTION_AUTO

        device = make_device(
            "heater",
            properties={"windDirectionMode": str(WIND_DIRECTION_AUTO)},
        )
        assert device.wind_direction_mode == WIND_DIRECTION_AUTO

    def test_wind_direction_fixed(self, make_device):
        """Test wind direction mode is fixed."""
        from custom_components.lipro.const.properties import WIND_DIRECTION_FIX

        device = make_device(
            "heater",
            properties={"windDirectionMode": str(WIND_DIRECTION_FIX)},
        )
        assert device.wind_direction_mode == WIND_DIRECTION_FIX

    def test_wind_direction_default(self, make_device):
        """Test wind direction mode default is 1 (auto)."""
        device = make_device("heater")
        assert device.wind_direction_mode == 1

    def test_wind_direction_options(self):
        """Test wind direction options from real source."""
        from custom_components.lipro.select import WIND_DIRECTION_OPTIONS

        assert WIND_DIRECTION_OPTIONS == ["auto", "fixed"]

    def test_wind_direction_value_mapping(self):
        """Test wind direction value mapping from real source."""
        from custom_components.lipro.const.properties import (
            WIND_DIRECTION_AUTO,
            WIND_DIRECTION_FIX,
        )
        from custom_components.lipro.select import (
            VALUE_TO_WIND_DIRECTION,
            WIND_DIRECTION_TO_VALUE,
        )

        assert WIND_DIRECTION_TO_VALUE["auto"] == WIND_DIRECTION_AUTO
        assert WIND_DIRECTION_TO_VALUE["fixed"] == WIND_DIRECTION_FIX
        assert VALUE_TO_WIND_DIRECTION[WIND_DIRECTION_AUTO] == "auto"
        assert VALUE_TO_WIND_DIRECTION[WIND_DIRECTION_FIX] == "fixed"


class TestLiproHeaterLightModeSelect:
    """Tests for LiproHeaterLightModeSelect entity."""

    def test_light_mode_off(self, make_device):
        """Test light mode is off."""
        from custom_components.lipro.const.properties import HEATER_LIGHT_OFF

        device = make_device(
            "heater",
            properties={"lightMode": str(HEATER_LIGHT_OFF)},
        )
        assert device.light_mode == HEATER_LIGHT_OFF

    def test_light_mode_main(self, make_device):
        """Test light mode is main."""
        from custom_components.lipro.const.properties import HEATER_LIGHT_MAIN

        device = make_device(
            "heater",
            properties={"lightMode": str(HEATER_LIGHT_MAIN)},
        )
        assert device.light_mode == HEATER_LIGHT_MAIN

    def test_light_mode_night(self, make_device):
        """Test light mode is night."""
        from custom_components.lipro.const.properties import HEATER_LIGHT_NIGHT

        device = make_device(
            "heater",
            properties={"lightMode": str(HEATER_LIGHT_NIGHT)},
        )
        assert device.light_mode == HEATER_LIGHT_NIGHT

    def test_light_mode_default(self, make_device):
        """Test light mode default is 0 (off)."""
        device = make_device("heater")
        assert device.light_mode == 0

    def test_light_mode_options(self):
        """Test light mode options from real source."""
        from custom_components.lipro.select import LIGHT_MODE_OPTIONS

        assert LIGHT_MODE_OPTIONS == ["off", "main", "night"]

    def test_light_mode_value_mapping(self):
        """Test light mode value mapping from real source."""
        from custom_components.lipro.const.properties import (
            HEATER_LIGHT_MAIN,
            HEATER_LIGHT_NIGHT,
            HEATER_LIGHT_OFF,
        )
        from custom_components.lipro.select import (
            LIGHT_MODE_TO_VALUE,
            VALUE_TO_LIGHT_MODE,
        )

        assert LIGHT_MODE_TO_VALUE["off"] == HEATER_LIGHT_OFF
        assert LIGHT_MODE_TO_VALUE["main"] == HEATER_LIGHT_MAIN
        assert LIGHT_MODE_TO_VALUE["night"] == HEATER_LIGHT_NIGHT
        assert VALUE_TO_LIGHT_MODE[HEATER_LIGHT_OFF] == "off"
        assert VALUE_TO_LIGHT_MODE[HEATER_LIGHT_MAIN] == "main"
        assert VALUE_TO_LIGHT_MODE[HEATER_LIGHT_NIGHT] == "night"


class TestLiproLightGearSelect:
    """Tests for LiproLightGearSelect entity."""

    def test_gear_options(self):
        """Test gear options from real source."""
        from custom_components.lipro.select import GEAR_OPTIONS

        assert GEAR_OPTIONS == ["gear_1", "gear_2", "gear_3"]

    def test_gear_list_parsing(self, make_device):
        """Test gear list parsing from JSON string."""
        device = make_device(
            "light",
            properties={
                "gearList": '[{"temperature":50,"brightness":100},{"temperature":30,"brightness":80},{"temperature":70,"brightness":60}]'
            },
        )

        gear_list = device.gear_list
        assert len(gear_list) == 3
        assert gear_list[0]["temperature"] == 50
        assert gear_list[0]["brightness"] == 100
        assert gear_list[1]["temperature"] == 30
        assert gear_list[1]["brightness"] == 80
        assert gear_list[2]["temperature"] == 70
        assert gear_list[2]["brightness"] == 60

    def test_gear_list_empty(self, make_device):
        """Test empty gear list."""
        device = make_device("light")
        assert device.gear_list == []
        assert device.has_gear_presets is False

    def test_has_gear_presets(self, make_device):
        """Test has_gear_presets property."""
        device = make_device(
            "light",
            properties={"gearList": '[{"temperature":50,"brightness":100}]'},
        )
        assert device.has_gear_presets is True

    def test_last_gear_index(self, make_device):
        """Test last gear index property."""
        device = make_device("light", properties={"lastGearIndex": "2"})
        assert device.last_gear_index == 2

    def test_last_gear_index_default(self, make_device):
        """Test last gear index default is -1."""
        device = make_device("light")
        assert device.last_gear_index == -1


class TestGearTemperatureConversion:
    """Tests for gear temperature conversion between percentage and Kelvin."""

    def test_percent_to_kelvin(self):
        """Test converting temperature percentage to Kelvin."""
        from custom_components.lipro.const.properties import percent_to_kelvin

        assert percent_to_kelvin(0) == 2700
        assert percent_to_kelvin(50) == 4600
        assert percent_to_kelvin(100) == 6500

    def test_kelvin_to_percent(self):
        """Test converting Kelvin to temperature percentage."""
        from custom_components.lipro.const.properties import kelvin_to_percent

        assert kelvin_to_percent(2700) == 0
        assert kelvin_to_percent(4600) == 50
        assert kelvin_to_percent(6500) == 100

    def test_roundtrip(self):
        """Test percent -> kelvin -> percent roundtrip."""
        from custom_components.lipro.const.properties import (
            kelvin_to_percent,
            percent_to_kelvin,
        )

        for pct in (0, 25, 50, 75, 100):
            assert kelvin_to_percent(percent_to_kelvin(pct)) == pct


class TestSelectConstants:
    """Tests for select-related constants."""

    def test_heater_light_constants(self):
        """Test heater light mode constants."""
        from custom_components.lipro.const.properties import (
            HEATER_LIGHT_MAIN,
            HEATER_LIGHT_NIGHT,
            HEATER_LIGHT_OFF,
        )

        assert HEATER_LIGHT_OFF == 0
        assert HEATER_LIGHT_MAIN == 1
        assert HEATER_LIGHT_NIGHT == 2

    def test_wind_direction_constants(self):
        """Test wind direction mode constants."""
        from custom_components.lipro.const.properties import (
            WIND_DIRECTION_AUTO,
            WIND_DIRECTION_FIX,
        )

        assert WIND_DIRECTION_AUTO == 1
        assert WIND_DIRECTION_FIX == 2

    def test_property_constants(self):
        """Test property constants."""
        from custom_components.lipro.const.properties import (
            PROP_LIGHT_MODE,
            PROP_WIND_DIRECTION_MODE,
        )

        assert PROP_LIGHT_MODE == "lightMode"
        assert PROP_WIND_DIRECTION_MODE == "windDirectionMode"


class TestSelectDeviceDetection:
    """Tests for select entity device detection."""

    def test_heater_device_detection(self):
        """Test heater device is correctly detected."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Heater",
            device_type=7,
            iot_name="",
            physical_model="heater",
        )
        assert device.is_heater is True

    def test_light_with_gear_detection(self):
        """Test light with gear presets is correctly detected."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            physical_model="light",
            properties={"gearList": '[{"temperature":50,"brightness":100}]'},
        )
        assert device.is_light is True
        assert device.has_gear_presets is True


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
