# Phase 62 Research

## Strategy

`Phase 62` 是 `v1.13` 的收口段：production formal-home slimming 已在 `Phase 61` 完成，本 phase 的最高价值不再是继续拆厚文件，而是把 naming honesty、public discoverability 与 governance truth 收到同一条低噪声故事线上。

## Research Findings

### 1. Honest seams must stay honest, not be blanket-renamed

以下 `support` / `surface` 命名已经被 baseline 明确冻结为真实角色，不应该为了“统一好看”而大规模改名：

- `runtime_access_support.py`
- `entry_lifecycle_support.py`
- `service_router_support.py`
- `developer_router_support.py`
- `manager_support.py`
- `share_client_support.py`
- `helper_support.py`
- `request_policy_support.py`
- `candidate_support.py`
- `endpoint_surface.py`
- `diagnostics_surface.py`
- `system_health_surface.py`
- `telemetry_surface.py`

这些对象的共同点是：
- formal home 另有其主链；
- 当前名字准确描述“support-only seam”或“control-plane bridge/surface”；
- active baseline、tests 与 current-story docs 已围绕它们冻结 inward-only / localized-collaborator truth。

### 2. `endpoint_surface.py` should stay in Phase 62

尽管 `endpoint_surface.py` 名字表面上容易引发联想，但它当前已经被多轮 phase 资产、baseline、focused tests 和 file matrix 明确冻结成 **REST endpoint operations collaborator**。在 `Phase 62` 重命名它，会制造高 fanout 文档/测试/ledger churn，但不会带来成比例的新 clarity。

因此本 phase 对它的裁决是：
- 保留文件名与当前 localized collaborator story；
- 只在 governance/docs wording 中强化“不是 public root / second façade”的语义；
- 不把它当作 Phase 62 的主要 rename 目标。

### 3. The strongest low-fanout rename candidate is `extra_support.py`

`custom_components/lipro/core/device/extra_support.py` 是当前最值得动的一刀：

- 与同 family `extras.py` / `extras_payloads.py` / `extras_features.py` 不对齐；
- `extra` 单数且过泛，不如 `extras_support.py` 诚实；
- fanout 极低，主要影响 `extras_payloads.py` 与 `extras_features.py`；
- outward behavior 完全由 `DeviceExtras` 属性承载，不会影响 public/formal root story。

### 4. `helper_support.py` is better clarified than renamed

`custom_components/lipro/services/diagnostics/helper_support.py` 的确存在 “helpers / helper_support” 双故事线噪音，但它的扇出显著高于 `extra_support.py`，且 active baselines/tests 已围绕它冻结 support-only mechanics seam 语义。

因此本 phase 对它的最优动作是：
- 保留文件名；
- 在 `PUBLIC_SURFACES.md`、`DEPENDENCY_MATRIX.md`、`FILE_MATRIX.md` 与 meta guards 中强化“report / feedback / capability / response mechanics seam”描述；
- 不在本 phase 主动引入高 fanout rename churn。

### 5. The real active noise is now in governance/docs, not business logic

活跃噪音主要集中在：

- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/baseline/GOVERNANCE_REGISTRY.json`
- `README.md`
- `README_zh.md`
- `CONTRIBUTING.md`
- `docs/README.md`
- `SUPPORT.md`

其中最明显的问题有两类：

1. **stale topology wording**：仍以 `Phase 54` 视角描述 helper/support truth，未承认 `Phase 61` 新 collaborator topology；
2. **discoverability wording drift**：public first hop 已经存在，但多个 docs 对“先看哪里、maintainer-only 内容放哪里”的说法仍可压缩。

### 6. Public discoverability should converge, not be redesigned

仓库当前 public docs 骨架已经正确：

- `README.md` / `README_zh.md` 负责 public first hop；
- `docs/README.md` 负责 docs index 与 bilingual boundary；
- `CONTRIBUTING.md` 负责 contributor fast path；
- `SUPPORT.md` / `SECURITY.md` / `docs/TROUBLESHOOTING.md` 负责 routing；
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` 明确 maintainer-only。

因此 `Phase 62` 的目标是 **wording convergence**：减少重复、保持双语一致、守住 retired tooling unsupported posture，而不是重新设计入口体系。

## Recommended Plan Slices

### `62-01` — Freeze keep-vs-rename decisions and land only the low-fanout rename

- 先做 keep-vs-rename inventory；
- 保留 honest seams 与 `endpoint_surface.py`；
- 只对低 fanout 的 `extra_support.py` family naming 下刀；
- 保持 `DeviceExtras` outward behavior 完全不变。

### `62-02` — Converge public docs fast path and retired-tooling wording

- 同步 `README.md` / `README_zh.md` / `docs/README.md` / `CONTRIBUTING.md` / `SUPPORT.md`；
- root README 只保留 public routing layer；
- docs index 继续作为 canonical docs map；
- maintainer-only release/rehearsal story 不回流 public first hop；
- retired compatibility stubs 继续明确 unsupported。

### `62-03` — Freeze active governance truth after naming/discoverability convergence

- 回写 `PUBLIC_SURFACES.md`、`DEPENDENCY_MATRIX.md`、`FILE_MATRIX.md`、必要时 `GOVERNANCE_REGISTRY.json`、`VERIFICATION_MATRIX.md`；
- 让 baseline/review truth 承认 `Phase 61` collaborator topology 与 `Phase 62` 的 keep-vs-rename decisions；
- 只在存在 active delete gate / compat alias 时才补 `RESIDUAL_LEDGER.md`。

### `62-04` — Add anti-regression guards and close out current-story docs

- 扩展或新增 focused meta guards，禁止 stale terminology / stale discoverability route 回流；
- 同步 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md` 与 `PROMOTED_PHASE_ASSETS.md`；
- 把 Phase 62 closeout 作为 v1.13 naming/discoverability convergence 的正式证据。

## Validation Recommendation

### Minimal commands

```bash
uv run pytest -q \
  tests/core/device/test_extras_payloads.py \
  tests/core/device/test_extras_features.py \
  tests/platforms/test_light_model_and_commands.py \
  tests/platforms/test_switch_behavior.py \
  tests/platforms/test_select_models.py
uv run pytest -q tests/meta/public_surface_phase_notes.py tests/meta/test_dependency_guards.py
uv run pytest -q tests/meta/toolchain_truth_docs_fast_path.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py
```

### Final phase gate

```bash
uv run ruff check \
  custom_components/lipro/core/device/extras_support.py \
  custom_components/lipro/core/device/extras_payloads.py \
  custom_components/lipro/core/device/extras_features.py \
  tests/meta/public_surface_phase_notes.py \
  tests/meta/test_dependency_guards.py \
  tests/meta/toolchain_truth_docs_fast_path.py \
  tests/meta/test_governance_release_contract.py \
  tests/meta/test_version_sync.py
uv run python scripts/check_file_matrix.py --check
uv run pytest -q \
  tests/core/device/test_extras_payloads.py \
  tests/core/device/test_extras_features.py \
  tests/platforms/test_light_model_and_commands.py \
  tests/platforms/test_switch_behavior.py \
  tests/platforms/test_select_models.py \
  tests/meta/public_surface_phase_notes.py \
  tests/meta/test_dependency_guards.py \
  tests/meta/toolchain_truth_docs_fast_path.py \
  tests/meta/test_governance_release_contract.py \
  tests/meta/test_governance_guards.py \
  tests/meta/test_version_sync.py
```

## Anti-Routes

### Anti-route 1 — Rename every `support`/`surface` file for visual consistency

这会直接抹掉 honest seam semantics，并制造大范围 churn，与 Phase 62 的低噪声目标相反。

### Anti-route 2 — Let docs wording redefine architecture truth

public docs 只能 follow code + governance truth，不能反向把 maintainer appendix、retired tooling 或 internal collaborator 说成正式入口。

### Anti-route 3 — Freeze docs but skip guards

如果没有 focused anti-regression guards，stale wording 很快会回流，Phase 62 的收益只会停留在一次性清扫。

### Anti-route 4 — Reopen Phase 61 slimming under a naming banner

一旦 Phase 62 再次改动 anonymous-share / diagnostics / OTA / select 的结构，就会混淆 milestone closeout story，增加不必要风险。

## Verdict

`Phase 62` 的最佳路线是：

- **保留 honest seams；**
- **只修低 fanout 且真正不对齐 family naming 的对象；**
- **压缩 public docs fast path wording；**
- **把 naming/discoverability truth 写回 baseline、ledgers、current-story docs 与 focused guards。**

这样最能满足 `RES-14 / DOC-07 / GOV-45`，同时避免用一轮“命名洁癖式重构”重新打开已完成的 production surgery。
