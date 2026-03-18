# Phase 27 Context

**Phase:** `27 Hotspot slimming, dependency strategy and maintainability follow-through`
**Milestone:** `v1.3 Quality-10 Remediation & Productization`
**Date:** `2026-03-17`
**Status:** `Ready for planning`
**Source:** `Phase 25` 总路线图 + `25.2 / 26` closeout + 针对 coordinator forwarders / 测试巨石的热点复审

## Why Phase 27 Exists

`25.1 / 25.2 / 26` 已把 correctness、formal telemetry surface 与 release trust chain 收口，但仓库仍留着一簇明显的 maintainability hotspot：

1. `Coordinator` 继续对外暴露一串纯委派到 `protocol_service` 的 forwarding methods；
2. schedule / diagnostics / OTA consumers 仍把这些 forwarders 当正式 surface；
3. `Phase C / H4` 之类历史迁移叙事仍残留在正式 runtime 代码；
4. `tests/core/test_init.py`、`tests/meta/test_governance_guards.py` 依旧过大，局部修改时回归面过宽。

## Goal

1. 让 runtime/protocol external consumers 显式依赖 `coordinator.protocol_service`，而不是继续经 coordinator 顶层 pure forwarders 取能力。
2. 删除已无生产消费者的 protocol forwarders，顺手清理 runtime 代码中的 phase residue / 历史叙事噪声。
3. 把 hotspot 对应的 baseline / dependency / residual truth 同步到位，确保 phase 27 不只是代码搬家。
4. 继续拆分测试巨石，把 service-handler / governance-closeout 主题拆到更稳定的专题文件，同时同步 `TESTING.md` 与 toolchain truth。

## Decisions (Locked)

- 本 phase 只沿现有 `Coordinator -> protocol_service -> LiproProtocolFacade` 正式主链收口；不得新建第二 root、事件总线或 DI story。
- `protocol_service` 是 runtime 对外的正式 protocol capability surface；schedule / diagnostics / OTA consumers 不再合法化 coordinator 顶层纯转发方法。
- 允许保留 entity-facing runtime helpers（如 `get_device` / `register_entity` / `get_device_lock`），因为它们不是 protocol-forwarder 家族。
- 本 phase 的测试拆分以“降低认知负担、维持门禁强度”为准，不为了文件数好看而复制第二套 truth。

## Non-Negotiable Constraints

- 不得把 `Coordinator.client`、`entry.runtime_data` 或 protocol child-facade internals 重新合法化为 control/service surface。
- 不得把 `Phase 27` 扩成新的 correctness 或 trust-chain phase；snapshot correctness 与 release productization 已在 `25.1 / 26` 收口。
- 不得为了拆测试引入 helper-only drift；若新增测试文件，必须同步 `TESTING.md` 与 `tests/meta/test_toolchain_truth.py`。
