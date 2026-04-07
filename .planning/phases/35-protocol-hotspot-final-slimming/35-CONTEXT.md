# Phase 35 Context

**Phase:** `35 Protocol hotspot final slimming`
**Milestone:** `v1.4 seed — Sustainment, Trust Gates & Final Hotspot Burn-down`
**Date:** `2026-03-18`
**Status:** `planned — context captured, ready for execution planning`
**Source:** `.planning/{ROADMAP,REQUIREMENTS,STATE,PROJECT}.md` + protocol hotspot audit + current protocol/API tests and public-surface guards

## Why Phase 35 Exists

`Phase 34` 已把 release trust / continuity 拉到更硬的治理水位，但协议层仍残留两处明显热点：

1. `custom_components/lipro/core/api/client.py` 仍同时承载 session/token proxy、request pipeline、mapping retry、endpoint forwarding。
2. `custom_components/lipro/core/protocol/facade.py` 仍吸附大量 `_rest_port` forwarding；这些是 formal root 之上的 glue，而不是 root 自身的不可拆职责。

如果继续放任这两处热点停留在“可运行但偏胖”的状态，协议层就会持续停在 9.x 分：root 看似统一，但复杂度仍被 façade 顶层吸附。

## Goal

1. 继续切薄 `LiproRestFacade` 与 `LiproProtocolFacade`，但严格沿现有 protocol seams 下沉职责。
2. 不引入第二 protocol root，不扩 public surface，不把 forwarding glue 合法化成永久故事线。
3. 让 hotspot slimming 伴随 targeted regressions 与 surface / dependency / residual truth 同步收口。

## Decisions (Locked)

- `LiproProtocolFacade` 仍是唯一正式 protocol-plane root；任何新 helper / surface 都只能是 localized collaborator，不得成为第二 façade 故事线。
- `LiproRestFacade` 仍是正式 REST child façade；允许内部抽取 request gateway / endpoint surface，但不得改写 external import story。
- 允许保留必要 thin delegates 兼容现有测试与局部私有依赖，但必须把复杂实现下沉，不得只是重命名搬家。
- `build_mqtt_facade()`、`attach_mqtt_facade()`、`protocol_diagnostics_snapshot()` 仍属于 protocol root 真职责，不在本 phase 做表面拆散。
- 若 public surface / file ownership / residual disposition 发生变化，必须同步回写 baseline / reviews，而不是只靠 phase 文档口头宣告。

## Non-Negotiable Constraints

- 不得引入第二条 protocol mainline。
- 不得让 control / runtime / tests 开始依赖新的内部 helper 名称。
- 不得因 hotspot slimming 反向增加 package export 或新增 undocumented surface。
- 不得为了“瘦身”删除现有定向回归覆盖。

## Canonical References

### Governance / Route Truth
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/PROJECT.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/developer_architecture.md`

### Protocol Hotspots
- `custom_components/lipro/core/api/client.py`
- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/protocol/__init__.py`
- `custom_components/lipro/core/__init__.py`

### Guard / Regression Truth
- `tests/core/api/test_protocol_contract_matrix.py`
- `tests/core/api/test_api_command_surface.py`
- `tests/core/api/test_api_transport_and_schedule.py`
- `tests/core/api/test_auth_recovery_telemetry.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_dependency_guards.py`

### Baseline / Residual Truth
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`

## Expected Scope

### In scope
- REST child-façade request / endpoint collaborator extraction
- protocol-root forwarding cluster slimming
- targeted protocol/API regressions and public-surface truth sync

### Out of scope
- runtime root slimming
- broad exception global burn-down
- giant test third-wave topicization
- release / continuity governance changes

## Open Planning Questions

1. `client.py` 最先抽哪一层最稳：request pipeline，还是 endpoint forwarding 尾巴？
2. `facade.py` 的 forwarding 下沉应落到 grouped protocol surface 还是单一 REST dispatch helper？
3. 哪些 tests 需要继续允许 private compatibility，哪些应被收口到 formal surface？
4. 哪些 baseline/review 文档需要在本 phase 真正发生语义更新，而不仅是 status 勾选？

---

*Phase directory: `35-protocol-hotspot-final-slimming`*
*Context gathered: 2026-03-18 from roadmap requirements and protocol hotspot audit.*
