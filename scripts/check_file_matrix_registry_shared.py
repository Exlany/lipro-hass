"""Shared types and row builders for file-matrix registry classification."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FileGovernanceRow:
    """One normalized file-governance record from the matrix inventory."""

    path: str
    area: str
    owner_phase: str
    fate: str
    residual: str


@dataclass(frozen=True, slots=True)
class OverrideTruthFamily:
    """One focused override family that contributes file-governance rows."""

    area: str
    owner_phase: str
    rows: tuple[tuple[str, str], ...]
    fate: str = "保留"


def row_for_path(
    path: str,
    area: str,
    owner_phase: str,
    fate: str = "保留",
    residual: str = "-",
) -> FileGovernanceRow:
    """Build one normalized governance row."""
    return FileGovernanceRow(
        path=path,
        area=area,
        owner_phase=owner_phase,
        fate=fate,
        residual=residual,
    )
