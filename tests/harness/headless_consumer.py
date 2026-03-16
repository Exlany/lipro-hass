"""Proof-only headless consumer harness for host-neutral nucleus reuse."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from custom_components.lipro.core.auth import (
    AuthBootstrapSeed,
    AuthSessionSnapshot,
    LiproAuthManager,
)
from custom_components.lipro.core.capability import (
    CapabilityRegistry,
    CapabilitySnapshot,
)
from custom_components.lipro.core.device import LiproDevice
from custom_components.lipro.core.protocol import LiproProtocolFacade
from custom_components.lipro.headless.boot import (
    HeadlessBootContext,
    build_headless_boot_context,
)

if TYPE_CHECKING:
    import aiohttp

DeviceRow = dict[str, object]
PropertiesMap = dict[str, object]

HEADLESS_PROOF_PUBLIC_PATHS = (
    'LiproProtocolFacade.get_devices',
    'LiproProtocolFacade.query_device_status',
    'LiproProtocolFacade.query_mesh_group_status',
)
HEADLESS_PROOF_ASSERTION_FAMILIES = (
    'rest.device-list',
    'rest.device-status',
    'rest.mesh-group-status',
)


def _require_device_rows(payload: object) -> list[DeviceRow]:
    if not isinstance(payload, dict):
        msg = 'Expected canonical device-page mapping'
        raise TypeError(msg)
    rows = payload.get('devices')
    if not isinstance(rows, list):
        msg = 'Expected canonical device-page devices list'
        raise TypeError(msg)
    normalized_rows: list[DeviceRow] = []
    for row in rows:
        if not isinstance(row, dict):
            msg = 'Expected canonical device rows to be mappings'
            raise TypeError(msg)
        normalized_rows.append(dict(row))
    return normalized_rows


def _build_properties_map(rows: object, *, id_key: str) -> dict[str, PropertiesMap]:
    if not isinstance(rows, list):
        msg = 'Expected canonical status rows list'
        raise TypeError(msg)
    properties_by_id: dict[str, PropertiesMap] = {}
    for row in rows:
        if not isinstance(row, dict):
            msg = 'Expected canonical status rows to be mappings'
            raise TypeError(msg)
        identifier = row.get(id_key)
        properties = row.get('properties')
        if isinstance(identifier, str) and isinstance(properties, dict):
            properties_by_id[identifier] = dict(properties)
    return properties_by_id


@dataclass(frozen=True, slots=True)
class HeadlessConsumerProof:
    """One proof artifact showing headless reuse of the canonical nucleus."""

    auth_session: AuthSessionSnapshot
    devices: tuple[LiproDevice, ...]
    capability_snapshots: dict[str, CapabilitySnapshot]
    public_paths: tuple[str, ...] = HEADLESS_PROOF_PUBLIC_PATHS
    assertion_families: tuple[str, ...] = HEADLESS_PROOF_ASSERTION_FAMILIES


class HeadlessConsumerHarness:
    """Build a proof-only headless consumer on top of the formal nucleus."""

    def __init__(
        self,
        *,
        session: aiohttp.ClientSession,
        client_factory: type[LiproProtocolFacade] = LiproProtocolFacade,
        auth_manager_factory: type[LiproAuthManager] = LiproAuthManager,
        capability_registry: CapabilityRegistry | None = None,
    ) -> None:
        self._session = session
        self._client_factory = client_factory
        self._auth_manager_factory = auth_manager_factory
        self._capability_registry = capability_registry or CapabilityRegistry()

    async def async_collect(self, seed: AuthBootstrapSeed) -> HeadlessConsumerProof:
        """Authenticate and materialize canonical devices through formal truth."""
        boot_context: HeadlessBootContext = build_headless_boot_context(
            seed,
            self._session,
            client_factory=self._client_factory,
            auth_manager_factory=self._auth_manager_factory,
        )
        auth_session = await self._async_authenticate(boot_context, seed)

        device_rows = _require_device_rows(await boot_context.protocol.get_devices())
        devices = tuple(LiproDevice.from_api_data(row) for row in device_rows)
        device_ids = [device.serial for device in devices]
        status_map = _build_properties_map(
            await boot_context.protocol.query_device_status(device_ids),
            id_key='deviceId',
        )
        group_ids = [device.serial for device in devices if device.is_group]
        group_status_map = _build_properties_map(
            await boot_context.protocol.query_mesh_group_status(group_ids)
            if group_ids
            else [],
            id_key='groupId',
        )

        for device in devices:
            device_properties = status_map.get(device.serial)
            if device_properties is not None:
                device.update_properties(device_properties)
            if device.is_group:
                group_properties = group_status_map.get(device.serial)
                if group_properties is not None:
                    device.update_properties(group_properties)

        capability_snapshots = {
            device.serial: self._capability_registry.from_device(device)
            for device in devices
        }
        return HeadlessConsumerProof(
            auth_session=auth_session,
            devices=devices,
            capability_snapshots=capability_snapshots,
        )

    @staticmethod
    async def _async_authenticate(
        boot_context: HeadlessBootContext,
        seed: AuthBootstrapSeed,
    ) -> AuthSessionSnapshot:
        if seed.password_hash:
            return await boot_context.async_login_with_password_hash()
        return await boot_context.async_ensure_authenticated()
