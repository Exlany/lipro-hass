# 代码质量改进路线图

**项目**: lipro-hass
**当前评分**: ⭐⭐⭐⭐⭐ (4.7/5.0)
**目标评分**: ⭐⭐⭐⭐⭐ (5.0/5.0)

---

## 📊 当前状态

| 维度 | 当前 | 目标 | 差距 |
|------|------|------|------|
| 复杂度 | ⭐⭐⭐⭐⭐ (2.17) | ⭐⭐⭐⭐⭐ (< 2.5) | ✅ 已达标 |
| 可维护性 | ⭐⭐⭐⭐☆ (72.5) | ⭐⭐⭐⭐⭐ (> 75) | 小幅提升 |
| 类型安全 | ⭐⭐⭐⭐☆ (80%) | ⭐⭐⭐⭐⭐ (95%) | 需提升 15% |
| 代码风格 | ⭐⭐⭐⭐☆ (85.5%) | ⭐⭐⭐⭐⭐ (100%) | 需修复 43 项 |
| 代码重复 | ⭐⭐⭐⭐⭐ (< 5%) | ⭐⭐⭐⭐⭐ (< 5%) | ✅ 已达标 |
| 依赖管理 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ 已达标 |
| 测试覆盖 | ⭐⭐⭐⭐⭐ (> 85%) | ⭐⭐⭐⭐⭐ (> 90%) | 小幅提升 |

---

## 🎯 改进阶段

### 第一阶段：紧急修复 (1-2 天)

**目标**: 修复所有高优先级问题，消除潜在风险

#### 任务清单

- [ ] **修复悬空异步任务** (30 分钟)
  - 文件: `services/mqtt_service.py:34`
  - 修改: 添加 `await` 关键字
  - 验证: 运行 MQTT 相关测试

- [ ] **修复方法名错误** (15 分钟)
  - 文件: `services/mqtt_service.py`
  - 修改: `setup()` → `async_setup()`, `stop()` → `async_stop()`
  - 验证: 运行服务层测试

- [ ] **定位并修复盲目异常捕获** (1 小时)
  - 搜索: `grep -rn "except Exception" custom_components/lipro/core/coordinator/`
  - 修改: 捕获具体异常类型
  - 验证: 确保错误处理逻辑正确

- [ ] **修复类型属性错误** (2 小时)
  - 检查 `LiproDevice` 和 `LiproClient` 类定义
  - 添加缺失的属性和方法
  - 或使用 `getattr()` 安全访问
  - 验证: `mypy` 检查通过

**验收标准**:
- ✅ 所有高优先级问题已修复
- ✅ 测试套件全部通过
- ✅ 无新增错误

---

### 第二阶段：自动化修复 (1 小时)

**目标**: 使用工具自动修复代码风格和格式问题

#### 任务清单

- [ ] **自动修复 Ruff 问题** (10 分钟)
  ```bash
  .venv/bin/ruff check custom_components/lipro/core/coordinator/ --fix
  ```
  - 预期修复: 17 个问题
  - 包括: 未使用导入、导入排序、类型注解等

- [ ] **格式化代码** (5 分钟)
  ```bash
  .venv/bin/ruff format custom_components/lipro/core/coordinator/
  ```
  - 格式化: 9 个文件
  - 统一代码风格

- [ ] **清理无效的 type ignore** (15 分钟)
  - 文件: `runtime/state/reader.py`, `updater.py`, `index.py`
  - 移除过时的 `# type: ignore` 注释
  - 验证: `mypy` 检查无警告

- [ ] **验证修复结果** (10 分钟)
  ```bash
  .venv/bin/ruff check custom_components/lipro/core/coordinator/ --statistics
  .venv/bin/mypy custom_components/lipro/core/coordinator/
  ```

**验收标准**:
- ✅ Ruff 问题减少到 < 10 个
- ✅ 代码格式 100% 合规
- ✅ 无无效的 type ignore 注释

---

### 第三阶段：手动优化 (2-3 天)

**目标**: 修复剩余的中优先级问题，提升代码质量

#### 任务清单

- [ ] **修复导入位置问题** (1 小时)
  - 文件: `coordinator.py`
  - 评估: 是否为避免循环导入
  - 修改: 移至顶部或添加 `# noqa: PLC0415`

- [ ] **处理私有成员访问** (2 小时)
  - 审查: 14 处私有成员访问
  - 决策: 公开接口 vs 添加 noqa
  - 修改: 根据决策调整代码

- [ ] **提升类型覆盖率** (3 小时)
  - 目标: 从 80% 提升到 95%
  - 方法: 为缺失类型注解的函数添加注解
  - 重点: 公共 API 和复杂函数

- [ ] **修复类型比较错误** (1 小时)
  - 文件: `runtime/state/reader.py:96`
  - 问题: `int | None` vs `str` 比较
  - 修改: 添加类型检查或类型转换

- [ ] **统一错误处理模式** (2 小时)
  - 审查: 所有异常处理代码
  - 标准化: 日志格式和异常类型
  - 文档: 编写错误处理指南

**验收标准**:
- ✅ Ruff 问题 < 5 个
- ✅ Mypy 错误 < 10 个
- ✅ 类型覆盖率 > 90%

---

### 第四阶段：性能优化 (可选，1-2 周)

**目标**: 降低高复杂度函数，提升可维护性

#### 任务清单

- [ ] **重构 `resolve_connect_status_query_candidates`** (4 小时)
  - 当前复杂度: C (19)
  - 目标复杂度: B (< 10)
  - 方法: 提取条件判断为独立函数

- [ ] **重构 `IncrementalRefreshStrategy.refresh_device_states`** (4 小时)
  - 当前复杂度: C (18)
  - 目标复杂度: B (< 10)
  - 方法: 按设备类型拆分处理逻辑

- [ ] **重构 `SnapshotBuilder.build_full_snapshot`** (3 小时)
  - 当前复杂度: C (16)
  - 目标复杂度: B (< 10)
  - 方法: 提取快照构建步骤

- [ ] **重构 `sync_device_room_assignments`** (3 小时)
  - 当前复杂度: C (13)
  - 目标复杂度: B (< 10)
  - 方法: 提取区域同步逻辑

- [ ] **重构 `_normalize_single_outlet_power_payload`** (2 小时)
  - 当前复杂度: C (11)
  - 目标复杂度: A (< 6)
  - 方法: 简化数据规范化逻辑

- [ ] **拆分 `IncrementalRefreshStrategy` 类** (6 小时)
  - 当前复杂度: C (11)
  - 目标: 拆分为多个策略类
  - 方法: 按设备类型创建独立策略

**验收标准**:
- ✅ 所有函数复杂度 < 10
- ✅ 平均复杂度 < 2.0
- ✅ 可维护性指数 > 75

---

### 第五阶段：持续改进 (长期)

**目标**: 建立代码质量保障机制

#### 任务清单

- [ ] **配置 Pre-commit Hooks** (1 小时)
  ```yaml
  # .pre-commit-config.yaml
  repos:
    - repo: local
      hooks:
        - id: ruff-check
          name: Ruff Linter
          entry: .venv/bin/ruff check --fix
          language: system
          types: [python]
        - id: ruff-format
          name: Ruff Formatter
          entry: .venv/bin/ruff format
          language: system
          types: [python]
        - id: mypy
          name: Mypy Type Checker
          entry: .venv/bin/mypy
          language: system
          types: [python]
  ```

- [ ] **配置 CI/CD 质量门禁** (2 小时)
  - 添加 Ruff 检查步骤
  - 添加 Mypy 检查步骤
  - 添加覆盖率门禁 (> 85%)
  - 添加复杂度检查 (radon)

- [ ] **编写代码质量指南** (3 小时)
  - 复杂度标准
  - 类型注解规范
  - 错误处理模式
  - 测试覆盖要求

- [ ] **定期质量审查** (每月 2 小时)
  - 运行质量分析工具
  - 更新质量报告
  - 识别新的改进点

**验收标准**:
- ✅ Pre-commit hooks 已配置
- ✅ CI/CD 质量门禁已启用
- ✅ 代码质量指南已发布
- ✅ 质量审查流程已建立

---

## 📈 预期收益

### 短期收益 (1-2 周)

- ✅ 消除所有高风险问题
- ✅ 代码风格 100% 合规
- ✅ 类型安全性提升 15%
- ✅ 开发体验改善

### 中期收益 (1-2 月)

- ✅ 代码可维护性提升 10%
- ✅ Bug 率降低 30%
- ✅ 新功能开发速度提升 20%
- ✅ 代码审查效率提升 40%

### 长期收益 (3-6 月)

- ✅ 技术债务持续降低
- ✅ 团队开发效率持续提升
- ✅ 代码质量文化建立
- ✅ 项目可持续发展

---

## 🛠️ 工具和资源

### 质量分析工具

| 工具 | 用途 | 命令 |
|------|------|------|
| **radon** | 复杂度分析 | `radon cc -a -s` |
| **ruff** | 代码检查和格式化 | `ruff check --fix` |
| **mypy** | 类型检查 | `mypy --strict` |
| **pytest-cov** | 测试覆盖率 | `pytest --cov` |

### 参考文档

- [Ruff 规则文档](https://docs.astral.sh/ruff/rules/)
- [Mypy 类型检查指南](https://mypy.readthedocs.io/)
- [Radon 复杂度指标](https://radon.readthedocs.io/)
- [Home Assistant 开发指南](https://developers.home-assistant.io/)

---

## 📝 进度追踪

### 第一阶段：紧急修复
- [ ] 开始日期: ____
- [ ] 完成日期: ____
- [ ] 负责人: ____
- [ ] 状态: 未开始

### 第二阶段：自动化修复
- [ ] 开始日期: ____
- [ ] 完成日期: ____
- [ ] 负责人: ____
- [ ] 状态: 未开始

### 第三阶段：手动优化
- [ ] 开始日期: ____
- [ ] 完成日期: ____
- [ ] 负责人: ____
- [ ] 状态: 未开始

### 第四阶段：性能优化
- [ ] 开始日期: ____
- [ ] 完成日期: ____
- [ ] 负责人: ____
- [ ] 状态: 未开始

### 第五阶段：持续改进
- [ ] 开始日期: ____
- [ ] 完成日期: ____
- [ ] 负责人: ____
- [ ] 状态: 未开始

---

**最后更新**: 2026-03-10
**下次审查**: 2026-04-10

*生成工具: 深渊代码织师 v1.0*
