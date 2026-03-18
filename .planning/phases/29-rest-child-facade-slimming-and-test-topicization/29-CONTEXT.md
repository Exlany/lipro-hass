# Phase 29 Context

**Phase:** `29 REST child-façade slimming and test topicization`
**Milestone:** `v1.3 Quality-10 Remediation & Productization`
**Date:** `2026-03-17`
**Status:** `planned — ready for execution`
**Source:** `ROADMAP` / `REQUIREMENTS` / `STATE` / `v1.3-HANDOFF` + current REST hotspot / API test inventory

## Why Phase 29 Exists

`Phase 27` 已完成第一轮 hotspot slimming，但 `LiproRestFacade` 仍是 `947` 行级别的 giant child façade，且剩余 API regressions 仍高度耦合在 `tests/core/api/test_api.py` 这种 monolith 中。若继续追求 10 分质量，不能把这些 debt 长期合法化为“child façade 可以无限膨胀”。

## Goal

1. 继续切薄 `custom_components/lipro/core/api/client.py`，优先拆 request/auth/transport、command/pacing、capability wrapper 这些剩余高 churn 家族。
2. 同步收口与 child-façade slimming 直接相关的 residual naming / façade-level overload truth。
3. 把与 REST hotspot 强耦合的 mega-tests 继续拆成稳定 topic suites，而不是把无关 control/runtime 巨石顺手吞进来。

## Decisions (Locked)

- 本 phase 只沿现有 `LiproProtocolFacade -> LiproRestFacade -> focused collaborators` 正式主链收口；不得新建第二 protocol root、service bus、DI container 或另一套 REST orchestrator。
- `LiproRestFacade` 仍是 child façade，不是可无限扩张的正式业务根。
- 测试 topicization 必须围绕 REST formal path：transport/auth semantics、command/pacing、capability wrappers。不要把 `tests/core/test_init.py`、大段 control/auth integration 误归为本 phase 的 home。
- typed hardening / broad-catch arbitration 只做 façade slimming 所必需的最小接缝；系统性 tightening 留给 `Phase 30/31`。

## Non-Negotiable Constraints

- 不得把 `Phase 29` 扩成 `Phase 28` 的 release/continuity phase，也不得偷跑 `Phase 30/31` 的 typed-budget / broad-catch cleanup。
- 不得因为拆 API façade 而扩大 `core.api` 对外 surface，或恢复 transport/helper re-export。
- 不得让 schedule decode 从 boundary / focused helper 退回 façade 私有语义。

## Canonical References

- `.planning/ROADMAP.md` — `Phase 29` goal / success criteria / sequencing
- `.planning/REQUIREMENTS.md` — `HOT-06`, `RES-05`, `TST-03`
- `.planning/STATE.md` — continuation route and next-focus truth
- `.planning/v1.3-HANDOFF.md` — maintained residual / typed-budget boundaries
- `custom_components/lipro/core/api/client.py` — current REST hotspot
- `custom_components/lipro/core/api/client_transport.py` — transport bridge collaborator
- `custom_components/lipro/core/api/client_auth_recovery.py` — auth/result arbitration collaborator
- `custom_components/lipro/core/api/request_policy.py` — pacing / retry policy home
- `custom_components/lipro/core/api/command_api_service.py` — command family focused home
- `custom_components/lipro/core/api/schedule_service.py`, `diagnostics_api_service.py`, `mqtt_api_service.py`, `power_service.py`
- `tests/core/api/test_api.py` — current API mega-suite
- `tests/meta/test_public_surface_guards.py`, `tests/meta/test_modularization_surfaces.py` — REST/public-surface guards

## Specifics To Lock During Planning

- 第一优先是 `transport/auth/result-arbitration bridge`：`client.py` 中 `_request_*` / auth-recovery / payload port 接缝与相邻 collaborators 的重叠必须继续下降。
- 第二优先是 `command pacing / busy-retry cluster`：`request_policy` 与 `command_api_service` 已是正式 home，但 façade 薄桥仍偏厚。
- 第三优先是 `schedule + misc capability wrappers`：让 façade 继续只做 capability routing，而不是保留 helper 重影。
- meta 只处理 REST/public-surface 相关守卫；capability wave 需优先落到已有 focused suites（如 `test_api_diagnostics_service.py`、`test_api_schedule_service.py`、`test_api_schedule_endpoints.py`），不把整份 `tests/meta/test_governance_guards.py` 或 runtime/control 巨石当成本 phase 主语。

## Expected Plan Shape

最优应为 `3 plans`：

1. request/auth/transport bridge slimming
2. command/pacing family slimming + API topicization
3. capability wrapper 收尾 + residual/public-surface truth sync
