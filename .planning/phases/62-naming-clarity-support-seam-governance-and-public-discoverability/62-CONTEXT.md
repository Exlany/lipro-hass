# Phase 62: Naming clarity, support-seam governance, and public discoverability - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning
**Source:** `Phase 58` remediation route + `Phase 61` closeout + current naming/discoverability census

<domain>
## Phase Boundary

本 phase 是一次 **命名诚实化 + discoverability follow-through + governance freeze**，不是新的 hotspot slimming 或 broad repository rewrite。

1. 只处理 `Phase 61` 之后仍残留的 naming / support-seam / public-fast-path 噪音；
2. 所有改动都必须建立在既有 formal homes 已经正确的前提上，不得为了“更优雅名字”重开 production architecture surgery；
3. `support` / `surface` 术语只允许留给真实角色语义：honest support-only seam 可以保留，真正误导或不对齐 family naming 的少数对象才允许改名；
4. README / docs index / contributor fast path / retired tooling discoverability 必须继续讲一条 public-first-hop story，maintainer-only release/runbook 不得重新回流 public first hop；
5. baseline、review ledger、current-story docs 与 meta guards 必须冻结 post-Phase-61 naming/discoverability truth，阻止 stale wording 与 duplicate route 回流。

</domain>

<decisions>
## Locked Decisions

- 本 phase 不重开 `anonymous_share`、diagnostics、OTA、select 的 inward slimming；那已经在 `Phase 61` 完成。
- 下列名字当前属于 **honest seam**，默认保留，不做 blanket rename：
  - `custom_components/lipro/control/runtime_access_support.py`
  - `custom_components/lipro/control/entry_lifecycle_support.py`
  - `custom_components/lipro/control/service_router_support.py`
  - `custom_components/lipro/control/developer_router_support.py`
  - `custom_components/lipro/core/anonymous_share/manager_support.py`
  - `custom_components/lipro/core/anonymous_share/share_client_support.py`
  - `custom_components/lipro/services/diagnostics/helper_support.py`
  - `custom_components/lipro/core/api/request_policy_support.py`
  - `custom_components/lipro/core/ota/candidate_support.py`
  - `custom_components/lipro/control/diagnostics_surface.py`
  - `custom_components/lipro/control/system_health_surface.py`
  - `custom_components/lipro/control/telemetry_surface.py`
  - `custom_components/lipro/core/api/endpoint_surface.py`
- 当前最强的 low-fanout rename 候选是 `custom_components/lipro/core/device/extra_support.py`：它和 `extras.py` / `extras_payloads.py` / `extras_features.py` 的 family naming 不对齐，且 fanout 很低，适合在本 phase 收口成 `extras_support.py` 或等价更诚实的 family-aligned wording。
- `custom_components/lipro/services/diagnostics/helper_support.py` 当前仍保留；本 phase 优先通过 governance/docs wording 强化其 mechanics-only seam 身份，而不是主动引入高 fanout rename churn。
- public discoverability 主链保持不变：
  - root public hop：`README.md` / `README_zh.md`
  - docs index：`docs/README.md`
  - contributor workflow：`CONTRIBUTING.md`
  - support/security/triage：`SUPPORT.md` / `SECURITY.md` / `docs/TROUBLESHOOTING.md`
  - maintainer-only appendix：`docs/MAINTAINER_RELEASE_RUNBOOK.md`
- 任何 docs wording / governance freeze 都不能把 maintainer-only release/rehearsal story 重新提升成 public first hop。

### Claude's Discretion
- 可以把 `extra_support.py` 收口成更诚实的 `extras_support.py` family naming，并同步更新低 fanout imports 与 focused extras regressions。
- 可以压缩 README / docs / CONTRIBUTING / SUPPORT 的 wording，前提是 routes 不变、双语同步、retired tooling 仍明确 unsupported。
- 可以新增 focused `Phase 62` meta guard，专门冻结 stale terminology / duplicate discoverability route / second-root wording，不必把所有新约束塞回单个 megaguard。

</decisions>

<canonical_refs>
## Canonical References

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/baseline/GOVERNANCE_REGISTRY.json`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-REMEDIATION-ROADMAP.md`
- `.planning/phases/61-formal-home-slimming-for-large-but-correct-production-modules/61-SUMMARY.md`
- `.planning/phases/61-formal-home-slimming-for-large-but-correct-production-modules/61-VERIFICATION.md`
- `custom_components/lipro/core/device/extra_support.py`
- `custom_components/lipro/core/device/extras.py`
- `custom_components/lipro/core/device/extras_payloads.py`
- `custom_components/lipro/core/device/extras_features.py`
- `custom_components/lipro/services/diagnostics/helper_support.py`
- `custom_components/lipro/core/api/endpoint_surface.py`
- `README.md`
- `README_zh.md`
- `CONTRIBUTING.md`
- `SUPPORT.md`
- `docs/README.md`
- `tests/core/device/test_extras_payloads.py`
- `tests/core/device/test_extras_features.py`
- `tests/platforms/test_light_model_and_commands.py`
- `tests/platforms/test_switch_behavior.py`
- `tests/platforms/test_select_models.py`
- `tests/meta/public_surface_phase_notes.py`
- `tests/meta/test_dependency_guards.py`
- `tests/meta/toolchain_truth_docs_fast_path.py`
- `tests/meta/test_version_sync.py`
- `tests/meta/test_governance_release_contract.py`

## Hotspot Observations

- active governance truth 里仍有 `Phase 54` wording，只认识 `manager_support.py` / `share_client_support.py` / `helper_support.py`，尚未反映 `Phase 61` 新形成的 collaborator topology；
- `extra_support.py` 与 `extras*` family 的命名不对齐，是当前收益最高、风险最低的 rename 切口；
- `endpoint_surface.py` 虽带 `surface`，但 active docs/tests 已将其冻结为 localized endpoint-operations collaborator；本 phase 不主动重命名它，避免大面积 churn；
- public docs fast path 已大体正确，但 README / README_zh / CONTRIBUTING / docs index / SUPPORT 之间仍有 wording 冗余，可进一步压缩为更低噪声 public story。

</canonical_refs>

<execution_shape>
## Recommended Execution Shape

- `62-01`：先做 keep-vs-rename inventory，并完成唯一低 fanout rename（`extra_support.py` family alignment）；
- `62-02`：并行做 public fast path wording convergence，压缩 docs/discoverability 噪音；
- `62-03`：把 keep/rename 与 discoverability 决策回写 baseline / review truth；
- `62-04`：补 anti-regression guards，并完成 current-story docs / promoted evidence closeout。

</execution_shape>

<verification>
## Verification Recommendation

### Smoke path

```bash
uv run pytest -q \
  tests/core/device/test_extras_payloads.py \
  tests/core/device/test_extras_features.py \
  tests/platforms/test_light_model_and_commands.py \
  tests/platforms/test_switch_behavior.py \
  tests/platforms/test_select_models.py \
  tests/meta/public_surface_phase_notes.py \
  tests/meta/test_dependency_guards.py \
  tests/meta/toolchain_truth_docs_fast_path.py \
  tests/meta/test_version_sync.py
```

### Stronger phase gate

```bash
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
uv run python scripts/check_file_matrix.py --check
```

</verification>
