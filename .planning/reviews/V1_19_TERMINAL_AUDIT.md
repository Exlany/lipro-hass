# v1.19 Terminal Audit

## Scope

本轮审计覆盖：

- `custom_components/lipro/**` 生产代码热点与 formal-home 边界
- `tests/**` 的巨石测试残留、governance guards、fixture authority 与 current-story 漂移面
- `.planning/**`、`docs/**`、`README*`、`pyproject.toml`、CI / release / issue templates 等文档与配置真源

## Verdict

仓库在 `v1.18 / Phase 70` 归档后已无明显第二正式主链回流；主要问题集中在：

1. 少数高密度长流程仍跨越 entity/runtime/protocol/test concerns
2. current-route / latest-archive truth 在文档与守卫中存在多点字面同步成本
3. 测试拓扑虽持续 topicize，但 hotspot / route guards 还缺少下一轮 focused freeze
4. 文档与治理面整体健康，但 `no active milestone route` 已不再适合作为后续执行起点

## Repo-Wide Findings

### 代码与架构

- `custom_components/lipro/entities/firmware_update.py` 仍同时承担安装仲裁、后台 OTA 刷新、错误翻译与 entity 状态写回。
- `custom_components/lipro/core/api/diagnostics_api_ota.py`、`custom_components/lipro/core/anonymous_share/share_client_submit.py`、`custom_components/lipro/core/api/request_policy_support.py`、`custom_components/lipro/core/coordinator/runtime/command_runtime.py` 仍存在高密度长函数。
- 未发现 protocol / runtime / control 第二正式根回流；问题更多是热点切薄与 formal helper home 继续收口。

### 测试与治理

- `tests/core/test_share_client.py`、`tests/core/coordinator/runtime/test_command_runtime.py` 等套件仍偏大，但已具备进一步 topicization 的基础。
- current-route / latest-archive truth 在多份 meta tests 中存在重复字面量，维护成本偏高。
- phase-hotspot guards 已有良好 precedent，但 `Phase 71` 尚无专属 no-growth/freeze contract。

### 文档与配置

- 当前 latest archived closeout pointer 仍应指向 `.planning/reviews/V1_18_EVIDENCE_INDEX.md`。
- 但 current-story 不应继续停留在“no active milestone route”；应升级为 `v1.19 / Phase 71 complete / closeout-ready`。
- 文档/配置总体一致，未见阻断性 drift；改动重点是 current-route 投影，而不是重写 archive truth。

## Phase 71 Chosen Scope

本 phase 只做“高收益、低漂移、可一次性验证”的收口：

1. 切薄 OTA / firmware-update / anonymous-share / request-pacing / command-runtime 长流程
2. 单点化 current-route / latest-archive truth 的测试消费面
3. 把 `v1.19 / Phase 71` 落成 closeout-ready current route，并保留 `v1.18` 作为 latest archived baseline
4. 新增 focused hotspot/route guards，阻止本轮 touched scope 反弹

## Deliberately Recorded, Not Reopened Here

以下问题已完成审计记录，但本轮不做大范围重写，以避免在无必要时扩大回归面：

- `Coordinator` 运行根的更深层 bootstrap/builder 重组
- `runtime_access` family 的 test-aware probing 进一步退役
- `EntryLifecycleController` / `EntryLifecycleSupport` 更彻底的编排归并
- `service_router` 四层转发族的 service-family 重切
- `services/diagnostics/helpers.py` 与 `helper_support.py` 更大范围去重
- `LiproEntity` 运行面策略下沉与 `schedule.py` formal runtime surface 化
- auth `Legacy` snapshot / compatibility wrapper 的更彻底退役

这些候选已被纳入本审计结论，可作为后续 milestone 的明确 seed，而不是 silent residual。
