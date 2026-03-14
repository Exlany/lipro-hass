# Phase 13: Explicit Domain Surface, Governance Guard Hardening & Hotspot Boundary Decomposition - Context

**Gathered:** 2026-03-14
**Status:** Executed

<domain>
## Phase Boundary

本 phase 只处理三件高杠杆事情：
1. 设备域动态表面收口；
2. runtime/status 热点 helper 化与内部术语收口；
3. 对外治理资产结构化守卫与文档同步。
</domain>

<decisions>
## Locked Decisions

- 不为了测试保留生产 compat 冗余；
- `LiproDevice` / `DeviceState` 必须去掉动态 `__getattr__`；
- `DeviceState` 继续保留叶子属性，但改成显式 property；
- `LiproDevice` 的 façade 表面改成显式 property / method 集合，而不是运行时动态委托；
- runtime 内部把协议协作者逐步叫作 `protocol`，但不强行破坏已有 `Coordinator.client` 对外消费点；
- 治理守卫优先断言结构与资产存在/联动，而不是绑死措辞细节。
</decisions>

<specifics>
## Specific Ideas

- 删除 `custom_components/lipro/core/device/device_delegation.py`；
- 让 `tests/core/device/test_device.py` 与 `tests/core/device/test_state.py` 直接锁定“无 `__getattr__`”；
- 为 README / README_zh 显性补链 `CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md`、`CODE_OF_CONDUCT.md`、`quality_scale.yaml`、`.devcontainer.json`；
- 用 `tests/meta/test_governance_guards.py` 校验 manifest/codeowners、known limitations 计数与 devcontainer interpreter truth。
</specifics>

<deferred>
## Deferred Ideas

- `LiproMqttClient` legacy naming 的最终退役；
- `service_router.py` 的更大规模拆分；
- 超大测试文件物理切分。
</deferred>
