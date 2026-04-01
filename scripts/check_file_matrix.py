"""Thin compatibility root for Python inventory, file-matrix coverage, and doc drift."""

from __future__ import annotations

import argparse
import importlib
import sys

_CHECKER_MODULE_NAMES = (
    'check_file_matrix_inventory',
    'check_file_matrix_markdown',
    'check_file_matrix_registry',
    'check_file_matrix_validation',
)


def _module_prefix() -> str:
    return '' if __package__ in {None, ''} else 'scripts.'


def _load_checker_modules() -> dict[str, object]:
    prefix = _module_prefix()
    return {
        module_name: importlib.import_module(f'{prefix}{module_name}')
        for module_name in _CHECKER_MODULE_NAMES
    }


_MODULES = _load_checker_modules()
_INVENTORY = _MODULES['check_file_matrix_inventory']
_MARKDOWN = _MODULES['check_file_matrix_markdown']
_REGISTRY = _MODULES['check_file_matrix_registry']
_VALIDATION = _MODULES['check_file_matrix_validation']

iter_python_files = _INVENTORY.iter_python_files
repo_root = _INVENTORY.repo_root
extract_reported_total = _MARKDOWN.extract_reported_total
generate_file_matrix_markdown = _MARKDOWN.generate_file_matrix_markdown
parse_file_matrix_paths = _MARKDOWN.parse_file_matrix_paths
FileGovernanceRow = _REGISTRY.FileGovernanceRow
classify_path = _REGISTRY.classify_path
FILE_MATRIX_PATH = _VALIDATION.FILE_MATRIX_PATH
VERIFICATION_MATRIX_PATH = _VALIDATION.VERIFICATION_MATRIX_PATH
run_checks = _VALIDATION.run_checks
validate_verification_matrix_paths = _VALIDATION.validate_verification_matrix_paths

__all__ = [
    'FILE_MATRIX_PATH',
    'VERIFICATION_MATRIX_PATH',
    'FileGovernanceRow',
    'classify_path',
    'extract_reported_total',
    'iter_python_files',
    'main',
    'parse_file_matrix_paths',
    'repo_root',
    'run_checks',
    'validate_verification_matrix_paths',
]


def _write_line(message: str) -> None:
    sys.stdout.write(f'{message}\n')


def main() -> int:
    """Run the governance CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--write',
        action='store_true',
        help='rewrite FILE_MATRIX.md from current inventory',
    )
    parser.add_argument(
        '--check', action='store_true', help='validate governance artifacts'
    )
    parser.add_argument(
        '--report', action='store_true', help='print current inventory summary'
    )
    args = parser.parse_args()

    root = repo_root()
    inventory = iter_python_files(root)

    if args.write:
        (root / FILE_MATRIX_PATH).write_text(
            generate_file_matrix_markdown(inventory),
            encoding='utf-8',
        )

    if args.report:
        _write_line(f'python_files_total={len(inventory)}')
        phase_counts: dict[str, int] = {}
        for path in inventory:
            phase = classify_path(path).owner_phase
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        for phase, count in sorted(phase_counts.items()):
            _write_line(f'{phase}={count}')

    if args.check:
        errors = run_checks(root)
        if errors:
            for error in errors:
                _write_line(error)
            return 1

    if not any((args.write, args.check, args.report)):
        parser.print_help()
        return 0
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
