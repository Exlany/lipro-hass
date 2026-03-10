"""Summarize and validate coverage JSON reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


def load_percent(path: Path) -> float:
    """Load total coverage percent from a pytest-cov JSON report."""
    data = json.loads(path.read_text())
    totals: dict[str, Any] = data.get("totals", {})
    percent = totals.get("percent_covered")
    if isinstance(percent, (int, float)):
        return float(percent)
    msg = f"Coverage JSON missing totals.percent_covered: {path}"
    raise ValueError(msg)



def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for coverage diff checks."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("coverage_json", nargs="?", default="coverage.json")
    parser.add_argument("--baseline", help="Optional baseline coverage.json to compare against")
    parser.add_argument("--minimum", type=float, default=95.0)
    return parser



def main() -> int:
    """Run the CLI entrypoint and return a process-friendly status code."""
    args = build_parser().parse_args()
    report_path = Path(args.coverage_json)
    current = load_percent(report_path)
    sys.stdout.write(f"Current coverage: {current:.2f}%\n")
    if current < args.minimum:
        sys.stdout.write(f"Coverage below minimum {args.minimum:.2f}%\n")
        return 1
    if args.baseline:
        baseline = load_percent(Path(args.baseline))
        diff = current - baseline
        sys.stdout.write(f"Coverage diff: {diff:+.2f}% (baseline {baseline:.2f}%)\n")
        if diff < 0:
            sys.stdout.write("Coverage regressed below baseline\n")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
