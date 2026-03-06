from __future__ import annotations

import pytest

from custom_components.lipro.core.coordinator.runtime.room_sync_runtime import (
    normalize_room_name,
    resolve_room_area_target_name,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, None),
        ("", None),
        ("   ", None),
        ("主卧", "主卧"),
        (" 主卧 ", "主卧"),
    ],
)
def test_normalize_room_name(raw, expected):
    assert normalize_room_name(raw) == expected


def test_resolve_room_area_target_name_force_sync():
    update_area, target = resolve_room_area_target_name(
        room_area_sync_force=True,
        old_room_name="主卧",
        new_room_name="儿童房",
        current_area_id="custom-area",
        current_area_name="手动区域",
    )
    assert update_area is True
    assert target == "儿童房"


def test_resolve_room_area_target_name_assign_when_no_current_area():
    update_area, target = resolve_room_area_target_name(
        room_area_sync_force=False,
        old_room_name="主卧",
        new_room_name="儿童房",
        current_area_id=None,
        current_area_name=None,
    )
    assert update_area is True
    assert target == "儿童房"


def test_resolve_room_area_target_name_skip_when_no_current_area_and_no_new_room():
    update_area, target = resolve_room_area_target_name(
        room_area_sync_force=False,
        old_room_name="主卧",
        new_room_name=None,
        current_area_id=None,
        current_area_name=None,
    )
    assert update_area is False
    assert target is None


def test_resolve_room_area_target_name_preserves_user_area():
    update_area, target = resolve_room_area_target_name(
        room_area_sync_force=False,
        old_room_name="主卧",
        new_room_name="儿童房",
        current_area_id="custom-area",
        current_area_name="手动区域",
    )
    assert update_area is False
    assert target is None


def test_resolve_room_area_target_name_updates_when_cloud_managed():
    update_area, target = resolve_room_area_target_name(
        room_area_sync_force=False,
        old_room_name="主卧",
        new_room_name="主卧新",
        current_area_id="area-old",
        current_area_name="主卧",
    )
    assert update_area is True
    assert target == "主卧新"


def test_resolve_room_area_target_name_clears_when_room_removed_and_cloud_managed():
    update_area, target = resolve_room_area_target_name(
        room_area_sync_force=False,
        old_room_name="书房",
        new_room_name=None,
        current_area_id="area-old",
        current_area_name="书房",
    )
    assert update_area is True
    assert target is None
