"""Compare pytest-benchmark results against the governed benchmark manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        msg = f"JSON must be an object: {path}"
        raise TypeError(msg)
    return data


def load_manifest(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    """Load the governed benchmark baseline manifest."""
    data = _load_json(path)
    policy = data.get("policy", {})
    benchmarks = data.get("benchmarks", {})
    if not isinstance(policy, dict) or not isinstance(benchmarks, dict):
        msg = f"Manifest missing policy/benchmarks mapping: {path}"
        raise TypeError(msg)
    normalized = {
        key: payload
        for key, payload in benchmarks.items()
        if isinstance(key, str) and isinstance(payload, dict)
    }
    return policy, normalized


def load_benchmark_means(path: Path) -> dict[str, float]:
    """Load benchmark mean durations keyed by pytest fullname."""
    data = _load_json(path)
    entries = data.get("benchmarks", [])
    if not isinstance(entries, list):
        msg = f"Benchmark JSON missing benchmarks list: {path}"
        raise TypeError(msg)

    results: dict[str, float] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        fullname = entry.get("fullname")
        stats = entry.get("stats")
        if not isinstance(fullname, str) or not isinstance(stats, dict):
            continue
        mean = stats.get("mean")
        if isinstance(mean, (int, float)):
            results[fullname] = float(mean)
    return results


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for benchmark baseline comparison."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "benchmark_json",
        nargs="?",
        default=".benchmarks/benchmark.json",
    )
    parser.add_argument(
        "--manifest",
        default="tests/benchmarks/benchmark_baselines.json",
        help="Machine-readable benchmark baseline manifest",
    )
    parser.add_argument(
        "--benchmark-set",
        choices=("all", "smoke"),
        default="all",
        help="Select the full manifest or the policy-declared smoke subset",
    )
    return parser


def _select_manifest(policy: dict[str, Any], manifest: dict[str, dict[str, Any]], benchmark_set: str) -> dict[str, dict[str, Any]]:
    if benchmark_set == "all":
        return manifest

    smoke_benchmarks = policy.get("smoke_benchmarks")
    if not isinstance(smoke_benchmarks, list) or not smoke_benchmarks:
        msg = "Manifest missing policy.smoke_benchmarks for smoke benchmark set"
        raise TypeError(msg)

    selected: dict[str, dict[str, Any]] = {}
    for benchmark_id in smoke_benchmarks:
        if not isinstance(benchmark_id, str):
            msg = "policy.smoke_benchmarks entries must be strings"
            raise TypeError(msg)
        contract = manifest.get(benchmark_id)
        if contract is None:
            msg = f"Smoke benchmark missing from manifest: {benchmark_id}"
            raise KeyError(msg)
        selected[benchmark_id] = contract
    return selected


def main() -> int:
    """Run benchmark baseline comparison and return a process-friendly status."""
    args = build_parser().parse_args()
    benchmark_path = Path(args.benchmark_json)
    manifest_path = Path(args.manifest)

    policy, full_manifest = load_manifest(manifest_path)
    manifest = _select_manifest(policy, full_manifest, args.benchmark_set)
    results = load_benchmark_means(benchmark_path)

    default_warning_ratio = float(policy.get("default_warning_ratio", 2.0))
    default_failure_ratio = float(policy.get("default_failure_ratio", 4.0))

    sys.stdout.write(f"Benchmark manifest: {manifest_path}\n")
    sys.stdout.write(f"Benchmark sample: {benchmark_path}\n")
    sys.stdout.write(f"Benchmark set: {args.benchmark_set}\n")

    warnings: list[str] = []
    failures: list[str] = []

    for benchmark_id, contract in manifest.items():
        current = results.get(benchmark_id)
        if current is None:
            failures.append(f"missing benchmark result: {benchmark_id}")
            continue

        baseline = contract.get("baseline_mean_seconds")
        if not isinstance(baseline, (int, float)) or baseline <= 0:
            failures.append(f"invalid baseline_mean_seconds for {benchmark_id}")
            continue

        warning_ratio = float(contract.get("warning_ratio", default_warning_ratio))
        failure_ratio = float(contract.get("failure_ratio", default_failure_ratio))
        warning_limit = float(baseline) * warning_ratio
        failure_limit = float(baseline) * failure_ratio
        ratio = current / float(baseline)

        sys.stdout.write(
            f"Benchmark {benchmark_id}: mean={current:.9f}s "
            f"baseline={float(baseline):.9f}s ratio={ratio:.2f}x "
            f"warning<= {warning_limit:.9f}s failure<= {failure_limit:.9f}s\n"
        )

        if current > failure_limit:
            failures.append(
                "blocking regression: "
                f"{benchmark_id} mean {current:.9f}s exceeds failure limit "
                f"{failure_limit:.9f}s ({ratio:.2f}x baseline)"
            )
        elif current > warning_limit:
            warnings.append(
                "threshold warning: "
                f"{benchmark_id} mean {current:.9f}s exceeds warning limit "
                f"{warning_limit:.9f}s ({ratio:.2f}x baseline)"
            )

    unexpected = sorted(set(results) - set(manifest))
    for benchmark_id in unexpected:
        sys.stdout.write(
            f"Benchmark unexpected result (not in manifest): {benchmark_id}\n"
        )

    for line in warnings:
        sys.stdout.write(f"WARNING: {line}\n")

    if failures:
        for line in failures:
            sys.stdout.write(f"FAIL: {line}\n")
        return 1

    if warnings:
        sys.stdout.write("Benchmark contract: warnings only\n")
    else:
        sys.stdout.write("Benchmark contract: ok\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
