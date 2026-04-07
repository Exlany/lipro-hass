# Phase 15 Research

**Date:** 2026-03-15
**Status:** Final
**Recommended Shape:** 5 plans / 3 waves

## Research Question

为了把 `Phase 15` 计划做准，我必须提前知道什么？

答案是：**先把“support-facing local debug truth”与“developer-feedback upload truth”分开，再把 governance / docs / CI / residual 的裁决一次写成单一故事线。** 当前真正未闭合的，不是“再做一轮泛重构”，而是以下七个仍然成立的确认问题。

## Already Fixed / Must Stay Out of Scope

- `control/service_router.py` 的 public handler home 身份不能动；只能继续下沉私有 glue，不能迁出 handler root（`.planning/phases/15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through/15-CONTEXT.md:39`，`.planning/phases/15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through/15-PRD.md:41`，`custom_components/lipro/control/service_router.py:230`）。
- `get_developer_report` 的本地调试价值不能被“上传脱敏”反向削弱；Phase 15 应新增 upload projector，而不是把 local report 一刀切匿名化（`.planning/phases/15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through/15-PRD.md:42`，`custom_components/lipro/services/diagnostics/helpers.py:201`）。
- 本 phase 不做 `LiproMqttClient` 物理 rename，不做 `_ClientBase` 家族的大规模文件级删除；只做 residual ownership / guard / locality follow-through（`.planning/phases/15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through/15-PRD.md:55`，`.planning/reviews/KILL_LIST.md:7`，`.planning/reviews/KILL_LIST.md:16`）。
- 不引入第二条正式主链，不把 support helper 升格为新的正式 root（`.planning/REQUIREMENTS.md:111`，`.planning/phases/15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through/15-PRD.md:43`）。

## Rechecked Confirmation Questions

### Q1 / `SPT-01`: developer feedback 合同为什么仍是 active gap？

**Why this still exists**

- 当前 local developer report 明确保留 `iot_name`，同时也保留 `name`、panel `keyName`、IR `rc_list[].name` 与 remote/gateway `name`；这说明它现在是“调试视图”，不是“上传契约”（`custom_components/lipro/core/utils/developer_report.py:60`，`custom_components/lipro/core/utils/developer_report.py:132`，`custom_components/lipro/core/utils/developer_report.py:245`，`custom_components/lipro/core/utils/developer_report.py:293`，`custom_components/lipro/core/utils/developer_report.py:320`）。
- 上传入口没有独立 projector；`submit_developer_feedback` 直接把 `collect_reports()` 的产物塞进 feedback payload，local view 与 upload view 共享同一对象图（`custom_components/lipro/control/service_router.py:230`，`custom_components/lipro/control/service_router.py:242`，`custom_components/lipro/services/diagnostics/helpers.py:187`，`custom_components/lipro/services/diagnostics/helpers.py:248`）。
- share worker 前的 sanitizer 只会删显式敏感 key，如 `deviceName` / `roomName`，但不会处理通用 `name`、panel `keyName`，也没有把“必须保留 `iotName`”写成显式 contract（`custom_components/lipro/core/anonymous_share/sanitize.py:34`，`custom_components/lipro/core/anonymous_share/sanitize.py:44`，`custom_components/lipro/core/anonymous_share/sanitize.py:64`，`custom_components/lipro/core/anonymous_share/report_builder.py:62`）。
- 现有 boundary fixture 只覆盖极简 payload：service 层只测 `{"runtime": {"ok": true}}`，share-worker 层只测 `{"note": "manual run"}`，并未覆盖 `iotName + user-defined labels` 的混合样本（`tests/services/test_services_diagnostics.py:411`，`tests/core/test_anonymous_share.py:1140`，`tests/fixtures/external_boundaries/support_payload/developer_feedback_service.canonical.json:1`，`tests/fixtures/external_boundaries/share_worker/developer_feedback_report.canonical.json:1`）。
- 本地 tests 还显式断言 `name` / `keyName` / `rc_list[].name` 保留，说明“local debug truth”与“upload truth”确实尚未分家（`tests/core/test_developer_report.py:218`，`tests/core/test_developer_report.py:233`，`tests/core/test_developer_report.py:296`）。

**What must be known before planning**

- `iotName` / `iot_name` 是供应商判型真源，必须保留，不能误伤（`.planning/phases/15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through/15-CONTEXT.md:23`，`.planning/phases/15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through/15-PRD.md:21`）。
- 用户自定义标签必须按“上传契约”显式处理：`deviceName`、通用 `name`、`roomName`、panel `keyName`、IR asset `rc_list[].name`、gateway/remote display name 默认都要匿名化/替换（`.planning/phases/15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through/15-PRD.md:22`，`.planning/phases/15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through/15-PRD.md:23`）。
- 最小风险做法不是改 `build_developer_report()`，而是在 submit path 增加 developer-feedback 专用 projector，保证 `get_developer_report` 继续服务本地调试。

### Q2 / `GOV-13`: governance truth repair 为什么仍然成立？

**Why this still exists**

- `ROADMAP` 已新增 Phase 15，但 `STATE` 仍写 `Current mode: Phase 14 complete`，frontmatter 仍是 `total_phases: 12 / completed_phases: 12 / total_plans: 43 / completed_plans: 43`；`PROJECT` 也还停留在 “Phase 14 已完成、milestone closeout pending” 叙事（`.planning/ROADMAP.md:252`，`.planning/STATE.md:8`，`.planning/STATE.md:22`，`.planning/PROJECT.md:3`）。
- `scripts/check_file_matrix.py` 的 `ACTIVE_DOC_PATHS` 只做一组硬编码存在性检查，且不包含 `.planning/PROJECT.md`；它并不验证 active docs 内部 source path 引用，也不校验 phase/status/date/footer 的跨文档一致性（`scripts/check_file_matrix.py:29`）。
- `tests/meta/test_governance_guards.py` 对 `Current mode` 只检查格式，不检查它是否与当前 phase truth 一致；phase-specific consistency tests 目前也只覆盖到 Phase 14（`tests/meta/test_governance_guards.py:117`，`tests/meta/test_governance_guards.py:280`，`tests/meta/test_governance_guards.py:429`）。

**What must be known before planning**

- Phase 15 必须先决定 active governance truth 的精确校验面：至少要覆盖 `PROJECT.md`、`STATE.md`、`ROADMAP.md`，并校验 phase/status/date/footer/closeout narrative。
- 若要真正消灭 dead-source 风险，守卫要么解析 active docs 中的 source path 引用，要么把允许的 truth sources 明确列成结构化清单并全部检查存在性；只检查固定列表不够。

### Q3 / `DOC-01`: install/support/version sync 为什么仍是实问题？

**Why this still exists**

- 锁定决策要求最低支持 HA 版本前置为 `2026.2.3`，但仓库当前真实口径仍是 `2026.3.1`：`pyproject.toml`、`hacs.json`、`SECURITY.md`、bug template、`CONTRIBUTING.md` 都如此（`.planning/phases/15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through/15-CONTEXT.md:34`，`.planning/phases/15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through/15-PRD.md:35`，`pyproject.toml:35`，`hacs.json:3`，`SECURITY.md:10`，`.github/ISSUE_TEMPLATE/bug.yml:98`，`CONTRIBUTING.md:196`）。
- README / README_zh 的安装入口没有前置最低 HA 版本，也没有把 private-repo HACS caveat 带到用户可见入口（`README.md:72`，`README_zh.md:71`）。
- CI 已经知道 private repo 需要跳过 HACS Validation，但这个事实没有同步到 README / README_zh；现在只有 workflow 和 CONTRIBUTING 知道（`.github/workflows/ci.yml:243`，`CONTRIBUTING.md:100`）。
- `tests/meta/test_version_sync.py` 目前只校验 `pyproject` / `hacs.json` / bug template，没把 README / README_zh / SECURITY / CONTRIBUTING 纳入同一版本真相（`tests/meta/test_version_sync.py:15`，`tests/meta/test_version_sync.py:55`，`tests/meta/test_version_sync.py:65`）。

**What must be known before planning**

- Phase 15 需要先裁决 canonical HA version source；建议仍以 `pyproject.toml` 的 HA pin 为 single input，再由 tests 强制 README / README_zh / SECURITY / bug template / CONTRIBUTING / HACS 跟随。
- private-repo HACS caveat 是“用户安装说明”而不只是“贡献者/CI 说明”；应当进 README 安装段。

### Q4 / `HOT-03`: service-router / developer-report hotspot 为什么还要再拆？

**Why this still exists**

- `service_router.py` 已经只保留 public handler home，但 developer report 与 developer feedback 仍共享同一 `collect_reports` 入口；upload shaping 并未独立成 focused helper（`custom_components/lipro/control/service_router.py:230`，`custom_components/lipro/control/service_router.py:242`）。
- `services/diagnostics/helpers.py` 里 `async_handle_get_developer_report()` 和 `async_handle_submit_developer_feedback()` 都以同一批 `reports` 为输入；这正是 PRD 明确要求拆开的“同一对象图 / 同一脱敏策略”（`custom_components/lipro/services/diagnostics/helpers.py:201`，`custom_components/lipro/services/diagnostics/helpers.py:222`，`.planning/phases/15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through/15-PRD.md:42`）。
- `developer_router_support.py` 已把部分 private glue 从 router 抽出，但 upload-only shaping 还没有独立 home；说明热点拆薄做了一半，还没到 contract-hardening 终点（`custom_components/lipro/control/developer_router_support.py:43`，`.planning/phases/14-legacy-stack-final-closure-api-spine-demolition-governance-truth-consolidation/14-04-SUMMARY.md:2`）。

**What must be known before planning**

- `service_router.py` 的 module identity 不能动；只能继续把 upload-only projector / label policy / payload normalization 下沉到 focused helper。
- 最小风险 home 应靠近 developer/share path，而不是把逻辑塞回 anonymous-share generic sanitizer，避免把“upload contract”误升级为全局 redaction truth。

### Q5 / `QLT-01`: testing / tooling / security gaps 哪些是真的？

**Why this still exists**

- marker registry `github / integration / slow` 只在 `pyproject.toml` 定义，repo 内没有任何 `@pytest.mark.github|integration|slow` 用例，属于名存实亡（`pyproject.toml:73`；repo-wide search `rg "pytest\.mark\.(github|integration|slow)" tests custom_components` 返回空）。
- `pytest-xdist` 与 `pytest-mypy-plugins` 只出现在依赖列表，没有任何 workflow / script / test 使用它们（`pyproject.toml:45`）。
- `coverage_diff.py` 支持 `--baseline`，但 CI 与 contributor contract 都只传 `coverage.json --minimum 95`；当前行为是阈值门，不是 diff 门（`scripts/coverage_diff.py:28`，`scripts/coverage_diff.py:43`，`.github/workflows/ci.yml:191`，`CONTRIBUTING.md:96`）。
- benchmark job 只在 `schedule/workflow_dispatch` 跑一次 benchmark，并没有基线/阈值/回归判定；现在更像 non-gating observability，但文档还把它写成同级 CI command group（`.github/workflows/ci.yml:206`，`CONTRIBUTING.md:98`）。
- dev dependency audit 只在 `schedule/workflow_dispatch` 导出并运行，且 `continue-on-error: true`；这是一项 policy 决策，但目前没有被写成清晰裁决，只是 workflow 行为（`.github/workflows/ci.yml:133`，`.github/workflows/ci.yml:145`，`.github/workflows/ci.yml:148`）。

**What must be known before planning**

- Phase 15 需要把这些 gap 分成三类：真正落地、明确删除、文档化仲裁 + 守卫；不能继续模糊共存。
- 对 benchmark / dev-audit 更推荐“写清 non-gating policy + 何时人工复核”，而不是临时做出伪阈值。

### Q6 / `TYP-03`: `RuntimeAccess` typing 为什么还没收干净？

**Why this still exists**

- `control/runtime_access.py` 仍广泛使用 `Any`：entry、coordinator、telemetry view、device mapping 都没有 narrow 成正式 contract（`custom_components/lipro/control/runtime_access.py:7`，`custom_components/lipro/control/runtime_access.py:17`，`custom_components/lipro/control/runtime_access.py:27`，`custom_components/lipro/control/runtime_access.py:53`，`custom_components/lipro/control/runtime_access.py:99`，`custom_components/lipro/control/runtime_access.py:106`，`custom_components/lipro/control/runtime_access.py:136`）。
- 这些宽类型正处于 control-plane 边界上；如果 Phase 15 不顺手收窄，support / diagnostics path 的 contract hardening 仍会建在松散 seam 上。

**What must be known before planning**

- 类型收口要局部进行：只 narrow `RuntimeAccess` 和 developer/support 相邻 seams，别把 Phase 15 扩成新的 typing campaign。
- 优先引入 small protocol / typed snapshot，而不是重开 runtime internals backdoor。

### Q7 / `RES-01`: `_ClientBase` / `LiproMqttClient` residual 为什么仍要跟进？

**Why this still exists**

- 这些 residual 并未删除，只是被更强地局部化：`KILL_LIST` 仍把 `_ClientBase` 与 `LiproMqttClient` 登记为“已登记，未删除”；`RESIDUAL_LEDGER` 也把它们当 active residual family 继续跟踪（`.planning/reviews/KILL_LIST.md:7`，`.planning/reviews/KILL_LIST.md:16`，`.planning/reviews/RESIDUAL_LEDGER.md:8`，`.planning/reviews/RESIDUAL_LEDGER.md:166`，`.planning/reviews/RESIDUAL_LEDGER.md:172`）。
- Phase 14 只做了 ownership / guard hardening，没有做 physical rename / family demolition；所以 Phase 15 仍要保持这些 residual 的故事线“更本地、更低语义、更难回流”，但不能越界到大重命名（`.planning/phases/14-legacy-stack-final-closure-api-spine-demolition-governance-truth-consolidation/14-04-SUMMARY.md:2`，`.planning/phases/15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through/15-PRD.md:56`）。

**What must be known before planning**

- 目标不是“趁机清完所有旧名”，而是确保它们不会影响 Phase 15 的 support/governance work。
- 最适合的动作是更新 guards / locality / docs，而不是 physical rename。

## Recommended Plan Shape

### Wave 1 — 先锁 contract truth

#### `15-01` Developer feedback upload projector + boundary fixtures

- 为 upload path 引入专用 projector / sanitizer；只作用于 `submit_developer_feedback`。
- fixture / regression 必须覆盖 `iotName` 保留、`deviceName` / generic `name` / `roomName` / `keyName` / `rc_list[].name` 匿名化。
- README / README_zh 的 developer feedback 文案同步改为“保留 vendor diagnosis identifiers，匿名化 user-defined labels”。

### Wave 2 — 再修 active truth 与热点边界

#### `15-02` Governance truth repair + guards

- 修正 `PROJECT.md` / `STATE.md` / `ROADMAP.md` 的 phase/status/date/footer/closeout 叙事。
- 扩展脚本 / guards，覆盖 active source path existence 与 Phase 15 planning truth。

#### `15-03` Install/support/version sync

- 统一 README / README_zh / `hacs.json` / `pyproject.toml` / `SECURITY.md` / bug template / CONTRIBUTING 的最低 HA 版本与 HACS private-repo caveat。
- 扩展 `tests/meta/test_version_sync.py` 到用户可见入口。

#### `15-04` Hotspot follow-through + local typing narrowing

- 保持 `service_router.py` public home 身份不变，只继续下沉 upload-only glue。
- 局部收窄 `RuntimeAccess` 与 developer/support 邻接 seams 的 `Any`。

### Wave 3 — 最后裁决 tooling / security / residual policy

#### `15-05` Tooling / security / residual arbitration

- 对 markers、`coverage_diff.py`、benchmark、dev audit、`pytest-xdist` / `pytest-mypy-plugins` 做“落地 / 删除 / documented arbitration”三选一。
- 把 `_ClientBase` / `LiproMqttClient` 的 residual story 继续本地化，并补 guard / docs，而不是做 rename。

## Minimal-Risk Implementation Path

1. **先新增 upload projector，不碰 local report shape。** 这样 `tests/core/test_developer_report.py` 不会因 contract hardening 被迫改写，回归面最小。
2. **只让 `submit_developer_feedback` 走新 projector。** `get_developer_report` 继续返回 local debug view，避免 support 工具与用户贴报流程被意外削弱。
3. **用 mixed fixtures 先锁契约，再改文案。** 否则 README / README_zh 会先说对，代码和 tests 仍是另一套 truth。
4. **治理修补要同轮覆盖 script + meta guards + docs。** 只改文档不改守卫，会让 Phase 15 刚落地就再次漂移。
5. **tooling/security 优先做裁决，不优先做“大启用”。** Phase 15 的价值是去伪语义，不是强行给 benchmark / xdist / mypy plugin 凑存在感。
6. **typing/residual 只做贴边 follow-through。** 只处理支撑 support/governance 合同所需的 narrow / guard，不重开 Phase 12/14 的大收口。

## Regression Risks

- **误伤 `iotName`**：若把 upload projector 做成 generic sanitizer，很容易把供应商判型真源也一起匿名化，直接损失诊断价值。
- **漏掉 generic label alias**：只 redaction `deviceName` / `roomName` 还不够；`name`、`keyName`、IR asset label 才是当前最真实的泄露面。
- **误改 local report**：如果直接改 `build_developer_report()`，会破坏既有 local debug 行为与测试期待。
- **router identity 漂移**：把 logic 迁出 `service_router.py` 太多，会碰到 repo contract 明确禁止的 public handler home 回退问题。
- **治理守卫过拟合**：若把 date/footer 校验做成过度精确的硬编码，后续每次 phase 变更都可能产生低价值维护噪音。
- **tooling policy 误变成伪 gate**：benchmark / dev-audit 若没有 baseline / threshold / policy，就不该伪装成强门禁。
- **typing 收窄打爆 mocks**：`RuntimeAccess` 是 patch-first seam，收窄时必须连同 tests / helper mock 一起调整。

## Validation Architecture

### Quick

- `uv run ruff check custom_components/lipro/control/service_router.py custom_components/lipro/control/developer_router_support.py custom_components/lipro/control/runtime_access.py custom_components/lipro/services/diagnostics/helpers.py custom_components/lipro/core/utils/developer_report.py custom_components/lipro/core/anonymous_share/report_builder.py custom_components/lipro/core/anonymous_share/sanitize.py`
- `uv run pytest -q tests/core/test_developer_report.py tests/services/test_services_diagnostics.py tests/core/test_anonymous_share.py tests/core/test_report_builder.py`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q -x tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_firmware_support_manifest_repo_asset.py`

### Full

- `uv run ruff check .`
- `uv run mypy`
- `uv run pytest tests/ -v --ignore=tests/benchmarks --cov=custom_components/lipro --cov-fail-under=95 --cov-report=json --cov-report=xml --cov-report=term-missing`
- `uv run pytest tests/snapshots/ -v`
- `uv run python scripts/coverage_diff.py coverage.json --minimum 95`
- `uv run python scripts/refactor_tools.py --coverage-json coverage.json --minimum-coverage 95`
- `./scripts/lint`

### Phase-15-specific policy notes

- 若 `coverage_diff.py` 继续保留 `diff` 语义，full gate 最终应升级为带 baseline 的命令，例如：`uv run python scripts/coverage_diff.py coverage.json --baseline <baseline.json> --minimum 95`；否则就应在本 phase 一并更名/重定义。
- benchmark 若未引入历史基线/阈值，只能继续作为 non-gating observability：`uv run pytest tests/benchmarks/ -v --benchmark-only --benchmark-json=.benchmarks/benchmark.json`。

## Decision

采用“**5 plans / 3 waves**”方案：先锁 developer feedback contract，随后同步治理真源与用户可见文档，再用最小边界动作收掉 hotspot / typing / tooling / residual follow-through。这样既直接响应 Phase 15 的 locked decisions，又不会把 support 修补演变成第二轮大重构。
