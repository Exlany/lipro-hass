# Residual Ledger

## Active Residual Families

| Family | Current example | Owner phase | Residual owner | Exit condition |
|--------|------------------|-------------|----------------|----------------|
| API compat wrappers | `custom_components/lipro/core/api/client.py` 中 `_build_compat_list_payload`、`get_device_list`、`query_iot_devices`、`query_outlet_devices`、`query_group_devices`，以及 `power_service.py` 的多行 `{"data": ...}` shaping | Phase 2 | `02-04 compat shell cleanup`（API/Protocol owner 主责，Runtime/Coordinator owner 迁移消费者） | `LiproRestFacade` canonical outputs 被 direct consumers 接受，compat wrappers 从 `LiproClient` / helper 层移除 |
| API mixin inheritance | `_ClientBase`、`_ClientPacingMixin`、`_ClientAuthRecoveryMixin`、`_ClientTransportMixin`、`_ClientEndpointsMixin` 与 endpoint mixin classes | Phase 2 | `02-02 façade + transport rewrite`（API/Protocol owner） | `ClientSessionState`、`TransportExecutor`、`AuthRecoveryCoordinator`、endpoint collaborators 落地，生产/测试不再依赖 mixin 类 |
| Legacy public names | `custom_components.lipro.core.api.LiproClient` 及其经 `custom_components.lipro.core` / `custom_components.lipro` 的再导出 | Phase 2 | `02-04 public-surface demotion`（API owner 收口；Entry/Auth owner 与 Runtime owner 迁移下游） | `PUBLIC_SURFACES.md` 与 direct consumer tests 改以 `LiproRestFacade` / unified protocol surface 为正式根；`LiproClient` 仅剩可删除 compat shell |
| Control-plane scatter | diagnostics / system_health / service wiring 分散 | Phase 3 | `Phase 3 control-plane closeout` | control plane public surface 收口 |
| Capability duplication | domain / entity / platform 多处表达 | Phase 4 | `Phase 4 capability registry closeout` | capability registry 成为单一真源 |

## Rules

- 新发现的 residual 必须登记，不能只在对话中提到。
- 每条 residual 至少要给出 **当前样本、owner、exit condition**，否则不算正式登记。
- 任何 residual 若进入第二个 phase 仍未收敛，必须解释为何继续存在。
- compat / mixin / legacy public-name residual 只允许存在于显式 compat shell / adapters 中，不得继续散落在正式 public surface 与业务逻辑内部。

## Phase 01 Closeout Review

- 已复核当前 residual families 与 Phase 01 baseline 的关系：本阶段只锁定 protocol boundary truth，不试图提前消除 residual。
- 本次**无新增 residual family**；canonical snapshots 与 immutable constraints 没有引入新的桥接层或临时兼容结构。
- `API compat wrappers` 与 `API mixin inheritance` 继续由 Phase 2 负责清理；Phase 01 仅为其提供不可漂移的 contract 输入边界。

## Phase 02 / `02-01` Residual Delta

- 为 `API compat wrappers`、`API mixin inheritance` 补齐了明确 owner 与 file-level current examples。
- 新增 `Legacy public names` residual family，用于约束 `LiproClient` 作为 public root name 的过渡存在方式。
- 本计划只做登记，不关闭 residual；真正清退动作留给 `02-02` ~ `02-04`。
