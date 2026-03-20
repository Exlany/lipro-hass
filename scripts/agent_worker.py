"""Retired compatibility stub kept only to fail fast with a migration hint."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)

_DEPRECATION_MESSAGE = (
    "scripts/agent_worker.py 已退役；当前仓库改用主代理主控 + 子代理按需派发，"
    "历史重构档案不再保留在仓库中。"
)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the retired worker entry point."""
    parser = argparse.ArgumentParser(description="Deprecated Lipro refactoring worker")
    parser.add_argument("--agent-id", default="", help="Deprecated worker identifier")
    parser.add_argument(
        "--task-file",
        type=Path,
        default=None,
        help="Deprecated task contract path",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path.cwd(),
        help="Repository root used for the compatibility message",
    )
    return parser


def main() -> int:
    """Print the deprecation notice and exit successfully."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = build_parser()
    args = parser.parse_args()
    LOGGER.error("%s", _DEPRECATION_MESSAGE)
    LOGGER.error("Use docs/README.md and CONTRIBUTING.md for the active tooling entrypoints: ./scripts/setup, ./scripts/develop, ./scripts/lint")
    LOGGER.error("base_dir=%s agent_id=%s", args.base_dir, args.agent_id or "<none>")
    if args.task_file is not None:
        LOGGER.error("task_file=%s", args.task_file)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
