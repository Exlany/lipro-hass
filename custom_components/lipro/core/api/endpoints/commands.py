"""Command endpoints and collaborators for the REST facade."""

from __future__ import annotations

from typing import Any

from ....const.api import PATH_SEND_COMMAND, PATH_SEND_GROUP_COMMAND
from ..client_base import _ClientBase
from ..command_api_service import (
    send_command_to_target as send_command_to_target_service,
)
from .payloads import _EndpointAdapter


class _ClientCommandEndpointsMixin(_ClientBase):
    """Legacy command endpoint mixin retained for focused helper tests."""

    async def send_command(
        self,
        device_id: str,
        command: str,
        device_type: int | str,
        properties: list[dict[str, str]] | None = None,
        iot_name: str = "",
    ) -> dict[str, Any]:
        """Send a command to a device."""
        return await send_command_to_target_service(
            path=PATH_SEND_COMMAND,
            target_id=device_id,
            command=command,
            device_type=device_type,
            properties=properties,
            iot_name=iot_name,
            to_device_type_hex=self._to_device_type_hex,
            iot_request_with_busy_retry=self._iot_request_with_busy_retry,
        )

    async def send_group_command(
        self,
        group_id: str,
        command: str,
        device_type: int | str,
        properties: list[dict[str, str]] | None = None,
        iot_name: str = "",
    ) -> dict[str, Any]:
        """Send a command to a mesh group."""
        return await send_command_to_target_service(
            path=PATH_SEND_GROUP_COMMAND,
            target_id=group_id,
            command=command,
            device_type=device_type,
            properties=properties,
            iot_name=iot_name,
            group_id=group_id,
            to_device_type_hex=self._to_device_type_hex,
            iot_request_with_busy_retry=self._iot_request_with_busy_retry,
        )


class CommandEndpoints(_EndpointAdapter, _ClientCommandEndpointsMixin):
    """Explicit command endpoint collaborator for ``LiproRestFacade``."""

    EXPORTED_METHODS = (
        "send_command",
        "send_group_command",
    )


__all__ = ["CommandEndpoints", "_ClientCommandEndpointsMixin"]
