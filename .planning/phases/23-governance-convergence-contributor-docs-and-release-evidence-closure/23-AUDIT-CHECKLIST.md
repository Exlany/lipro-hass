# Phase 23 Audit Coverage Checklist

**Purpose:** map every 2026-03-16 audit finding to an execution plan or explicit defer.

| Audit Finding | Disposition |
|---|---|
| `fan.py` preset/options mismatch | `23-04` |
| `runtime_access.py` side-effect injection | `23-04` |
| default installer path must remain `latest` | `23-04`, `23-08` |
| entity -> coordinator write path drift | `23-05` |
| runtime compat normalization in `snapshot.py` | `23-05` |
| broad catch / typed-failure hardening | `23-05` checklist |
| `service_router.py` hotspot | `23-06` |
| `developer_report.py` hotspot | `23-06` |
| control/services bidirectional coupling | `23-06` |
| `.planning/codebase/TESTING.md` drift | `23-07` |
| script ↔ tests coupling | `23-07` |
| wording-guard brittleness | `23-07` or explicit follow-up |
| giant tests / private-internal coupling | `23-07` or explicit follow-up |
| bug template vs troubleshooting tension | `23-08` |
| docs / internal planning exposure | `23-08` |
| release supply-chain hardening | `23-08` or explicit defer |
| firmware manifest metadata | `23-08` or explicit defer |
| bus factor / maintainer posture | `23-08` |

## Rules

- No item may be silently dropped.
- If an item is not executed in the current wave set, it must be named in the relevant plan's defer/follow-up section.
- Default installer UX remains `ARCHIVE_TAG=latest` unless the user explicitly changes that requirement in a future planning pass.
