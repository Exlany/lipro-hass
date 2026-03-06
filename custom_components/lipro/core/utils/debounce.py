"""Debounce helper for Lipro integration."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Final

from .log_safety import safe_error_placeholder

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

_LOGGER = logging.getLogger(__name__)

# Default debounce delay in seconds
DEFAULT_DEBOUNCE_DELAY: Final = 0.5


class Debouncer:
    """Debouncer for rate-limiting API calls.

    When a function is called multiple times in quick succession (e.g., slider
    dragging), only the last call will be executed after the delay period.
    """

    def __init__(
        self,
        delay: float = DEFAULT_DEBOUNCE_DELAY,
        on_error: Callable[[Exception], None] | None = None,
    ) -> None:
        """Initialize the debouncer.

        Args:
            delay: Delay in seconds before executing the function.
            on_error: Optional callback invoked when debounced task fails.

        """
        self._delay = delay
        self._on_error = on_error
        self._timer: asyncio.TimerHandle | None = None
        self._pending_task: asyncio.Task[None] | None = None
        self._lock = asyncio.Lock()
        self._last_error: Exception | None = None

    @property
    def last_error(self) -> Exception | None:
        """Return the last execution exception, if any."""
        return self._last_error

    async def async_call(
        self,
        func: Callable[..., Coroutine[Any, Any, Any]],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Schedule a debounced function call.

        If called again before the delay expires, the previous call is cancelled
        and a new timer is started with the new arguments.

        Args:
            func: Async function to call.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        """
        async with self._lock:
            self._cancel_timer()
            self._cancel_pending_task()

            # Schedule new execution
            loop = asyncio.get_running_loop()
            self._timer = loop.call_later(
                self._delay,
                self._execute,
                func,
                args,
                kwargs,
            )

    def _execute(
        self,
        func: Callable[..., Coroutine[Any, Any, Any]],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> None:
        """Execute the debounced function.

        Args:
            func: Async function to call.
            args: Positional arguments.
            kwargs: Keyword arguments.

        """
        self._timer = None
        self._pending_task = asyncio.create_task(self._run_func(func, args, kwargs))

    async def _run_func(
        self,
        func: Callable[..., Coroutine[Any, Any, Any]],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> None:
        """Run the function and handle exceptions.

        Args:
            func: Async function to call.
            args: Positional arguments.
            kwargs: Keyword arguments.

        """
        try:
            await func(*args, **kwargs)
            self._last_error = None
        except asyncio.CancelledError:
            _LOGGER.debug("Debounced call cancelled")
        except Exception as err:
            self._last_error = err
            _LOGGER.error(
                "Error in debounced call (%s)",
                safe_error_placeholder(err),
                exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
            )
            if self._on_error is not None:
                try:
                    self._on_error(err)
                except Exception as callback_err:
                    _LOGGER.error(
                        "Debounce error callback failed (%s)",
                        safe_error_placeholder(callback_err),
                        exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
                    )

    def _cancel_timer(self) -> None:
        """Cancel pending timer handle if present."""
        if self._timer is None:
            return
        self._timer.cancel()
        self._timer = None

    def _cancel_pending_task(self) -> None:
        """Cancel pending execution task if still running."""
        if self._pending_task is None:
            return
        if not self._pending_task.done():
            self._pending_task.cancel()
        self._pending_task = None

    def cancel(self) -> None:
        """Cancel any pending debounced call."""
        self._cancel_timer()
        self._cancel_pending_task()
