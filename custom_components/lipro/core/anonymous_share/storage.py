"""Anonymous share storage helpers.

Currently this module stores the set of already-reported device keys so we can
deduplicate device records across restarts without blocking the event loop.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Final

_REPORTED_DEVICES_CACHE_NAME: Final[str] = ".lipro_reported_devices.json"


def load_reported_device_keys(
    storage_path: str,
    *,
    logger: logging.Logger,
) -> tuple[bool, set[str]]:
    """Load reported device keys from disk.

    Returns:
        (loaded, keys) where loaded indicates whether the cache file existed and
        could be read successfully.
    """
    cache_file = Path(storage_path) / _REPORTED_DEVICES_CACHE_NAME
    try:
        if not cache_file.exists():
            return False, set()

        data = json.loads(cache_file.read_text(encoding="utf-8"))
        raw_devices = data.get("devices", [])
        if not isinstance(raw_devices, list):
            return False, set()

        keys = {item for item in raw_devices if isinstance(item, str)}
        logger.debug(
            "Loaded %d reported device keys from cache",
            len(keys),
        )
        return True, keys
    except (OSError, json.JSONDecodeError, TypeError) as err:
        logger.warning("Failed to load reported devices cache: %s", err)
        return False, set()


def save_reported_device_keys(
    storage_path: str,
    keys: set[str],
    *,
    logger: logging.Logger,
) -> None:
    """Persist reported device keys to disk."""
    cache_file = Path(storage_path) / _REPORTED_DEVICES_CACHE_NAME
    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(
            json.dumps({"devices": sorted(keys)}, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError as err:
        logger.warning("Failed to save reported devices cache: %s", err)


__all__ = ["load_reported_device_keys", "save_reported_device_keys"]
