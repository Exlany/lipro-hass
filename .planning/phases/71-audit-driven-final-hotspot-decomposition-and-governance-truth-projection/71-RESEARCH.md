# Phase 71 Research

## Inputs

- `.planning/reviews/V1_19_TERMINAL_AUDIT.md`
- repo-wide 子代理审计：代码架构、测试/治理、文档/配置三条并行视角
- 已验证的 `v1.18` archive baseline 与 `Phase 70` closeout assets

## Findings That Directly Drive Implementation

### Hotspot Selection

以下热点具备“可局部切薄 + outward behavior 可保持稳定 + 已有 focused tests”的共同特征：

- `firmware_update.async_install`
- `diagnostics_api_ota._query_primary_ota_rows`
- `diagnostics_api_ota.query_ota_info_with_outcome`
- `share_client_submit.submit_share_payload_with_outcome`
- `request_policy_support.throttle_change_state`
- `command_runtime._execute_device_command`
- `command_runtime._verify_delivery`

### Governance Selection

最值得在本轮同做的治理动作不是“再写一层 prose”，而是：

- 用 shared test constants 降低 current-route / latest-archive literal drift
- 把 `v1.19 current route` 写入 planning truth，同时继续保留 `v1.18` archive pointer
- 增加 `Phase 71` focused hotspot/route guards，直接冻结本轮 touched scope

## Rejected Alternatives

- **大规模重构 coordinator / lifecycle / router**：收益高，但回归面过大，不适合与 current-route activation 同轮合并。
- **直接归档 v1.19**：用户要求本轮做到 `$gsd-next`；更诚实的终态是 `Phase 71 complete / closeout-ready`，下一步路由到 `$gsd-complete-milestone v1.19`。
- **继续维持 no-active-route**：与实际已执行 phase 的 current truth 冲突，会把 `v1.19` 变成 conversation-only work。
