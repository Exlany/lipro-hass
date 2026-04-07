"""Utility helpers for validating refactor outcomes."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.coverage_diff import load_percent
elif __package__ in {None, ""}:
    from coverage_diff import load_percent
else:
    from scripts.coverage_diff import load_percent


@dataclass(slots=True)
class RefactorValidator:
    """Small utility facade used by refactor validation scripts/tests."""

    minimum_coverage: float = 95.0

    def validate_coverage(self, report_path: Path) -> tuple[bool, float]:
        """Validate that a coverage report meets the configured minimum."""
        percent = load_percent(report_path)
        return percent >= self.minimum_coverage, percent

    def summarize_paths(self, *paths: Path) -> dict[str, bool]:
        """Return a simple existence map for important validation paths."""
        return {str(path): path.exists() for path in paths}

    def validate_api_contracts(self) -> list[str]:
        """Return the named API contracts that must remain available."""
        return [
            "DeviceApiResponse",
            "CommandResultApiResponse",
            "DiagnosticsApiResponse",
            "ScheduleApiResponse",
        ]



def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for refactor validation commands."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage-json", default="coverage.json")
    parser.add_argument("--minimum-coverage", type=float, default=95.0)
    return parser



def main() -> int:
    """Run the CLI entrypoint and return a process-friendly status code."""
    args = build_parser().parse_args()
    validator = RefactorValidator(minimum_coverage=args.minimum_coverage)
    ok, percent = validator.validate_coverage(Path(args.coverage_json))
    sys.stdout.write(
        f"coverage={percent:.2f}% minimum={args.minimum_coverage:.2f}% ok={ok}\n"
    )
    sys.stdout.write(
        "api_contracts=" + ",".join(validator.validate_api_contracts()) + "\n"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
