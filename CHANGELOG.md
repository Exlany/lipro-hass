# 更新日志

## [Unreleased]（未发布）

## [1.0.4] - 2026-11-13

### 变更（Changed）

- 更新经过兼容性验证的依赖与 GitHub Actions，并修正贡献及排障文档中的版本和验证说明。
- 将最低支持及开发验证基线升级到 Home Assistant `2026.10.4`，使用匹配稳定版的测试插件 `0.13.375`；Python 最低版本仍为 `3.14.2`。
- 移除旧 HA 依赖覆盖，采用新稳定版原生依赖；运行时 aiohttp 下限更新到 `3.14.5`。

### 修复（Fixed）

- 修复 Home Assistant 原地修改实体 ID 后，运行时实体索引无法正确清理的问题（#88）。
- 修复匿名分享并发提交时可能丢失或重复提交数据的问题，并加强错误信息脱敏和缓存校验。
- 修复令牌有效期未持久化、非有限选项值处理，以及本地覆盖率检查遗漏变更文件的问题。
- 修复截断或转义响应中的敏感字段日志脱敏，以及离线安装文件相对路径解析。
- 恢复全量类型、格式和锁文件检查，修复 Hassfest 发现路径及跨多个提交的 PR 覆盖率比较。
- 安全扫描无法验证时明确阻断，不再将跳过扫描报告为通过。

### 安全说明（Security）

- Home Assistant 管理其自身的 `aiohttp` 版本。旧版本环境可能仍使用受已公开漏洞影响的 `aiohttp 3.14.3`；建议将 Home Assistant 更新到使用 `aiohttp 3.14.4` 或更新版本的发行版。集成的运行依赖安全检查使用按版本范围重新解析的依赖，不能代表所有现有 Home Assistant 安装的依赖状态。

## [1.0.3] - 2026-06-25

### 变更（Changed）

- 同步项目版本、Home Assistant manifest 与锁文件版本到 `1.0.3`。
- 将 release 验证依赖与动作版本更新到当前锁定基线，并保持 Home Assistant 版本与 HACS 元数据一致。
- 将运行时 `aiohttp` 下限提升到已修复安全问题的 `3.14.1`。

### 修复（Fixed）

- 将固件支持数据文件从 `firmware_support_manifest.json` 改名为 `firmware_support.json`，避免 HACS/default 的 manifest 搜索误识别。
- 清理公开支持与文档元数据，移除残留架构归档文档，并统一 `manifest.json` 文档入口到仓库根 `README.md`。
- 新增与 HACS/default Hassfest job 对齐的预检流程，提前发现 manifest 命名冲突。
- 恢复 Python 3.14 语法重写后不兼容的异常处理写法，确保当前测试运行时可导入。

## [1.0.2] - 2026-04-28

### 变更（Changed）

- 优化了 REST / protocol 内部边界的可维护性，减少超大 façade 文件里的重复样板与隐式中转。
- 完善了设备定时相关调用链的一致性，补齐 mesh / standard schedule 之间的参数透传行为。
- 同步收紧了开发者架构文档、维护者发布手册与治理基线之间的当前路线说明，降低后续维护时的定位成本。
- 持续压缩内部实现热点，保持对外导入入口与正式根对象不变。
- 同步项目版本、Home Assistant manifest 与锁文件版本到 `1.0.2`。

### 修复（Fixed）

- 修复了 schedule `group_id` 在部分 REST/protocol forwarding 链路中的透传缺口。
- 修复了当前治理/验证文档仍引用过期路线状态与旧测试路径的若干漂移项。
- 修复了维护者发布语义与 private-access / mirror reachability 条件之间的不一致表述。
- 放宽 MQTT benchmark 的阻断阈值，避免 GitHub runner 微基准波动误杀 release/CI 流程，同时保留 warning 信号。
- 修复私有仓库未启用 CodeQL code scanning 时 release gate 误失败的问题。

## [1.0.0] - 2026-02-08

### 新增（Added）

- Lipro Smart Home Home Assistant 集成首次发布。
- 云端 API 集成 + MQTT 实时推送更新。
- 支持的设备类型：
  - Light（灯光）：开关、亮度、色温
  - Cover（窗帘）：开/关、位置、停止
  - Switch（开关/插座）：开关
  - Fan（风扇）：开关、风速、预设模式
  - Climate（浴霸）：开关、预设模式
  - Binary Sensor（传感器）：人体、门窗、光照、电池
- 配置流程：手机号+密码认证。
- 选项流程：配置刷新间隔（10-300 秒）。
- 重新认证与重新配置流程。
- 乐观状态更新，提升 UI 响应速度。
- 滑块防抖，避免 API 过载。
- MQTT 指数退避重连。
- 为高级用户提供自定义服务 `lipro.send_command`。
- 中英文双语支持。
- 诊断支持与敏感数据脱敏。
