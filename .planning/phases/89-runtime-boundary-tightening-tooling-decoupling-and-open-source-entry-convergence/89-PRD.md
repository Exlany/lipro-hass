# Phase 89 PRD

## Title

Runtime boundary tightening, tooling decoupling, and open-source entry convergence

## Problem Statement

`v1.23` 已把 repo-wide terminal audit 与 zero-active residual posture 归档为最新可信基线，但 2026-03-27 的再次全仓终审证明，仓库仍残留几类不应继续延后的结构性问题：

1. `entities/*` 仍直连 `command_service`、`protocol_service`、`get_device_lock` 等 runtime internals，entity/runtime/protocol 边界不够诚实。
2. `Coordinator` 与 `RuntimeOrchestrator` 仍并行承担部分 wiring 责任，runtime root story 仍不够单一。
3. architecture/file-matrix tooling 仍残留 script↔tests helper coupling 与 `sys.path` 注入痕迹，governance kernel 不够独立。
4. `README*`、`docs/README.md`、issue templates、`manifest.json` 等对 distribution/support/issues 的表述仍有 mixed signal，开源入口体验不够统一。
5. 代码地图与治理文档已刷新，但必须和本轮收敛一起同步回写，避免 planning/docs truth 再次落后于代码现实。

## Phase Goal

在不引入第二架构故事线、不重开已关闭 residual 的前提下，把上述问题压回同一条 north-star 主链，并留下 focused regressions / governance proof，确保下一次复查看到的是更薄、更诚实、更稳定的正式边界。

## In Scope

- 为 entities/platforms 增加显式 runtime verbs，移除对 runtime services / lock / OTA protocol seam 的直接依赖。
- 让 runtime bootstrap/service assembly 更集中地归回 orchestrator/factory story。
- 将 governance tooling 共享 helper 从 `tests.helpers` 脱耦到 script-owned home。
- 收敛 README/docs/templates/manifest 的公开入口与 issue/support routing 叙事。
- 同步 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}` 与 `.planning/codebase/*` 的 current-story truth。
- 为上述变更补齐 focused tests / meta guards / quality proof。

## Out of Scope

- 不重开 `v1.23` 已关闭的 residual/delete-gate family。
- 不进行大规模目录重命名或 phase-history 测试文件改名迁移。
- 不在本 phase 内彻底消灭所有 `*_support` / `misc.py` 命名债；仅处理与当前正式边界直接相关的高价值项。
- 不把 dynamic import elimination 扩展成 boundary 全家族重构；仅在 touched path 上避免继续扩大。

## Requirements

- **ARC-23**：entity/platform 仅消费显式 runtime public verbs。
- **RUN-09**：runtime wiring 继续收敛到单一 bootstrap story。
- **GOV-64**：governance tooling 脱离 `tests.helpers` 与 ad-hoc `sys.path` 注入。
- **HOT-39**：hotspot 在正式 home 内 inward split/收窄，而非继续膨胀。
- **OSS-12**：open-source entry / docs / metadata 讲同一条路由故事。
- **QLT-36**：touched scope 维持 `ruff`/`mypy`/governance/tooling/pytest` 全绿。
- **TST-28**：补齐 focused regressions / guards 防止回流。

## Acceptance Criteria

1. `custom_components/lipro/entities/base.py` 与 `custom_components/lipro/entities/firmware_update.py` 不再直接使用 `coordinator.command_service`、`coordinator.protocol_service`、`coordinator.get_device_lock(...)`。
2. `custom_components/lipro/runtime_types.py` 的 entity-facing runtime protocol 以显式 verbs 表达实体允许消费的能力；相关测试夹具同步到新 surface。
3. `custom_components/lipro/core/coordinator/coordinator.py` 的 runtime services/bootstrap construction 不再与 `RuntimeOrchestrator` 并行讲两套装配故事。
4. `scripts/check_architecture_policy.py` 不再 import `tests.helpers.*`，且 script-side shared helpers 有正式 home。
5. `README.md`、`docs/README.md`、`.github/ISSUE_TEMPLATE/*.yml`、`custom_components/lipro/manifest.json` 对 distribution / support / issues 的表述彼此一致。
6. `.planning/codebase/*`、`.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}`、必要 baseline/review docs 与上述变更同步。
7. 相关 focused pytest、`uv run ruff check .`、`uv run mypy`、`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check` 全部通过。

## Recommended Plan Shape

- Plan 89-01：tighten entity/runtime public surface and OTA/runtime verbs
- Plan 89-02：converge runtime wiring onto one bootstrap story
- Plan 89-03：decouple governance tooling from tests helper homes
- Plan 89-04：unify open-source entry/docs/metadata signals and refresh current-story docs
