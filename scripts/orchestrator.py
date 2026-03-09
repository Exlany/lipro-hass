"""Compatibility stub for the retired refactoring orchestrator script."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)

_DEPRECATION_MESSAGE = (
    "scripts/orchestrator.py 已退役；当前仓库改用主代理主控执行 docs/refactoring 计划，"
    "不再依赖额外 Python 编排平台。"
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
    """Print the deprecation notice and exit successfully."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = build_parser().parse_args()
    LOGGER.info("%s", _DEPRECATION_MESSAGE)
    LOGGER.info("command=%s base_dir=%s", args.command, args.base_dir)
    LOGGER.info("See docs/refactoring/EXECUTION_GUIDE.md for the supported workflow.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
