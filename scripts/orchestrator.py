"""Retired compatibility stub kept only to fail fast with a migration hint."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)

_DEPRECATION_MESSAGE = (
    "scripts/orchestrator.py 已退役；当前仓库仅保留它作为 unsupported 的 fail-fast 入口，"
    "请改走现役工具链。"
)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the retired orchestrator entry point."""
    parser = argparse.ArgumentParser(
        description="Deprecated Lipro refactoring orchestrator"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="status",
        help="Deprecated subcommand placeholder",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path.cwd(),
        help="Repository root used for the compatibility message",
    )
    return parser


def main() -> int:
    """Print the deprecation notice and exit with the fail-fast status."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = build_parser().parse_args()
    LOGGER.error("%s", _DEPRECATION_MESSAGE)
    LOGGER.error(
        "Use docs/README.md and CONTRIBUTING.md for the active tooling entrypoints: ./scripts/setup, ./scripts/develop, ./scripts/lint"
    )
    LOGGER.error("command=%s base_dir=%s", args.command, args.base_dir)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
