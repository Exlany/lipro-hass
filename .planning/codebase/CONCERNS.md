# CONCERNS
> Snapshot: `2026-03-18`
> Freshness: Phase 32 对齐刷新；仅按 `AGENTS.md`、`.planning/{ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md`、`docs/developer_architecture.md` 与当前 CI/release/public-doc truth 截面成立。上述真源变更后，本图谱必须同步刷新或标记过时。
> Derived collaboration map: 本文件是受约束的协作图谱 / 派生视图，仅用于导航、协作与局部审阅。
> Authority: 若与 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md` 或 `docs/developer_architecture.md` 冲突，以后者为准；本图谱不得反向充当当前治理真源，且必须同步回写、标记为过时，或注明历史观察。
> Focus: `concerns`
> Scope: 技术债、架构残留、真正风险、测试盲区、文档治理、安全/敏感信息/观测面风险

## 1. 裁决口径

- **已登记的迁移残留**：已进入 `.planning/reviews/RESIDUAL_LEDGER.md` / `.planning/reviews/KILL_LIST.md`，当前仍需收口，但**不应再被当作“新发现的未登记风险”**。
- **真正风险**：当前仓库仍可能误导贡献者、泄露敏感信息、放大架构回归或让治理真源失真；需要优先处理。
- **误报**：看起来像问题，但按北极星、治理账本与测试守卫判断，当前属于**刻意保留、受控或已关闭**，不应升级为 active concern。

### 优先级

- **P1**：应尽快修补；已影响治理可信度、安全口径或回归面。
- **P2**：应在下一轮治理/重构中处理；会持续抬高维护税。
- **P3**：已登记并受控；继续观察，不宜越权扩大。
- **N/A**：误报，不升级。

## 2. 已登记的迁移残留

### 2.1 API compat wrappers 仍在 helper 层残留

- **判定**：已登记的迁移残留，不是新的未登记架构回退。
- **现状**：helper 侧仍保留 canonical-to-legacy envelope shaping，尤其 outlet power 路径仍会在 list 场景回吐 `{"data": rows}` 兼容形态。
- **为何仍要盯住**：它已退出正式 public façade，但继续存在会让后续 helper 调用者误把 compat 形态当 canonical truth。
- **建议优先级**：**P2**
- **证据路径**：
  - `.planning/reviews/RESIDUAL_LEDGER.md:7`
  - `custom_components/lipro/core/api/power_service.py:38`

### 2.2 API mixin / typing spine 仍是活跃技术债

- **判定**：已登记的迁移残留，不是双主链回流。
- **现状**：`_ClientBase` 仍作为 internal typing anchor 存活，endpoint payload helper 仍挂在 compat/mixin 叙事之下。
- **风险边界**：当前被限制在 `core/api` 内，且受 locality guard 约束；问题在于**可维护性与认知负担**，不是正式 public surface 重新外溢。
- **建议优先级**：**P2**
- **证据路径**：
  - `.planning/reviews/RESIDUAL_LEDGER.md:8`
  - `custom_components/lipro/core/api/client_base.py:51`
  - `custom_components/lipro/core/api/endpoints/payloads.py:232`

### 2.3 `LiproMqttClient` legacy naming 仍是 split-root 残留

- **判定**：已登记的迁移残留。
- **现状**：正式协议根已收口到 `LiproProtocolFacade`，但 concrete transport 仍保留 legacy root naming；delete gate 仍未关闭。
- **风险边界**：今天它主要是**命名/认知债**，而不是 formal root 复活；真正危险在于未来新代码重新直连 concrete transport。
- **建议优先级**：**P2**
- **证据路径**：
  - `.planning/reviews/RESIDUAL_LEDGER.md:9`
  - `.planning/reviews/KILL_LIST.md:16`
  - `custom_components/lipro/core/mqtt/mqtt_client.py:23`

### 2.4 boundary/replay coverage 仍有显式 de-scope 残留

- **判定**：已登记的迁移残留，不应被误写成“遗漏治理”。
- **现状**：`External-boundary advisory naming`、`Protocol-boundary family coverage`、`Replay scenario coverage` 都已被明确写进 ledger；其中一部分 family 被显式 de-scope，而不是隐式漏测。
- **风险边界**：当前问题是**coverage debt 已登记但未清零**；若后续重新扩 scope，必须重新开 phase，而不是在现有 truth 外偷偷长出第二套边界故事线。
- **建议优先级**：**P3**
- **证据路径**：
  - `.planning/reviews/RESIDUAL_LEDGER.md:10`
  - `.planning/reviews/RESIDUAL_LEDGER.md:11`
  - `.planning/reviews/RESIDUAL_LEDGER.md:12`
  - `tests/meta/test_external_boundary_authority.py:17`
  - `tests/meta/test_protocol_replay_assets.py:47`

## 3. 真正风险

### 3.1 `submit_developer_feedback` 的“已脱敏”口径与实际 payload 不一致

- **类型**：安全 / 敏感信息 / 文档契约失真 / 测试盲区
- **判定**：**N/A（Phase 16 已校准）**
- **问题**：`build_developer_report()` 会把 `dev.name`、`dev.iot_name` 等可识别字段塞进 developer report；`build_developer_feedback_report()` 只做通用 `sanitize_value()`，不会删除普通 `name` / `iot_name` 键；随后 `submit_developer_feedback()` 直接上传到 share worker。
- **为何严重**：README、services 描述和翻译都宣称这是“sanitized developer diagnostics”；但当前实现更接近“脱敏凭证后的详细设备调试报告”，两者不是同一隐私级别。
- **测试盲区**：现有边界 fixture 与测试只覆盖 `note`、`phone` 这类最小样本，未覆盖**包含设备名/iot_name/IR 资产/mesh 结构**的真实 developer feedback payload。
- **建议优先级**：**已关闭**
- **建议**：
  - 要么在 developer-feedback upload 之前额外 drop/redact `name`、`iot_name`、用户自定义 label 等字段；
  - 要么把对外文案改成“包含受限调试元数据的 opt-in 支持上报”，不要继续宣称等同匿名/脱敏报告；
  - 同时补一组带 `name` / `iot_name` / `rc_list.name` 的回归测试与 external-boundary fixture。
- **证据路径**：
  - `custom_components/lipro/core/utils/developer_report.py:173`
  - `custom_components/lipro/core/utils/developer_report.py:174`
  - `custom_components/lipro/core/utils/developer_report.py:293`
  - `custom_components/lipro/core/utils/developer_report.py:320`
  - `custom_components/lipro/core/anonymous_share/report_builder.py:69`
  - `custom_components/lipro/core/anonymous_share/manager.py:358`
  - `custom_components/lipro/services.yaml:210`
  - `custom_components/lipro/services.yaml:227`
  - `custom_components/lipro/translations/en.json:340`
  - `custom_components/lipro/translations/en.json:350`
  - `README_zh.md:44`
  - `tests/core/test_anonymous_share.py:739`
  - `tests/core/test_anonymous_share.py:1140`
  - `tests/fixtures/external_boundaries/share_worker/developer_feedback_report.canonical.json:11`

### 3.2 `.planning/codebase/*` 若没有明确身份与守卫，会误导贡献者把本地图谱当 active truth

- **类型**：文档治理 / 架构仲裁 / 协作误导
- **判定**：**真正风险**
- **问题**：本地图谱曾混有 `Phase 14` closeout-ready、`Python 3.13`、`execution.py = runtime-auth seam` 等旧叙事；同时目录默认被 `.gitignore` 忽略，导致它既像 active doc，又不易被协作修正。
- **为何严重**：一旦贡献者先读到本目录，就会误把派生视图当权威链，进而把已关闭 seam、过期 phase/status 或旧工具链口径重新写回仓库。
- **测试盲区**：在 Phase 16 之前，`check_file_matrix.py` / `check_architecture_policy.py` / `test_governance_guards.py` 还没有对 `.planning/codebase/*.md` 的身份提示、README、gitignore unignore 与 closed-seam wording 做 fail-fast。
- **建议优先级**：**P1**
- **建议**：
  - 为 `.planning/codebase/*.md` 建立统一 derived collaboration map disclaimer；
  - 新增 `.planning/codebase/README.md` 明确权威顺序、使用边界与刷新策略；
  - 给脚本与 meta guards 加上 codebase-map policy 与 closed-seam drift 守卫。
- **证据路径**：
  - `.planning/codebase/STACK.md:2`
  - `.planning/codebase/STACK.md:13`
  - `.planning/codebase/STRUCTURE.md:78`
  - `.planning/codebase/STRUCTURE.md:118`
  - `.planning/codebase/STRUCTURE.md:151`
  - `.gitignore:82`
  - `scripts/check_file_matrix.py:472`
  - `tests/meta/test_governance_guards.py:493`


### 3.3 对外文档落后于 CI 真相：HACS/private repo 与最低 HA 版本口径没有前置到安装入口

- **类型**：文档治理 / 发布体验 / 支持成本 / 测试盲区
- **判定**：**真正风险**
- **问题**：README 中仍把 HACS 作为推荐安装路径，但 CI 明确写明私有仓库会跳过 HACS validation；同时最低支持 HA 版本 `2026.2.3` 只出现在 `hacs.json`、`pyproject.toml`、`SECURITY.md`、Issue 模板与 CONTRIBUTING 中，README/README_zh 的安装入口并未前置说明。
- **为何重要**：这不是代码漏洞，但会持续制造“本地能装/CI 过不了”与“用户环境低于最低版本却先按 README 安装”的支持噪音。
- **测试盲区**：`test_version_sync.py` 只同步 `hacs.json` / bug template / `pyproject.toml`，不守 README 安装文案是否同步最小版本与 HACS caveat。
- **建议优先级**：**P2**
- **建议**：
  - 在 `README.md` / `README_zh.md` 的 HACS 安装段直接标出最低 HA 版本；
  - 写明 HACS validation 在 private repo 场景不会执行；
  - 如要长期保持一致，新增 README↔`hacs.json` 的元测试。
- **证据路径**：
  - `README.md:74`
  - `README_zh.md:73`
  - `CONTRIBUTING.md:97`
  - `CONTRIBUTING.md:100`
  - `CONTRIBUTING.md:196`
  - `SECURITY.md:10`
  - `.github/workflows/ci.yml:246`
  - `.github/workflows/ci.yml:249`
  - `tests/meta/test_version_sync.py:55`
  - `tests/meta/test_version_sync.py:65`

### 3.4 control/support 热点仍过于集中，放大后续回归 blast radius

- **类型**：架构回归 / 可维护性 / 间接测试盲区
- **判定**：**真正风险**
- **问题**：`control/service_router.py` 仍承载 14 个 service handler；`core/utils/developer_report.py` 仍把 mesh、panel、IR、recent_commands、redaction-ish shaping 堆在一个 400+ 行文件里。
- **为何重要**：这类热点不是“今天跑不通”的故障，但会显著抬高任何 support/diagnostics/developer-service 变更的 blast radius；`3.1` 的 sanitized 口径偏差就发生在这一热点带上。
- **建议优先级**：**P2**
- **建议**：
  - 让 `service_router.py` 继续退化成 identity-only adapter，把 developer/anonymous-share/diagnostics handlers 拆到独立 home；
  - 把 developer report 的“本地调试视图”与“上传给 worker 的 payload shaping”显式分离，避免再次共享同一对象图。
- **证据路径**：
  - `custom_components/lipro/control/service_router.py:138`
  - `custom_components/lipro/control/service_router.py:335`
  - `custom_components/lipro/core/utils/developer_report.py:36`
  - `custom_components/lipro/core/utils/developer_report.py:338`
  - `.planning/reviews/RESIDUAL_LEDGER.md:166`

### 3.5 依赖安全门更偏向 runtime，dev-toolchain 风险只做非阻塞追踪

- **类型**：安全 / 供应链 / 工具治理
- **判定**：**真正风险**
- **问题**：本地 `./scripts/lint` 默认只审计 runtime requirements；CI 中 dev dependency 的 `pip-audit` 只在 `schedule` / `workflow_dispatch` 跑，且 `continue-on-error: true`。
- **为何重要**：这不影响运行面安全边界的主线，但会让 dev-toolchain 的供应链问题更容易拖成“知道有风险但 PR 不会 fail”的慢性债。
- **建议优先级**：**P3**
- **建议**：至少把高风险 dev dependency CVE 变成有记录的门禁策略，而不是仅保留 schedule/manual 的非阻塞摘要。
- **证据路径**：
  - `scripts/lint:41`
  - `scripts/lint:56`
  - `scripts/lint:62`
  - `.github/workflows/ci.yml:145`
  - `.github/workflows/ci.yml:148`
  - `CONTRIBUTING.md:65`

## 4. 误报 / 不应升级的问题

### 4.1 `LiproClient` / `raw_client` / `DeviceCapabilities` 现在是历史引用，不是 live public surface

- **判定**：**误报**
- **原因**：这些名字仍频繁出现在治理文档、fixtures、tests 中，用于证明“已删除/已关闭”；但代码正式出口已经收口，不能再把它们当 active architecture regression。
- **优先级**：**N/A**
- **证据路径**：
  - `.planning/reviews/KILL_LIST.md:15`
  - `.planning/reviews/KILL_LIST.md:17`
  - `.planning/reviews/KILL_LIST.md:22`
  - `custom_components/lipro/core/api/__init__.py:1`
  - `custom_components/lipro/core/protocol/compat.py:5`

### 4.2 assurance tooling 依赖 `tests.harness` 不是 production backflow

- **判定**：**误报**
- **原因**：`scripts/export_ai_debug_evidence_pack.py` 看起来像“脚本依赖测试代码”，但在本仓治理中它被明确登记为 assurance-only / pull-only truth consumer，而不是 runtime/control/public root。
- **优先级**：**N/A**
- **证据路径**：
  - `.planning/baseline/PUBLIC_SURFACES.md:23`
  - `.planning/baseline/PUBLIC_SURFACES.md:29`
  - `.planning/baseline/PUBLIC_SURFACES.md:30`
  - `.planning/baseline/ARCHITECTURE_POLICY.md:42`
  - `tests/meta/test_evidence_pack_authority.py:60`
  - `scripts/export_ai_debug_evidence_pack.py:11`

### 4.3 telemetry/evidence 中的真实时间戳与 `entry_ref` / `device_ref` 不是泄露回归

- **判定**：**误报**
- **原因**：北极星已明确允许真实时间戳，以及“报告内稳定、跨报告不可关联”的伪匿名引用；集成测试也验证了跨报告 ref 不可关联。
- **优先级**：**N/A**
- **证据路径**：
  - `docs/NORTH_STAR_TARGET_ARCHITECTURE.md:263`
  - `docs/NORTH_STAR_TARGET_ARCHITECTURE.md:264`
  - `tests/integration/test_ai_debug_evidence_pack.py:56`
  - `tests/integration/test_ai_debug_evidence_pack.py:64`
  - `custom_components/lipro/core/telemetry/exporter.py:54`

### 4.4 平台层读取 `entry.runtime_data` 本身不是 control-plane bypass

- **判定**：**误报**
- **原因**：guard 禁的是 control surface 四处散落读取 runtime internals；平台实体把 `entry.runtime_data` 当 HA runtime home 使用是正式故事线的一部分，control 面另有 `runtime_access.py` 统一定位。
- **优先级**：**N/A**
- **证据路径**：
  - `.planning/baseline/DEPENDENCY_MATRIX.md:58`
  - `.planning/baseline/PUBLIC_SURFACES.md:71`
  - `custom_components/lipro/control/runtime_access.py:17`
  - `custom_components/lipro/binary_sensor.py:34`
  - `custom_components/lipro/light.py:50`

## 5. 结论

- 当前仓库的主风险不再是“大架构没定”，而是 **support/reporting 路径的脱敏口径失真** 与 **active governance docs 的悬空指针**。
- active residual 已基本被账本收口，**不要把已关闭 legacy seam 误判为 live regression**；真正需要优先处理的是 P1 文档/隐私问题。
- 若下一轮只继续“登记 residual”而不修 P1/P2 concern，仓库会从架构收口阶段滑回**治理叙事失真 + 支持面隐私不清**的慢性维护税。
