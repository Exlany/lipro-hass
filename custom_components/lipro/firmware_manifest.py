"""Firmware support manifest loading for the update platform."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import functools
import logging
from pathlib import Path

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util

from .core.ota.manifest import (
    load_verified_firmware_manifest_file,
    parse_verified_firmware_manifest_payload,
)

_LOGGER = logging.getLogger(__name__)

_TIME_MIN_UTC = datetime.min.replace(tzinfo=UTC)
_FIRMWARE_SUPPORT_MANIFEST = "firmware_support_manifest.json"

_REMOTE_MANIFEST_CACHE_TTL = timedelta(minutes=30)
_REMOTE_MANIFEST_TIMEOUT_SECONDS = 5
_REMOTE_FIRMWARE_SUPPORT_URLS = (
    "https://lipro-share.lany.me/api/firmware-support",
    "https://lipro-share.lany.me/firmware_support_manifest.json",
)

type _RemoteManifestData = tuple[frozenset[str], dict[str, frozenset[str]]]


@dataclass(slots=True)
class _RemoteManifestState:
    """Remote firmware manifest cache state."""

    time: datetime
    data: _RemoteManifestData


_REMOTE_MANIFEST_STATE = _RemoteManifestState(
    time=_TIME_MIN_UTC,
    data=(frozenset(), {}),
)
_REMOTE_MANIFEST_LOCK = asyncio.Lock()


@functools.lru_cache(maxsize=1)
def load_verified_firmware_manifest() -> _RemoteManifestData:
    """Load optional local firmware certification manifest."""
    manifest_path = Path(__file__).with_name(_FIRMWARE_SUPPORT_MANIFEST)
    return load_verified_firmware_manifest_file(
        manifest_path,
        on_error=lambda path, err: _LOGGER.debug(
            "Failed to load firmware support manifest %s: %s",
            path,
            err,
        ),
    )


async def async_load_remote_firmware_manifest(
    hass: HomeAssistant,
) -> _RemoteManifestData:
    """Load firmware certification manifest from remote service with cache."""
    now = dt_util.utcnow()
    cached_time = _REMOTE_MANIFEST_STATE.time
    cached_data = _REMOTE_MANIFEST_STATE.data
    if now - cached_time < _REMOTE_MANIFEST_CACHE_TTL:
        return cached_data

    async with _REMOTE_MANIFEST_LOCK:
        now = dt_util.utcnow()
        cached_time = _REMOTE_MANIFEST_STATE.time
        cached_data = _REMOTE_MANIFEST_STATE.data
        if now - cached_time < _REMOTE_MANIFEST_CACHE_TTL:
            return cached_data

        session = async_get_clientsession(hass)
        timeout = aiohttp.ClientTimeout(total=_REMOTE_MANIFEST_TIMEOUT_SECONDS)
        for url in _REMOTE_FIRMWARE_SUPPORT_URLS:
            try:
                async with session.get(url, timeout=timeout) as response:
                    if response.status != 200:
                        continue
                    payload = await response.json(content_type=None)
            except (aiohttp.ClientError, TimeoutError, ValueError) as err:
                _LOGGER.debug(
                    "Remote firmware manifest fetch failed from %s: %s", url, err
                )
                continue

            versions, versions_by_type = parse_verified_firmware_manifest_payload(
                payload
            )
            if versions or versions_by_type:
                _REMOTE_MANIFEST_STATE.data = (versions, versions_by_type)
                _REMOTE_MANIFEST_STATE.time = now
                return versions, versions_by_type

        _REMOTE_MANIFEST_STATE.time = now
        return cached_data
