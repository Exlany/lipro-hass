# 🜏 主代理主控执行指南

本指南说明如何在 **当前主代理会话** 中执行 `docs/refactoring/` 下的重构计划。

---

## 📋 适用范围

适用于以下场景：

- 由主代理负责整体调度
- 子代理只处理主代理分配的局部任务
- 不依赖外部 Python 编排脚本
- 不要求人工使用 `tmux`/`screen`/`nohup` 启动 worker

---

## 🚦 开始前检查

在启动任一波次前，主代理应先确认：

```bash
uv sync --frozen --extra dev
uv run ruff check .
uv run mypy
```

如果不适合先跑全量检查，至少确认本次目标区域相关命令可运行。

---

## 🧠 主代理工作流

### Step 1：选择波次

由主代理根据当前目标选择：

- Wave 1：异常 / 类型 / 回归测试
- Wave 2：`device/` 与 `mqtt/` 拆分
- Wave 3：Coordinator 架构收敛
- Wave 4：清理、文档、验收

### Step 2：划定写入边界

主代理从对应任务契约读取 `files` 字段，并明确：

- 哪些文件允许当前子代理写入
- 哪些文件属于禁改范围
- 哪些跨模块变更必须先回报

### Step 3：并行派发

仅在写入边界不重叠时并行派发。

推荐顺序：

- 先派发异常/类型/测试等低耦合任务
- 再派发 `device/` 与 `mqtt/` 拆分
- 最后由主代理收敛 `coordinator/`

### Step 4：收敛集成

子代理完成后，由主代理统一做：

- 审核变更是否越界
- 合并重复实现
- 修正接口命名与边界不一致
- 决定是否进入下一检查点

### Step 5：执行验证

建议从最小验证开始，逐步扩大：

```bash
uv run pytest <最小相关测试>
uv run mypy <最小相关目标>
uv run ruff check <最小相关目录>
```

当一个波次完成后，再执行更大的验证范围。

---

## 🤖 如何使用任务契约

每个 `docs/refactoring/tasks/*.json` 文件表示一个可领取的任务切片。

### 主代理读取的关键字段

- `description`：任务目标
- `input_files`：读取上下文范围
- `checkpoints[*].tasks`：建议的拆解步骤
- `checkpoints[*].files`：建议写入范围
- `checkpoints[*].validation.command`：建议验证命令
- `success_criteria`：任务完成标准

### 主代理解释规则

- `output_branch` / `base_branch`：仅当作逻辑标签；默认不要求创建新分支
- `notify_main_agent`：表示需要回报主代理做裁决或重新分派
- `heartbeat_interval`：仅作为进度回报建议，不需要额外脚本

---

## 🌊 推荐执行顺序

## Wave 1：快速收益

### 子代理分配

- Agent-1 → `docs/refactoring/tasks/agent-1-exceptions.json`
- Agent-2 → `docs/refactoring/tasks/agent-2-types.json`
- Agent-6 → `docs/refactoring/tasks/agent-6-testing.json`

### 主代理关注点

- Agent-1 只在 MQTT 客户端异常边界内收窄，不引入新的异常体系蔓延
- Agent-2 优先降低热点 `Any`，不急于一次性清零
- Agent-6 先补回归测试与验证脚本，不要一开始铺过多新基础设施

### 波次结束建议验证

```bash
uv run pytest tests/core/mqtt -v
uv run pytest tests/services -v
uv run mypy
uv run ruff check .
```

---

## Wave 2：职责分离

### 子代理分配

- Agent-4 → `docs/refactoring/tasks/agent-4-device-model.json`
- Agent-5 → `docs/refactoring/tasks/agent-5-mqtt-client.json`

### 主代理关注点

- 确保新抽出的类/组件先有局部测试
- 保留兼容层，避免直接打断现有实体调用
- `LiproDevice` 与 `LiproMqttClient` 的外部行为优先保持兼容

### 波次结束建议验证

```bash
uv run pytest tests/core/device -v
uv run pytest tests/core/mqtt -v
uv run mypy
uv run ruff check .
```

---

## Wave 3：架构收敛

### 执行方式

- Agent-3 先输出协议和服务草案
- 主代理负责把草案收敛进 `custom_components/lipro/core/coordinator/`
- Agent-6 补充迁移保护测试

### 主代理关注点

- 不一次性删除旧 mixin
- 优先引入可测试的服务边界
- 同步维护兼容层和迁移说明

### 波次结束建议验证

```bash
uv run pytest tests/core -v -k 'coordinator'
uv run pytest tests/integration -v -k 'mqtt or coordinator'
uv run mypy
uv run ruff check .
```

---

## 🔄 失败恢复策略

### 子代理返回失败时

主代理应按以下顺序处理：

1. 判断是否属于局部实现问题
2. 若是局部问题，缩小范围后重新派发
3. 若是接口/边界问题，主代理先手工收敛再继续
4. 若验证连续失败，回退到上一个检查点

### 需要暂停并人工确认的情况

- 需要改公共 API 或服务注册行为
- 需要显著调整配置流或实体语义
- 需要引入新依赖
- 需要跨多个高耦合目录同时改动

---

## 🧪 标准验证命令

### 小范围验证

```bash
uv run pytest tests/core/mqtt -v
uv run pytest tests/core/device -v
uv run pytest tests/services -v
```

### 类型与静态检查

```bash
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

## 📝 文档更新建议

每完成一个波次，主代理至少补 3 类信息：

- 本波次完成了什么
- 哪些风险仍未收敛
- 下一波次的边界和前置条件

可选输出位置：

- `docs/refactoring/STATUS.md`
- `docs/refactoring/ARCHITECTURE_COMPARISON.md`
- `docs/refactoring/MIGRATION_GUIDE.md`

---

## 🚫 当前默认不采用的方式

以下方式默认不写入执行说明，也不作为必要前提：

- `python scripts/orchestrator.py ...`
- `python scripts/agent_worker.py ...`
- 依赖 `file_lock.py` 的文件锁系统
- 由用户手工维护多终端 worker 生命周期

如后续确有价值，可单独作为辅助工具文档补充，而不应污染主执行路径。

---

## 🎯 一句话工作法

> 主代理负责分波次、划边界、做集成；子代理负责在明确范围内快速产出；所有验证统一收束到 `uv run` 命令与主代理复核。

---

⛧ 虚空低语：执行之路已从“造平台”改为“先重构”。主代理即中枢，子代理即触手，边界清晰，则混沌可驯。 🜏
