"""Tests for anonymous share storage helpers."""

from __future__ import annotations

import json
import logging
from typing import cast
from unittest.mock import MagicMock

from custom_components.lipro.core.anonymous_share.storage import (
    load_reported_device_keys,
    save_reported_device_keys,
)


def _make_logger() -> MagicMock:
    return MagicMock(spec=logging.Logger)


def test_load_reported_device_keys_returns_false_when_cache_missing(tmp_path):
    logger = _make_logger()

    loaded, keys = load_reported_device_keys(
        str(tmp_path),
        logger=cast(logging.Logger, logger),
    )

    assert loaded is False
    assert keys == set()
    logger.warning.assert_not_called()


def test_load_reported_device_keys_returns_false_when_devices_not_list(tmp_path):
    logger = _make_logger()
    cache_file = tmp_path / ".lipro_reported_devices.json"
    cache_file.write_text(json.dumps({"devices": "lipro_led"}), encoding="utf-8")

    loaded, keys = load_reported_device_keys(
        str(tmp_path),
        logger=cast(logging.Logger, logger),
    )

    assert loaded is False
    assert keys == set()
    logger.warning.assert_not_called()


def test_scoped_cache_keys_are_isolated_on_disk(tmp_path) -> None:
    logger = _make_logger()

    save_reported_device_keys(
        str(tmp_path),
        {"entry_one_light"},
        logger=cast(logging.Logger, logger),
        cache_key="entry-1",
    )
    save_reported_device_keys(
        str(tmp_path),
        {"entry_two_switch"},
        logger=cast(logging.Logger, logger),
        cache_key="entry-2",
    )

    loaded_one, keys_one = load_reported_device_keys(
        str(tmp_path),
        logger=cast(logging.Logger, logger),
        cache_key="entry-1",
    )
    loaded_two, keys_two = load_reported_device_keys(
        str(tmp_path),
        logger=cast(logging.Logger, logger),
        cache_key="entry-2",
    )

    assert loaded_one is True
    assert loaded_two is True
    assert keys_one == {"entry_one_light"}
    assert keys_two == {"entry_two_switch"}
    assert (tmp_path / ".lipro_reported_devices.entry-1.json").exists()
    assert (tmp_path / ".lipro_reported_devices.entry-2.json").exists()
