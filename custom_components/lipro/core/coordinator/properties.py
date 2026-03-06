"""Coordinator entity/property update helpers.

This mixin owns:
- Entity registration for debounce-protection
- Applying property updates with protection filters
"""

from __future__ import annotations

import logging
from typing import Any

from ...const.properties import PROP_FAN_GEAR
from ..device import LiproDevice
from ..utils.log_safety import summarize_properties_for_log
from ..utils.redaction import redact_identifier
from .entity_protocol import LiproEntityProtocol
from .state import _CoordinatorStateMixin

_LOGGER = logging.getLogger(__name__)


class _CoordinatorPropertiesMixin(_CoordinatorStateMixin):
    """Mixin: entity registration and safe property application."""

    def register_entity(self, entity: LiproEntityProtocol) -> None:
        """Register an entity for debounce protection tracking."""
        if not entity.unique_id:
            return

        self._entities[entity.unique_id] = entity

        device_serial = entity.device.serial
        entities = self._entities_by_device.setdefault(device_serial, [])
        for idx, existing in enumerate(entities):
            if existing.unique_id == entity.unique_id:
                entities[idx] = entity
                break
        else:
            entities.append(entity)

    def unregister_entity(self, entity: LiproEntityProtocol) -> None:
        """Unregister an entity."""
        if not entity.unique_id:
            return

        if self._entities.get(entity.unique_id) is entity:
            del self._entities[entity.unique_id]

        device_serial = entity.device.serial
        if device_serial not in self._entities_by_device:
            return

        entities = self._entities_by_device[device_serial]
        self._entities_by_device[device_serial] = [
            e for e in entities if e is not entity
        ]
        if not self._entities_by_device[device_serial]:
            del self._entities_by_device[device_serial]

    def _get_protected_keys_for_device(self, device_serial: str) -> set[str]:
        """Collect debounce-protected property keys for a device."""
        protected_keys: set[str] = set()
        for entity in self._entities_by_device.get(device_serial, []):
            protected_keys.update(entity.get_protected_keys())
        return protected_keys

    def _filter_protected_properties(
        self,
        device_serial: str,
        properties: dict[str, Any],
    ) -> dict[str, Any]:
        """Filter out debounce-protected properties from an incoming update."""
        protected_keys = self._get_protected_keys_for_device(device_serial)
        if not protected_keys:
            return properties

        blocked_keys = protected_keys.intersection(properties)
        if not blocked_keys:
            return properties

        filtered = {k: v for k, v in properties.items() if k not in blocked_keys}
        _LOGGER.debug(
            "Skipping protected keys for device %s: %s",
            redact_identifier(device_serial) or "***",
            blocked_keys,
        )
        return filtered

    def _apply_properties_update(
        self,
        device: LiproDevice,
        properties: dict[str, Any],
        *,
        apply_protection: bool = True,
    ) -> dict[str, Any]:
        """Apply property updates to a device with optional debounce protection."""
        if apply_protection:
            properties = self._filter_protected_properties(device.serial, properties)
            properties = self._filter_pending_command_mismatches(
                device.serial, properties
            )

        if not properties:
            return {}

        self._adapt_fan_gear_range(device, properties)
        device.update_properties(properties)
        self._observe_command_confirmation(device.serial, properties)
        if _LOGGER.isEnabledFor(logging.DEBUG):
            summary = summarize_properties_for_log(properties)
            _LOGGER.debug(
                "Updated %s: count=%d keys=%s",
                device.name,
                summary["count"],
                summary["keys"],
            )
        return properties

    @staticmethod
    def _adapt_fan_gear_range(device: LiproDevice, properties: dict[str, Any]) -> None:
        """Infer max fan gear from runtime state for products missing config."""
        if not device.is_fan_light:
            return

        raw_gear = properties.get(PROP_FAN_GEAR)
        if raw_gear is None:
            return

        try:
            observed_gear = int(str(raw_gear).strip())
        except (TypeError, ValueError):
            return

        if observed_gear <= 0:
            return
        observed_gear = min(observed_gear, 100)

        baseline_max = max(1, device.default_max_fan_gear_in_model)
        device.max_fan_gear = max(device.max_fan_gear, baseline_max)

        if observed_gear <= device.max_fan_gear:
            return

        old_max = device.max_fan_gear
        device.max_fan_gear = observed_gear
        _LOGGER.debug(
            "Device %s: inferred fan gear range 1-%d from runtime status (was 1-%d)",
            device.name,
            device.max_fan_gear,
            old_max,
        )


__all__ = ["_CoordinatorPropertiesMixin"]
