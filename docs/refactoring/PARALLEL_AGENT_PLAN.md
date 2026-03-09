# 🜏 Lipro-Hass 主代理主控重构计划

## 📋 目标

本计划用于指导 `lipro-hass` 的渐进式重构，目标聚焦于四类已确认问题：

1. Coordinator mixin 继承链过深
2. `Any` 类型使用过多
3. `LiproDevice` / `LiproMqttClient` 职责过重
4. MQTT 客户端关键路径中的宽泛异常处理

本计划采用 **主代理主控 + 子代理协作** 模式执行，而不是依赖额外的 Python 编排脚本。

---

## 🧭 执行模型

### 主代理职责

主代理（当前会话）负责：

- 选择当前执行波次（wave）
- 将任务分配给不重叠写入范围的子代理
- 审核子代理结果并做最终集成
- 在跨模块修改时统一裁决
- 运行针对性验证命令
- 更新阶段状态与总结

### 子代理职责

子代理只负责：

- 在指定写入范围内完成改动
- 严格遵守任务契约文件 `docs/refactoring/tasks/*.json`
- 在触及未授权文件前先回报主代理
- 提供精简的结果说明与剩余风险

### 本计划明确不依赖

以下机制不作为当前默认执行方式：

- `scripts/orchestrator.py` 主控脚本
- `scripts/agent_worker.py` worker 脚本
- `tmux` / `screen` / `nohup` 人工编排
- 文件锁脚本或额外心跳守护进程

如确有需要，主代理可临时使用这些脚本做辅助，但 **不作为计划前提**。

---

## 🪓 并行原则

### 1. 写入范围先于任务内容

每个子代理优先按 `files` 字段定义写入范围；若任务说明与写入范围冲突，以主代理重新裁决后的范围为准。

### 2. 一次只并行独立切片

只有当两个任务满足以下条件时才允许并行：

- 写入文件不重叠
- 验证命令互不阻塞
- 失败时可独立回滚

### 3. 高耦合模块最后收敛

`custom_components/lipro/core/coordinator/` 属于高耦合区域，避免一开始并行大拆；应在外围问题收敛后，由主代理主导集成。

### 4. 验证命令统一使用 `uv run`

所有 Python 相关验证命令统一使用：

- `uv run pytest ...`
- `uv run mypy ...`
- `uv run ruff check ...`
- `uv run python ...`

---

## 🌊 波次规划

## Wave 0：主代理准备

**执行者**：主代理  
**目标**：建立基线、确认范围、冻结接口假设

### 输出

- 基线结论与风险列表
- 各子代理写入边界
- 当前波次的验证命令集合
- 可选状态文件：`docs/refactoring/STATUS.md`

### 主代理检查项

- 当前分支/工作树干净可控
- `uv sync --frozen --extra dev` 可用
- 相关测试与类型检查命令能在本地运行
- `docs/refactoring/tasks/*.json` 与当前策略一致

---

## Wave 1：快速收益

**目标**：先处理低风险、高收益问题，为后续结构重构清障。

### 并行分配

| 子代理 | 任务契约 | 建议写入范围 | 目标 |
|---|---|---|---|
| Agent-1 | `docs/refactoring/tasks/agent-1-exceptions.json` | `custom_components/lipro/core/mqtt/`, `pyproject.toml` | 收窄 MQTT 关键路径异常处理 |
| Agent-2 | `docs/refactoring/tasks/agent-2-types.json` | `custom_components/lipro/core/command/result.py`, `custom_components/lipro/services/diagnostics_service.py`, `custom_components/lipro/core/api/diagnostics_service.py`, `custom_components/lipro/core/api/schedule_service.py` | 降低高频 `Any` 热点 |
| Agent-6 | `docs/refactoring/tasks/agent-6-testing.json` | `tests/`, `.github/workflows/ci.yml`, `pyproject.toml` | 为 Wave 1/2 提供回归保护 |

### 集成门槛

- MQTT 相关测试无回归
- 触达文件的 `mypy`/`ruff` 不退化
- 覆盖率要求不下降
- 不引入新的公共接口破坏

---

## Wave 2：职责分离

**目标**：拆分两个超大类，但保持 API/实体行为兼容。

### 并行分配

| 子代理 | 任务契约 | 建议写入范围 | 目标 |
|---|---|---|---|
| Agent-4 | `docs/refactoring/tasks/agent-4-device-model.json` | `custom_components/lipro/core/device/`, `tests/core/device/` | 拆分 `LiproDevice` |
| Agent-5 | `docs/refactoring/tasks/agent-5-mqtt-client.json` | `custom_components/lipro/core/mqtt/`, `tests/core/mqtt/` | 拆分 `LiproMqttClient` |

### 注意事项

- Agent-4 不直接改 Coordinator 主流程
- Agent-5 不擅自改实体层 API
- 任何跨 `device/` 与 `mqtt/` 的接口变更，需先回报主代理

---

## Wave 3：架构收敛

**目标**：把高耦合的 Coordinator 从继承驱动逐步迁移到组合/服务协作。

### 执行方式

该波次默认 **主代理主导**，子代理提供局部实现或原型：

| 执行者 | 任务契约 | 建议范围 | 目标 |
|---|---|---|---|
| Agent-3 | `docs/refactoring/tasks/agent-3-architecture.json` | `custom_components/lipro/core/coordinator/protocols.py`, `custom_components/lipro/core/coordinator/services/` | 定义协议与服务骨架 |
| 主代理 | 同上收敛实现 | `custom_components/lipro/core/coordinator/` | 处理服务整合、迁移顺序、兼容层 |
| Agent-6 | `docs/refactoring/tasks/agent-6-testing.json` | `tests/core/coordinator/`, `tests/integration/` | 增补迁移保护测试 |

### 原则

- 不直接一次性删除旧 mixin
- 先引入协议/服务，再迁移调用方
- 保留兼容层，直到替换完成后再清理旧代码

---

## Wave 4：清理与验收

**目标**：合并遗留兼容层、补文档、完成全量验证。

### 交付物

- 架构对比文档
- 迁移指南
- 针对重构区域的最终测试报告
- 风险与后续 TODO 清单

---

## 📦 任务契约使用方式

`docs/refactoring/tasks/*.json` 继续作为 **任务契约文件** 使用，但解释规则如下：

### 保留字段

- `description`：任务目标
- `input_files`：主要上下文来源
- `checkpoints`：建议的原子提交粒度
- `files`：默认写入范围
- `validation.command`：该检查点完成后的建议验证命令
- `success_criteria`：任务完成标准

### 解释规则

- `output_branch` / `base_branch` 视为 **逻辑工作流标签**，不强制要求创建真实 Git 分支
- `notify_main_agent` 语义统一解释为 **通知主代理**
- `reporting` 字段仅表示建议进度粒度，不要求额外心跳脚本

---

## ✅ 验证基线

### 最小验证

每个检查点至少满足以下之一：

- `uv run pytest <target>`
- `uv run mypy <target>`
- `uv run ruff check <target>`

### 波次结束验证

建议按从小到大执行：

```bash
uv run pytest tests/core/mqtt -v
uv run pytest tests/core/device -v
uv run pytest tests/core -v -k 'coordinator or mqtt or device'
uv run mypy
uv run ruff check .
```

### 全量验收

```bash
uv run pytest tests/ -v --cov=custom_components/lipro --cov-report=term-missing
uv run mypy
uv run ruff check .
```

---

## ⚠️ 风险控制

### 何时禁止并行

遇到以下情况时，主代理应停止并行、改为串行收敛：

- 多个任务同时需要改 `custom_components/lipro/core/coordinator/`
- 需要改动公共数据结构并波及实体、服务、测试三层
- 需要改变对外暴露的服务接口或配置流行为

### 何时回滚到上一个检查点

- 目标测试集持续失败
- 类型检查明显退化
- 子代理超出写入边界
- 同一问题两次修复仍未稳定

---

## 🎯 完成标准

### 代码质量

- 关键路径测试通过
- 变更区域的 `mypy` 检查通过
- 变更区域的 `ruff` 检查通过
- 不新增无说明的宽泛异常处理
- `Any` 热点文件数量明显下降

### 架构质量

- Coordinator 逐步从继承耦合转向组合协作
- `LiproDevice` / `LiproMqttClient` 职责切分更清晰
- 新增协议/服务边界可独立测试

### 文档质量

- 每个波次结束后有简短总结
- 最终有迁移说明和风险清单

---

## 🗂️ 建议的主代理调度顺序

1. 先执行 Wave 1 并完成收敛
2. 再执行 Wave 2 的 `device/` 与 `mqtt/` 拆分
3. 最后进入 Wave 3 做 Coordinator 级整合
4. 所有跨切面问题都由主代理统一收束

---

⛧ 虚空低语：此计划不再要求额外编排平台，而是以主代理为中枢、以任务契约为边界、以小步迭代为秩序。混沌可控，重构可行。 🜏
