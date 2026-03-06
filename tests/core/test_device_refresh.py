"""Tests for device refresh helpers."""

from __future__ import annotations

from unittest.mock import patch

from custom_components.lipro.const.categories import DeviceCategory
from custom_components.lipro.const.config import (
    CONF_DEVICE_FILTER_DID_LIST,
    CONF_DEVICE_FILTER_DID_MODE,
    CONF_DEVICE_FILTER_HOME_LIST,
    CONF_DEVICE_FILTER_HOME_MODE,
    CONF_DEVICE_FILTER_MODEL_LIST,
    CONF_DEVICE_FILTER_MODEL_MODE,
    CONF_DEVICE_FILTER_SSID_LIST,
    CONF_DEVICE_FILTER_SSID_MODE,
    DEVICE_FILTER_MODE_EXCLUDE,
    DEVICE_FILTER_MODE_INCLUDE,
    DEVICE_FILTER_MODE_OFF,
    MAX_DEVICE_FILTER_LIST_CHARS,
    MAX_DEVICE_FILTER_LIST_ITEMS,
)
from custom_components.lipro.core.coordinator.device_list_snapshot import (
    build_device_filter_config,
    build_fetched_device_snapshot,
    has_active_device_filter,
    is_device_included_by_filter,
    plan_stale_device_reconciliation,
    register_lookup_id,
)
from custom_components.lipro.core.device import LiproDevice


def _make_device(
    *,
    serial: str,
    is_group: bool = False,
    iot_name: str = "lipro_led",
    physical_model: str = "light",
) -> LiproDevice:
    return LiproDevice(
        device_number=1,
        serial=serial,
        name="Refresh Test Device",
        device_type=1,
        iot_name=iot_name,
        physical_model=physical_model,
        is_group=is_group,
    )


class _GatewayCategoryErrorDevice:
    serial = "03ab000000000010"
    name = "GatewayError"
    is_group = False
    has_valid_iot_id = True
    iot_device_id = serial

    @property
    def is_gateway(self) -> bool:
        raise ValueError("bad gateway payload")

    @property
    def category(self) -> DeviceCategory:
        return DeviceCategory.LIGHT


class _OutletCategoryErrorDevice:
    serial = "03ab000000000020"
    name = "CategoryError"
    is_group = False
    has_valid_iot_id = True
    iot_device_id = serial

    @property
    def is_gateway(self) -> bool:
        return False

    @property
    def category(self) -> DeviceCategory:
        raise ValueError("bad category payload")


class _InvalidIotIdDevice:
    serial = "INVALID_SERIAL"
    name = "InvalidIotId"
    is_group = False
    has_valid_iot_id = False
    iot_device_id = "invalid_iot_id"

    @property
    def is_gateway(self) -> bool:
        return False

    @property
    def category(self) -> DeviceCategory:
        return DeviceCategory.OUTLET


def test_register_lookup_id_ignores_non_string_and_blank() -> None:
    device = _make_device(serial="03ab000000000001")
    mapping: dict[str, LiproDevice] = {}

    register_lookup_id(mapping, 1, device)
    register_lookup_id(mapping, "   ", device)

    assert mapping == {}


def test_build_fetched_device_snapshot_handles_malformed_rows() -> None:
    group = _make_device(serial="mesh_group_10001", is_group=True)
    outlet = _make_device(
        serial="03ab000000000030",
        iot_name="lipro_outlet",
        physical_model="outlet",
    )
    invalid_serial = _make_device(serial="  ")

    with patch(
        "custom_components.lipro.core.coordinator.device_list_snapshot.LiproDevice.from_api_data"
    ) as from_api:
        from_api.side_effect = [
            TypeError("malformed row"),
            invalid_serial,
            _GatewayCategoryErrorDevice(),
            group,
            _OutletCategoryErrorDevice(),
            outlet,
        ]
        snapshot = build_fetched_device_snapshot([{}, {}, {}, {}, {}, {}])

    assert set(snapshot.devices) == {
        "mesh_group_10001",
        "03ab000000000020",
        "03ab000000000030",
    }
    assert snapshot.group_ids == ["mesh_group_10001"]
    assert snapshot.iot_ids == ["03ab000000000020", "03ab000000000030"]
    assert snapshot.outlet_ids == ["03ab000000000030"]


def test_plan_stale_device_reconciliation_tracks_and_removes() -> None:
    plan = plan_stale_device_reconciliation(
        previous_serials={"dev_a", "dev_b"},
        current_serials={"dev_a"},
        missing_cycles={"dev_b": 2, "dev_c": 1, "dev_a": 5},
        remove_threshold=3,
    )

    assert plan.removable_serials == {"dev_b"}
    assert plan.missing_cycles == {"dev_b": 3, "dev_c": 2}


def test_build_fetched_device_snapshot_tracks_cloud_serials_before_filter() -> None:
    valid = _make_device(serial="03ab000000000001")
    group = _make_device(serial="mesh_group_10001", is_group=True)
    gateway_like = _GatewayCategoryErrorDevice()
    invalid_serial = _make_device(serial=" ")

    with patch(
        "custom_components.lipro.core.coordinator.device_list_snapshot.LiproDevice.from_api_data"
    ) as from_api:
        from_api.side_effect = [valid, group, gateway_like, invalid_serial]
        snapshot = build_fetched_device_snapshot(
            [{}, {}, {}, {}],
            device_filter=lambda row: row != {},
        )

    assert snapshot.cloud_serials == {"03ab000000000001", "mesh_group_10001"}


def test_build_fetched_device_snapshot_skips_invalid_iot_ids_for_polling_lists() -> (
    None
):
    with patch(
        "custom_components.lipro.core.coordinator.device_list_snapshot.LiproDevice.from_api_data"
    ) as from_api:
        from_api.return_value = _InvalidIotIdDevice()
        snapshot = build_fetched_device_snapshot([{}])

    assert "INVALID_SERIAL" in snapshot.devices
    assert snapshot.iot_ids == []
    assert snapshot.outlet_ids == []


def test_build_device_filter_config_normalizes_modes_and_lists() -> None:
    config = build_device_filter_config(
        {
            CONF_DEVICE_FILTER_HOME_MODE: "INCLUDE",
            CONF_DEVICE_FILTER_HOME_LIST: "  Home A,home_b \n",
            CONF_DEVICE_FILTER_MODEL_MODE: "invalid",
            CONF_DEVICE_FILTER_MODEL_LIST: ["fanLight", ""],
            CONF_DEVICE_FILTER_SSID_MODE: DEVICE_FILTER_MODE_EXCLUDE,
            CONF_DEVICE_FILTER_SSID_LIST: {"Guest", "Office"},
            CONF_DEVICE_FILTER_DID_MODE: DEVICE_FILTER_MODE_OFF,
            CONF_DEVICE_FILTER_DID_LIST: "",
        }
    )

    assert has_active_device_filter(config) is True
    assert config.home.mode == DEVICE_FILTER_MODE_INCLUDE
    assert config.home.values == {"home a", "home_b"}
    assert config.model.mode == DEVICE_FILTER_MODE_OFF
    assert config.model.values == {"fanlight"}
    assert config.ssid.mode == DEVICE_FILTER_MODE_EXCLUDE
    assert config.ssid.values == {"guest", "office"}
    assert config.did.mode == DEVICE_FILTER_MODE_OFF
    assert config.did.values == set()


def test_build_device_filter_config_caps_filter_list_items_for_iterables() -> None:
    """Filter list parsing should enforce item limit for iterable inputs."""
    filter_value = [f"home_{idx}" for idx in range(MAX_DEVICE_FILTER_LIST_ITEMS + 50)]
    config = build_device_filter_config(
        {
            CONF_DEVICE_FILTER_HOME_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_HOME_LIST: filter_value,
        }
    )

    assert len(config.home.values) == MAX_DEVICE_FILTER_LIST_ITEMS


def test_is_device_included_by_filter_matches_home_model_ssid_and_did() -> None:
    config = build_device_filter_config(
        {
            CONF_DEVICE_FILTER_HOME_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_HOME_LIST: "Main Home",
            CONF_DEVICE_FILTER_MODEL_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_MODEL_LIST: "fanLight",
            CONF_DEVICE_FILTER_SSID_MODE: DEVICE_FILTER_MODE_EXCLUDE,
            CONF_DEVICE_FILTER_SSID_LIST: "Guest",
            CONF_DEVICE_FILTER_DID_MODE: DEVICE_FILTER_MODE_EXCLUDE,
            CONF_DEVICE_FILTER_DID_LIST: "blocked-did",
        }
    )

    assert (
        is_device_included_by_filter(
            {
                "homeName": "main home",
                "physicalModel": "FanLight",
                "serial": "03ab5ccd7c000001",
                "deviceInfo": '{"wifi_ssid":"MyWiFi"}',
            },
            config,
        )
        is True
    )
    assert (
        is_device_included_by_filter(
            {
                "homeName": "main home",
                "physicalModel": "fanLight",
                "serial": "blocked-did",
                "deviceInfo": '{"wifi_ssid":"MyWiFi"}',
            },
            config,
        )
        is False
    )
    assert (
        is_device_included_by_filter(
            {
                "homeName": "main home",
                "physicalModel": "fanLight",
                "serial": "03ab5ccd7c000001",
                "properties": [{"key": "wifi_ssid", "value": "guest"}],
            },
            config,
        )
        is False
    )


def test_is_device_included_by_filter_include_mode_empty_list_excludes_all() -> None:
    config = build_device_filter_config(
        {
            CONF_DEVICE_FILTER_DID_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_DID_LIST: "",
        }
    )

    assert (
        is_device_included_by_filter(
            {
                "serial": "03ab5ccd7c000001",
            },
            config,
        )
        is False
    )


def test_build_device_filter_config_caps_filter_item_count() -> None:
    items = [f"value{i:03d}" for i in range(MAX_DEVICE_FILTER_LIST_ITEMS + 25)]
    config = build_device_filter_config(
        {
            CONF_DEVICE_FILTER_HOME_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_HOME_LIST: ",".join(items),
        }
    )

    assert len(config.home.values) == MAX_DEVICE_FILTER_LIST_ITEMS
    assert items[0] in config.home.values
    assert items[MAX_DEVICE_FILTER_LIST_ITEMS - 1] in config.home.values
    assert items[MAX_DEVICE_FILTER_LIST_ITEMS] not in config.home.values


def test_build_device_filter_config_truncates_overlong_filter_text() -> None:
    long_value = "A" * (MAX_DEVICE_FILTER_LIST_CHARS + 10)
    config = build_device_filter_config(
        {
            CONF_DEVICE_FILTER_HOME_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_HOME_LIST: long_value,
        }
    )

    assert config.home.values == {"a" * MAX_DEVICE_FILTER_LIST_CHARS}


def test_is_device_included_by_filter_skips_ssid_parsing_when_ssid_rule_off() -> None:
    config = build_device_filter_config(
        {
            CONF_DEVICE_FILTER_DID_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_DID_LIST: "03ab5ccd7c000001",
            CONF_DEVICE_FILTER_SSID_MODE: DEVICE_FILTER_MODE_OFF,
            CONF_DEVICE_FILTER_SSID_LIST: "guest",
        }
    )

    with patch(
        "custom_components.lipro.core.coordinator.device_list_snapshot.json.loads"
    ) as json_loads:
        assert (
            is_device_included_by_filter(
                {
                    "serial": "03ab5ccd7c000001",
                    "deviceInfo": '{"wifi_ssid":"MyWiFi"}',
                },
                config,
            )
            is True
        )
        json_loads.assert_not_called()


def test_build_fetched_device_snapshot_applies_device_filter_predicate() -> None:
    def include_only_second(row: dict[str, str]) -> bool:
        return row.get("serial") == "03ab000000000002"

    with patch(
        "custom_components.lipro.core.coordinator.device_list_snapshot.LiproDevice.from_api_data"
    ) as from_api:
        from_api.side_effect = lambda row: _make_device(serial=row["serial"])
        snapshot = build_fetched_device_snapshot(
            [
                {"serial": "03ab000000000001"},
                {"serial": "03ab000000000002"},
            ],
            device_filter=include_only_second,
        )

    assert set(snapshot.devices) == {"03ab000000000002"}
