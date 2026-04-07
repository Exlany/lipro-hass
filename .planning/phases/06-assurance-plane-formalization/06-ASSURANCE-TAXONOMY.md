# Phase 06 Assurance Taxonomy

**Status:** Active
**Updated:** 2026-03-13

## Formal Assurance Layers

1. **Architecture guards**
   - 关注依赖方向、public surface、formal root。
   - 代表资产：`.planning/baseline/DEPENDENCY_MATRIX.md`、`.planning/baseline/PUBLIC_SURFACES.md`、`tests/meta/test_dependency_guards.py`、`tests/meta/test_public_surface_guards.py`。

2. **Governance guards**
   - 关注 file inventory、authority 口径、residual / kill completeness。
   - 代表资产：`.planning/reviews/FILE_MATRIX.md`、`.planning/reviews/RESIDUAL_LEDGER.md`、`.planning/reviews/KILL_LIST.md`、`scripts/check_file_matrix.py`、`tests/meta/test_governance_guards.py`。

3. **Runtime assurance**
   - 关注 command / refresh / state / mqtt / telemetry 的正式主链与关键运行信号。
   - 代表资产：`CoordinatorTelemetryService`、runtime integration tests、coordinator public snapshots。

4. **Acceptance validation**
   - 关注 phase must_haves 是否被代码、测试、文档、治理台账同时满足。
   - 代表资产：`*-PLAN.md`、`*-SUMMARY.md`、`*-VALIDATION.md`、`.planning/baseline/VERIFICATION_MATRIX.md`。

## Required Runtime Signals

Phase 6 起，以下信号必须能被正式观测：
- auth recovery / reauth trigger
- MQTT connect / disconnect / reconnect backoff
- command trace / confirmation / last failure
- refresh latency / state-batch latency
- group reconciliation request / connect-state event

## Truth Source Order

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/baseline/*.md`
3. `.planning/ROADMAP.md` / `.planning/REQUIREMENTS.md` / `.planning/STATE.md`
4. `.planning/reviews/*.md`
5. `docs/developer_architecture.md`
6. historical docs / archive
