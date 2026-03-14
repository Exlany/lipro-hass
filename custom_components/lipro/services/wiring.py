"""Compatibility shell re-exporting the formal control-plane router."""

from __future__ import annotations

from ..control.service_router import (
    _get_device_and_coordinator,
    _summarize_service_properties,
    async_get_clientsession,
    async_handle_add_schedule,
    async_handle_delete_schedules,
    async_handle_fetch_body_sensor_history,
    async_handle_fetch_door_sensor_history,
    async_handle_get_anonymous_share_report,
    async_handle_get_city,
    async_handle_get_developer_report,
    async_handle_get_schedules,
    async_handle_query_command_result,
    async_handle_query_user_cloud,
    async_handle_refresh_devices,
    async_handle_send_command,
    async_handle_submit_anonymous_share,
    async_handle_submit_developer_feedback,
    get_anonymous_share_manager,
)

_async_handle_add_schedule = async_handle_add_schedule
_async_handle_delete_schedules = async_handle_delete_schedules
_async_handle_fetch_body_sensor_history = async_handle_fetch_body_sensor_history
_async_handle_fetch_door_sensor_history = async_handle_fetch_door_sensor_history
_async_handle_get_anonymous_share_report = async_handle_get_anonymous_share_report
_async_handle_get_city = async_handle_get_city
_async_handle_get_developer_report = async_handle_get_developer_report
_async_handle_get_schedules = async_handle_get_schedules
_async_handle_query_command_result = async_handle_query_command_result
_async_handle_query_user_cloud = async_handle_query_user_cloud
_async_handle_refresh_devices = async_handle_refresh_devices
_async_handle_send_command = async_handle_send_command
_async_handle_submit_anonymous_share = async_handle_submit_anonymous_share
_async_handle_submit_developer_feedback = async_handle_submit_developer_feedback

__all__ = [
    "_async_handle_add_schedule",
    "_async_handle_delete_schedules",
    "_async_handle_fetch_body_sensor_history",
    "_async_handle_fetch_door_sensor_history",
    "_async_handle_get_anonymous_share_report",
    "_async_handle_get_city",
    "_async_handle_get_developer_report",
    "_async_handle_get_schedules",
    "_async_handle_query_command_result",
    "_async_handle_query_user_cloud",
    "_async_handle_refresh_devices",
    "_async_handle_send_command",
    "_async_handle_submit_anonymous_share",
    "_async_handle_submit_developer_feedback",
    "_get_device_and_coordinator",
    "_summarize_service_properties",
    "async_get_clientsession",
    "async_handle_add_schedule",
    "async_handle_delete_schedules",
    "async_handle_fetch_body_sensor_history",
    "async_handle_fetch_door_sensor_history",
    "async_handle_get_anonymous_share_report",
    "async_handle_get_city",
    "async_handle_get_developer_report",
    "async_handle_get_schedules",
    "async_handle_query_command_result",
    "async_handle_query_user_cloud",
    "async_handle_refresh_devices",
    "async_handle_send_command",
    "async_handle_submit_anonymous_share",
    "async_handle_submit_developer_feedback",
    "get_anonymous_share_manager",
]
