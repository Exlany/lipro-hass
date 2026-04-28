"""Tests for LiproEntity base class."""

from __future__ import annotations

from time import monotonic
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.lipro.const.base import DOMAIN, MANUFACTURER
from custom_components.lipro.entities.base import DEBOUNCE_PROTECTION_WINDOW
from custom_components.lipro.light import LiproLight
from homeassistant.helpers.update_coordinator import CoordinatorEntity


def _make_entity(coordinator, device):
    """Create a LiproLight entity with HA state writing mocked out."""
    entity = LiproLight(coordinator, device)
    patch.object(entity, "async_write_ha_state", new=MagicMock()).start()
    return entity


# =========================================================================
# Initialization
# =========================================================================


class TestLiproEntityInit:
    """Tests for LiproEntity __init__."""

    def test_unique_id_without_suffix(self, mock_coordinator, make_device):
        """Light device gets unique_id == device.unique_id (no suffix)."""
        device = make_device("light")
        entity = _make_entity(mock_coordinator, device)

        assert entity.unique_id == device.unique_id

    def test_unique_id_with_suffix(self, mock_coordinator, make_device):
        """Fan-light device gets unique_id with '_light' suffix."""
        device = make_device("fanLight")
        entity = _make_entity(mock_coordinator, device)

        assert entity.unique_id == f"{device.unique_id}_light"

    def test_device_info_contains_identifiers(self, mock_coordinator, make_device):
        """DeviceInfo includes (DOMAIN, serial) identifier tuple."""
        device = make_device("light")
        entity = _make_entity(mock_coordinator, device)

        info = entity.device_info
        assert (DOMAIN, device.serial) in info["identifiers"]
        assert info["name"] == device.name
        assert info["manufacturer"] == MANUFACTURER

    def test_device_info_serial_number(self, mock_coordinator, make_device):
        """Non-group device includes serial_number in DeviceInfo."""
        device = make_device("light", serial="03ab5ccd7c111111")
        entity = _make_entity(mock_coordinator, device)

        assert entity.device_info["serial_number"] == "03ab5ccd7c111111"

    def test_device_info_no_serial_for_group(self, mock_coordinator, make_device):
        """Group device omits serial_number from DeviceInfo."""
        device = make_device("light", serial="mesh_group_10001", is_group=True)
        entity = _make_entity(mock_coordinator, device)

        assert "serial_number" not in entity.device_info


# =========================================================================
# Availability
# =========================================================================


class TestLiproEntityAvailability:
    """Tests for LiproEntity.available property."""

    def test_available_when_coordinator_success_and_device_available(
        self, mock_coordinator, make_device
    ):
        """Entity is available when coordinator succeeded and device is available."""
        device = make_device("light")
        mock_coordinator.get_device.return_value = device
        entity = _make_entity(mock_coordinator, device)

        assert entity.available is True

    def test_unavailable_when_coordinator_failed(self, mock_coordinator, make_device):
        """Entity is unavailable when coordinator last update failed."""
        device = make_device("light")
        mock_coordinator.get_device.return_value = device
        entity = _make_entity(mock_coordinator, device)

        mock_coordinator.last_update_success = False

        assert entity.available is False

    def test_unavailable_when_device_disconnected(self, mock_coordinator, make_device):
        """Entity is unavailable when device itself is not available."""
        device = make_device("light")
        device.available = False
        mock_coordinator.get_device.return_value = device
        entity = _make_entity(mock_coordinator, device)

        assert entity.available is False


# =========================================================================
# Device property
# =========================================================================


class TestLiproEntityDeviceProperty:
    """Tests for LiproEntity.device property."""

    def test_device_returns_fresh_from_coordinator(self, mock_coordinator, make_device):
        """device property returns fresh device from coordinator."""
        original = make_device("light", name="Original")
        updated = make_device("light", name="Updated")
        entity = _make_entity(mock_coordinator, original)

        mock_coordinator.set_device(updated)

        assert entity.device.name == "Updated"

    def test_capabilities_returns_canonical_snapshot(
        self, mock_coordinator, make_device
    ):
        """capabilities property should expose the device snapshot directly."""
        device = make_device("light")
        entity = _make_entity(mock_coordinator, device)

        assert entity.capabilities == device.capabilities

    def test_device_falls_back_to_initial_when_not_in_coordinator(
        self, mock_coordinator, make_device
    ):
        """device property falls back to initial device when coordinator returns None."""
        device = make_device("light", name="Initial")
        entity = _make_entity(mock_coordinator, device)

        # Coordinator has no device for this serial (devices dict is empty)
        assert entity.device.name == "Initial"


# =========================================================================
# Send command
# =========================================================================


class TestLiproEntitySendCommand:
    """Tests for LiproEntity.async_send_command."""

    async def test_send_command_uses_formal_command_service_by_default(
        self, mock_coordinator, make_device
    ):
        """async_send_command should route through the formal runtime verb."""
        device = make_device("light")
        mock_coordinator.get_device.return_value = device
        entity = _make_entity(mock_coordinator, device)

        result = await entity.async_send_command(
            "powerOn", [{"key": "powerState", "value": "1"}]
        )

        assert result is True
        mock_coordinator.command_service.async_send_command.assert_not_awaited()
        mock_coordinator.async_send_command.assert_awaited_once_with(
            device, "powerOn", [{"key": "powerState", "value": "1"}]
        )

    async def test_send_command_prefers_command_service_when_available(
        self, mock_coordinator, make_device
    ) -> None:
        """Runtime command dispatch should ignore leaked service handles."""
        device = make_device("light")
        mock_coordinator.get_device.return_value = device
        mock_coordinator.command_service = MagicMock()
        mock_coordinator.command_service.async_send_command = AsyncMock(
            return_value=True
        )
        entity = _make_entity(mock_coordinator, device)

        result = await entity.async_send_command(
            "powerOn", [{"key": "powerState", "value": "1"}]
        )

        assert result is True
        mock_coordinator.command_service.async_send_command.assert_not_awaited()
        mock_coordinator.async_send_command.assert_awaited_once_with(
            device, "powerOn", [{"key": "powerState", "value": "1"}]
        )

    async def test_send_command_with_optimistic_state_updates_device(
        self, mock_coordinator, make_device
    ):
        """Optimistic state is applied to device and HA state is written."""
        device = make_device("light")
        mock_coordinator.get_device.return_value = device
        entity = _make_entity(mock_coordinator, device)

        await entity.async_send_command(
            "powerOn", None, optimistic_state={"powerState": "1"}
        )

        assert device.properties["powerState"] == "1"
        mock_coordinator.async_apply_optimistic_state.assert_awaited_once_with(
            device, {"powerState": "1"}
        )
        entity.async_write_ha_state.assert_called_once()

    async def test_send_command_skips_when_unavailable(
        self, mock_coordinator, make_device
    ):
        """Command is skipped and returns False when entity is unavailable."""
        device = make_device("light")
        device.available = False
        mock_coordinator.get_device.return_value = device
        entity = _make_entity(mock_coordinator, device)

        result = await entity.async_send_command("powerOn")

        assert result is False
        mock_coordinator.async_send_command.assert_not_awaited()

    async def test_send_command_failure_triggers_refresh(
        self, mock_coordinator, make_device
    ):
        """Failed command with optimistic state triggers coordinator refresh."""
        device = make_device("light")
        mock_coordinator.get_device.return_value = device
        mock_coordinator.async_send_command.return_value = False
        entity = _make_entity(mock_coordinator, device)

        result = await entity.async_send_command(
            "powerOn", None, optimistic_state={"powerState": "1"}
        )

        assert result is False
        mock_coordinator.async_request_refresh.assert_awaited_once()


# =========================================================================
# Debounce
# =========================================================================


class TestLiproEntityDebounce:
    """Tests for LiproEntity debounce protection."""

    def test_is_debouncing_false_by_default(self, mock_coordinator, make_device):
        """Entity is not debouncing by default."""
        device = make_device("light")
        entity = _make_entity(mock_coordinator, device)

        assert entity.is_debouncing is False

    def test_get_protected_keys_empty_when_not_debouncing(
        self, mock_coordinator, make_device
    ):
        """Protected keys are empty when not in debounce window."""
        device = make_device("light")
        entity = _make_entity(mock_coordinator, device)

        assert entity.get_protected_keys() == set()

    async def test_send_command_debounced_sets_protection_window(
        self, mock_coordinator, make_device
    ):
        """Debounced command with optimistic state activates protection window."""
        device = make_device("light")
        mock_coordinator.get_device.return_value = device
        entity = _make_entity(mock_coordinator, device)

        await entity.async_send_command_debounced(
            "changeState",
            [{"key": "brightness", "value": "80"}],
            optimistic_state={"brightness": "80"},
        )

        assert entity.is_debouncing is True
        assert entity._debounce_protected_until > monotonic()
        assert (
            entity._debounce_protected_until <= monotonic() + DEBOUNCE_PROTECTION_WINDOW
        )

    async def test_send_command_debounced_skips_when_unavailable(
        self, mock_coordinator, make_device
    ):
        """Debounced command should return early when entity is unavailable."""
        device = make_device("light", properties={"brightness": "10"})
        device.available = False
        mock_coordinator.get_device.return_value = device
        entity = _make_entity(mock_coordinator, device)

        await entity.async_send_command_debounced(
            "changeState",
            [{"key": "brightness", "value": "80"}],
            optimistic_state={"brightness": "80"},
        )

        # Optimistic state should not be applied when unavailable.
        assert device.properties["brightness"] == "10"
        entity.async_write_ha_state.assert_not_called()
        assert entity._debouncer is None
        mock_coordinator.async_send_command.assert_not_awaited()

    async def test_get_protected_keys_returns_keys_during_protection(
        self, mock_coordinator, make_device
    ):
        """Protected keys are returned while in debounce window."""
        device = make_device("light")
        mock_coordinator.get_device.return_value = device
        entity = _make_entity(mock_coordinator, device)

        await entity.async_send_command_debounced(
            "changeState",
            [{"key": "brightness", "value": "80"}],
            optimistic_state={"brightness": "80"},
        )

        protected = entity.get_protected_keys()
        assert "brightness" in protected

    async def test_get_protected_keys_returns_copy_during_protection(
        self, mock_coordinator, make_device
    ):
        """Callers should not be able to mutate the debounce protection set."""
        device = make_device("light")
        mock_coordinator.get_device.return_value = device
        entity = _make_entity(mock_coordinator, device)

        await entity.async_send_command_debounced(
            "changeState",
            [{"key": "brightness", "value": "80"}],
            optimistic_state={"brightness": "80"},
        )

        protected = entity.get_protected_keys()
        protected.add("temperature")

        assert entity._debounce_protected_keys == {"brightness"}

    async def test_debounce_protected_keys_replaced_on_new_call(
        self, mock_coordinator, make_device
    ):
        """Newest debounced payload should replace protected keys, not accumulate."""
        device = make_device("light")
        mock_coordinator.get_device.return_value = device
        entity = _make_entity(mock_coordinator, device)

        await entity.async_send_command_debounced(
            "changeState",
            [{"key": "brightness", "value": "80"}],
            optimistic_state={"brightness": "80"},
        )
        await entity.async_send_command_debounced(
            "changeState",
            [{"key": "temperature", "value": "60"}],
            optimistic_state={"temperature": "60"},
        )

        assert entity.get_protected_keys() == {"temperature"}

    def test_get_protected_keys_clears_stale_keys_after_window(
        self, mock_coordinator, make_device
    ):
        """Expired debounce window should clear stale protected keys."""
        device = make_device("light")
        entity = _make_entity(mock_coordinator, device)
        entity._debounce_protected_keys = {"brightness"}
        entity._debounce_protected_until = monotonic() - 1

        assert entity.get_protected_keys() == set()
        assert entity._debounce_protected_keys == set()

    async def test_send_command_internal_failure_clears_protection_and_refreshes(
        self, mock_coordinator, make_device
    ):
        """Failed internal send clears protection and requests coordinator refresh."""
        device = make_device("light")
        mock_coordinator.get_device.return_value = device
        mock_coordinator.async_send_command.return_value = False
        entity = _make_entity(mock_coordinator, device)
        entity._debounce_protected_keys = {"brightness"}
        entity._debounce_protected_until = monotonic() + 100

        await entity._send_command_internal(
            "changeState",
            [{"key": "brightness", "value": "80"}],
            optimistic_state={"brightness": "80"},
        )

        assert entity._debounce_protected_keys == set()
        assert entity._debounce_protected_until == 0
        mock_coordinator.async_request_refresh.assert_awaited_once()


# =========================================================================
# Lifecycle
# =========================================================================


class TestLiproEntityLifecycle:
    """Tests for LiproEntity lifecycle hooks."""

    async def test_async_added_to_hass_registers_entity(
        self, mock_coordinator, make_device
    ):
        """async_added_to_hass registers entity with coordinator."""
        device = make_device("light")
        entity = _make_entity(mock_coordinator, device)

        with patch.object(
            CoordinatorEntity, "async_added_to_hass", new_callable=AsyncMock
        ):
            await entity.async_added_to_hass()

        mock_coordinator.register_entity.assert_called_once_with(entity)

    async def test_async_will_remove_from_hass_unregisters_and_cancels_debouncer(
        self, mock_coordinator, make_device
    ):
        """async_will_remove_from_hass unregisters entity and cancels debouncer."""
        device = make_device("light")
        entity = _make_entity(mock_coordinator, device)

        # Give the entity a debouncer to cancel
        debouncer = MagicMock()
        entity._debouncer = debouncer

        with patch.object(
            CoordinatorEntity, "async_will_remove_from_hass", new_callable=AsyncMock
        ):
            await entity.async_will_remove_from_hass()

        debouncer.cancel.assert_called_once()
        assert entity._debouncer is None
        mock_coordinator.unregister_entity.assert_called_once_with(entity)
