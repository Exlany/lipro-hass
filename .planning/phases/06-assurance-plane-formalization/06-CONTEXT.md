# Phase 06: Assurance Plane 正式化 - Context

**Gathered:** 2026-03-13
**Status:** Execution-aligned
**Decision mode:** North-star arbitration by default
**Source:** `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, `.planning/baseline/DEPENDENCY_MATRIX.md`, `.planning/baseline/PUBLIC_SURFACES.md`, `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/baseline/AUTHORITY_MATRIX.md`, `.github/workflows/ci.yml`, `.pre-commit-config.yaml`, `tests/meta/**`, `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`

## Phase Boundary

本阶段唯一目标：

**把北极星约束、runtime telemetry、治理台账与验证矩阵正式化为 Assurance Plane，使架构退化、权威漂移、compat 回流、双主链复发能够被自动阻断。**

本阶段必须完成：
- 定义 assurance taxonomy、truth sources、指标口径与 phase 验收模板；
- 补齐 governance / architecture / docs authority 的 meta guards；
- 把新正式结构接入 snapshot / integration / contract coverage；
- 更新 CI / pre-commit，使“结构未退化”成为正式门禁。

本阶段明确**不做**：
- 重新设计 runtime 主链（属于 Phase 5，Phase 6 只消费其交付物）；
- 全仓 compat 最终删除与文档总收口（属于 Phase 7）。

## Current Structural Tension

当前 Assurance Plane 的主骨架已经落地，但还缺少最终收尾：
- `tests/meta/` 已具备 dependency/public-surface/external-boundary/governance 守卫；
- CI 已有独立 governance job，pre-commit 也已接入 governance / diagnostics gate；
- 仍需把 phase summary / validation / final authority order 与 runnable proof 完整落表，避免“代码真相已变，phase 包仍写 Ready for execution”。

## Locked Decisions

- Assurance Plane 是正式第五平面，不是附属脚本集合；
- `CoordinatorTelemetryService` 是 runtime observability 的正式输入面；
- `.planning/baseline/*` 与 `.planning/reviews/*` 是 guard 可读取的治理真源；
- active docs 不能继续平行宣称多个“当前唯一权威”；
- CI / pre-commit 质量门必须证明结构不退化，而非仅证明单测通过。

## Downstream Handoff

- **To Phase 7**：交付稳定的 governance checker、meta guards、CI gate、docs authority rules 与 verification template，使 Phase 7 可以专注于 file-level closeout 与终态报告。
