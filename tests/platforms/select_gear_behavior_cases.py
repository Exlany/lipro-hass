"""Gear-preset behavior cases for the Lipro select platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


def _build_light_gear_select(mock_coordinator, make_device, properties: dict[str, object]):
    from custom_components.lipro.select import LiproLightGearSelect

    device = make_device("light", properties=properties)
    mock_coordinator.devices = {device.serial: device}
    mock_coordinator.get_device = lambda serial: mock_coordinator.devices.get(serial)
    return LiproLightGearSelect(mock_coordinator, device), device


class TestLightGearSelectBehavior:
    """Focused behavior cases for gear-preset selection."""

    @pytest.mark.asyncio
    async def test_light_gear_select_options_are_trimmed(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        from custom_components.lipro.select import LiproLightGearSelect

        select, _device = _build_light_gear_select(
            mock_coordinator,
            make_device,
            {
                "gearList": '[{"temperature":50,"brightness":100},{"temperature":40,"brightness":80}]'
            },
        )
        assert isinstance(select, LiproLightGearSelect)
        assert select.options == ["gear_1", "gear_2"]

    @pytest.mark.asyncio
    async def test_light_gear_select_options_empty_without_presets(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        select, _device = _build_light_gear_select(mock_coordinator, make_device, {})
        assert select.options == []

    @pytest.mark.asyncio
    async def test_light_gear_select_options_cap_to_max_presets(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        from custom_components.lipro.select import GEAR_OPTIONS

        select, _device = _build_light_gear_select(
            mock_coordinator,
            make_device,
            {
                "gearList": '[{"temperature":50,"brightness":100},{"temperature":40,"brightness":80},{"temperature":30,"brightness":60},{"temperature":20,"brightness":40}]'
            },
        )

        assert select.options == GEAR_OPTIONS

    @pytest.mark.asyncio
    async def test_light_gear_select_current_option_none_without_presets(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        select, _device = _build_light_gear_select(mock_coordinator, make_device, {})
        assert select.current_option is None

    def test_light_gear_select_coerce_none_value(self) -> None:
        from custom_components.lipro.select import LiproLightGearSelect

        assert LiproLightGearSelect._coerce_int_like(None) is None

    @pytest.mark.asyncio
    async def test_light_gear_select_extra_state_attributes_include_presets_and_range(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        select, _device = _build_light_gear_select(
            mock_coordinator,
            make_device,
            {
                "gearList": '[{"temperature":50,"brightness":100},{"temperature":40,"brightness":80}]'
            },
        )

        attrs = select.extra_state_attributes

        assert "preset_warm" in attrs
        assert "preset_neutral" in attrs
        preset_warm = attrs["preset_warm"]
        assert isinstance(preset_warm, str)
        assert preset_warm.startswith("100% / ")
        assert "color_temp_range" in attrs

    @pytest.mark.asyncio
    async def test_light_gear_select_extra_state_attributes_skip_invalid_rows(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        select, _device = _build_light_gear_select(
            mock_coordinator,
            make_device,
            {
                "gearList": '[{"temperature":null,"brightness":100},{"temperature":40,"brightness":80}]'
            },
        )

        attrs = select.extra_state_attributes

        assert "preset_warm" not in attrs
        assert "preset_neutral" in attrs

    @pytest.mark.asyncio
    async def test_light_gear_select_skips_invalid_rows_without_reindexing_valid_presets(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        select, _device = _build_light_gear_select(
            mock_coordinator,
            make_device,
            {
                "brightness": "80",
                "temperature": "40",
                "gearList": '[{"temperature":"bad","brightness":"100"},{"temperature":40,"brightness":80}]',
            },
        )

        attrs = select.extra_state_attributes

        assert select.current_option == "gear_2"
        assert "preset_warm" not in attrs
        assert attrs["preset_neutral"].startswith("80% / ")
        assert "color_temp_range" in attrs

    @pytest.mark.asyncio
    async def test_light_gear_select_applies_later_valid_slot_without_reindexing(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        mock_coordinator.async_send_command = AsyncMock(return_value=True)
        mock_coordinator.async_request_refresh = AsyncMock()
        select, device = _build_light_gear_select(
            mock_coordinator,
            make_device,
            {
                "gearList": '[{"temperature":"bad","brightness":"100"},{"temperature":40,"brightness":80}]'
            },
        )

        with patch.object(select, "async_write_ha_state"):
            await select.async_select_option("gear_2")

        mock_coordinator.async_send_command.assert_awaited_with(
            device,
            "CHANGE_STATE",
            [
                {"key": "brightness", "value": "80"},
                {"key": "temperature", "value": "40"},
            ],
        )
        mock_coordinator.async_request_refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_light_gear_select_no_presets_returns_early(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        mock_coordinator.async_send_command = AsyncMock(return_value=True)
        select, _device = _build_light_gear_select(mock_coordinator, make_device, {})

        with patch.object(select, "async_write_ha_state"):
            await select.async_select_option("gear_1")

        mock_coordinator.async_send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_light_gear_select_current_option_no_match_returns_none(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        select, _device = _build_light_gear_select(
            mock_coordinator,
            make_device,
            {
                "brightness": "1",
                "temperature": "99",
                "gearList": '[{"temperature":50,"brightness":100}]',
            },
        )
        assert select.current_option is None

    @pytest.mark.asyncio
    async def test_light_gear_select_invalid_option_returns_early(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        mock_coordinator.async_send_command = AsyncMock(return_value=True)
        select, _device = _build_light_gear_select(
            mock_coordinator,
            make_device,
            {"gearList": '[{"temperature":50,"brightness":100}]'},
        )

        with patch.object(select, "async_write_ha_state"):
            await select.async_select_option("invalid")
        mock_coordinator.async_send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_light_gear_select_index_out_of_range_returns_early(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        mock_coordinator.async_send_command = AsyncMock(return_value=True)
        select, _device = _build_light_gear_select(
            mock_coordinator,
            make_device,
            {"gearList": '[{"temperature":50,"brightness":100}]'},
        )

        with patch.object(select, "async_write_ha_state"):
            await select.async_select_option("gear_3")
        mock_coordinator.async_send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_light_gear_select_invalid_gear_payload_returns_early(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        mock_coordinator.async_send_command = AsyncMock(return_value=True)
        select, _device = _build_light_gear_select(
            mock_coordinator,
            make_device,
            {"gearList": "[1]"},
        )

        with patch.object(select, "async_write_ha_state"):
            await select.async_select_option("gear_1")
        mock_coordinator.async_send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_light_gear_select_string_numeric_payload_supported(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        mock_coordinator.async_send_command = AsyncMock(return_value=True)
        mock_coordinator.async_request_refresh = AsyncMock()
        select, _device = _build_light_gear_select(
            mock_coordinator,
            make_device,
            {
                "brightness": "100",
                "temperature": "50",
                "gearList": '[{"temperature":"50","brightness":"100"}]',
            },
        )

        assert select.current_option == "gear_1"
        with patch.object(select, "async_write_ha_state"):
            await select.async_select_option("gear_1")
        mock_coordinator.async_send_command.assert_called_once()
        mock_coordinator.async_request_refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_light_gear_select_invalid_numeric_payload_returns_early(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        mock_coordinator.async_send_command = AsyncMock(return_value=True)
        select, _device = _build_light_gear_select(
            mock_coordinator,
            make_device,
            {"gearList": '[{"temperature":"bad","brightness":"100"}]'},
        )

        assert select.current_option is None
        with patch.object(select, "async_write_ha_state"):
            await select.async_select_option("gear_1")
        mock_coordinator.async_send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_light_gear_select_valid_option_updates_and_requests_refresh(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        mock_coordinator.async_send_command = AsyncMock(return_value=True)
        mock_coordinator.async_request_refresh = AsyncMock()
        select, _device = _build_light_gear_select(
            mock_coordinator,
            make_device,
            {"gearList": '[{"temperature":50,"brightness":100}]'},
        )

        with patch.object(select, "async_write_ha_state"):
            await select.async_select_option("gear_1")

        mock_coordinator.async_send_command.assert_called_once()
        mock_coordinator.async_request_refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_light_gear_select_failed_command_requests_refresh(
        self,
        mock_coordinator,
        make_device,
    ) -> None:
        mock_coordinator.async_send_command = AsyncMock(return_value=False)
        mock_coordinator.async_request_refresh = AsyncMock()
        select, _device = _build_light_gear_select(
            mock_coordinator,
            make_device,
            {"gearList": '[{"temperature":50,"brightness":100}]'},
        )

        with patch.object(select, "async_write_ha_state"):
            await select.async_select_option("gear_1")

        mock_coordinator.async_send_command.assert_called_once()
        mock_coordinator.async_request_refresh.assert_awaited_once()
