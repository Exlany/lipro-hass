"""Behavior-driven platform entity tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _entry_with_runtime(coordinator: MagicMock) -> MagicMock:
    """Build a lightweight config entry stub for async_setup_entry tests."""
    entry = MagicMock()
    entry.runtime_data = coordinator
    return entry


@pytest.mark.asyncio
async def test_cover_async_setup_entry_and_command(hass, mock_coordinator, make_device):
    """Cover platform creates LiproCover entities and sends real commands."""
    from custom_components.lipro.cover import LiproCover, async_setup_entry

    curtain = make_device("curtain", serial="curtain_1", properties={"position": "40"})
    mock_coordinator.set_devices(curtain)
    async_add_entities = MagicMock()

    await async_setup_entry(
        hass, _entry_with_runtime(mock_coordinator), async_add_entities
    )
    entities = async_add_entities.call_args[0][0]

    assert len(entities) == 1
    assert isinstance(entities[0], LiproCover)
    assert entities[0].current_cover_position == 40

    patch.object(entities[0], "async_write_ha_state", new=MagicMock()).start()
    await entities[0].async_open_cover()
    mock_coordinator.async_send_command.assert_awaited_with(
        curtain, "CURTAIN_OPEN", None
    )


@pytest.mark.asyncio
async def test_switch_async_setup_entry_builds_main_and_feature_switches(
    hass, mock_coordinator, make_device
):
    """Switch platform creates both main switch and feature switches."""
    from custom_components.lipro.switch import (
        LiproPropertySwitch,
        LiproSwitch,
        async_setup_entry,
    )

    outlet = make_device("outlet", serial="outlet_1")
    light = make_device("light", serial="light_1", properties={"fadeState": "1"})
    mock_coordinator.set_devices(outlet, light)
    async_add_entities = MagicMock()

    await async_setup_entry(
        hass, _entry_with_runtime(mock_coordinator), async_add_entities
    )
    entities = async_add_entities.call_args[0][0]

    assert any(isinstance(entity, LiproSwitch) for entity in entities)
    assert any(isinstance(entity, LiproPropertySwitch) for entity in entities)

    main_switch = next(entity for entity in entities if isinstance(entity, LiproSwitch))
    patch.object(main_switch, "async_write_ha_state", new=MagicMock()).start()
    await main_switch.async_turn_on()
    mock_coordinator.async_send_command.assert_awaited_with(outlet, "POWER_ON", None)


@pytest.mark.asyncio
async def test_climate_async_setup_entry_and_preset_command(
    hass, mock_coordinator, make_device
):
    """Climate platform creates heater entity and sends preset command."""
    from custom_components.lipro.climate import LiproHeater, async_setup_entry
    from custom_components.lipro.const.properties import HEATER_MODE_DRY

    heater = make_device("heater", serial="heater_1", properties={"heaterMode": "1"})
    mock_coordinator.set_devices(heater)
    async_add_entities = MagicMock()

    await async_setup_entry(
        hass, _entry_with_runtime(mock_coordinator), async_add_entities
    )
    entities = async_add_entities.call_args[0][0]

    assert len(entities) == 1
    assert isinstance(entities[0], LiproHeater)

    patch.object(entities[0], "async_write_ha_state", new=MagicMock()).start()
    await entities[0].async_set_preset_mode("dry")
    mock_coordinator.async_send_command.assert_awaited_with(
        heater,
        "CHANGE_STATE",
        [{"key": "heaterMode", "value": str(HEATER_MODE_DRY)}],
    )


@pytest.mark.asyncio
async def test_binary_sensor_async_setup_entry_creates_composed_entities(
    hass, mock_coordinator, make_device
):
    """Binary sensor platform creates connectivity + body-sensor entities."""
    from custom_components.lipro.binary_sensor import (
        LiproConnectivitySensor,
        LiproMotionSensor,
        async_setup_entry,
    )

    body_sensor = make_device("bodySensor", serial="body_1")
    mock_coordinator.set_devices(body_sensor)
    async_add_entities = MagicMock()

    await async_setup_entry(
        hass, _entry_with_runtime(mock_coordinator), async_add_entities
    )
    entities = async_add_entities.call_args[0][0]

    assert any(isinstance(entity, LiproConnectivitySensor) for entity in entities)
    assert any(isinstance(entity, LiproMotionSensor) for entity in entities)


@pytest.mark.asyncio
async def test_sensor_and_select_platforms_entity_behavior(
    hass, mock_coordinator, make_device
):
    """Sensor/select platforms create entities and send select command."""
    from custom_components.lipro.select import (
        LiproLightGearSelect,
        async_setup_entry as setup_select,
    )
    from custom_components.lipro.sensor import (
        LiproBatterySensor,
        LiproOutletPowerSensor,
        async_setup_entry as setup_sensor,
    )

    outlet = make_device(
        "outlet",
        serial="outlet_1",
    )
    outlet.outlet_power_info = {
        "nowPower": 18.2,
        "energyList": [{"t": "20240101", "v": 1.1}],
    }
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
    mock_coordinator.set_devices(outlet, light, battery_light)

    sensor_add = MagicMock()
    await setup_sensor(hass, _entry_with_runtime(mock_coordinator), sensor_add)
    sensor_entities = sensor_add.call_args[0][0]
    assert any(isinstance(entity, LiproOutletPowerSensor) for entity in sensor_entities)
    assert any(isinstance(entity, LiproBatterySensor) for entity in sensor_entities)

    select_add = MagicMock()
    await setup_select(hass, _entry_with_runtime(mock_coordinator), select_add)
    select_entities = select_add.call_args[0][0]
    gear = next(
        entity for entity in select_entities if isinstance(entity, LiproLightGearSelect)
    )

    mock_coordinator.async_request_refresh = AsyncMock()
    patch.object(gear, "async_write_ha_state", new=MagicMock()).start()
    await gear.async_select_option("gear_1")
    mock_coordinator.async_send_command.assert_awaited_with(
        light,
        "CHANGE_STATE",
        [
            {"key": "brightness", "value": "60"},
            {"key": "temperature", "value": "20"},
        ],
    )


@pytest.mark.asyncio
async def test_switch_async_setup_entry_builds_panel_config_switches(
    hass, mock_coordinator, make_device
):
    """Switch platform only adds panel config switches for panel devices."""
    from custom_components.lipro.switch import (
        LiproPanelPropertySwitch,
        async_setup_entry,
    )

    panel = make_device(
        "switch",
        serial="panel_1",
        properties={"led": "1", "memory": "0"},
    )
    outlet = make_device(
        "outlet",
        serial="outlet_1",
        properties={"memory": "1"},
    )
    mock_coordinator.set_devices(panel, outlet)
    async_add_entities = MagicMock()

    await async_setup_entry(
        hass, _entry_with_runtime(mock_coordinator), async_add_entities
    )
    entities = async_add_entities.call_args[0][0]

    panel_switches = [
        entity for entity in entities if isinstance(entity, LiproPanelPropertySwitch)
    ]

    # Should have 2 panel switches (LED + Memory) for panel device only
    assert len(panel_switches) == 2
    assert all(entity.device.serial == panel.serial for entity in panel_switches)
