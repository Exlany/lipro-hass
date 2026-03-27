---
phase: 85-terminal-audit-refresh-and-residual-routing
plan: "01"
subsystem: governance
tags: [baseline, docs, architecture, audit, routing]
requires: []
provides:
  - target topology truth now names current formal protocol/control homes
  - dependency matrix now points shared backoff truth only at core/utils/backoff.py
  - maintainer-facing architecture docs expose v1.23 / Phase 85 freshness markers
affects: [Phase 85, terminal-audit, baseline-truth, maintainer-docs]
tech-stack:
  added: []
  patterns: [single formal home, neutral backoff truth, freshness markers]
key-files:
  created:
    - .planning/phases/85-terminal-audit-refresh-and-residual-routing/85-01-SUMMARY.md
  modified:
    - .planning/baseline/TARGET_TOPOLOGY.md
    - .planning/baseline/DEPENDENCY_MATRIX.md
    - .planning/baseline/ARCHITECTURE_POLICY.md
    - docs/developer_architecture.md
key-decisions:
  - "Protocol/control/runtime-infra wording was refreshed to match current formal homes without creating new roots."
  - "Shared exponential backoff truth stays only in custom_components/lipro/core/utils/backoff.py; request_policy no longer carries a parallel compat story."
  - "Per user instruction, execution artifacts were updated without any git commit or state/roadmap mutation."
patterns-established:
  - "Freshness markers: baseline and maintainer docs now expose v1.23 / Phase 85 alignment at the top of each file."
  - "Control narrative: control/ is the formal home, services remain helpers, runtime_infra keeps shared listener ownership only."
requirements-completed: [AUD-04, GOV-62]
duration: "~15min"
completed: 2026-03-27
---

# Plan 85-01 Summary

**Baseline topology, dependency truth, and maintainer architecture docs now align to the v1.23 / Phase 85 audit route without reviving legacy compat or split-control stories**

## Performance

- **Duration:** ~15 min
- **Completed:** 2026-03-27T07:10:48Z
- **Tasks:** 1
- **Files modified:** 4

## Accomplishments

- `TARGET_TOPOLOGY.md` 现明确 `core/protocol/` 为 protocol formal root home，并把 `control/`、`services/`、`runtime_infra.py` 的现行角色拆分清楚。
- `DEPENDENCY_MATRIX.md` 彻底移除 shared backoff 的旧 compat 叙事，统一指向 `custom_components/lipro/core/utils/backoff.py`。
- `ARCHITECTURE_POLICY.md` 与 `docs/developer_architecture.md` 增加 `v1.23 / Phase 85` freshness / alignment 标记，便于维护者快速辨识当前真源。

## Verification

- `uv run python scripts/check_architecture_policy.py --check` ✅ 通过（exit code 0，无额外输出）
- `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_phase72_runtime_bootstrap_route_guards.py` ✅ 通过（`30 passed in 2.48s`）

## Files Created/Modified

- `.planning/baseline/TARGET_TOPOLOGY.md` - 修正 protocol/control 归属与 target directory intent，去除 legacy client 现行叙事。
- `.planning/baseline/DEPENDENCY_MATRIX.md` - 收口 shared backoff 真源，删除 `request_policy.py` parallel compat story。
- `.planning/baseline/ARCHITECTURE_POLICY.md` - 同步 freshness / alignment truth，声明本轮仅刷新基线投影而不改 rule ids。
- `docs/developer_architecture.md` - 标注当前 route alignment，并把 `runtime_infra.py` 纳入 maintainer 快速导航。
- `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-01-SUMMARY.md` - 记录本计划执行结果与验证证据。

## Decisions Made

- 不新增 formal home；仅把文档真源收敛到已存在的 `protocol` / `control` / `runtime_infra` 结构。
- 将 backoff 共享 primitive 的权威表述统一到 `custom_components/lipro/core/utils/backoff.py`，避免后续审计再次读出两条故事线。
- 遵从契约者指令：不创建 git commit，不修改 `.planning/STATE.md`、`.planning/ROADMAP.md` 或 `.planning/REQUIREMENTS.md`。

## Deviations from Plan

None - plan executed exactly as written for the requested files and verification steps.

## Issues Encountered

- `apply_patch` 调用方式收到工具层警示，但补丁已成功落盘；未影响文件内容与验证结果。

## Next Phase Readiness

- `85-01` 的 baseline/docs truth 已对齐，后续 `85-02` 可以在此基础上冻结 repo-wide audit verdict 与 residual routing。
- 当前工作树保留未提交改动，便于契约者继续审阅或自行提交。

---
*Phase: 85-terminal-audit-refresh-and-residual-routing*
*Completed: 2026-03-27*
