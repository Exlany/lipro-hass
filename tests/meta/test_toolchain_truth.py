"""Thin shell for topicized toolchain truth suites."""

from __future__ import annotations

from . import (
    toolchain_truth_checker_paths,
    toolchain_truth_ci_contract,
    toolchain_truth_docs_fast_path,
    toolchain_truth_python_stack,
    toolchain_truth_release_contract,
    toolchain_truth_testing_governance,
)

_MODULES = (
    toolchain_truth_checker_paths,
    toolchain_truth_ci_contract,
    toolchain_truth_docs_fast_path,
    toolchain_truth_python_stack,
    toolchain_truth_release_contract,
    toolchain_truth_testing_governance,
)

for module in _MODULES:
    for name in dir(module):
        if name.startswith("test_"):
            globals()[name] = getattr(module, name)

__all__ = sorted(name for name in globals() if name.startswith("test_"))
