"""Setup-focused behavior cases for the Lipro select platform."""

from __future__ import annotations

from collections.abc import Iterable
from types import SimpleNamespace
from typing import cast

import pytest


class TestSelectSetupBehavior:
    """Behavior cases for select-platform setup routing."""

    @pytest.mark.asyncio
    async def test_async_setup_entry_creates_expected_entities(
        self,
        hass,
        make_device,
    ) -> None:
        """Setup should create heater selects and gear select for eligible lights."""
        from custom_components.lipro.select import (
            LiproHeaterLightModeSelect,
            LiproHeaterWindDirectionSelect,
            LiproLightGearSelect,
            async_setup_entry,
        )

        devices = {
            "heater": make_device("heater"),
            "gear_light": make_device(
                "light",
                properties={"gearList": '[{"temperature":50,"brightness":100}]'},
            ),
            "plain_light": make_device("light"),
        }
        coordinator = SimpleNamespace(
            devices=devices,
            iter_devices=lambda: tuple(devices.values()),
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
            del update_before_add
            captured.extend(entities)

        await async_setup_entry(
            hass,
            cast(LiproConfigEntry, entry),
            cast(AddEntitiesCallback, _add_entities),
        )

        assert any(
            isinstance(entity, LiproHeaterWindDirectionSelect) for entity in captured
        )
        assert any(
            isinstance(entity, LiproHeaterLightModeSelect) for entity in captured
        )
        assert any(isinstance(entity, LiproLightGearSelect) for entity in captured)
        assert len(captured) == 3
