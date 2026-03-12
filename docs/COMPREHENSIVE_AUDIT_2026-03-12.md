# Lipro-HASS 全量复核报告（2026-03-12）

> 审计范围：`custom_components/`、`scripts/`、`tests/` 下全部 Python 文件  
> 实际覆盖：377 个 Python 文件（生产 224 / 测试 153）  
> 复核方式：主代理仲裁 + 并行子代理只读复核 + 仓库级静态检查与全量测试  
> 当前状态：本文件为本轮唯一权威审计/收口报告

---

## 1. 结论先行

### 1.1 当前结论

- 仓库已从“高优先级运行风险较多”的状态，收口到“主链稳定、边界清晰、仅剩低优先级治理项”的状态。
- 本轮复核后，**未发现仍然开放的 P0 / P1 真实运行风险**。
- 旧审计里最关键的误差，不是“完全看错”，而是：
  1. 部分结论已被后续代码演进覆盖；
  2. 部分问题属于文档/协议漂移，被误判成运行时崩溃；
  3. 部分问题真实存在，但真实优先级低于原结论。

### 1.2 当前真实优先级

| 优先级 | 主题 | 当前判断 |
|---|---|---|
| P0 | 运行时崩溃 | **无开放项** |
| P1 | 真实运行风险 | **无开放项** |
| P2 | 架构治理 | **本轮已清零，无开放项** |
| P3 | 文档治理 | 历史文档已归档，活跃文档已收敛 |

---

## 1.3 全量覆盖分工

本轮复核按以下 4 个切片覆盖全部 `377` 个 Python 文件：

| 切片 | 覆盖范围 | 文件数 |
|---|---|---:|
| S1 | `custom_components/lipro/core/coordinator/**.py` | 56 |
| S2 | `tests/core/coordinator/**.py` + coordinator 顶层测试 | 19 |
| S3 | `custom_components/lipro/core/**.py`（除 coordinator）+ `tests/core/**.py`（除 coordinator） | 184 |
| S4 | entities / helpers / services / flow / scripts / 其余 tests | 118 |
| **合计** |  | **377** |

主代理负责仲裁与最终修复；子代理负责分片只读巡检；最终结论以仓库级 `ruff` / `mypy` / `pytest` 结果为准。

---

## 2. 问题到底是什么

本轮真正需要处理的，不是“推翻整个架构”，而是把几条已经成型的新架构主线彻底收口：

1. **命令主链要只有一个正式入口**
   - 旧的 `CommandRuntime.send_command()` / `send_batch_commands()` 兼容层会把运行时边界再次拉回旧体系。
   - 现已清理，正式命令入口只保留 `send_device_command()`。

2. **设备刷新要有统一原语，而不是依赖 DataUpdateCoordinator 副作用**
   - 旧实现里 `refresh_devices` facade 走 `async_request_refresh()`，显式刷新不一定真的强制重拉设备快照。
   - 现已收敛到 `Coordinator.async_refresh_devices()`，由 coordinator 统一负责：强制全量快照、状态同步、MQTT 订阅同步、监听器通知。

3. **命令后的刷新与确认学习要由同一条确认链路负责**
   - 旧实现中命令成功后，`CommandRuntime` 已安排 post-refresh；`CoordinatorCommandService` 又额外做 5 秒 confirmation fallback，形成重复刷新。
   - 现已删除服务层重复 fallback，把 post-command refresh policy 收口回命令 runtime / confirmation manager。

4. **确认跟踪逻辑不能只存在于 helper 测试里**
   - `CommandConfirmationTracker` 里的 stale 过滤与 latency 学习原本已设计完成，但未真正接入状态写入主链。
   - 现已在 coordinator 的属性更新回调中接回：先过滤 stale 状态，再观察确认，再写入状态 runtime。

5. **供应商协议约束要显式标注，不要和用户 secret 混淆**
   - `MD5`、签名 key、merchant code、MQTT AES key 不是“可替换配置”，而是上游协议兼容常量。
   - 现已统一通过 `custom_components/lipro/core/utils/vendor_crypto.py` 收口，并在常量处补齐语义说明。

---

## 3. 哪些旧结论已经失真

| 旧结论 | 当前结论 | 说明 |
|---|---|---|
| `StatusRuntime/TuningRuntime 未消费` | **失真** | `custom_components/lipro/core/coordinator/coordinator.py` 已真实消费 `StatusRuntime`；`custom_components/lipro/core/coordinator/services/command_service.py` 已真实消费 `TuningRuntime` |
| `CommandRuntime.send_command()` 是必须修的高危占位 | **已失效** | 本轮直接移除了旧兼容层，正式架构只保留 `send_device_command()` |
| `refresh_devices` facade 可直接代表强制设备重载 | **曾失真，现已修复** | 现由 `custom_components/lipro/core/coordinator/coordinator.py` 的统一刷新原语承载 |
| `硬编码签名材料 = secret 泄露` | **失真** | 真实属性是供应商协议常量，不是部署密钥；风险属于兼容性约束，不是密钥管理失效 |
| `MD5 使用 = 安全缺陷` | **片面** | 这里是供应商协议兼容哈希，不应用于用户密码学安全场景；现已集中封装与注释 |
| `文档中的历史检查清单仍可作为执行真源` | **失真** | 活跃执行信息已吸收到本报告，旧清单已归档 |

---

## 4. 本轮已完成的关键收口

### 4.1 命令架构

- 删除旧命令兼容层与 tests-only 结果类型：
  - `custom_components/lipro/core/coordinator/runtime/command_runtime.py`
  - 已删除 `custom_components/lipro/core/coordinator/runtime/command_result.py`
- 统一正式命令入口为 `send_device_command()`。
- 命令服务不再额外安排 5 秒 fallback，避免与 post-refresh 机制重复。

### 4.2 刷新架构

- 新增统一刷新原语：`custom_components/lipro/core/coordinator/coordinator.py`
- `CoordinatorDeviceRefreshService` 改为直接委托该原语：
  - `custom_components/lipro/core/coordinator/services/device_refresh_service.py`
- `_async_update_data()` 与显式 refresh service 现在共享同一条刷新/同步语义。

### 4.3 命令确认学习

- 将 stale mismatch 过滤与 confirmation latency 学习正式接回状态写入链路：
  - `custom_components/lipro/core/coordinator/coordinator.py`
  - `custom_components/lipro/core/coordinator/runtime/command/confirmation.py`
  - `custom_components/lipro/core/coordinator/runtime/command_runtime.py`

### 4.4 协议兼容约束

- 新增共享 helper：`custom_components/lipro/core/utils/vendor_crypto.py`
- 登录哈希与传输签名统一走共享 helper：
  - `custom_components/lipro/flow/login.py`
  - `custom_components/lipro/core/api/transport_signing.py`
- 供应商常量语义补齐：
  - `custom_components/lipro/const/api.py`

---

## 5. 当前低优先级状态

本轮原先列出的 3 个低优先级治理项已完成：

1. 已删除误导性的 `update_device_online_status()` 死 API；
2. 已退役 `DeviceRuntime` 中未被正式主链消费的 dormant 增量刷新分支；
3. 已对齐 `README_zh.md` 与 `README.md` 的示例章节，消除镜像漂移。

当前未再发现需要立即继续清理的低优先级架构残留；后续工作可以回到正常功能演进与常规代码审查节奏。

---

## 6. 全库验证结果

本轮以仓库当前代码为准完成复核：

- `uv run ruff check .` ✅
- `uv run mypy` ✅ `Success: no issues found in 371 source files`
- `uv run pytest tests/ --ignore=tests/benchmarks -q` ✅ `2053 passed`

这意味着：

- 生产代码、测试代码、类型边界在当前工作树下一致；
- 本轮删除旧兼容层、接回确认学习、重写刷新语义后，没有引入新的仓库级回归；
- 旧审计里“第四批仍未完成”的结论，现已不再成立。

---

## 7. 文档收敛结果

### 7.1 活跃文档

- `docs/COMPREHENSIVE_AUDIT_2026-03-12.md`：当前权威审计/验证报告
- `docs/developer_architecture.md`：当前收敛架构与边界说明
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`：北极星终态设计基准
- `docs/NORTH_STAR_EXECUTION_PLAN_2026-03-12.md`：北极星执行计划、分工与启动批次
- `docs/adr/README.md` + `docs/adr/*.md`：长期生效的架构决策记录

### 7.2 已归档历史文档

- `docs/archive/AUDIT_ISSUES_CHECKLIST_2026-03-12.md`
- `docs/archive/refactor_completion_plan_2026-03-11.md`
- `docs/archive/refactor_residual_audit_2026-03-12.md`
- `docs/archive/TEST_STATUS_2026-03-10.md`

归档原则：
- 保留历史上下文；
- 退出活跃决策层；
- 不再作为当前执行真源。

---

## 8. 最终判断

如果从顶层设计看，本仓库当前已经具备以下特征：

- 命令路径、刷新路径、状态写入路径已经围绕 coordinator 收敛成单一主链；
- 协议兼容约束与运行时安全问题已经被明确区分；
- 测试、类型检查与 lint 与当前实现保持一致；
- 历史审计/重构文档不再与当前实现并行争夺“真源”地位。

因此，**本轮审计后的最终结论是：仓库已完成这一阶段的高优先级债务清理，可以从“风险修补”切换到“低优先级治理与演进优化”。**
