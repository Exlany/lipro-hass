# Phase 134: Request-policy ownership, entity de-reflection, and fan truth hardening - Context

**Gathered:** 2026-04-02
**Status:** planned + executed in one active phase
**Milestone:** `v1.40 Request Policy Ownership, Entity De-Reflection & Fan Truth Hardening`
**Current route:** `v1.40 active milestone route / starting from latest archived baseline = v1.39`
**Requirements basket:** `GOV-90`, `ARC-43`, `HOT-62`, `HOT-63`, `QLT-56`, `TST-54`
**Default next command:** `$gsd-complete-milestone v1.40`

<domain>
## Phase Boundary

本 phase 只做三件被 north-star 与当前治理真源同时允许的事：

1. 把 `RequestPolicy` 的 pacing/busy-retry state 收回实例 owner，终止 module-level mutating pacing entry 的第二条主链；
2. 把 `descriptors.py` / `light.py` / `binary_sensor.py` 的 dotted-path 与反射式 projection 改为显式 resolver / state-reader；
3. 修复 `fan.py` 的 unknown-mode truth，并同步 docs / guards / verification，使 `$gsd-next` 的等价结论诚实落到 `$gsd-complete-milestone v1.40`。

本 phase 不是“顺手处理所有 formal hotspot”的隐式大杂烩；`runtime_access.py`、`auth_service.py` 与 `dispatch.py` 若继续追打，必须走下一条显式路线。
</domain>

<decisions>
## Locked Decisions

- `v1.40` 是唯一 current active milestone，`Phase 134` 是唯一 active phase。
- current route truth 固定为 `v1.40 active milestone route / starting from latest archived baseline = v1.39`。
- `latest archived baseline` 继续是 `v1.39`，evidence pointer 固定为 `.planning/reviews/V1_39_EVIDENCE_INDEX.md`。
- `RequestPolicy` 的 mutable pacing state 只能由实例 owner 持有；support helpers 只吃 `_CommandPacingCaches` bundle。
- entity projection 不再容忍 dotted-path/getattr 反射；unknown `fanMode` 不再伪装成 `cycle`。
- verification 至少覆盖 focused production tests、governance follow-up route tests、public-surface guards 与 targeted `ruff`。
</decisions>

<canonical_refs>
## Canonical References

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `.planning/baseline/GOVERNANCE_REGISTRY.json`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `custom_components/lipro/core/api/request_policy.py`
- `custom_components/lipro/core/api/request_policy_support.py`
- `custom_components/lipro/entities/descriptors.py`
- `custom_components/lipro/light.py`
- `custom_components/lipro/binary_sensor.py`
- `custom_components/lipro/fan.py`
</canonical_refs>
