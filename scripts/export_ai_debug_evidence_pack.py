"""Export one AI Debug Evidence Pack from formal assurance sources."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests.harness.evidence_pack import (
    AiDebugEvidenceCollector,
    build_pack_index_markdown,
)


def export_ai_debug_evidence_pack(
    output_dir: Path,
    *,
    report_id: str | None = None,
    generated_at: str | None = None,
) -> tuple[Path, Path]:
    """Build and write the JSON pack plus markdown index."""
    collector = AiDebugEvidenceCollector()
    pack = collector.collect(report_id=report_id, generated_at=generated_at)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "ai_debug_evidence_pack.json"
    index_path = output_dir / "ai_debug_evidence_pack.index.md"
    json_path.write_text(
        json.dumps(pack.to_dict(), indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    index_path.write_text(build_pack_index_markdown(pack) + "\n", encoding="utf-8")
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
