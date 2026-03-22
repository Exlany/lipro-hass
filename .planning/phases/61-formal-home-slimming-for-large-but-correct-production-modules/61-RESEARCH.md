# Phase 61: Formal-Home Slimming for Large-but-Correct Production Modules - Research

**Researched:** 2026-03-22
**Domain:** production hotspot inward decomposition / typed seam preservation
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- 只处理 architecturally-correct 但仍偏厚的正式 home：`anonymous_share`、diagnostics service family、OTA candidate 与 `select`。
- outward homes 必须稳定：`manager.py`、`share_client.py`、`services/diagnostics/__init__.py`、`core/ota/candidate.py`、`select.py` 继续是 formal/public home。
- split 只允许 inward：不新增 public root、compat shell、second helper story 或 second formal home。
- 新 seam 必须保持 typed contract、honest ownership 与 boundary clarity；禁止回流动态 dict truth、宽布尔失败或 helper-owned truth。
- `*_support.py` / `*_surface.py` 的命名诚实化与 public discoverability 清理留给 `Phase 62`。

### Claude's Discretion

- 可以把 submission / token refresh / diagnostics polling / OTA arbitration / select gear projection 提炼成更窄协作者。
- 可以同步补 focused tests 或 split 高密度 family tests，只要 runnable topology 更清晰。
- 可以引入 no-growth budget / maintainability evidence，但不要把治理逻辑复制成第二套 authority prose。

</user_constraints>

<requirements>
## Requirement Mapping

| Requirement | Meaning in Phase 61 | Recommended enforcement |
|-------------|---------------------|-------------------------|
| `HOT-15` | 正式 production homes 继续 inward split，不新长第二根 | root thin shell + named internal collaborators + outward imports stable |
| `QLT-20` | 结构切分必须带来真实维护性收益 | focused family tests / hotspot budget guards / smaller failure radius |
| `TYP-15` | 新协作者继续 typed contract，不回流原始 dict/fallback | dataclass / typed helper inputs / explicit return types / no-growth Any budget |

</requirements>

<findings>
## Current Architecture Findings

### 1. `anonymous_share` family is correct but still mixes facade + lifecycle + transport orchestration

- `custom_components/lipro/core/anonymous_share/manager.py` 当前约 `413` 行 class body，里面既有 scope facade/state delegation，也有 submit lifecycle 与 aggregate orchestration。
- `submit_developer_feedback()`、`submit_report()`、`_submit_share_payload_with_outcome()` 与 `_async_finalize_successful_submit()` 构成一条 submit path，但仍直接塞在 manager root 中。
- `manager_support.py` 已承载 scope state / report storage / interval policy，但“submit lifecycle”尚未提炼成更 focused 的 collaborator。
- `share_client.py` 当前最重逻辑集中在 `refresh_install_token_with_outcome()`（约 `106` 行）与 `submit_share_payload_with_outcome()`（约 `167` 行）；response parsing、HTTP branch、token retry/fallback 一起拥挤在同一个 class root。

### 2. diagnostics family already has a stable public surface, but internal responsibilities remain mixed

- `custom_components/lipro/services/diagnostics/__init__.py` 已是稳定 public import surface，这很好，说明 refactor 应只沿 `helpers.py` / `handlers.py` inward split。
- `helpers.py` 同时承担 service-call coercion、developer-report collection、feedback payload projection、optional capability error mapping 与 sensor-history result building。
- `handlers.py` 同时承担 bounded polling、query_command_result orchestration、optional capability passthrough 与 sensor-history handlers。
- 现有 `helper_support.py` 已说明 diagnostics family 允许“public root + internal helper family”模式；Phase 61 适合继续细分为更诚实的 polling / capability / developer-feedback homes。

### 3. OTA candidate home is correct, but four stories are stacked in one module

- `custom_components/lipro/core/ota/candidate.py` 目前把 candidate normalization、projection、install confirmation policy、inline/local-manifest certification arbitration 全塞在一起。
- `entities/firmware_update.py` 只消费 `build_candidate()`、`project_candidate()`、`evaluate_install()` 等 typed API，因此最安全的 slimming 路线是保留 `candidate.py` outward home，向内抽出 install-policy 与 certification helpers。

### 4. `select.py` is a true HA platform root, but still hosts both setup wiring and dense gear logic

- `select.py` 目前同时承载：platform setup、mapped property select base、gear preset parsing / projection / validation / command application。
- `LiproLightGearSelect` class 约 `166` 行，gear projection / selection / attribute building / command application 语义集中。
- 现有 tests 也体现出 split 价值：`tests/platforms/test_select_behavior.py` 约 `431` 行，混合 mapped-property 与 gear preset 行为。

### 5. Existing test families already expose the best decomposition seams

- anonymous-share tests 已天然按 `recording` / `submission` 分层。
- OTA candidate tests 可继续分成 install-policy 与 certification truth。
- diagnostics tests 可以分成 developer-feedback / command-result / optional-capability 三类。
- select tests 可以分成 mapped-property selects 与 gear-preset behavior 两类。

</findings>

<strategy>
## Concrete Implementation Strategy

### Strategy A — Keep the formal outward homes, split only internal collaborators

这是 Phase 61 的推荐路线。

- `manager.py` / `share_client.py` / `helpers.py` / `handlers.py` / `candidate.py` / `select.py` 继续保留为 outward home。
- 把最厚的 branch clusters inward split 到新 internal modules；root 只负责 orchestration / re-export / stable class home。
- 不在本 phase 做 `*_support.py` 全仓命名重写；先把 responsibilities 切干净，再在 `Phase 62` 做 naming honesty。

### Strategy B — Topicize the focused test families in parallel with code slimming

- 针对 anonymous-share / diagnostics / OTA / select 同步生成更聚焦测试文件。
- 保留 daily runnable root 或 family home，但让 failures 更容易定位到子 concern。
- 在不重复 authority prose 的前提下，增加一份 `Phase 61` meta budget / maintainability guard，阻止 touched hotspots 回长。

### Strategy C — Prefer typed projection helpers over mutable helper-owned truth

- install evaluation / certification arbitration / gear projection 等都适合用 dataclass 或 typed tuple/result helpers。
- service handlers 的 branch extraction 应保留 typed inputs/outputs，避免 `dict[str, object]` 成为兜底真源。

</strategy>

<recommended_plans>
## Recommended Plan Slices

### `61-01` — Slim the anonymous-share manager/share-client family

**Target files**
- `custom_components/lipro/core/anonymous_share/manager.py`
- `custom_components/lipro/core/anonymous_share/share_client.py`
- new internal collaborators under `custom_components/lipro/core/anonymous_share/`
- `tests/core/anonymous_share/test_manager_submission.py`
- targeted new/updated anonymous-share tests

**Recommended extraction seams**
- manager submit lifecycle / aggregate submit orchestration
- share-client token refresh flow
- share-client submit branch/fallback orchestration

**Non-goals**
- 不改 outward class names
- 不改 registry/public entrypoints
- 不在此阶段重命名 `manager_support.py` / `share_client_support.py`

### `61-02` — Slim the diagnostics service family

**Target files**
- `custom_components/lipro/services/diagnostics/helpers.py`
- `custom_components/lipro/services/diagnostics/handlers.py`
- new internal collaborators under `custom_components/lipro/services/diagnostics/`
- focused diagnostics tests

**Recommended extraction seams**
- developer-report collection / feedback payload projection
- optional-capability fan-out glue
- command-result polling orchestration
- sensor-history handler cluster

**Non-goals**
- 不改变 `services/diagnostics/__init__.py` stable import surface
- 不让 `control/service_router.py` 追新的 internal module path

### `61-03` — Slim OTA candidate arbitration and install policy

**Target files**
- `custom_components/lipro/core/ota/candidate.py`
- new internal collaborators under `custom_components/lipro/core/ota/`
- focused OTA / firmware-update tests

**Recommended extraction seams**
- certification arbitration helpers
- install confirmation policy helpers
- candidate projection / normalization helpers where it improves clarity

**Non-goals**
- 不改变 `candidate.py` outward API
- 不让 `entities/firmware_update.py` 追内部模块路径

### `61-04` — Slim select internals and freeze focused maintainability evidence

**Target files**
- `custom_components/lipro/select.py`
- new internal select collaborators if needed
- `tests/platforms/test_select_behavior.py`
- `tests/platforms/test_select_models.py`
- new meta budget / maintainability guard(s)

**Recommended extraction seams**
- mapped-property select normalization helpers
- gear preset projection / selection / attribute building
- focused select regressions for mapped-property vs gear preset behavior
- phase-specific maintainability/no-growth guard for touched hotspots

**Non-goals**
- 不改变 `select.py` 作为 HA platform root 的地位
- 不把 select internals 变成第二 public route

</recommended_plans>

<verification>
## Verification Recommendation

### Smoke path

```bash
uv run pytest -q \
  tests/core/anonymous_share/test_manager_recording.py \
  tests/core/anonymous_share/test_manager_submission.py \
  tests/services/test_services_diagnostics.py \
  tests/core/ota/test_ota_candidate.py \
  tests/platforms/test_select_behavior.py \
  tests/platforms/test_select_models.py
```

### Stronger phase gate (recommended after implementation)

```bash
uv run pytest -q \
  tests/core/anonymous_share/test_manager_recording.py \
  tests/core/anonymous_share/test_manager_submission.py \
  tests/services/test_services_diagnostics.py \
  tests/core/ota/test_ota_candidate.py \
  tests/platforms/test_select_behavior.py \
  tests/platforms/test_select_models.py \
  tests/meta/test_dependency_guards.py \
  tests/meta/test_governance_guards.py
```

### If new focused suites / budget guards are added

- 把新增 diagnostics / OTA / select focused suites 纳入 phase gate。
- 若新增 `tests/meta/test_phase61_formal_home_budget_guards.py`，将其加入 phase gate，冻结 touched hotspots 的 no-growth typed/exception posture。

</verification>

<anti_routes>
## Risks and Anti-Routes

### Anti-route 1 — Rename first, clarify ownership later

这会把 `Phase 61` 与 `Phase 62` 混在一起，容易在 responsibilities 还没切干净时制造更多命名噪音。

### Anti-route 2 — Move helpers outward until roots get smaller

如果新文件变成另一层 public-ish helper root，等于把 monolith 变成了 second story，不符合北极星。

### Anti-route 3 — Keep old tests giant and only move production code

这样无法证明 `QLT-20` 的 maintainability 收益，容易留下“代码变薄但 failure radius 没变”的假收益。

### Anti-route 4 — Accept dynamic dict fallbacks in new seams

这会直接违背 `TYP-15`：新的 collaborator 看似更窄，实际上类型更松。

### Main implementation risks

- anonymous-share submit path 与 legacy bool compatibility 并存，拆分时要防止 typed outcome contract 漂移。
- diagnostics service family 横跨 control/service/runtime seam，split 时必须守住 `services/diagnostics/__init__.py` 的 outward contract。
- `select.py` 作为 HA platform file，不能为了变薄而让 entity construction/import routes 变复杂。
- OTA candidate helpers 被 `entities/firmware_update.py` 直接消费，任何 API 漂移都需要马上回归验证。

</anti_routes>

<verdict>
## Verdict

`Phase 61` 的最佳路线不是“均匀拆文件”，而是继续复用仓库已经在 `Phase 59/60` 证明可行的 **thin formal home + named internal family** 模式：

- `anonymous_share` 先抽 submit lifecycle / transport flow；
- diagnostics 再按 developer-feedback / polling / capability concern 收口；
- OTA 单独抽出 certification / install-policy helpers；
- 最后用 select 与 focused tests / budget guards 冻结 maintainability 收益。

这样能最直接满足 `HOT-15 / QLT-20 / TYP-15`，并为 `Phase 62` 的 naming / discoverability 收口提供干净边界。
</verdict>
