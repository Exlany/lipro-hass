"""Classification registry for file-governance matrix rows."""

from __future__ import annotations

from scripts.check_file_matrix_registry_classifiers import (
    classify_component_path,
    classify_script_path,
    classify_test_path,
)
from scripts.check_file_matrix_registry_overrides import OVERRIDE_TRUTH_FAMILIES
from scripts.check_file_matrix_registry_shared import (
    FileGovernanceRow,
    OverrideTruthFamily,
    row_for_path,
)


def _family_key(family: OverrideTruthFamily) -> str:
    return f"{family.owner_phase}|{family.area}|{family.fate}"


def _build_override_index(
    families: tuple[OverrideTruthFamily, ...],
) -> dict[str, FileGovernanceRow]:
    overrides: dict[str, FileGovernanceRow] = {}
    duplicate_paths: list[str] = []

    for family in families:
        for path, residual in family.rows:
            if path in overrides:
                duplicate_paths.append(path)
                continue
            overrides[path] = row_for_path(
                path,
                family.area,
                family.owner_phase,
                family.fate,
                residual,
            )

    if duplicate_paths:
        duplicates = ", ".join(sorted(set(duplicate_paths)))
        msg = f"duplicate override paths: {duplicates}"
        raise ValueError(msg)

    return overrides


OVERRIDES = _build_override_index(OVERRIDE_TRUTH_FAMILIES)


def iter_override_truth_families() -> tuple[OverrideTruthFamily, ...]:
    """Return the focused override families that feed the registry."""
    return OVERRIDE_TRUTH_FAMILIES


def classify_path(path: str) -> FileGovernanceRow:
    """Map one Python file path to its governed area and phase ownership."""
    if path in OVERRIDES:
        return OVERRIDES[path]

    for classifier in (
        classify_component_path,
        classify_test_path,
        classify_script_path,
    ):
        row = classifier(path)
        if row is not None:
            return row
    return row_for_path(path, "Cross-cutting", "Phase 7")
