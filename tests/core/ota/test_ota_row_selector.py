"""Tests for OTA row selector helpers."""

from __future__ import annotations

from custom_components.lipro.core.ota.row_selector import (
    arbitrate_rows,
    build_device_fingerprint,
    row_targets_other_device,
    score_row,
    select_best_row,
    select_best_row_for_device,
)


def _selector_kwargs() -> dict[str, str]:
    return {
        "serial": "03ab5ccd7c333333",
        "device_type": "ff000001",
        "iot_name": "21p3",
        "product_id": "11",
        "physical_model": "lipro-light-21p3",
    }


def test_select_best_row_returns_none_for_empty_rows() -> None:
    assert select_best_row([], **_selector_kwargs()) is None


def test_select_best_row_skips_non_dict_rows() -> None:
    rows: list[object] = [
        "invalid",
        {"deviceType": "ff000001", "latestVersion": "7.10.8"},
        {
            "deviceId": "03ab5ccd7c333333",
            "deviceType": "ff000001",
            "bleName": "21P3",
            "latestVersion": "7.10.9",
        },
    ]

    best = select_best_row(rows, **_selector_kwargs())

    assert best is rows[2]


def test_score_row_accumulates_all_expected_weights() -> None:
    score = score_row(
        {
            "deviceId": "03ab5ccd7c333333",
            "deviceType": "ff000001",
            "bleName": "21P3",
            "iotName": "21P3",
            "productId": "11",
            "physicalModel": "LIPRO-LIGHT-21P3",
            "latestVersion": "7.10.9",
        },
        **_selector_kwargs(),
    )

    assert score == 27


def test_row_targets_other_device_returns_false_for_non_dict_row() -> None:
    assert row_targets_other_device(None, expected_serial="03ab5ccd7c333333") is False


def test_row_targets_other_device_ignores_blank_serial_and_checks_next_key() -> None:
    row = {"deviceId": "   ", "serial": "03ab5ccd7c999999"}

    assert row_targets_other_device(row, expected_serial="03ab5ccd7c333333") is True


def test_arbitrate_rows_requests_direct_query_when_cached_row_targets_other_device() -> (
    None
):
    """Serial-targeted cached rows should request one direct refresh before use."""
    fingerprint = build_device_fingerprint(
        serial="03ab5ccd7c111111",
        device_type="ff000001",
        iot_name="21P3",
        product_id=11,
        physical_model="light",
    )

    arbitration = arbitrate_rows(
        [{"deviceId": "03ab5ccd7c222222", "latestVersion": "1.1.0"}],
        fingerprint=fingerprint,
        from_cache=True,
    )

    assert arbitration.selected_row == {
        "deviceId": "03ab5ccd7c222222",
        "latestVersion": "1.1.0",
    }
    assert arbitration.should_retry_without_cache is True


def test_select_best_row_for_device_prefers_higher_score() -> None:
    fingerprint = build_device_fingerprint(
        serial="03ab5ccd7c333333",
        device_type="ff000001",
        iot_name="21P3",
        product_id=11,
        physical_model="lipro-light-21p3",
    )
    low_score = {
        "deviceType": "ff000001",
        "latestVersion": "7.10.8",
    }
    high_score = {
        "deviceId": "03ab5ccd7c333333",
        "deviceType": "ff000001",
        "bleName": "21P3",
        "iotName": "21P3",
        "latestVersion": "7.10.9",
    }

    assert (
        select_best_row_for_device(
            [low_score, high_score],
            fingerprint=fingerprint,
        )
        is high_score
    )
