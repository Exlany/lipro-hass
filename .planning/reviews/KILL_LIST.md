# Kill List

## Candidate Removals (Phase 02 Registered)

| Target | Current carrier | Owner | Earliest delete phase | Delete when | `02-01` status |
|--------|------------------|-------|-----------------------|-------------|----------------|
| `_ClientBase` | `custom_components/lipro/core/api/client_base.py` | `02-02 façade + transport rewrite` | Phase 2 | 生产与测试都不再需要 mixin typing spine | 已登记，未删除 |
| `_ClientPacingMixin` | `custom_components/lipro/core/api/client_pacing.py` | `02-02 façade + transport rewrite` | Phase 2 | pacing / busy-retry 状态归入 `RequestPolicy` / transport chain，测试不再实例化 mixin host | 已登记，未删除 |
| `_ClientAuthRecoveryMixin` | `custom_components/lipro/core/api/client_auth_recovery.py` | `02-02 façade + transport rewrite` | Phase 2 | auth classification / refresh / replay 迁入 `AuthRecoveryCoordinator`，私有路径不再被 patch | 已登记，未删除 |
| `_ClientTransportMixin` | `custom_components/lipro/core/api/client_transport.py` | `02-02 façade + transport rewrite` | Phase 2 | transport 入口完全改为 `TransportExecutor` + `TransportCore` 显式组合 | 已登记，未删除 |
| `_ClientEndpointsMixin` | `custom_components/lipro/core/api/endpoints/__init__.py` | `02-03 endpoint collaborator migration` | Phase 2 | façade 只装配显式 endpoint collaborators，不再继承聚合 mixin | 已登记，未删除 |
| legacy endpoint mixin classes | `custom_components/lipro/core/api/endpoints/{auth,commands,devices,misc,payloads,schedule,status}.py` | `02-03 endpoint collaborator migration` | Phase 2 | 各 endpoint / payload helper 已迁成 explicit collaborators / normalizers | 已登记，未删除 |
| `_build_compat_list_payload` | `custom_components/lipro/core/api/client.py` | `02-04 compat shell cleanup` | Phase 2 | direct consumers 不再要求 `{"data": [...]}` envelope | 已登记，未删除 |
| legacy compat wrapper methods | `custom_components/lipro/core/api/client.py::{get_device_list,query_iot_devices,query_outlet_devices,query_group_devices}` | `02-04 compat shell cleanup` | Phase 2 | runtime / tests 改用 canonical façade outputs 或统一 compat adapter |
| `LiproClient` 作为正式 REST root name | `custom_components/lipro/core/api/__init__.py` 及其再导出链 | `02-04 public-surface demotion`（与 Phase 2.5 handoff 对齐） | Phase 2.5+ | `PUBLIC_SURFACES.md`、downstream imports 与 direct consumer tests 已切换到 `LiproRestFacade` / unified protocol surface | 已登记，未删除 |
| 多行 power payload 的 compat wrapping | `custom_components/lipro/core/api/power_service.py` | `02-04 compat shell cleanup` | Phase 2 | power helper 只返回 canonical rows；兼容 envelope 仅存在于 compat shell | 已登记，未删除 |

## Deletion Gate

删除前必须满足：
1. 下游消费者已迁移。
2. contract / regression tests 通过。
3. residual ledger 已关闭对应条目。
4. summary 明确记录是“正式删除”还是“仅登记、不删除”。

## Phase 01 Closeout Review

- 已检查 kill list 与 Phase 01 baseline 产物的关系，本次**无新增删除项**。
- `_Client*Mixin` 与 compat wrappers 仍是后续 Phase 2 的主要清理对象；Phase 01 只补足它们必须遵守的 contract baseline。
- canonical snapshots、immutable constraints 与 phase summaries 属于治理资产，不进入删除候选。

## Phase 02 / `02-01` Registration Note

- 本计划只做 kill candidate 登记与删除门槛澄清，不执行任何生产代码删除。
- mixin inheritance、compat wrappers、legacy public names 已从“口头债务”升级为文件级 kill targets。
- 若后续 `02-02` ~ `02-04` 没有实际删除动作，summary 必须说明仍阻塞于哪个 direct consumer / public surface。
