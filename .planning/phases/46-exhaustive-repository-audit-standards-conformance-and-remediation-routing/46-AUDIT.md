# Phase 46 Master Audit

## Audit Method

- 裁决顺序遵循 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` → `.planning/PROJECT.md` → `.planning/ROADMAP.md` → `.planning/REQUIREMENTS.md` → `.planning/STATE.md` → baseline / reviews truth。
- file-level 覆盖以 `46-01-REPO-INVENTORY.md` 为唯一索引真源；分片分析分别由 `46-02-ARCHITECTURE-CODE-AUDIT.md` 与 `46-03-TOOLCHAIN-OSS-GOVERNANCE-AUDIT.md` 提供。
- 审阅不是重新发明架构，而是验证当前单一北极星主链的成熟度、缺陷、残留与后续优先级。
- 旧 `Phase 41` 审计只作为历史参考，不作为当前 active truth；本次 shipped baseline 明确是 `v1.6` archived truth。

## Scope Completeness

- `git ls-files` 跟踪文件：`1321`
- 本地 `Phase 46` 工作区额外文件：`5`
- 总 inventoried surfaces：`1326`
- `deep-review`：`646`
- `classification-only`（里程碑归档 / 历史 phase execution trace）：`675`
- `local-phase`：`5`
- blind spots：`0`

### Coverage verdict

- **当前生产/测试/文档/工作流/治理真源已完成全仓 file-level 清点。**
- `.planning/phases/**` 与历史里程碑文档没有被当作 current truth 重新评审，而是被正确归类为 archive / execution trace / promoted evidence 候选。
- 当前仓库最重要的事实不是“有没有漏看某个文件”，而是“已经看完后，哪些问题仍值得进入正式 Phase 47+ 路由”。

## Architecture Verdict

### 总评

- **结论：主链基本收敛，无第二正式 root 回流。**
- `LiproProtocolFacade`、`Coordinator`、`LiproRestFacade`、runtime protocol service、control/runtime access、adapter shells 的正式故事线是清楚的。
- 当前 architectural risk 不是“方向错了”，而是**正确方向上的 formal roots / helper homes 仍偏厚**。

### Strengths

- 单一 protocol root、单一 runtime root、thin adapter story 仍被严格守住。
- `Protocol`、collaborator injection、`OperationOutcome`、`reason_code`、runtime capability ports 等设计信号显示仓库已经摆脱 mixin / inheritance spaghetti。
- 依赖门禁健康：未发现 platform / entity 直连 protocol internals，也未看到 control bypass runtime public surface 的明显回流。
- residual ledger 明确记录“当前无 active residual family”，这说明仓库不再靠匿名兼容债生存。

### Gaps

- formal roots 仍大：`core/protocol/facade.py`、`core/api/rest_facade.py`、`core/coordinator/coordinator.py`、`control/runtime_access.py`、`__init__.py`、`control/entry_lifecycle_controller.py` 都已进入高杠杆维护区。
- `RuntimeAccess` 是本次架构审阅中最值得警惕的对象：它是正确的唯一 helper home，但已接近 projection megafile。
- `core/command` 的 write-side helper 与 protocol/api policy 之间仍有 ownership 漂移，`dispatch.py` / `result.py` / `result_policy.py` 的边界尚未完全压实。
- 局部 auth/error shared home 尚未完全闭合：`services/execution.py` 已是正式 shared home，但 `services/diagnostics/helpers.py` 仍保留近似的 reauth/error loop 语义。

## Testing and Verification Verdict

### 总评

- **结论：测试体系结构成熟，但 mega-test 与 megaguard 仍显著影响 failure localization。**
- 测试目录分层本身是优点；真正的问题集中在少数超大 suite 与治理 megaguards，而不是测试体系失控。

### Strengths

- `core / platforms / services / flows / integration / snapshots / benchmarks / meta` 形成了清楚的验证拓扑。
- protocol contract → replay → harness → asset authority 是全仓测试设计中最成熟的 assurance chain。
- external-boundary fixtures、authority checks、OTA/update/path-specific tests 形成了漂亮的 contract-hardening 案例。
- meta guards 让依赖方向、public surface、toolchain truth、release contract 与 budget no-growth 都可机审。

### Gaps

- `tests/meta/test_governance_closeout_guards.py` 是最重的治理 megaguard，phase / milestone / promotion / archive story 被过度吸附在一个文件里。
- `tests/core/test_coordinator.py`、`tests/core/test_diagnostics.py` 属于典型 runtime-root / diagnostics megas，失败解释半径过大。
- `tests/core/api/test_api_command_surface.py`、`tests/core/mqtt/test_transport_runtime.py`、`tests/platforms/test_update.py` 虽已部分分段，但仍是 topicization 优先对象。
- 仓顶零散 tests（例如 coordinator public/runtime、refactor tools）目录归属不够自然，削弱发现性。

## Typing and Exception Verdict

### 总评

- **结论：异常语义已达高成熟度，类型债仍主要集中在 REST child façade 相关 surface。**
- 生产代码没有 `type: ignore`、没有 broad catch，这说明“typed failure semantics”已经不是口号。

### Strengths

- `mypy strict = true` 已开启，仓库把类型约束作为正式工程规则对待。
- `tests/meta/test_phase31_runtime_budget_guards.py` 与 `tests/meta/test_phase45_hotspot_budget_guards.py` 把 touched-zone type/exception budget 变成 no-growth guard。
- `OperationOutcome` + `reason_code` 在 diagnostics、MQTT runtime、anonymous share 路径中使用成熟，是异常语义亮点。

### Gaps

- 生产侧 `Any` 仍然重压在 `core/api/endpoint_surface.py`、`core/api/rest_facade.py`、`core/api/request_gateway.py` 一带。
- `RuntimeAccess` 与少数 projection-heavy helpers 仍依赖较多 `cast` / reflection-style read-model coercion。
- repo-wide `Any` 粗指标容易被 test helpers 与 budget marker 字面量放大，因此未来需要显式区分 production debt 与 test/guard literal debt。
- 类型债已从“广域无序”收敛为“局部集中”；这正是下一轮最适合继续减量的形态。

## Documentation Workflow and OSS Verdict

### 总评

- **结论：仓库已具备高质量的 release / security / governance 工程化素养，但 continuity 明显受单维护者模式约束。**
- open-source posture 更像“严治理、高信任、release-security-first 的维护型仓库”，而不是“低门槛社区驱动仓库”。

### Strengths

- public fast-path 清楚：`README/README_zh -> troubleshooting -> support/security -> contributing/templates`。
- maintainer appendix 隔离得当：runbook、north-star、developer architecture、`.planning/*` 没有粗暴塞给普通用户。
- `ci.yml` 与 `release.yml` 形成高成熟度供应链闭环：CI reuse、tagged gates、CodeQL、pip-audit、install smoke、SBOM、attestation、cosign、release identity 一应俱全。
- governance truth 很强：authority matrix、promoted phase asset allowlist、residual ledger、file matrix 让 current truth 与 archive truth 的边界清楚可机审。

### Gaps

- 最大风险是 single-maintainer / no delegate：文档已诚实承认，但仍缺少真正的 custody recovery contract。
- `install.sh` 的 remote unpinned `latest` 默认行为，与 stable guidance 偏向 verified release assets 之间存在张力。
- `Documentation` URL 仍指向根 README，而非 docs index；scripts active/deprecated 混放也增加认知噪音。
- maintainer appendix 与治理真源中文占比高，这对未来国际化接棒不够友好。

## Top Strengths

1. **单一正式主链依旧成立**：没有 split-root 或 legacy public-name 回流。
2. **供应链与发布安全非常成熟**：release-security-first 设计可对标优秀开源工程实践。
3. **治理真源体系强**：authority / review / promotion / archive 边界清楚，几乎没有“只存在于对话里的规则”。
4. **typed failure semantics 已经进入核心路径**：生产路径 broad catch 与 `type: ignore` 接近归零。
5. **protocol contract / replay / external-boundary assurance chain 质量高**：这条测试主链是仓库的标杆案例。

## Top Gaps

1. **`RuntimeAccess` 与若干 formal-root/helper hotspots 仍偏大**。
2. **governance megaguards 与 runtime-root megas 影响 failure localization**。
3. **REST child façade family 的 `Any` 债仍然集中**。
4. **single-maintainer continuity contract 仍偏弱**。
5. **docs/tooling discoverability 仍有少量噪音**（scripts stub、Documentation URL、maintainer appendix globalization）。

## Priority Risks

### P0

- **Continuity contract 缺位**：当前最值得进入正式路由的高优先级仓库级风险，不是结构回退，而是维护者缺席时的 custody resilience。

### P1

- **formal-root / helper hotspot 继续增厚**：尤其是 `RuntimeAccess`、`Coordinator`、`LiproRestFacade`、`EntryLifecycleController`、`__init__.py`。
- **mega-tests / megaguards 进一步恶化失败定位体验**：优先是 closeout guards、coordinator、diagnostics、update/platform tests。
- **command/result ownership 漂移与 diagnostics auth/error duplicated semantics**：若不收口，会在后续迭代中变成软性分叉点。

### P2

- **localized compat shims 未被完全显式化**：它们不再是 active residual family，但仍值得在治理文本中更诚实地表述。
- **maintainer appendix 的全球化接棒摩擦**：对普通用户无碍，但对未来 delegate onboarding 有影响。
- **scripts / docs discoverability 噪音**：不是大问题，但会持续增加认知成本。

## Final Verdict

- `lipro-hass` 当前不是“需要再救一次”的仓库，而是一个**已经完成主链收敛、进入高阶 maintainability / continuity / typed-surface / test-topology 精修阶段**的仓库。
- **无 P0 发布阻断型架构缺陷**，这点非常重要。
- 但这也意味着下一轮工作必须更精确：不能再靠“大重构”叙事，而要靠 **formal-root 限流、REST typed surface 减债、mega-test topicization、continuity contract 正式化** 四条路线继续推进。
- 因此本 phase 的正确收口不是“再改几处代码”，而是把上述问题正式压成 `Phase 47+` 路线，并把本次终极审阅升级为 promoted evidence。
