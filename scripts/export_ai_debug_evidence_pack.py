"""Export one AI Debug Evidence Pack from formal assurance sources."""

from __future__ import annotations

import argparse
from collections.abc import Callable
import importlib
import json
from pathlib import Path
import sys
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from tests.harness.evidence_pack import AiDebugEvidenceCollector

MarkdownBuilder = Callable[[Any], str]


def _load_evidence_pack_support() -> tuple[type[AiDebugEvidenceCollector], MarkdownBuilder]:
    try:
        support_module = importlib.import_module("tests.harness.evidence_pack")
    except ModuleNotFoundError as exc:
        if exc.name == "tests" or (exc.name or "").startswith("tests."):
            msg = (
                "Run this exporter as a module from the repository root: "
                "`uv run python -m scripts.export_ai_debug_evidence_pack ...`"
            )
            raise RuntimeError(msg) from exc
        raise
    collector_type = cast("type[AiDebugEvidenceCollector]", support_module.AiDebugEvidenceCollector)
    markdown_builder = cast("MarkdownBuilder", support_module.build_pack_index_markdown)
    return collector_type, markdown_builder


def export_ai_debug_evidence_pack(
    output_dir: Path,
    *,
    report_id: str | None = None,
    generated_at: str | None = None,
) -> tuple[Path, Path]:
    """Build and write the JSON pack plus markdown index."""
    collector_type, markdown_builder = _load_evidence_pack_support()
    collector = collector_type()
    pack = collector.collect(report_id=report_id, generated_at=generated_at)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "ai_debug_evidence_pack.json"
    index_path = output_dir / "ai_debug_evidence_pack.index.md"
    json_path.write_text(
        json.dumps(pack.to_dict(), indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    index_path.write_text(markdown_builder(pack) + "\n", encoding="utf-8")
    return json_path, index_path


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for evidence-pack export."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report-id", type=str, default=None)
    parser.add_argument("--generated-at", type=str, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the evidence-pack exporter CLI and print written paths."""
    args = build_parser().parse_args(argv)
    json_path, index_path = export_ai_debug_evidence_pack(
        args.output_dir,
        report_id=args.report_id,
        generated_at=args.generated_at,
    )
    sys.stdout.write(f"{json_path.as_posix()}\n{index_path.as_posix()}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
