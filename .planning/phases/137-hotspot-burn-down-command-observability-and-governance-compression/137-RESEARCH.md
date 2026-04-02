# Phase 137 Research

## Dual-Audit Synthesis

- `v1.41` archived audit 已确认：当前仓库正式架构方向正确，主要问题不是缺少架构，而是 **mega-facade/manual delegation wall、auth hotspot 过厚、device relay wall、stringly command grammar、connect-status failure semantics、derived-governance cost**。
- 补充审阅确认：在开源/治理侧，当前最大成本已从“架构不清”转为“执行痕迹未真正退场、真源/派生链扇出过大、部分 guard 只验证出现过而不验证角色正确”。

## Repo-wide Metrics Snapshot

- Python files in repo-visible scope: `762`
- Docs files: `27`
- YAML files: `5`
- JSON files: `41`
- `.planning/phases/` Markdown assets: `1654`
  - `PLAN`: `516`
  - `CONTEXT`: `146`
  - `RESEARCH`: `127`
- `PROMOTED_PHASE_ASSETS.md` allowlisted long-term assets: `523`
  - `PLAN/CONTEXT/RESEARCH`: `0`

## Architectural Read of Hotspots

### Code hotspots
- `rest_facade.py` 与 `protocol/facade.py` 已从 mixin 聚合转为显式组合，但仍保留大量静态 method binding 与 property forwarding；问题已从“错误架构”变成“formal root discoverability / rebinding seam / manual delegation cost”。
- `auth/manager.py` 的问题不是命名差，而是 credential seed、token state、adaptive expiry、refresh lock、re-login fallback 仍聚在一个 manager 内，导致 policy continuation 很容易再次堆叠。
- `device/device.py` 通过 `_component_property()` / `_component_method()` 降低样板，但 outward relay taxonomy 仍过大，需限制继续膨胀。
- `command/dispatch.py` 已有 `CommandRoute`/`CommandDispatchPlan`，说明 typed route 已开始出现；下一步应继续把 fallback / trace / route semantics 数据化，而不是保留 stringly command grammar 到处扩写。
- `status_service.py::query_connect_status()` 目前把 API failure、wrapped non-mapping payload 与真实空结果都压成 `{}`；这对调用侧观测/诊断不够诚实。

### Governance / open-source hotspots
- `.planning` 体系已经很强，但 live selector、registry、verification matrix、developer/runbook note 与 tests/meta 之间的派生同步成本偏高。
- execution trace 规则与仓库现实已分叉：规则说 non-promoted `PLAN/CONTEXT/RESEARCH` 只是执行痕迹，但仓库长期保留并被主入口反向引用。
- semantic guard 仍有 blind spot：runbook 类文档即便同时保留新旧 canonical bullet，只要“最新路径 somewhere 存在”，相关 tests 仍可能通过。

## Planning Recommendation

- 本 phase 采用 3-plan 单 phase 结构最合理：
  1. `137-01` governance/docs/test contract hardening。
  2. `137-02` protocol/rest/auth 高优先 hotspot 分解。
  3. `137-03` device/command/observability 语义收口。
- 这样既能保证 `$gsd-execute-phase 137` 一次跑完整 phase，又避免把治理收口和代码 burn-down 混成不可验证的大杂烩。
