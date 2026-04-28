"""Request pacing helpers for the formal REST facade."""

from __future__ import annotations

import asyncio
import time

MONOTONIC = time.monotonic

__all__ = ["MONOTONIC", "asyncio", "time"]
