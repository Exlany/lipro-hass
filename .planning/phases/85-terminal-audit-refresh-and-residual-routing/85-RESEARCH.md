# Phase 85: Terminal audit refresh and residual routing - Research

**Researched:** 2026-03-27
**Domain:** repo-wide terminal audit / governance-truth refresh / residual routing
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- 本 phase 对应 `ROADMAP.md` 中 `Phase 85`，只覆盖 `AUD-04` 与 `GOV-62`。
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/PROJECT.md`、`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md` 是当前裁决主链；任何 audit verdict 若与旧 baseline/review prose 冲突，以当前主链和正式代码结构为准。
- 当前 active route truth 已固定为 `v1.23 active route / Phase 85 planning-ready / latest archived baseline = v1.22`；`phase_dir` 必须使用 `85-terminal-audit-refresh-and-residual-routing`，不得再写回旧的 inventory-freeze slug。
- repo-wide terminal audit 至少要明确覆盖并裁决下列已观察到的问题：
  - `.planning/baseline/TARGET_TOPOLOGY.md` 仍含 `AuthSession` / `LiproClient` compat shell / 旧 control home 叙事；
  - `.planning/baseline/DEPENDENCY_MATRIX.md` 仍保留 backoff compat surface 旧说法，与现行 `core/utils/backoff.py` 真源冲突；
  - `docs/developer_architecture.md` 与部分 baseline 文档 freshness 标记滞后；
  - `custom_components/lipro/core/anonymous_share/share_client.py` 仍有 silent compat wrapper / delete-gate debt；
  - `custom_components/lipro/runtime_infra.py` 与若干 mega tests 仍是明显热点，但是否立即拆分需要 phase-level routing 决定。
- Phase 85 的输出必须让维护者能直接看到：哪些问题已在本 phase 关闭、哪些被路由到 `Phase 86/87/88`、哪些被明确保留且原因充分。
- 不得把已关闭的 `LiproClient` / `LiproMqttClient` / archived-only route / old bootstrap stories 误写回 active family。

### Claude's Discretion
- 可以新增一个 phase-local audit artifact（例如 `85-RESEARCH.md` / `85-SUMMARY.md` / `.planning/reviews/V1_23_TERMINAL_AUDIT.md`）来承载 file-level verdict，但不要再造第二套长期治理真源；长期 truth 仍应回写到 baseline/reviews/current-route docs。
- 若某个 silent residual 可以低风险直接删除（例如仅测试引用的 compat alias），允许在本 phase 关闭；否则以诚实路由优先。
- audit verdict 可以按 `close now / route next / explicitly keep` 或类似矩阵呈现，只要 machine-checkable、后续 phase 可直接消费。

### Deferred Ideas (OUT OF SCOPE)
- `Phase 86` 负责 production residual eradication / boundary re-tightening；不要在本 phase 把 `runtime_infra.py` 之类热点硬拆到半套状态。
- `Phase 87` 负责 assurance hotspot decomposition；本 phase 可以登记 mega-test hotspots，但不必一次性完成所有 topicization。
- `Phase 88` 负责 governance sync / milestone freeze；本 phase 不直接做 milestone closeout。
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| AUD-04 | 必须基于当前仓库真相，对 `custom_components`、`tests`、`scripts`、docs、workflows 与 planning/baseline/review assets 做一次 terminal repo-wide audit，产出 file-level verdict、hotspot ranking 与 live residual inventory。 | `## Repo-Wide Audit Findings by Severity`、`## Route to Phase 86 / 87 / 88` |
| GOV-62 | audit 结论必须同步到 current-story docs 与 baseline/review truth；不得把已关闭 residual 误写回 active family，也不得留下 conversation-only verdict。 | `## Phase 85 Close Now`、`## Recommended Plan Decomposition`、`## Minimal Sufficient Validation Checklist` |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- `AGENTS.md` 先于其它真源；若与 `CLAUDE.md` 冲突，以 `AGENTS.md` 为准。
- `CLAUDE.md` 只是兼容入口，不新增第二套规则，也不覆盖 `docs/*` / `.planning/*` 真源。
- 继续遵守 `CLAUDE.md` 给出的读取顺序；当前 phase 仍以 `.planning/STATE.md` 作为当前焦点与下一步依据。
- 不创建、也不依赖 `agent.md`。

## Summary

本 phase 的正确问题不是“还要不要继续大拆 production/test”，而是：先把 **当前真源 drift**、**静默 compat debt** 与 **hotspot carry-forward** 讲成一张可执行的路由表。现有仓库主链已经明确：`Phase 85` 只承担审计与路由，不承担大规模 surgery；因此最优策略是 **先修当前真源，再冻结去向**。

审计结果很清楚：最严重的 drift 在 baseline/current-topology prose，而不是 runtime root 本身。`.planning/baseline/TARGET_TOPOLOGY.md` 仍把 `AuthSession`、旧 control home 与 `LiproClient` 过渡故事写进 target-state 文档；`.planning/baseline/DEPENDENCY_MATRIX.md` 仍保留 Phase 52/54 的 backoff compat 叙事，即使 Phase 56 已把 `core/utils/backoff.py` 冻结为正式真源；`docs/developer_architecture.md` 内容大体仍对，但 freshness 已停在 `Phase 74`。这些都属于 **Phase 85 应立即关闭** 的真源问题。相反，`runtime_infra.py` 与三份 mega tests 更像 **已知热点**：应诚实路由，不应在本 phase 半拆半留。

**Primary recommendation:** Phase 85 先关闭 baseline/current-story drift，并只做一个低风险 code close-now（若要碰代码，只删 `ShareWorkerClient._safe_read_json` 这一条 test-only alias）；其余 production residual 路由到 `Phase 86`，assurance mega-test topicization 路由到 `Phase 87`，最终治理冻结与 repo-wide 质量证明路由到 `Phase 88`。

## Standard Stack

| Tool / Asset | Verified | Purpose | Why Standard Here |
|--------------|----------|---------|-------------------|
| current truth chain | repo docs | 裁决 audit verdict | `NORTH_STAR -> PROJECT/ROADMAP/REQUIREMENTS/STATE -> baseline/reviews` 是唯一正式主链 |
| `pytest` | `9.0.0` | focused/meta verification | 现有 tests 已覆盖 route、governance、share-client 与 runtime hotspots |
| `pyproject.toml` | present | pytest config truth | `tool.pytest.ini_options` 已定义 tests 路径与 asyncio 模式 |
| `scripts/check_file_matrix.py --check` | repo script | FILE_MATRIX 一致性检查 | `GOV-62` / `GOV-63` 的直接 guard |
| `scripts/check_architecture_policy.py --check` | repo script | baseline/dependency law sanity | 适合验证 `DEPENDENCY_MATRIX` / policy 没被写歪 |

## Repo-Wide Audit Findings by Severity

| Severity | Finding | Evidence | Phase Action | Confidence |
|----------|---------|----------|--------------|------------|
| HIGH | `TARGET_TOPOLOGY` 仍把 retired topology 词汇写成 target-state：Protocol 行含 `AuthSession`，Control 行仍指向 `custom_components/lipro/__init__.py`/service surfaces，且残留规则仍把 `LiproClient` 描述为过渡存在。 | `.planning/baseline/TARGET_TOPOLOGY.md:17`, `.planning/baseline/TARGET_TOPOLOGY.md:20`, `.planning/baseline/TARGET_TOPOLOGY.md:58`；与 `docs/developer_architecture.md:24`, `docs/developer_architecture.md:62`, `.planning/reviews/RESIDUAL_LEDGER.md:29` 冲突 | Close now in Phase 85 | HIGH |
| HIGH | `DEPENDENCY_MATRIX` 同一文件内自相矛盾：Phase 52/54 仍把 `compute_exponential_retry_wait_time()` / `request_policy.py` 讲成 active compat story，但 Phase 56 已把 `core/utils/backoff.py` 冻结为 neutral truth。 | `.planning/baseline/DEPENDENCY_MATRIX.md:129`, `.planning/baseline/DEPENDENCY_MATRIX.md:155` vs `.planning/baseline/DEPENDENCY_MATRIX.md:161`, `.planning/baseline/DEPENDENCY_MATRIX.md:162`, `.planning/baseline/DEPENDENCY_MATRIX.md:163` | Close now in Phase 85 | HIGH |
| MEDIUM | `docs/developer_architecture.md` 明确自称 current-topology guide，但 freshness 仍停在 `Phase 74`；它不再是充分的 current-truth 证明。 | `docs/developer_architecture.md:3`；当前 route 见 `.planning/STATE.md`, `.planning/ROADMAP.md` | Close now in Phase 85 | HIGH |
| MEDIUM | `ShareWorkerClient` 仍有 1 个 test-only alias 和 2 个 live bool-compat outward methods。只有 `_safe_read_json` 是孤立的低风险残留；另外两条仍被 port/manager/tests 广泛消费。 | `custom_components/lipro/core/anonymous_share/share_client.py:88`, `custom_components/lipro/core/anonymous_share/share_client.py:101`, `custom_components/lipro/core/anonymous_share/share_client.py:125`；`_safe_read_json` 仅命中 `tests/core/test_share_client_primitives.py`，而 bool methods 命中 `share_client_ports.py`、`manager.py` 与多份 tests | `_safe_read_json` 可选 close now；bool contracts route Phase 86 | HIGH |
| MEDIUM | `runtime_infra.py` 仍是 433 LOC 的 formal ownership hub，承载 device-registry listener、pending reload bookkeeping 与 runtime infra lock。它是热点，但不是 active residual family，也不是 kill target。 | `custom_components/lipro/runtime_infra.py`（433 LOC）；`docs/developer_architecture.md:65`；`.planning/reviews/RESIDUAL_LEDGER.md:57`；`.planning/reviews/KILL_LIST.md:235` | Route to Phase 86 | HIGH |
| MEDIUM | 三份 assurance suites 仍承担 giant truth-carrier 角色：`test_api_diagnostics_service.py` 622 LOC / 21 test nodes，`test_protocol_contract_matrix.py` 627 LOC / 31 test nodes，`test_mqtt_runtime.py` 644 LOC / 10 grouped areas。 | `wc -l` + `rg -c` on the three files；`ROADMAP.md` / `REQUIREMENTS.md` 已把 assurance hotspot decomposition 明确放到 `Phase 87` | Route to Phase 87 | HIGH |
| LOW | `RESIDUAL_LEDGER` / `KILL_LIST` 中仍保留历史 compat / delete-gate prose，但这些是 archive evidence，不是 active drift。 | `.planning/reviews/RESIDUAL_LEDGER.md`, `.planning/reviews/KILL_LIST.md` 历史章节 | Explicitly keep | HIGH |

## Phase 85 Close Now

1. **同步 baseline 真源**
   - 改 `.planning/baseline/TARGET_TOPOLOGY.md`，把 target-state 叙事与当前 north-star/current-topology 对齐：去掉 `AuthSession` / `LiproClient` target-story 残影，改正 control formal home。
2. **消除 dependency prose 自相矛盾**
   - 改 `.planning/baseline/DEPENDENCY_MATRIX.md`，删掉或历史化 Phase 52/54 的 backoff carry-forward 句子，保留 Phase 56 之后的 `core/utils/backoff.py` truth。
3. **刷新 current-topology guide**
   - 改 `docs/developer_architecture.md` 的 freshness / alignment 标记，并在需要处补一句：它是 current guide，不得反向压过 current route truth。
4. **可选小刀口 code cleanup**
   - 若 Phase 85 要顺手关一条真正低风险 residual，只删 `custom_components/lipro/core/anonymous_share/share_client.py:88` 的 `_safe_read_json` alias，并同步 `tests/core/test_share_client_primitives.py`；**不要** 在同一计划里半迁移 `refresh_install_token()` / `submit_share_payload()`。

## Route to Phase 86 / 87 / 88

| Item | Route | Why Not Phase 85 | Exit Condition |
|------|-------|------------------|----------------|
| `ShareWorkerClient.refresh_install_token()` / `submit_share_payload()` bool outward contract | Phase 86 | 仍受 `share_client_ports.py`、`manager.py` 与多份 tests 消费；半迁移会制造 dual outward story | 对外只剩 typed outcome contract，bool compatibility 彻底退场 |
| `runtime_infra.py` maintainability slimming | Phase 86 | 它是 formal ownership home，不宜在 audit phase 半拆；应做 inward decomposition，而非迁 root | file 继续保留正式 owner 身份，但内部 helper 更窄、测试更 focused |
| `tests/core/api/test_api_diagnostics_service.py` topicization | Phase 87 | 属于 assurance hotspot，不影响 current truth 修复 | OTA / sensor-history / command-result / query-user-cloud 分题材拆开 |
| `tests/core/api/test_protocol_contract_matrix.py` topicization | Phase 87 | giant truth-carrier，应按 decoder/root/replay reuse 拆分 | boundary decoders、unified root、fixture reuse 各自成专题 suite |
| `tests/core/coordinator/runtime/test_mqtt_runtime.py` topicization | Phase 87 | 运行时热点验证仍过于集中 | connect/reconnect/message handling/notification suites 分离 |
| `FILE_MATRIX / RESIDUAL_LEDGER / KILL_LIST / PUBLIC_SURFACES / developer_architecture` 最终 freeze 与 repo-wide proof | Phase 88 | 要等 86/87 的 production + assurance closeout 全落地后才能冻结最终 post-eradication truth | `zero orphan residuals`，所有 carry-forward 都有 owner/exit/evidence |

## Architecture Patterns

### Pattern 1: 先修当前真源，再谈 carry-forward

**What:** 先用 `NORTH_STAR -> PROJECT/ROADMAP/REQUIREMENTS/STATE -> baseline/reviews` 裁决 drift，再决定 close now / route next。  
**When to use:** 所有文档/治理 drift 的优先级判断。  
**Example:**

```bash
rg -n "AuthSession|LiproClient|compute_exponential_retry_wait_time" \
  .planning/baseline/TARGET_TOPOLOGY.md \
  .planning/baseline/DEPENDENCY_MATRIX.md
```

### Pattern 2: 正式 home 保持不动，只做 inward decomposition

**What:** 对 `runtime_infra.py`、share-client family 这类正式 owner，只允许 inward split / helper narrowing，不重开第二 root。  
**When to use:** `Phase 86` production hotspot cleanup。  
**Anti-patterns to avoid:**

- 把 formal owner 当成 delete target
- 为了“拆热点”新造 listener subsystem / wrapper chain
- 把 archived evidence prose 当 current story 去重写

### Pattern 3: 测试按 contract family 拆，不按行数瞎切

**What:** mega tests 要按 boundary family / runtime concern 拆成 topical suites。  
**When to use:** `Phase 87` assurance topicization。  
**Anti-patterns to avoid:**

- 只因文件太长而横切，结果 assertion 语义更散
- 新增一个更大的 umbrella test 充当“topicization”

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| audit verdict carrier | 第二套长期 review doc family / spreadsheet | current truth docs + 一个 phase-local audit artifact | 避免第二真源 |
| share-client migration | 新 wrapper 同时兼容 bool 与 typed outcome | 现有 `_with_outcome` 正式 contract + 明确 port 收敛 | typed truth 已存在，不该再包一层 |
| runtime hotspot cleanup | 新 listener/runtime root | 在 `runtime_infra.py` 内 inward split helper | 保持 ownership 不漂移 |
| assurance split | 一个更大的 audit mega-suite | topical suites + focused no-regrowth guards | 降低 giant truth-carrier 浓度 |

## Common Pitfalls

### Pitfall 1: 把 archive prose 当 current truth

**What goes wrong:** 误把 `RESIDUAL_LEDGER` / `KILL_LIST` 历史阶段文字当现行 drift。  
**How to avoid:** 先看 current route docs，再看 baseline/reviews 的当前裁决段落。  
**Warning signs:** “为了统一口径”去重写 archive-only evidence。

### Pitfall 2: 为了拆热点而移动 formal owner

**What goes wrong:** `runtime_infra.py` / `share_client.py` 被误当成“应该消失”的文件，而不是需要 inward slimming 的 formal home。  
**How to avoid:** 先查 `FILE_MATRIX` / `KILL_LIST` 是否把它标成正式 owner。  
**Warning signs:** plan 开始讨论“新 root”“新 router”“新 subsystem”。

### Pitfall 3: bool → typed outcome 半迁移

**What goes wrong:** production 与 tests 同时承认 bool path + outcome path，导致 residual 更隐蔽。  
**How to avoid:** Phase 85 只删孤立 alias；真正 outward contract 收敛整包放到 Phase 86。  
**Warning signs:** 代码里同时新增 adapter、keep compat、又改测试断言语义。

## Recommended Plan Decomposition

| Plan | Wave | Depends on | Scope | Output |
|------|------|------------|-------|--------|
| `85-01` repo-wide audit verdict matrix | Wave 1 | none | 形成 severity / ownership / close-now-vs-route-next 裁决表 | `85-RESEARCH.md` + 后续 `85-SUMMARY.md` 输入 |
| `85-02` current-truth drift close-now | Wave 2 | `85-01` | 修 `TARGET_TOPOLOGY`、`DEPENDENCY_MATRIX`、`developer_architecture`；如要碰代码，仅处理 `_safe_read_json` alias | baseline/docs sync + 可选 tiny code cleanup |
| `85-03` focused guards and routing freeze | Wave 3 | `85-02` | 用 focused meta/file-matrix checks 锁住 active route、phase slug、stale-claim 不回流，并把 `close now / route next / explicitly keep` 写成 machine-checkable truth | guard updates + review/baseline follow-up freeze |

**Why this is optimal:** Wave 1 先裁决，Wave 2 只做低风险 close-now，Wave 3 再锁 no-regrowth；这样既满足 `AUD-04` / `GOV-62`，又不会偷跑到 `HOT-37` / `HOT-38` 的主战场。

## Minimal Sufficient Validation Checklist

- `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_closeout_guards.py`
- `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance*.py tests/meta/test_version_sync.py`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run python scripts/check_architecture_policy.py --check`
- 若删 `ShareWorkerClient._safe_read_json`：`uv run pytest -q tests/core/test_share_client_primitives.py tests/core/test_share_client_refresh.py tests/core/test_share_client_submit.py`

## Environment Availability

本 phase 无外部服务依赖；只需要本地 repo 工具链。当前环境已验证：

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` | Python/test commands | ✓ | repo-local usable | — |
| `pytest` | validation | ✓ | `9.0.0` | — |

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest 9.0.0` |
| Config file | `pyproject.toml` |
| Quick run command | `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_closeout_guards.py` |
| Full suite command | `uv run pytest -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| AUD-04 | 审计输出能裁决 current drift、hotspot 与 route-next ownership | meta + script | `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_closeout_guards.py` + `uv run python scripts/check_file_matrix.py --check` | ✅ |
| GOV-62 | current-story docs/baseline/reviews 不误写回 closed residual，且 route truth 一致 | meta | `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance*.py tests/meta/test_version_sync.py` | ✅ |

### Wave 0 Gaps

None — 现有 test / script infrastructure 已足够支撑 Phase 85；缺的不是 framework，而是把 drift 和 route verdict 写准。

## Sources

### Primary (HIGH confidence)

- `AGENTS.md`
- `CLAUDE.md`
- `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-CONTEXT.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `.planning/baseline/TARGET_TOPOLOGY.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `docs/developer_architecture.md`
- `custom_components/lipro/core/anonymous_share/share_client.py`
- `custom_components/lipro/runtime_infra.py`
- `tests/core/api/test_api_diagnostics_service.py`
- `tests/core/api/test_protocol_contract_matrix.py`
- `tests/core/coordinator/runtime/test_mqtt_runtime.py`
- `pyproject.toml`

## Metadata

**Confidence breakdown:**
- Audit findings: HIGH — 都来自当前 repo 真源与实际 grep/usage 结果。
- Routing: HIGH — 直接与 `ROADMAP.md` / `REQUIREMENTS.md` 的 `85 -> 88` 分工吻合。
- Future production cleanup shape: MEDIUM — `Phase 86` 的切法已很清楚，但最终 helper boundaries 仍要看实施时的局部代码形状。

**Research date:** 2026-03-27  
**Valid until:** 下一个 active-route 切换或 7 天内（以先到者为准）
