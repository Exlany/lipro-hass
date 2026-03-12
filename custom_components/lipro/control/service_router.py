"""Formal control-plane router for HA service callbacks."""

from __future__ import annotations

from ..services.wiring import (
    _async_handle_add_schedule,
    _async_handle_delete_schedules,
    _async_handle_fetch_body_sensor_history,
    _async_handle_fetch_door_sensor_history,
    _async_handle_get_anonymous_share_report,
    _async_handle_get_city,
    _async_handle_get_developer_report,
    _async_handle_get_schedules,
    _async_handle_query_command_result,
    _async_handle_query_user_cloud,
    _async_handle_refresh_devices,
    _async_handle_send_command,
    _async_handle_submit_anonymous_share,
    _async_handle_submit_developer_feedback,
    _get_device_and_coordinator,
    _summarize_service_properties,
    async_get_clientsession,
    get_anonymous_share_manager,
)

async_handle_add_schedule = _async_handle_add_schedule
async_handle_delete_schedules = _async_handle_delete_schedules
async_handle_fetch_body_sensor_history = _async_handle_fetch_body_sensor_history
async_handle_fetch_door_sensor_history = _async_handle_fetch_door_sensor_history
async_handle_get_anonymous_share_report = _async_handle_get_anonymous_share_report
async_handle_get_city = _async_handle_get_city
async_handle_get_developer_report = _async_handle_get_developer_report
async_handle_get_schedules = _async_handle_get_schedules
async_handle_query_command_result = _async_handle_query_command_result
async_handle_query_user_cloud = _async_handle_query_user_cloud
async_handle_refresh_devices = _async_handle_refresh_devices
async_handle_send_command = _async_handle_send_command
async_handle_submit_anonymous_share = _async_handle_submit_anonymous_share
async_handle_submit_developer_feedback = _async_handle_submit_developer_feedback
get_device_and_coordinator = _get_device_and_coordinator
summarize_service_properties = _summarize_service_properties

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
    "get_device_and_coordinator",
    "summarize_service_properties",
]
