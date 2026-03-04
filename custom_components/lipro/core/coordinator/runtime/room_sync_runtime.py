"""Pure room/area sync helpers.

This module contains pure functions used to decide when to sync Lipro cloud
room changes into Home Assistant device registry area assignments.
"""

from __future__ import annotations


def normalize_room_name(room_name: str | None) -> str | None:
    """Normalize room names from cloud payloads to comparable values."""
    if not isinstance(room_name, str):
        return None
    normalized = room_name.strip()
    return normalized or None


def resolve_room_area_target_name(
    *,
    room_area_sync_force: bool,
    old_room_name: str | None,
    new_room_name: str | None,
    current_area_id: str | None,
    current_area_name: str | None,
) -> tuple[bool, str | None]:
    """Decide whether to update area_id and what area name to target.

    Returns:
        (update_area, target_area_name)

        - update_area=False: do not include area_id in registry update.
        - update_area=True and target_area_name is None: clear area_id.
        - update_area=True and target_area_name is not None: set area_id to the
          area matching target_area_name.
    """
    if room_area_sync_force:
        return True, new_room_name

    if current_area_id is None:
        if new_room_name is None:
            return False, None
        return True, new_room_name

    # Preserve user-customized areas unless current area matches the previous
    # cloud room name (cloud-managed mapping).
    if current_area_name == old_room_name:
        return True, new_room_name

    return False, None
