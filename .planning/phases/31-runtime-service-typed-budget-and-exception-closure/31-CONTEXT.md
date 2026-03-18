# Phase 31 Context

**Phase:** `31 Runtime/service typed budget and exception closure`
**Milestone:** `v1.3 Quality-10 Remediation & Productization`
**Date:** `2026-03-17`
**Status:** `planned — ready for execution`
**Source:** `ROADMAP` / `REQUIREMENTS` / `STATE` / `v1.3-HANDOFF` + runtime/service distributed backlog baseline

## Why Phase 31 Exists

`Phase 30` 先收紧 protocol/control 后，剩余 typed / broad-catch debt 已可以按 runtime/service/platform touched zones 预算化处理。`v1.3-HANDOFF` 给出的 baseline 是 `Any=614`、`except Exception=36`、`type: ignore=12`；其中生产代码切片里，runtime/service/platform 范围可先视作 `Any=127 / broad-catch=22 / type_ignore=0`。若不把这最后一层收口成 budget + guard + closeout truth，仓库会再次回到“以后再清”的状态。

## Goal

1. 先处理 runtime root / transport lifecycle 的 broad-catch 主链风险。
2. 再处理 runtime device/state payload typing 这类最可量化下降的 `Any` 簇。
3. 然后处理 service/platform/entity tails，避免把 user-facing 边缘面长期挂在 backlog 名下。
4. 最后把 typed budget、broad-catch budget 与 no-growth guards 固化成治理真源。

## Decisions (Locked)

- 本 phase 不再重开 protocol/control contract 设计；只消费 `Phase 30` 已收紧的上游 contract。
- budget 必须按 zone 表达，而不是只报一个全仓总数。
- 测试里的 `Any` / `type: ignore` 先作为 informational budget，不与生产 budget 混算。
- broad-catch 只允许保留在 documented `fail_closed` / `degraded_skip` / `best_effort_teardown` 语义下；“记录日志继续跑”不是默认合法模式。
- HA 必需签名噪声（如 `**kwargs: Any`）不应被包装成虚假的 typed 胜利；要先区分 sanctioned_any 与 backlog_any。

## Non-Negotiable Constraints

- 不得为追求数字下降而引入大量噪声型类型包装。
- 不得把所有剩余 debt 全部抬成 blocker；budget 需要诚实地区分 active cleanup 与 documented defer。
- 不得把 platform/entity 与 runtime/service 的职责再搅混成单个 cleanup 巨相。

## Canonical References

- `.planning/ROADMAP.md` — `Phase 31` goal / success criteria
- `.planning/REQUIREMENTS.md` — `TYP-07`, `ERR-05`, `GOV-23`
- `.planning/STATE.md` — continuation truth
- `.planning/v1.3-HANDOFF.md` — baseline counts and split rationale
- `.planning/baseline/VERIFICATION_MATRIX.md` — `TYP-* / ERR-* / GOV-*` acceptance expectations
- `.planning/baseline/AUTHORITY_MATRIX.md` — machine truth / governance ownership boundaries
- `custom_components/lipro/core/coordinator/**/*.py`
- `custom_components/lipro/services/**/*.py`
- `custom_components/lipro/entities/**/*.py`
- `custom_components/lipro/*.py`
- `tests/core/coordinator/**/*.py`
- `tests/services/**/*.py`
- `tests/platforms/**/*.py`
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_governance_closeout_guards.py`

## Specifics To Lock During Planning

- `runtime lifecycle / transport broad-catch` 必须先处理：它挂在 runtime root / MQTT setup-shutdown 主链。
- `runtime device payload typing` 是最适合量化下降的 `Any` 簇。
- `service/platform/entity tails` 必须 topicized 处理，不与 runtime mainline 混在一起。
- `GOV-23` 应最后定版；不应在 `Phase 30` 就冻结最终 repo-wide budget truth。

## Expected Plan Shape

最优应为 `4 plans`：

1. runtime lifecycle / transport exception closure
2. runtime device/state typed narrowing
3. service/platform/entity targeted closure
4. budget truth / no-growth guards / closeout evidence
