"""Behavior-driven platform entity tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


def _entry_with_runtime(coordinator: MagicMock) -> MagicMock:
    """Build a lightweight config entry stub for async_setup_entry tests."""
    entry = MagicMock()
    entry.runtime_data = coordinator
    return entry


@pytest.mark.asyncio
async def test_cover_async_setup_entry_and_command(mock_coordinator, make_device):
    """Cover platform creates LiproCover entities and sends real commands."""
    from custom_components.lipro.cover import LiproCover, async_setup_entry

    curtain = make_device("curtain", serial="curtain_1", properties={"position": "40"})
    mock_coordinator.devices = {curtain.serial: curtain}
    mock_coordinator.get_device = MagicMock(side_effect=mock_coordinator.devices.get)
    async_add_entities = MagicMock()

    await async_setup_entry(None, _entry_with_runtime(mock_coordinator), async_add_entities)
    entities = async_add_entities.call_args[0][0]

    assert len(entities) == 1
    assert isinstance(entities[0], LiproCover)
    assert entities[0].current_cover_position == 40

    entities[0].async_write_ha_state = MagicMock()
    await entities[0].async_open_cover()
    mock_coordinator.async_send_command.assert_awaited_with(
        curtain, "CURTAIN_OPEN", None
    )


@pytest.mark.asyncio
async def test_switch_async_setup_entry_builds_main_and_feature_switches(
    mock_coordinator, make_device
):
    """Switch platform creates both main switch and feature switches."""
    from custom_components.lipro.switch import (
        LiproFadeSwitch,
        LiproSwitch,
        async_setup_entry,
    )

    outlet = make_device("outlet", serial="outlet_1")
    light = make_device("light", serial="light_1", properties={"fadeState": "1"})
    mock_coordinator.devices = {outlet.serial: outlet, light.serial: light}
    mock_coordinator.get_device = MagicMock(side_effect=mock_coordinator.devices.get)
    async_add_entities = MagicMock()

    await async_setup_entry(None, _entry_with_runtime(mock_coordinator), async_add_entities)
    entities = async_add_entities.call_args[0][0]

    assert any(isinstance(entity, LiproSwitch) for entity in entities)
    assert any(isinstance(entity, LiproFadeSwitch) for entity in entities)

    main_switch = next(entity for entity in entities if isinstance(entity, LiproSwitch))
    main_switch.async_write_ha_state = MagicMock()
    await main_switch.async_turn_on()
    mock_coordinator.async_send_command.assert_awaited_with(
        outlet, "POWER_ON", None
    )


@pytest.mark.asyncio
async def test_climate_async_setup_entry_and_preset_command(mock_coordinator, make_device):
    """Climate platform creates heater entity and sends preset command."""
    from custom_components.lipro.climate import LiproHeater, async_setup_entry
    from custom_components.lipro.const import HEATER_MODE_DRY

    heater = make_device("heater", serial="heater_1", properties={"heaterMode": "1"})
    mock_coordinator.devices = {heater.serial: heater}
    mock_coordinator.get_device = MagicMock(side_effect=mock_coordinator.devices.get)
    async_add_entities = MagicMock()

    await async_setup_entry(None, _entry_with_runtime(mock_coordinator), async_add_entities)
    entities = async_add_entities.call_args[0][0]

    assert len(entities) == 1
    assert isinstance(entities[0], LiproHeater)

    entities[0].async_write_ha_state = MagicMock()
    await entities[0].async_set_preset_mode("dry")
    mock_coordinator.async_send_command.assert_awaited_with(
        heater,
        "CHANGE_STATE",
        [{"key": "heaterMode", "value": str(HEATER_MODE_DRY)}],
    )


@pytest.mark.asyncio
async def test_binary_sensor_async_setup_entry_creates_composed_entities(
    mock_coordinator, make_device
):
    """Binary sensor platform creates connectivity + body-sensor entities."""
    from custom_components.lipro.binary_sensor import (
        LiproConnectivitySensor,
        LiproMotionSensor,
        async_setup_entry,
    )

    body_sensor = make_device("bodySensor", serial="body_1")
    mock_coordinator.devices = {body_sensor.serial: body_sensor}
    mock_coordinator.get_device = MagicMock(side_effect=mock_coordinator.devices.get)
    async_add_entities = MagicMock()

    await async_setup_entry(None, _entry_with_runtime(mock_coordinator), async_add_entities)
    entities = async_add_entities.call_args[0][0]

    assert any(isinstance(entity, LiproConnectivitySensor) for entity in entities)
    assert any(isinstance(entity, LiproMotionSensor) for entity in entities)


@pytest.mark.asyncio
async def test_sensor_and_select_platforms_entity_behavior(mock_coordinator, make_device):
    """Sensor/select platforms create entities and send select command."""
    from custom_components.lipro.select import LiproLightGearSelect, async_setup_entry as setup_select
    from custom_components.lipro.sensor import LiproBatterySensor, LiproOutletPowerSensor, async_setup_entry as setup_sensor

    outlet = make_device(
        "outlet",
        serial="outlet_1",
        extra_data={"power_info": {"nowPower": 18.2, "energyList": [{"t": "20240101", "v": 1.1}]}},
    )
    light = make_device(
        "light",
        serial="light_gear",
        properties={"gearList": '[{"temperature":20,"brightness":60}]'},
    )
    battery_light = make_device(
        "light",
        serial="light_bat",
        properties={"battery": "88"},
    )
    mock_coordinator.devices = {
        outlet.serial: outlet,
        light.serial: light,
        battery_light.serial: battery_light,
    }
    mock_coordinator.get_device = MagicMock(side_effect=mock_coordinator.devices.get)

    sensor_add = MagicMock()
    await setup_sensor(None, _entry_with_runtime(mock_coordinator), sensor_add)
    sensor_entities = sensor_add.call_args[0][0]
    assert any(isinstance(entity, LiproOutletPowerSensor) for entity in sensor_entities)
    assert any(isinstance(entity, LiproBatterySensor) for entity in sensor_entities)

    select_add = MagicMock()
    await setup_select(None, _entry_with_runtime(mock_coordinator), select_add)
    select_entities = select_add.call_args[0][0]
    gear = next(entity for entity in select_entities if isinstance(entity, LiproLightGearSelect))

    mock_coordinator.async_request_refresh = AsyncMock()
    gear.async_write_ha_state = MagicMock()
    await gear.async_select_option("gear_1")
    mock_coordinator.async_send_command.assert_awaited_with(
        light,
        "CHANGE_STATE",
        [
            {"key": "brightness", "value": "60"},
            {"key": "temperature", "value": "20"},
        ],
    )
