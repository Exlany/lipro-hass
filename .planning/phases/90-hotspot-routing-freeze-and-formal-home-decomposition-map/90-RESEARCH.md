# Phase 90 Research

**Phase:** `90-hotspot-routing-freeze-and-formal-home-decomposition-map`
**Date:** 2026-03-28
**Status:** Research complete

## Research Objective

把 repo-wide 终审结论收敛成 `Phase 90` 可执行的 formal-home decomposition map：
- 不重做一轮泛化审计；
- 不提前实现 `Phase 91 -> 93` 的重构活；
- 先冻结 ownership、thin-shell protection、delete-gate 规则与后续 phase sequencing。

## Repo-wide Audit Summary

### Strengths already in place
- 仓库已经具备清晰的 north-star 与 governance hierarchy：`docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`、baseline/review docs 与 meta guards 形成稳定的单一裁决链。
- protocol/runtime/control/domain/assurance 五平面分层已经成立，`LiproProtocolFacade`、`Coordinator`、`custom_components/lipro/control/` 这些正式 homes 明确，且 meta guards 能阻止明显回流。
- 过往 phases 已多轮证明“保留 outward formal home + inward split”是本仓库最成功的 refactor 路径；`runtime_access_support*`、`manager_submission.py`、`request_policy_support.py`、`runtime/mqtt/*` 都是可复用先例。
- 开源治理与 docs-first route 已经明显优于早期状态：公开入口、issue routing、release/runbook、baseline/review truth 的一致性都较高。

### Repo-wide weaknesses that still matter
- 生产代码仍有一组高密度 formal homes：`command_runtime.py`、`rest_facade.py`、`request_policy.py`、`mqtt_runtime.py`、`anonymous_share/manager.py`、`__init__.py`、`runtime_access.py`、`entities/base.py`、`entities/firmware_update.py`。
- 最大风险不再是“旧 compat 名称没删完”，而是 **厚 formal homes + typed boundary debt + redaction drift** 若处理失序，会重新长回第二故事线。
- `FILE_MATRIX`/`RESIDUAL_LEDGER` 已经把大部分历史 residual 关闭，但 repo-wide 审阅仍显示：后续 phases 必须以更精确的 owner/delete-gate 语言推进，而不是把“大文件”直接解释成“应该删除”。
- `anonymous_share` 与 `control/redaction` 的脱敏语义尚未完全统一；若现在重定 ownership，会打乱 protocol/control 边界。
- runtime/protocol hotspot 的后续工作若没有先冻结 map，极易在 `__init__.py`、`runtime_access.py`、entity shells 等 outward surfaces 发生 orchestration 回流。

## Hotspot Freeze Table

| Hotspot | Plane | Current role | Phase 90 verdict | Inward split lane | Downstream phase |
|---|---|---|---|---|---|
| `custom_components/lipro/core/coordinator/runtime/command_runtime.py` | Runtime | command orchestration host | Keep as formal home | `core/coordinator/runtime/command/*` | Phase 91 |
| `custom_components/lipro/core/api/rest_facade.py` | Protocol | REST child façade composition home | Keep as formal home | endpoint/request/transport collaborators beside facade | Phase 91 |
| `custom_components/lipro/core/api/request_policy.py` | Protocol | `429` / busy / pacing policy home | Keep as formal home | `request_policy_support.py` + gateway/executor separation | Phase 91 |
| `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py` | Runtime | MQTT runtime orchestration host | Keep as formal home | `runtime/mqtt/{connection,dedup,message_handler,reconnect}.py` | Phase 91 |
| `custom_components/lipro/core/anonymous_share/manager.py` | Protocol | scoped/aggregate share manager home | Keep as formal home | `manager_submission.py` and share-client collaborators | Phase 92 |
| `custom_components/lipro/__init__.py` | HA adapter | entry bootstrap thin shell | Protected thin shell | inward split only if needed | Phase 91+ |
| `custom_components/lipro/control/runtime_access.py` | Control | runtime read/projection surface | Protected thin shell | typed support/type families only | Phase 92 |
| `custom_components/lipro/entities/base.py` | Domain projection | entity base shell | Protected thin shell | entity-local helpers or typed public verbs | Phase 92 |
| `custom_components/lipro/entities/firmware_update.py` | Domain projection | firmware update projection shell | Protected thin shell / hotspot | OTA collaborator helpers without ownership drift | Phase 92 |

## Artifact Families That Must Stay In Sync

### Planning truth
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`

**Why:** current-route prose、phase basket、default next command、opening phase target 都必须共同承认同一条 `v1.25 active route` 故事。

### Baseline truth
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/AUTHORITY_MATRIX.md`（若 authority wording 被触及）

**Why:** `Phase 90` 的输出不是代码重构，而是把 “哪些 home 保留/哪些 shell 受保护/哪些验证必须存在” 变成基线语言。

### Review truth
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`

**Why:** formal-home 裁决、delete-gate 语言、carry-forward 与 explicitly-keep verdict 需要在 review 台账里落表，防止后续 phase 再靠口头约定。

### Derived collaboration maps
- `.planning/codebase/ARCHITECTURE.md`
- `.planning/codebase/STRUCTURE.md`
- `.planning/codebase/CONCERNS.md`
- `.planning/codebase/CONVENTIONS.md`

**Why:** 这些文件不是 authority truth，但它们是 repo-wide 审阅导航图。Phase 90 若完成 map freeze，应同步 derived collaboration maps 的 hotspot narrative，避免 onboarding / future planning 再吃旧 story。

### Guard surfaces
- `tests/meta/governance_current_truth.py`
- `tests/meta/test_governance_route_handoff_smoke.py`
- `tests/meta/governance_followup_route_current_milestones.py`
- `tests/meta/test_governance_bootstrap_smoke.py`
- `tests/meta/test_dependency_guards.py`
- `tests/meta/test_public_surface_guards.py`
- phase-specific guard file(s) to be added for `Phase 90`

**Why:** 只改 docs 不改 guards，会让 current-route truth 再次漂移；只改 guards 不改 docs，会让 phase 结论不可读。

## Phase 90 Anti-patterns to Avoid

1. **把大文件直接等同于 delete target**
   - 风险：会误删 formal home 或把合法 ownership 描述成 debt。
   - 反模式信号：在 `FILE_MATRIX` / `KILL_LIST` 把 `command_runtime.py`、`rest_facade.py`、`request_policy.py`、`mqtt_runtime.py`、`manager.py` 写成“待删除”。

2. **为追求“更薄”而创造第二 outward root**
   - 风险：引入新的 façade/root/helper-owned truth，破坏 north-star 单一主链。
   - 反模式信号：新增 top-level `*_surface.py`、`*_runtime.py`、`*_client.py` 作为新的 public truth。

3. **把 `Phase 91 -> 93` 的实现活偷跑进 `Phase 90`**
   - 风险：路线失焦，计划/执行/验证边界不再可仲裁。
   - 反模式信号：在 `Phase 90` 直接做 typing narrowing、redaction unification、mega-test topicization、benchmark freeze。

4. **在 outward shells 回流 orchestration**
   - 风险：下一次复查又会出现“为了修热点顺手把逻辑塞回壳层”。
   - 反模式信号：`__init__.py`、`runtime_access.py`、`entities/base.py`、`entities/firmware_update.py` 新增 orchestration/stateful logic。

5. **让 derived collaboration maps 取代 baseline/review authority**
   - 风险：后续计划与执行会以 `.planning/codebase/*.md` 为 authority truth，形成第二条治理链。

## Recommended Plan Slicing

### Plan 90-01 — Freeze hotspot ownership and sequencing
- **Wave:** 1
- **Goal:** 把 five-hotspot ownership、thin-shell protection line 与 phase sequencing 写进 planning truth。
- **Touches:** `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`, `.planning/phases/90-*/90-RESEARCH.md`
- **Output:** 明确的 formal-home map、protected thin-shell line、`Phase 90 -> 93` sequencing prose。

### Plan 90-02 — Sync baseline/review ledgers to the frozen map
- **Wave:** 1
- **Depends on:** none
- **Goal:** 把 frozen map 落到 `FILE_MATRIX / RESIDUAL_LEDGER / KILL_LIST / VERIFICATION_MATRIX`，并校准 derived codebase concerns narrative。
- **Touches:** `.planning/baseline/{PUBLIC_SURFACES,DEPENDENCY_MATRIX,VERIFICATION_MATRIX}.md`, `.planning/reviews/{FILE_MATRIX,RESIDUAL_LEDGER,KILL_LIST}.md`, `.planning/codebase/{ARCHITECTURE,STRUCTURE,CONCERNS,CONVENTIONS}.md`, `docs/developer_architecture.md`
- **Output:** 所有长期治理文档对同一组 hotspots 讲同一条 ownership story。

### Plan 90-03 — Add focused guards for hotspot-map no-regrowth
- **Wave:** 2
- **Depends on:** `90-01`, `90-02`
- **Goal:** 用 focused meta guards 锁住 current-route truth、formal-home freeze、thin-shell protection 与 no-delete-drift。
- **Touches:** `tests/meta/test_phase90_hotspot_map_guards.py`, `tests/meta/public_surface_phase_notes.py`, `tests/meta/dependency_guards_review_ledgers.py`, `tests/meta/governance_*`, `tests/meta/test_public_surface_guards.py`, `tests/meta/test_dependency_guards.py`
- **Output:** 若后续 phase 试图把 formal homes 写成 delete targets、把 shells 写成 orchestration homes、或让 current-route truth 漂移，tests 立即失败。

## Recommended Verification Floor

### Minimum sufficient
- `uv run pytest -q tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_bootstrap_smoke.py`
- `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py`
- `uv run python scripts/check_file_matrix.py --check`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init plan-phase 90`

### Broader confidence
- `uv run pytest -q tests/meta`
- `uv run ruff check .`
- `uv run mypy`

## Planning Implications

- `Phase 90` 是“把全仓终审压缩成唯一 current truth”的 phase，不是“开始随手拆热点”的 phase。
- 最优计划数量是 **3 个**：一组管 planning truth、一组管 baseline/review truth、一组管 guards/verification。再切更细会把 freeze story 打散；再并更粗会让验证困难。
- `90-01` 与 `90-02` 可以并行，因为前者主要处理 planning truth，后者主要处理 baseline/review truth；但 `90-03` 需要在二者完成后再锁 guard，适合 Wave 2。
- 如果执行中发现新的 residual，只能以 explicit ledger entry 方式记录，不能临时扩成新的 repo-wide cleanup campaign。

## Final Research Verdict

`Phase 90` 的最优执行姿势是：
**先把 repo-wide 终审的“问题清单”转成 formal-home / thin-shell / delete-gate / sequencing 四类 machine-check truth，再用 focused guards 锁死；真正的代码重构从 `Phase 91` 开始。**
