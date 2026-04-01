"""Check total coverage floors with optional baseline and changed-surface gates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

_SOURCE_ROOT = "custom_components/lipro/"


def _load_report(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        msg = f"Coverage JSON must be an object: {path}"
        raise TypeError(msg)
    return data


def load_percent(path: Path) -> float:
    """Load total coverage percent from a pytest-cov JSON report."""
    data = _load_report(path)
    totals = data.get("totals", {})
    if not isinstance(totals, dict):
        msg = f"Coverage JSON missing totals mapping: {path}"
        raise TypeError(msg)
    percent = totals.get("percent_covered")
    if isinstance(percent, (int, float)):
        return float(percent)
    msg = f"Coverage JSON missing totals.percent_covered: {path}"
    raise TypeError(msg)


def load_file_percents(path: Path) -> dict[str, float]:
    """Load per-file coverage percentages from a pytest-cov JSON report."""
    data = _load_report(path)
    files = data.get("files", {})
    if not isinstance(files, dict):
        msg = f"Coverage JSON missing files mapping: {path}"
        raise TypeError(msg)

    result: dict[str, float] = {}
    for file_path, payload in files.items():
        if not isinstance(file_path, str) or not isinstance(payload, dict):
            continue
        summary = payload.get("summary", {})
        if not isinstance(summary, dict):
            continue
        percent = summary.get("percent_covered")
        if isinstance(percent, (int, float)):
            result[file_path] = float(percent)
    return result


def load_changed_files(path: Path) -> list[str]:
    """Load newline-delimited changed files while preserving order."""
    seen: set[str] = set()
    changed_files: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        file_path = raw_line.strip()
        if not file_path or file_path in seen:
            continue
        seen.add(file_path)
        changed_files.append(file_path)
    return changed_files


def _is_expected_source_file(path: str) -> bool:
    return path.endswith(".py") and path.startswith(_SOURCE_ROOT)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for coverage floor / diff checks."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("coverage_json", nargs="?", default="coverage.json")
    parser.add_argument(
        "--baseline",
        help="Optional baseline coverage.json for total-coverage diff mode",
    )
    parser.add_argument(
        "--minimum",
        type=float,
        default=95.0,
        help="Blocking total coverage floor percentage",
    )
    parser.add_argument(
        "--changed-files",
        "--changed-files-file",
        dest="changed_files",
        help="Optional newline-delimited changed-file list for changed-surface gating",
    )
    parser.add_argument(
        "--changed-minimum",
        "--minimum-changed-file-coverage",
        dest="changed_minimum",
        type=float,
        help="Blocking per-file floor for changed measured files (defaults to --minimum)",
    )
    parser.add_argument(
        "--fail-on-changed-regression",
        action="store_true",
        help="Fail when a changed measured file regresses below its baseline coverage",
    )
    return parser


def main() -> int:
    """Run the CLI entrypoint and return a process-friendly status code."""
    args = build_parser().parse_args()
    report_path = Path(args.coverage_json)
    current = load_percent(report_path)
    sys.stdout.write(f"Current coverage: {current:.2f}%\n")

    failed = False
    if current < args.minimum:
        sys.stdout.write(f"Coverage below minimum {args.minimum:.2f}%\n")
        failed = True

    if args.baseline:
        baseline = load_percent(Path(args.baseline))
        diff = current - baseline
        sys.stdout.write(f"Coverage diff: {diff:+.2f}% (baseline {baseline:.2f}%)\n")
        if diff < 0:
            sys.stdout.write("Coverage regressed below baseline\n")
            failed = True
    else:
        sys.stdout.write("Coverage diff: skipped (no baseline provided)\n")

    if args.changed_files:
        changed_floor = (
            args.changed_minimum if args.changed_minimum is not None else args.minimum
        )
        file_percents = load_file_percents(report_path)
        changed_paths = load_changed_files(Path(args.changed_files))
        measured_paths = [path for path in changed_paths if path in file_percents]
        missing_source_paths = [
            path
            for path in changed_paths
            if _is_expected_source_file(path) and path not in file_percents
        ]

        if not measured_paths and not missing_source_paths:
            sys.stdout.write(
                "Changed-surface coverage: skipped (no measured files in change set)\n"
            )
        else:
            sys.stdout.write(f"Changed-surface coverage floor: {changed_floor:.2f}%\n")
            changed_surface_failed = False
            baseline_file_percents = (
                load_file_percents(Path(args.baseline)) if args.baseline else {}
            )
            for file_path in measured_paths:
                percent = file_percents[file_path]
                sys.stdout.write(
                    f"Changed-surface file: {file_path} = {percent:.2f}%\n"
                )
                if percent < changed_floor:
                    sys.stdout.write(
                        "Changed-surface coverage below minimum for "
                        f"{file_path}: {percent:.2f}% < {changed_floor:.2f}%\n"
                    )
                    changed_surface_failed = True
                if args.fail_on_changed_regression and file_path in baseline_file_percents:
                    baseline_percent = baseline_file_percents[file_path]
                    sys.stdout.write(
                        "Changed-surface baseline: "
                        f"{file_path} = {baseline_percent:.2f}%\n"
                    )
                    if percent < baseline_percent:
                        sys.stdout.write(
                            "Changed-surface coverage regressed below baseline for "
                            f"{file_path}: {percent:.2f}% < {baseline_percent:.2f}%\n"
                        )
                        changed_surface_failed = True
                elif args.fail_on_changed_regression:
                    sys.stdout.write(
                        "Changed-surface baseline: skipped for new measured file "
                        f"{file_path}\n"
                    )

            for file_path in missing_source_paths:
                sys.stdout.write(
                    f"Changed-surface coverage missing report entry: {file_path}\n"
                )
                changed_surface_failed = True

            if changed_surface_failed:
                failed = True
            else:
                sys.stdout.write("Changed-surface coverage: ok\n")
    else:
        sys.stdout.write(
            "Changed-surface coverage: skipped (no changed file list provided)\n"
        )

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
