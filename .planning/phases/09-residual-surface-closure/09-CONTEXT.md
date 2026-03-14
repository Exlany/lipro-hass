# Phase 9 Context

**Phase:** `9 Residual Surface Closure`
**Milestone:** `v1.1 Protocol Fidelity & Operability (residual closure extension)`
**Date:** 2026-03-14
**Status:** Proposed

## Why Phase 9 Exists

`docs/COMPREHENSIVE_AUDIT_2026-03-13.md` 已确认主线可运行且 `Phase 8` 已完成，但仍保留一组不该长期合法化的 residual surfaces：

- protocol root 仍被 child surface 隐式扩面；
- concrete transport 仍通过 `raw_client` compat seam 暴露；
- `Coordinator.devices` 仍暴露 live mutable dict；
- outlet power 仍通过 `device.extra_data["power_info"]` 旁写；
- 多个根/包级 compat export 继续放大历史语义。

这些问题未必立即造成 P0，但会削弱“唯一正式 root / 单一 truth chain / residual 可删除”的北极星裁决，因此必须收口到显式、可验证、可删除的最小集合。

## Goal

1. 收窄 `LiproProtocolFacade` 的正式 public surface，使 protocol root 的 contract 显式可裁决；
2. 将 compat shells / concrete transport exposure 压缩到明确、可计数、可删除的 transitional seam；
3. 把 runtime 设备访问改成只读 view 或正式 service contract，避免 live mutable dict 泄露；
4. 把 outlet power 从 `extra_data` 旁写迁移到正式 primitive，并让 entity/diagnostics/runtime 共用同一真源；
5. 同步 residual/governance/docs/guards，防止 residual surface 回流。

## Decisions (Locked)

- **正式 protocol root 不变**：`LiproProtocolFacade` 继续是唯一正式 protocol-plane root。
- **compat 只能显式存在**：如某个 compat seam 仍需保留，必须被限定在显式 transitional home，并有 delete gate；不得再从根模块/包级出口反向定义正式 surface。
- **runtime 只读优先**：对设备集合的跨层访问优先使用只读 view 或 formal service，而不是暴露 live mutable dict。
- **power truth 必须收口**：outlet power 的正式读取路径必须统一；若需要迁移兼容，只能作为过渡读适配，不能继续把 `extra_data` 当正式真源。
- **治理与实现同相位收口**：`PUBLIC_SURFACES / RESIDUAL_LEDGER / KILL_LIST / VERIFICATION_MATRIX / FILE_MATRIX` 与相关 guards 必须在同一 phase 内同步。

## Non-Negotiable Constraints

- 不得引入第二条 protocol/runtime 主链；
- 不得为了兼容继续扩大 formal public surface；
- 不得用文档声明掩盖代码事实；
- 不得破坏 `Phase 8` exporter/evidence truth chain；
- 所有收口都必须有 targeted regression proof，并在必要时补 meta/public-surface guards。
