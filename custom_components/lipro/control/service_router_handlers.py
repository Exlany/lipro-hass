"""Private family index wired by ``control.service_router``."""

from __future__ import annotations

from .service_router_command_handlers import async_handle_send_command
from .service_router_diagnostics_handlers import (
    async_handle_fetch_body_sensor_history,
    async_handle_fetch_door_sensor_history,
    async_handle_get_city,
    async_handle_get_developer_report,
    async_handle_query_command_result,
    async_handle_query_user_cloud,
    async_handle_submit_developer_feedback,
)
from .service_router_maintenance_handlers import async_handle_refresh_devices
from .service_router_schedule_handlers import (
    async_handle_add_schedule,
    async_handle_delete_schedules,
    async_handle_get_schedules,
)
from .service_router_share_handlers import (
    async_handle_get_anonymous_share_report,
    async_handle_submit_anonymous_share,
)

__all__ = [
    'async_handle_add_schedule',
    'async_handle_delete_schedules',
    'async_handle_fetch_body_sensor_history',
    'async_handle_fetch_door_sensor_history',
    'async_handle_get_anonymous_share_report',
    'async_handle_get_city',
    'async_handle_get_developer_report',
    'async_handle_get_schedules',
    'async_handle_query_command_result',
    'async_handle_query_user_cloud',
    'async_handle_refresh_devices',
    'async_handle_send_command',
    'async_handle_submit_anonymous_share',
    'async_handle_submit_developer_feedback',
]
