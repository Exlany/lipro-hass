# Phase 72 Context

## Phase

- **Number:** `72`
- **Title:** `Runtime bootstrap convergence, lifecycle orchestration consolidation, and runtime-access probe retirement`
- **Milestone:** `v1.20 Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement`
- **Starting baseline:** `v1.19 archived / evidence-ready`

## Why This Phase Exists

`v1.19` 已把 current-route / latest-archive truth、OTA / anonymous-share / request-pacing / command-runtime hotspots 收口到 archived baseline；但 `.planning/reviews/V1_19_TERMINAL_AUDIT.md` 明确保留了更深层、却仍适合按 north-star seams inward 收口的 runtime/control residual：

- `Coordinator` bootstrap / builder 过厚
- `EntryLifecycleController` / `EntryLifecycleSupport` orchestration 分散
- `runtime_access` family 仍存在 test-aware probing folklore
- current active route 需要 machine-checkable 地切到 `v1.20 / Phase 72 -> 74`

## In Scope

- `custom_components/lipro/coordinator_entry.py`
- `custom_components/lipro/control/entry_lifecycle_controller.py`
- `custom_components/lipro/control/entry_lifecycle_support.py`
- `custom_components/lipro/control/runtime_access.py`
- `custom_components/lipro/control/runtime_access_support.py`
- `custom_components/lipro/control/runtime_access_support_*`
- touched `tests/core/**` and `tests/meta/**` around runtime/control bootstrap truth
- `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`

## Constraints

- 不新增 outward roots / public surfaces
- latest archived baseline 继续是 `v1.19`
- `V1_19_EVIDENCE_INDEX.md` 只保留 latest pull-only closeout pointer 身份
- 所有 Python / test / script 命令统一 `uv run ...`
