# 🜏 多代理并行重构执行指南

## 📋 快速开始

### 1. 环境准备

```bash
cd /path/to/lipro-hass

# 安装依赖
pip install -r requirements.txt
pip install pytest-snapshot pytest-benchmark pytest-mypy-plugins

# 确保 Git 仓库干净
git status
```

### 2. 初始化主控代理

```bash
# 初始化重构环境
python scripts/orchestrator.py init

# 检查任务加载
ls -la docs/refactoring/tasks/
```

### 3. 启动主控代理

```bash
# 启动主控代理（前台运行）
python scripts/orchestrator.py start

# 或者后台运行
nohup python scripts/orchestrator.py start > orchestrator.log 2>&1 &
```

### 4. 监控进度（另一个终端）

```bash
# 实时监控
python scripts/orchestrator.py monitor

# 或者查看状态文件
watch -n 5 cat docs/refactoring/STATUS.md
```

---

## 🤖 子代理执行

### 方式 1: 手动启动子代理

主控代理会在日志中输出需要执行的命令，例如：

```bash
# Agent-1: 异常处理重构
python scripts/agent_worker.py \
  --agent-id agent-1 \
  --task-file docs/refactoring/tasks/agent-1-exceptions.json

# Agent-2: 类型安全提升
python scripts/agent_worker.py \
  --agent-id agent-2 \
  --task-file docs/refactoring/tasks/agent-2-types.json

# Agent-6: 测试增强
python scripts/agent_worker.py \
  --agent-id agent-6 \
  --task-file docs/refactoring/tasks/agent-6-testing.json
```

### 方式 2: 并行启动多个代理

```bash
# 使用 tmux 或 screen 创建多个会话
tmux new-session -d -s agent-1 'python scripts/agent_worker.py --agent-id agent-1 --task-file docs/refactoring/tasks/agent-1-exceptions.json'
tmux new-session -d -s agent-2 'python scripts/agent_worker.py --agent-id agent-2 --task-file docs/refactoring/tasks/agent-2-types.json'
tmux new-session -d -s agent-6 'python scripts/agent_worker.py --agent-id agent-6 --task-file docs/refactoring/tasks/agent-6-testing.json'

# 查看会话
tmux ls

# 连接到会话
tmux attach -t agent-1
```

### 方式 3: 从检查点恢复

如果代理执行失败，可以从最后成功的检查点恢复：

```bash
python scripts/agent_worker.py \
  --agent-id agent-1 \
  --task-file docs/refactoring/tasks/agent-1-exceptions.json \
  --recover-from-checkpoint
```

---

## 📊 监控与调试

### 查看代理日志

```bash
# 查看特定代理日志
tail -f docs/refactoring/agent-1.log

# 查看主控代理日志
tail -f docs/refactoring/orchestrator.log
```

### 查看检查点状态

```bash
# 查看 Agent-1 的检查点
ls -la docs/refactoring/checkpoints/agent-1/

# 查看特定检查点
cat docs/refactoring/checkpoints/agent-1/cp-1-1.json
```

### 查看心跳

```bash
# 查看代理心跳
cat docs/refactoring/heartbeats/agent-1.json
```

### 查看失败记录

```bash
# 查看失败任务
cat docs/refactoring/failures/agent-1.json
```

---

## 🔧 故障处理

### 代理超时

**症状**: 代理 5 分钟无心跳

**处理**:
1. 检查代理进程是否存在：`ps aux | grep agent_worker`
2. 查看代理日志：`tail -100 docs/refactoring/agent-1.log`
3. 手动重启代理（使用 `--recover-from-checkpoint`）

### 测试失败

**症状**: 检查点验证失败

**处理**:
1. 查看测试输出：`pytest tests/core/mqtt/test_client.py -v`
2. 修复代码问题
3. 重新运行代理（会自动回滚到上一个检查点）

### 文件锁冲突

**症状**: 代理无法获取文件锁

**处理**:
1. 查看锁文件：`cat docs/refactoring/locks.json`
2. 确认锁的持有者是否仍在运行
3. 如果持有者已停止，手动释放锁：
   ```bash
   # 编辑 locks.json，删除对应的锁
   vim docs/refactoring/locks.json
   ```

### Git 冲突

**症状**: 多个代理修改同一文件导致冲突

**处理**:
1. 主控代理会自动检测冲突
2. 人工仲裁：查看冲突文件，决定保留哪个版本
3. 解决冲突后，重新启动受影响的代理

---

## 🎯 执行阶段

### Phase 0: 准备阶段（主控代理自动执行）

- 创建分支结构
- 建立快照测试
- 配置重构工具

### Phase 1: 快速收敛（Week 1-2）

**Wave 1.1: 并行执行（3 个代理）**

```bash
# 同时启动 3 个代理
tmux new-session -d -s agent-1 'python scripts/agent_worker.py --agent-id agent-1 --task-file docs/refactoring/tasks/agent-1-exceptions.json'
tmux new-session -d -s agent-2 'python scripts/agent_worker.py --agent-id agent-2 --task-file docs/refactoring/tasks/agent-2-types.json'
tmux new-session -d -s agent-6 'python scripts/agent_worker.py --agent-id agent-6 --task-file docs/refactoring/tasks/agent-6-testing.json'
```

**预期结果**:
- Agent-1: 7 处异常处理修复完成
- Agent-2: 4 个高频文件类型安全化
- Agent-6: 测试覆盖率 ≥ 95%

### Phase 2: 架构解耦（Week 3-6）

**Wave 2.1: Agent-3 独立执行（Week 3）**

```bash
python scripts/agent_worker.py \
  --agent-id agent-3 \
  --task-file docs/refactoring/tasks/agent-3-architecture.json
```

**Wave 2.2: Agent-4 + Agent-5 并行执行（Week 4-5）**

```bash
# 同时启动 2 个代理
tmux new-session -d -s agent-4 'python scripts/agent_worker.py --agent-id agent-4 --task-file docs/refactoring/tasks/agent-4-device-model.json'
tmux new-session -d -s agent-5 'python scripts/agent_worker.py --agent-id agent-5 --task-file docs/refactoring/tasks/agent-5-mqtt-client.json'
```

**Wave 2.3: Agent-3 + Agent-6 协作（Week 6）**

```bash
# Coordinator V2 迁移（需要 Agent-3 和 Agent-6 协作）
# 这个阶段需要人工协调
```

---

## 📈 进度跟踪

### 实时状态

```bash
# 查看实时状态
cat docs/refactoring/STATUS.md
```

示例输出：

```markdown
# 🜏 重构进度监控

**更新时间**: 2026-03-09 15:30:00

**总体进度**: 45.0% (9/20)

## 代理状态

- 🟢 **Exception Refactor Agent** (agent-1): working
  - 任务: exception-handling-refactoring (60%, 3/5 checkpoints)
  - 统计: 2 完成, 0 失败

- 🟢 **Type Safety Agent** (agent-2): working
  - 任务: type-safety-improvement (40%, 2/5 checkpoints)
  - 统计: 1 完成, 0 失败

- ⚪ **Architecture Refactor Agent** (agent-3): idle
  - 统计: 0 完成, 0 失败
```

### 最终报告

重构完成后，查看最终报告：

```bash
cat docs/refactoring/FINAL_REPORT.md
```

---

## 🔄 重试失败任务

如果有任务失败，可以重新分配：

```bash
python scripts/orchestrator.py retry-failed
```

---

## ✅ 验证重构结果

### 运行完整测试套件

```bash
pytest tests/ -v --cov=custom_components/lipro --cov-report=html
```

### 运行类型检查

```bash
mypy custom_components/lipro/ --strict
```

### 运行快照测试

```bash
pytest tests/snapshots/ -v
```

### 运行基准测试

```bash
pytest tests/benchmarks/ -v --benchmark-compare=baseline
```

### 检查代码质量

```bash
ruff check custom_components/lipro/
```

---

## 📚 相关文档

- [并行代理计划](PARALLEL_AGENT_PLAN.md) - 总体架构和任务分解
- [任务定义](tasks/) - 各代理的详细任务
- [重构工具](../../scripts/refactor_tools.py) - 验证工具
- [架构对比](ARCHITECTURE_COMPARISON.md) - 重构前后对比（完成后生成）

---

## 🆘 获取帮助

### 常见问题

**Q: 代理执行到一半卡住了怎么办？**

A:
1. 检查日志：`tail -f docs/refactoring/agent-X.log`
2. 检查进程：`ps aux | grep agent_worker`
3. 如果进程存在但无输出，可能在等待用户输入（检查代码中的 `input()` 调用）
4. 强制停止：`pkill -f agent_worker`，然后使用 `--recover-from-checkpoint` 重启

**Q: 如何跳过某个检查点？**

A: 不建议跳过检查点。如果必须跳过，可以：
1. 手动创建检查点成功记录：
   ```bash
   echo '{"checkpoint_id": "cp-1-1", "status": "success", "timestamp": 1234567890}' > docs/refactoring/checkpoints/agent-1/cp-1-1.json
   ```
2. 重新启动代理

**Q: 多个代理修改同一文件怎么办？**

A:
1. 主控代理会通过文件锁机制防止冲突
2. 如果确实需要修改同一文件，应该调整任务依赖关系
3. 人工仲裁：停止冲突的代理，手动合并代码，然后重启

---

⛧ 虚空低语：执行指南已织就。愿代理之网运转无碍，混沌终归秩序。

**Iä! Iä! Execute fhtagn!** 🜏
