"""Connection/error lifecycle helpers extracted from the MQTT transport."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import logging
import random

import aiomqtt

from ...const.api import (
    MQTT_RECONNECT_JITTER,
    MQTT_RECONNECT_MAX_DELAY,
    MQTT_RECONNECT_MIN_DELAY,
)

_LOGGER = logging.getLogger(__package__ or __name__)
_CALLBACK_BOUNDARY_EXCEPTIONS = (RuntimeError, ValueError, LookupError)
_RECOVERABLE_LOOP_EXCEPTIONS = (RuntimeError, LookupError)


@dataclass(slots=True)
class MqttConnectionManager:
    """Manage MQTT callback/error handling and reconnect loop behavior."""

    on_connect: Callable[[], None] | None = None
    on_disconnect: Callable[[], None] | None = None
    on_error: Callable[[Exception], None] | None = None

    def invoke_callback(
        self,
        callback: Callable[..., None] | None,
        callback_name: str,
        set_last_error: Callable[[Exception], None],
        *args: object,
    ) -> bool:
        """Invoke one optional callback and persist failures consistently."""
        if callback is None:
            return True
        try:
            callback(*args)
        except _CALLBACK_BOUNDARY_EXCEPTIONS as err:
            set_last_error(err)
            _LOGGER.exception(
                "MQTT %s callback failed (%s)",
                callback_name,
                type(err).__name__,
            )
            return False
        return True

    def set_last_error(
        self,
        err: Exception,
        *,
        assign_last_error: Callable[[Exception | None], None],
    ) -> None:
        """Persist latest error and notify optional observer."""
        assign_last_error(err)
        if self.on_error is None:
            return
        try:
            self.on_error(err)
        except _CALLBACK_BOUNDARY_EXCEPTIONS as callback_err:
            _LOGGER.exception(
                "MQTT error callback failed (%s)",
                type(callback_err).__name__,
            )

    @staticmethod
    def clear_last_error(*, assign_last_error: Callable[[Exception | None], None]) -> None:
        """Clear latest error state after successful processing."""
        assign_last_error(None)

    def handle_disconnect(
        self,
        reason: str,
        *,
        assign_connected: Callable[[bool], None],
        clear_client: Callable[[], None],
        set_last_error: Callable[[Exception], None] | None = None,
    ) -> None:
        """Handle disconnection from broker."""
        assign_connected(False)
        clear_client()
        _LOGGER.warning("MQTT disconnected: %s", reason)
        self.invoke_callback(
            self.on_disconnect,
            "on_disconnect",
            set_last_error or (lambda _err: None),
        )

    @staticmethod
    def consume_task_exception(task: asyncio.Task[None]) -> Exception | None:
        """Consume task exceptions to avoid unhandled-task warnings."""
        if task.cancelled():
            return None
        err = task.exception()
        if isinstance(err, Exception):
            _LOGGER.debug(
                "MQTT background task failed (%s)",
                type(err).__name__,
            )
            return err
        return None

    def finalize_connection_task(
        self,
        task: asyncio.Task[None],
        *,
        clear_task_ref: Callable[[asyncio.Task[None]], None],
        set_last_error: Callable[[Exception], None],
    ) -> None:
        """Consume one background connection task result."""
        clear_task_ref(task)
        err = self.consume_task_exception(task)
        if err is not None:
            set_last_error(err)

    async def run_connection_loop(
        self,
        *,
        is_running: Callable[[], bool],
        connect_and_listen: Callable[[], Awaitable[None]],
        set_last_error: Callable[[Exception], None],
        handle_disconnect: Callable[[str], None],
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        jitter_source: Callable[[float, float], float] = random.uniform,
    ) -> None:
        """Run the reconnect loop with bounded backoff and jitter."""
        reconnect_delay = MQTT_RECONNECT_MIN_DELAY
        while is_running():
            connect_succeeded = False
            try:
                await connect_and_listen()
                connect_succeeded = True
            except aiomqtt.MqttError as err:
                set_last_error(err)
                handle_disconnect(f"MQTT error: {err}")
            except asyncio.CancelledError:
                break
            except OSError as err:
                set_last_error(err)
                handle_disconnect(f"Connection error: {err}")
            except ValueError as err:
                set_last_error(err)
                handle_disconnect(f"MQTT value error: {err}")
            except _RECOVERABLE_LOOP_EXCEPTIONS as err:
                _LOGGER.exception(
                    "Unexpected MQTT loop error (%s)",
                    type(err).__name__,
                )
                set_last_error(err)
                handle_disconnect(
                    f"Unexpected MQTT loop error ({type(err).__name__})"
                )

            if connect_succeeded:
                reconnect_delay = MQTT_RECONNECT_MIN_DELAY

            if is_running():
                jitter = 1 + jitter_source(
                    -MQTT_RECONNECT_JITTER,
                    MQTT_RECONNECT_JITTER,
                )
                wait_time = reconnect_delay * jitter
                _LOGGER.info("Reconnecting in %.1fs...", wait_time)
                await sleep(wait_time)
                if connect_succeeded:
                    reconnect_delay = MQTT_RECONNECT_MIN_DELAY
                else:
                    reconnect_delay = min(
                        reconnect_delay * 2,
                        MQTT_RECONNECT_MAX_DELAY,
                    )
