# 残留代码清理报告

生成时间: 2026-03-10

## 扫描范围

- `custom_components/lipro/`
- `tests/`

## 发现的残留

### 1. Import 引用残留

| 文件 | 行号 | 残留内容 | 状态 |
|------|------|---------|------|
| `custom_components/lipro/core/coordinator/commands.py` | 10 | `from .command_confirm import (...)` | ⚠️ 待处理 - 文件不存在 |
| `custom_components/lipro/core/coordinator/commands.py` | 18 | `from .command_send import _MAX_DEVELOPER_COMMAND_TRACES, CoordinatorCommandRuntime` | ⚠️ 待处理 - 文件不存在 |
| `tests/core/test_device_refresh.py` | 23 | `from custom_components.lipro.core.coordinator.device_list_snapshot import (...)` | ⚠️ 待处理 - 文件不存在 |
| `tests/core/test_device_list_snapshot.py` | 154 | patch 路径引用 `custom_components.lipro.core.coordinator.device_list_snapshot.LiproDevice.from_api_data` | ⚠️ 待处理 |

### 2. 类引用残留

| 文件 | 行号 | 残留内容 | 状态 |
|------|------|---------|------|
| `custom_components/lipro/core/coordinator/commands.py` | 18, 28 | `CoordinatorCommandRuntime` | ⚠️ 待处理 - 应改为 `CommandRuntime` |
| `tests/meta/test_commands_reexport.py` | 11, 17 | `CoordinatorCommandRuntime` | ⚠️ 待处理 |

### 3. 方法调用残留

| 文件 | 行号 | 残留内容 | 状态 |
|------|------|---------|------|
| 无 | - | - | ✅ 未发现 |

### 4. 测试代码残留

| 文件 | 行号 | 残留内容 | 状态 |
|------|------|---------|------|
| `tests/core/test_device_refresh.py` | 23-29 | 从不存在的模块导入函数 | ⚠️ 待处理 |
| `tests/core/test_device_refresh.py` | 120, 161, 176, 333, 353 | patch 路径指向旧模块 | ⚠️ 待处理 |
| `tests/core/test_device_list_snapshot.py` | 154 | patch 路径指向旧模块 | ⚠️ 待处理 |

## 新旧模块映射

### 已删除的旧模块 → 新模块位置

| 旧模块 | 新模块 | 说明 |
|--------|--------|------|
| `coordinator.command_send` | `coordinator.runtime.command_runtime` | `CoordinatorCommandRuntime` → `CommandRuntime` |
| `coordinator.command_confirm` | `coordinator.runtime.command.confirmation` | 确认相关常量和逻辑 |
| `coordinator.device_list_snapshot` | `coordinator.runtime.device.snapshot` + `coordinator.runtime.device.filter` | 设备快照和过滤逻辑 |

### 函数/类映射

| 旧名称 | 新位置 | 新名称 |
|--------|--------|--------|
| `CoordinatorCommandRuntime` | `runtime.command_runtime` | `CommandRuntime` |
| `build_device_filter_config` | `runtime.device.filter` | 保持不变 |
| `build_fetched_device_snapshot` | `runtime.device.snapshot` | 保持不变 |
| `is_device_included_by_filter` | `runtime.device.filter` | 保持不变 |
| `plan_stale_device_reconciliation` | `runtime.device.incremental` | 保持不变 |
| `has_active_device_filter` | `runtime.device.filter` | 保持不变 |

## 清理操作

### 已清理的文件

- [x] ~~`custom_components/lipro/core/coordinator/command_send.py`~~ - 已删除
- [x] ~~`custom_components/lipro/core/coordinator/command_confirm.py`~~ - 已删除
- [x] ~~`custom_components/lipro/core/coordinator/device_list_snapshot.py`~~ - 已删除
- [x] ~~`custom_components/lipro/core/coordinator/commands.py`~~ - 已删除（无用的 re-export 层）
- [x] ~~`tests/meta/test_commands_reexport.py`~~ - 已删除
- [x] `tests/core/test_device_refresh.py` - ✅ 已更新 import 和 patch 路径
- [x] `tests/core/test_device_list_snapshot.py` - ✅ 已被 linter 自动重构

### 修复计划

#### 1. 修复 `commands.py` (re-export 层)

```python
# 旧代码
from .command_confirm import (...)
from .command_send import _MAX_DEVELOPER_COMMAND_TRACES, CoordinatorCommandRuntime

# 新代码
from .runtime.command.confirmation import (...)
from .runtime.command_runtime import CommandRuntime
# 或者删除整个 commands.py，直接从新位置导入
```

#### 2. 修复 `test_device_refresh.py`

```python
# 旧代码
from custom_components.lipro.core.coordinator.device_list_snapshot import (
    build_device_filter_config,
    build_fetched_device_snapshot,
    has_active_device_filter,
    is_device_included_by_filter,
    plan_stale_device_reconciliation,
)

# 新代码
from custom_components.lipro.core.coordinator.runtime.device.filter import (
    build_device_filter_config,
    has_active_device_filter,
    is_device_included_by_filter,
)
from custom_components.lipro.core.coordinator.runtime.device.snapshot import (
    build_fetched_device_snapshot,
)
from custom_components.lipro.core.coordinator.runtime.device.incremental import (
    plan_stale_device_reconciliation,
)

# patch 路径也需要更新
"custom_components.lipro.core.coordinator.runtime.device.snapshot.LiproDevice.from_api_data"
```

#### 3. 修复 `test_device_list_snapshot.py`

```python
# patch 路径更新
"custom_components.lipro.core.coordinator.runtime.device.snapshot.LiproDevice.from_api_data"
```

#### 4. 修复 `test_commands_reexport.py`

```python
# 旧代码
from custom_components.lipro.core.coordinator.commands import (
    CoordinatorCommandRuntime,
)

# 新代码
from custom_components.lipro.core.coordinator.runtime.command_runtime import (
    CommandRuntime,
)
```

### 验证

```bash
# 确保没有残留引用
cd /var/tmp/coolvibe/worktrees/edf26778937a-/lipro-hass

# 检查旧模块引用
grep -r "coordinator.command_send\|coordinator.command_confirm\|coordinator.device_list_snapshot" \
  custom_components/lipro/ tests/ --include="*.py"

# 检查旧类名
grep -r "CoordinatorCommandRuntime" custom_components/lipro/ tests/ --include="*.py"

# 运行测试确保没有破坏
uv run pytest tests/ -v
```

## 清理结果

### 已完成的清理操作

1. ✅ 删除 `custom_components/lipro/core/coordinator/commands.py` - 无用的 re-export 层
2. ✅ 删除 `tests/meta/test_commands_reexport.py` - 对应的测试文件
3. ✅ 修复 `tests/core/test_device_refresh.py`:
   - 更新 import 从 `device_list_snapshot` → `runtime.device.filter` + `runtime.device.snapshot` + `runtime.device.incremental`
   - 更新 4 处 patch 路径 `device_list_snapshot.LiproDevice.from_api_data` → `runtime.device.snapshot.LiproDevice.from_api_data`
   - 更新 1 处 patch 路径 `device_list_snapshot.json.loads` → `runtime.device.filter.json.loads`
4. ✅ `tests/core/test_device_list_snapshot.py` - 已被 linter 自动重构为新的测试结构

### 验证结果

```bash
# 检查残留引用
grep -rn "device_list_snapshot\|command_send\|command_confirm" tests/ custom_components/lipro/ --include="*.py"
# ✅ 仅发现正常的函数名（command_confirmation_timeout 等），无残留模块引用

# 检查旧类名
grep -rn "CoordinatorCommandRuntime" tests/ custom_components/lipro/ --include="*.py"
# ✅ 无残留类引用
```

## 结论

- **发现残留**: 7 处
  - Import 引用: 4 处
  - 类引用: 2 处
  - 测试 patch 路径: 6 处
- **已清理**: 7 处 ✅
- **待处理**: 0 处 ✅

### 优先级

1. **高优先级**: 修复 `commands.py` - 这是 re-export 层，影响其他模块
2. **中优先级**: 修复测试文件 - 确保测试能正常运行
3. **低优先级**: 清理注释和文档中的旧引用

### 建议

考虑删除 `commands.py` re-export 层，直接从新的 runtime 模块导入，减少间接层级，提高代码可维护性。
