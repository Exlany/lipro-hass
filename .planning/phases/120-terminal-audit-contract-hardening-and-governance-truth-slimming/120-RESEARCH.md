# Phase 120: terminal audit closure, contract hardening, and governance truth slimming - Research

**Researched:** 2026-04-01
**Domain:** Home Assistant integration contract tightening, flow error taxonomy, toolchain guard hardening, and governance/docs truth slimming
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- `Coordinator` public runtime home remains `custom_components/lipro/coordinator_entry.py`; only contract truth, tooling truth, and docs truth may tighten.
- `Phase 120` is the only delivery phase in `v1.34`; all touched requirements must map to it exactly once.
- maintainer continuity may only be tightened as honest freeze posture / custody-restoration wording; no hidden delegate, mirror, or private fallback may be implied.
- current docs must prefer stable pointers or latest-archived pointers over version-pinned `.planning/vX_*` references.

### Claude's Discretion
- choose the narrowest typed aliases / helpers that remove loose mapping folklore without introducing a second truth carrier
- decide whether `send_command` strictness lives in schema validators, normalization helpers, or both, as long as the outward truth is single-source
- choose the smallest viable guard strategy (AST / helper-based / behavior-based) that removes brittle string containment checks
- pick the appropriate archive-facing home for the developer-architecture appendix so current docs stay slim and history remains reachable

### Deferred Ideas (OUT OF SCOPE)
- repo-external delegate onboarding、non-GitHub mirror continuity、private fallback implementation：本 phase 只允许诚实记录，不负责仓外闭环。
- `.planning/PROJECT.md` / `.planning/ROADMAP.md` 全量历史瘦身：本轮以 current-route correctness 为主，不做大规模历史重写。
- any new product-facing behavior or UX expansion unrelated to audit follow-through.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ARC-32 | runtime/service formal contract tightening must stay single-source | Plan 120-01 contract aliasing + runtime-access normalization |
| HOT-52 | `send_command` validation must collapse to one schema truth | Plan 120-01 schema validator / normalizer convergence |
| QLT-47 | flow errors must distinguish auth/connectivity/entry/response/unexpected cases | Plan 120-02 error taxonomy + translations/tests |
| GOV-78 | current docs/runbook/template must use stable pointers | Plan 120-03 stable current-route / latest-archived pointers |
| GOV-79 | toolchain guards must stop relying on brittle import/phase literals | Plan 120-03 AST/behavior-based guards + lint metadata |
| DOC-10 | `docs/developer_architecture.md` must shed historical appendix | Plan 120-03 appendix relocation / slim current doc |
| OSS-15 | maintainer continuity must stay honest without fake delegate | Plan 120-03 freeze-posture codification |
| TST-42 | focused regressions must freeze all above truths | All three plans add/refresh focused tests |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- `AGENTS.md` is the canonical repository contract; `CLAUDE.md` does not create a second rule set.
- Read-order truth for planning is: `AGENTS.md` → `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` → `.planning/MILESTONES.md` → `.planning/PROJECT.md` → `.planning/ROADMAP.md` → `.planning/REQUIREMENTS.md` → `.planning/STATE.md` → baseline/reviews/docs.
- Current milestone / phase / next-step truth must follow `.planning/STATE.md`.
- Do not create or rely on `agent.md`.

## Problem Statement

`v1.33` 已把 MQTT boundary、runtime contract 单一真源与 release/governance freshness 收口成 archived baseline，但终审仍暴露 6 类 repo-internal residual：

1. `runtime_types.py` 仍暴露 loose payload types（如 `list[dict[str, str]]`、`Mapping[str, object]`），而 `runtime_access.py` 的 snapshot fallback 仍可回退到 raw coordinator facts。
2. `services/command.py` 目前存在“手写类型闸门 + voluptuous schema”双轨验证，字段一旦扩展就存在 drift 风险。
3. `flow/login.py` 与 `flow/submission.py` 仍把多类失败压成 `unknown`，导致 UI 提示、回归定位与 stored-entry corruption 分辨率不足。
4. `scripts/check_file_matrix.py` 维持三套导入分支；相关 meta guards 主要靠字符串包含/排除，脆弱且难随重构演进。
5. `scripts/lint` 的 changed-surface assurance 被 `phase113_*` 变量名与硬编码 pattern 绑死，成为当前治理债。
6. `docs/developer_architecture.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`.github/pull_request_template.md` 仍混有历史 appendix / 版本钉死 pointer；maintainer continuity 也必须继续诚实表达 freeze posture，而不是暗示 hidden delegate。

## Summary

本 phase 不需要新依赖，也不需要新 public root；它本质上是一次 **single-source truth hardening**。最优路径不是“大重写”，而是沿现有正式 homes 做三束收口：

- **Plan 120-01**：runtime/service contract tightening，把 typed alias、schema normalizer 与 runtime-access helper 拉回单一 formal truth。
- **Plan 120-02**：flow error taxonomy hardening，把 `invalid_entry` / `invalid_response` / `unexpected_error` 明确成 UI/translation/test 层都能消费的语义。
- **Plan 120-03**：toolchain/docs/governance truth slimming，把 brittle string guards、`phase113_*` fast-path 与 version-pinned doc pointers 统一收回结构化真源。

**Primary recommendation:** 只在现有正式 home 内收紧 contract 与 pointer，避免新增 helper root、parallel schema、或“为了文档瘦身而创造第二套 archive truth”。

## Ground Truth

### Repository Truth Already in Place

- North-star 明确禁止第二正式主链、compat shell 回流、control/entity 直连 internals，并要求迁移残留持续收口。来源：`docs/NORTH_STAR_TARGET_ARCHITECTURE.md`。
- `AGENTS.md` 已把 `LiproProtocolFacade`、`Coordinator`、`control/` home、`RuntimeAccess` 与 governance truth sources 固定为唯一裁决基线。来源：`AGENTS.md`。
- `v1.34` 现已被 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` 与 GSD 解析器识别为 active milestone，`Phase 120` 被识别为 discussed / planning-ready。来源：`.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`。

### Hotspot Facts Verified Locally

- `CommandServiceLike.async_send_command` 与 `LiproRuntimeCoordinator.async_send_command` 仍使用 `list[dict[str, str]] | None`；`ProtocolDiagnosticsContextLike` / `ProtocolTelemetryFacadeLike` 仍以 broad `Mapping[str, object]` 暴露 diagnostics snapshots。来源：`custom_components/lipro/runtime_types.py`。
- `services/command.py` 先做 `_validate_send_command_payload_types()`，再做 `SERVICE_SEND_COMMAND_SCHEMA(...)`，形成双重 truth。来源：`custom_components/lipro/services/command.py`, `custom_components/lipro/services/contracts.py`。
- `validate_reauth_submission()` / `validate_reconfigure_submission()` 在缺失 `phone_id` 或 persisted phone 非法时仍回 `errors['base'] = 'unknown'`。来源：`custom_components/lipro/flow/submission.py`, `tests/flows/test_flow_submission.py`。
- `async_try_hashed_login()` 把 malformed response 与 unexpected login failure 都映射到 `unknown`。来源：`custom_components/lipro/flow/login.py`, `tests/flows/test_config_flow_user.py`。
- `scripts/check_file_matrix.py` 现在依赖 `TYPE_CHECKING` + direct-script + package import 三套分支；`tests/meta/test_phase89_tooling_decoupling_guards.py` 主要通过字符串片段断言导入形态。来源：`scripts/check_file_matrix.py`, `tests/meta/test_phase89_tooling_decoupling_guards.py`。
- `scripts/lint` 的 changed-surface fast path 仍用 `phase113_*` 正则变量作为治理入口。来源：`scripts/lint`。
- `docs/developer_architecture.md` 当前正文后半段仍带多段历史 phase appendix；runbook 与 PR 模板仍引用具体 `V1_33` / `v1.33` 路径。来源：`docs/developer_architecture.md`, `docs/MAINTAINER_RELEASE_RUNBOOK.md`, `.github/pull_request_template.md`。

## Decisions

### D-01 Contract tightening stays inside formal homes
- 类型收紧只能在 `runtime_types.py`、`services/contracts.py`、`runtime_access.py` 这些正式 home 内完成。
- 不新增“typed helper home”去与现有 formal truth 并列竞争。

### D-02 `send_command` must have one outward truth
- outward truth 应是单一 schema / normalization path；若保留 strictness，strictness 应由 schema validator / normalization helper 表达，而不是再额外维持一套手写字段闸门。

### D-03 Flow errors need UI-consumable taxonomy
- 至少应显式区分：`invalid_auth`、`cannot_connect`、`invalid_entry`、`invalid_response`、`unexpected_error`。
- stored-entry corruption / missing `phone_id` 应归为 `invalid_entry`，而不是继续与 upstream malformed response 混为同一类 unknown。

### D-04 Toolchain guards should assert structure, not prose accidents
- 对 `check_file_matrix.py` 的 guard 应优先断言 import topology / helper resolution behavior，而不是靠字符串包含/排除。
- `scripts/lint` fast-path 需要从 phase literal 升级为 reusable changed-surface assurance metadata（命名、pattern、pytest target 三者解耦）。

### D-05 Current docs must stop carrying history as live guidance
- `docs/developer_architecture.md` 保留 current architecture / current truth / current reading order；历史 appendix 下沉到 archive-facing home 并通过稳定 pointer reachability 保留。
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` 与 `.github/pull_request_template.md` 只能依赖稳定 current-route family 或 latest archived pointer，不能继续钉死具体 `v1.33` 路径。

### D-06 Continuity wording must remain honest-by-default
- 本仓无法在 Phase 120 内新增真实 delegate 或仓外 continuity 设施，因此研究/计划都不得产生“delegate 已存在”的假象。
- 可执行动作仅限：freeze posture、custody restoration 条件、current public routing 的单一真源化。

## Standard Stack

### Core
| Library / Surface | Version / Truth | Purpose | Why Standard |
|-------------------|-----------------|---------|--------------|
| Python | `>=3.14.2` | repo runtime / typing baseline | 全仓已锁定 `py314` 语义与类型语法。来源：`pyproject.toml` |
| Home Assistant | `2026.3.1` (dev pin) | integration host contract | tests / flows / service handlers 都围绕该版本验证。来源：`pyproject.toml` |
| `voluptuous` | `>=0.15.2,<1.0.0` | service schema / input normalization | 已是项目正式 schema stack；本 phase 应复用，不引入替代验证库。来源：`pyproject.toml`, `custom_components/lipro/services/contracts.py` |
| `pytest` + `pytest-homeassistant-custom-component` | repo dev deps | focused regressions | 现有 flows / runtime / governance tests 全部依赖。来源：`pyproject.toml`, `tests/` |
| `ruff` / `mypy` | repo dev deps | lint / typing gates | 本 phase 直接触及 typing 与 docs/toolchain guards。来源：`pyproject.toml` |

### Supporting
| Surface | Purpose | When to Use |
|---------|---------|-------------|
| `RuntimeAccess` formal helpers | runtime snapshot / device lookup read-model | 当 control-plane 需要读取 coordinator facts 时，优先走 formal helper，而不是 raw field fallback |
| `services/contracts.py` | service payload schema truth | 当服务参数需要 stricter typing / normalization 时，扩展这里而不是在 handler 内另起规则 |
| translations (`en.json`, `zh-Hans.json`) | flow error UX contract | 新 error key 必须同步翻译与 flow regression |
| meta/toolchain guards | no-regrowth proof | 对 import topology、lint fast-path 与 docs pointer 的 current-truth 冻结 |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `voluptuous` single-source schema | 手写 dataclass / pydantic validator | 本仓无此正式栈；会制造第二套 validation truth |
| AST/behavior guard | 字符串包含断言 | 字符串快但脆；对 refactor 与 import refolding 非常敏感 |
| stable pointer / latest archived pointer | 版本钉死 `.planning/vX_*` | 写起来快，但下一 milestone 必然漂移 |

## Architecture Patterns

### Pattern 1: Formal home aliases, not duplicate protocols
**What:** service-facing type aliases 应继续从 `runtime_types.py` 暴露，再由 consumer 通过 `type X = FormalProtocol` 复用。
**When to use:** runtime / service / control 共享 contract 时。
**Use in this phase:** `services/command.py`、`runtime_access.py`、相关 guards。

### Pattern 2: Strict normalization belongs to schema truth
**What:** handler 只负责从 call/data 抽取 payload，再调用 formal schema / normalizer；不要保留 দ্বিতीय手写字段 validator。
**When to use:** `send_command`、future service payload validation。
**Use in this phase:** `services/contracts.py` + `services/command.py`。

### Pattern 3: Current docs are thin selectors; history is pull-only
**What:** current docs 只讲 current route / current guidance / stable pointers；历史 appendix 下沉到 archive-facing home。
**When to use:** developer architecture docs, runbook pointers, PR template guidance。
**Use in this phase:** `docs/developer_architecture.md`, `docs/MAINTAINER_RELEASE_RUNBOOK.md`, `.github/pull_request_template.md`。

### Anti-Patterns to Avoid
- **Second truth validator:** handler 自己一套字段闸门，schema 再一套。
- **String-contains governance:** meta guard 只盯字符串片段，不验证结构或行为。
- **Phase-literal tooling:** `phase113_*` 这种命名把 historical phase 变成 live operational contract。
- **Current/history 混层:** current docs 承载大段历史 appendix，或 current template 指向具体 archived version file。

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| strict service validation | handler-local second validator | `services/contracts.py` 中的 strict schema / normalizer | outward truth 必须单一，避免 drift |
| runtime snapshot fallback | raw coordinator field probes scattered in callers | `RuntimeAccess` formal helper / typed view | 保持 control-plane 只依赖 public/read-model surface |
| toolchain import proof | brittle string grep | AST / helper-behavior assertion | 重构后更稳，能真正验证 topology |
| current-route doc linking | version-pinned `.planning/vX_*` | stable current-route family + latest archived pointer | 下个 milestone 不必再次全面漂移修补 |

**Key insight:** 本 phase 的最佳解不是“更多 helper”，而是把现有 formal homes 的 outward truth 再收窄一层，让同一份 truth 同时被实现、测试与文档消费。

## Common Pitfalls

### Pitfall 1: 类型别名只改 outward protocol，未改 consumer tests
**What goes wrong:** `runtime_types.py` 收紧后，tests 或 service consumers 仍按旧 `list[dict[str, str]]` 推断，导致类型或 runtime drift。
**How to avoid:** 同步修改 consumer type alias、focused guard、service tests。

### Pitfall 2: 新增 error key 但没同步 translations / flow tests
**What goes wrong:** config flow 显示未翻译 key 或旧 tests 继续断言 `unknown`。
**How to avoid:** translation + flow regression + submission regression 同波次提交。

### Pitfall 3: 把 toolchain 去脆化写成更复杂的字符串断言
**What goes wrong:** 看似减少了字面量，实则仍是 brittle grep。
**How to avoid:** 优先断言 helper API、AST import module、或真实 CLI behavior。

### Pitfall 4: 文档瘦身时误删 current truth reachability
**What goes wrong:** appendix 虽然移走了，但 current docs 没有留下稳定入口，导致历史证据不可达。
**How to avoid:** 下沉历史时，current docs 只保留一跳 reachability；archive asset 仍保留 pull-only 身份。

## Code Examples

### Example 1: consumer should alias formal protocol instead of redefining it
- Existing good pattern: `custom_components/lipro/services/command.py` 已使用 `type CommandService = CommandServiceLike`、`type CommandCoordinator = LiproCoordinator`。
- Planner implication: 保留这种 alias-home 模式，只收紧 formal protocol 本身。

### Example 2: runtime-access should prefer formal helper over raw fallback
- Existing good pattern: `custom_components/lipro/control/runtime_access.py` 已暴露 `get_runtime_device_mapping()`、`is_runtime_device_mapping_degraded()`。
- Planner implication: snapshot / diagnostics projection 的 fallback 优先调用 formal helper，不再直接依赖 raw coordinator fields。

## Environment Availability

Step 2.6: SKIPPED (no external dependencies identified). 本 phase 只涉及仓内 Python / Markdown / shell / governance 资产；执行依赖已由 repo 自带 `uv`, `pytest`, `ruff`, `mypy` 与 GSD 工具链覆盖。

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest` + `pytest-homeassistant-custom-component` |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| Quick run command | `uv run pytest -q <focused tests>` |
| Full suite command | `uv run pytest -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ARC-32 | runtime/service formal contract truth remains single-source | unit / meta | `uv run pytest tests/core/test_runtime_access.py tests/meta/test_runtime_contract_truth.py -q` | ✅ |
| HOT-52 | `send_command` strict validation remains single-source | unit | `uv run pytest tests/services/test_service_resilience.py tests/core/coordinator/services/test_command_service.py -q` | ✅ |
| QLT-47 | flow error taxonomy differentiates new keys | flow / unit | `uv run pytest tests/flows/test_config_flow_user.py tests/flows/test_config_flow_reauth.py tests/flows/test_config_flow_reconfigure.py tests/flows/test_flow_submission.py -q` | ✅ |
| GOV-78 | runbook/template/docs use stable pointers | meta | `uv run pytest tests/meta/test_governance_release_docs.py -q` | ✅ |
| GOV-79 | toolchain guards assert structure and lint fast-path is data-driven | meta | `uv run pytest tests/meta/toolchain_truth_checker_paths.py tests/meta/test_phase89_tooling_decoupling_guards.py -q` | ✅ |
| DOC-10 | developer architecture current doc is slim and reachable | meta | `uv run pytest tests/meta/test_governance_release_docs.py -q` | ✅ |
| OSS-15 | continuity wording remains honest and no hidden delegate implied | meta | `uv run pytest tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_contract.py -q` | ✅ |
| TST-42 | touched scope keeps focused regressions synchronized | combined | `uv run pytest tests/meta/test_runtime_contract_truth.py tests/services/test_service_resilience.py tests/flows/test_config_flow_user.py tests/meta/toolchain_truth_checker_paths.py tests/meta/test_governance_release_docs.py -q` | ✅ |

### Sampling Rate
- **Per task commit:** targeted `uv run pytest -q ...` for the touched family
- **Per wave merge:** `uv run pytest -q` on all Phase 120 focused files + `uv run ruff check .`
- **Phase gate:** `uv run pytest -q` and `uv run python scripts/check_file_matrix.py --check`

### Wave 0 Gaps
- None — existing runtime, flow, toolchain, and governance test infrastructure already covers the phase; only focused cases need extension/update.

## Execution Mapping

### Plan 120-01 — Runtime/service contract tightening and runtime-access normalization
**Boundary:** `custom_components/lipro/runtime_types.py`, `custom_components/lipro/control/runtime_access.py`, `custom_components/lipro/services/contracts.py`, `custom_components/lipro/services/command.py`, runtime/service tests.

**Must achieve:**
- formal typed aliases replace loose payload/mapping folklore where repo already has a named contract
- `send_command` outward validation becomes one schema/normalization truth
- runtime snapshot / diagnostics projection prefer formal helper-derived facts over raw field fallback

**Verification spine:** `tests/core/test_runtime_access.py`, `tests/meta/test_runtime_contract_truth.py`, `tests/services/test_service_resilience.py`, `tests/core/coordinator/services/test_command_service.py`

### Plan 120-02 — Flow error taxonomy hardening and translations/tests alignment
**Boundary:** `custom_components/lipro/flow/login.py`, `custom_components/lipro/flow/submission.py`, `custom_components/lipro/translations/{en,zh-Hans}.json`, flow tests.

**Must achieve:**
- `invalid_entry` / `invalid_response` / `unexpected_error` become explicit flow/base error outcomes
- reauth/reconfigure stored-entry corruption is no longer folded into `unknown`
- translations and regressions move in the same change set

**Verification spine:** `tests/flows/test_config_flow_user.py`, `tests/flows/test_config_flow_reauth.py`, `tests/flows/test_config_flow_reconfigure.py`, `tests/flows/test_flow_submission.py`

### Plan 120-03 — Toolchain guard de-brittling, docs appendix slimming, and stable governance pointers
**Boundary:** `scripts/check_file_matrix.py`, `scripts/lint`, `tests/meta/toolchain_truth_checker_paths.py`, `tests/meta/test_phase89_tooling_decoupling_guards.py`, `docs/developer_architecture.md`, `docs/MAINTAINER_RELEASE_RUNBOOK.md`, `.github/pull_request_template.md`, relevant governance docs/tests.

**Must achieve:**
- `check_file_matrix` import story collapses to one operational truth and guards assert structure/behavior
- changed-surface assurance loses `phase113_*` naming and becomes reusable metadata
- current docs point to stable current-route family or latest archived pointer; history remains reachable but no longer clutters current guidance
- continuity text remains honest and freeze-oriented

**Verification spine:** `tests/meta/toolchain_truth_checker_paths.py`, `tests/meta/test_phase89_tooling_decoupling_guards.py`, `tests/meta/test_governance_release_docs.py`, `tests/meta/test_governance_release_contract.py`

## Sources

### Primary (HIGH confidence)
- `AGENTS.md` — formal homes, authority order, modification constraints
- `CLAUDE.md` — read order and no-second-rules constraint
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — north-star laws and forbidden regressions
- `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, `.planning/MILESTONES.md` — current milestone and phase truth
- `custom_components/lipro/runtime_types.py`, `custom_components/lipro/control/runtime_access.py`, `custom_components/lipro/services/{contracts,command}.py`, `custom_components/lipro/flow/{login,submission}.py`, `scripts/check_file_matrix.py`, `scripts/lint`, `docs/developer_architecture.md`, `docs/MAINTAINER_RELEASE_RUNBOOK.md`, `.github/pull_request_template.md`
- focused tests under `tests/core/`, `tests/flows/`, `tests/services/`, `tests/meta/`

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — entirely derived from `pyproject.toml` and current repo tooling.
- Architecture: HIGH — derived from north-star docs, `AGENTS.md`, and local hotspots/tests.
- Pitfalls: HIGH — derived from current implementation/tests rather than external assumptions.

**Research date:** 2026-04-01
**Valid until:** 2026-05-01 (repo-internal phase; refresh if milestone scope changes)
