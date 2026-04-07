# Phase 60: Tooling truth decomposition and file-governance maintainability - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning
**Source:** PRD + `v1.12` archive + `Phase 58` remediation route + current hotspot audit

<domain>
## Phase Boundary

本 phase 是一次 **tooling / governance hotspot inward decomposition**，不是 production architecture rewrite。

1. 必须优先处理 repo-maintenance 真热点：`scripts/check_file_matrix.py` 与 `tests/meta/test_toolchain_truth.py`；
2. 必须保留 `FILE_MATRIX / VERIFICATION_MATRIX / TESTING / current-story docs` 的单一 authority chain；
3. 必须保留 `scripts.check_file_matrix` 被外部 meta guards import 的稳定 contract；
4. 不得把 owner / authority / acceptance 规则迁出正式真源，形成第二条治理故事线。

</domain>

<decisions>
## Locked Decisions

- `scripts/check_file_matrix.py` 当前约 `1331` 行，是 repo-maintenance tooling hotspot 的第一优先级。
- `tests/meta/test_toolchain_truth.py` 当前约 `607` 行，混合 toolchain / release / docs / governance / codebase-map 多条故事线，是验证热点的第二优先级。
- `scripts.check_file_matrix` 的既有 public import contract 必须稳定保留，至少包括：`repo_root`、`classify_path`、`iter_python_files`、`parse_file_matrix_paths`、`extract_reported_total`、`run_checks` 与 CLI 行为。
- phase 的首要收益是 **ownership clarity / failure localization / truth-chain honesty**，不是机械平均行数。
- `.planning/reviews/FILE_MATRIX.md` 与 `.planning/baseline/VERIFICATION_MATRIX.md` 继续是 authority truth；tooling split 不得把这些规则复制到第二份 helper 文档里。

### Claude's Discretion
- 可把 `scripts/check_file_matrix.py` 变成 thin root + internal families，只要 outward contract 稳定。
- 可把 `tests/meta/test_toolchain_truth.py` 拆成 topical modules，只要 daily runnable roots 与 guard intent 仍清晰。
- 可同步修正文档中的 toolchain / verification command anchors，只要不越界到 `Phase 61 / 62` 的 production / naming 主体。

</decisions>

<canonical_refs>
## Canonical References

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/v1.12-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_12_EVIDENCE_INDEX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/codebase/TESTING.md`
- `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-REMEDIATION-ROADMAP.md`
- `.planning/phases/59-verification-localization-and-governance-guard-topicization/59-SUMMARY.md`
- `.planning/phases/59-verification-localization-and-governance-guard-topicization/59-VERIFICATION.md`
- `scripts/check_file_matrix.py`
- `tests/meta/test_toolchain_truth.py`
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_evidence_pack_authority.py`
- `tests/meta/test_phase31_runtime_budget_guards.py`
- `tests/meta/test_phase45_hotspot_budget_guards.py`
- `tests/meta/test_phase50_rest_typed_budget_guards.py`
- `tests/meta/test_governance_closeout_guards.py`

## Hotspot Observations

- `scripts/check_file_matrix.py` 同时承载 repo/path 常量、governance row model / overrides、path classification、markdown render/parse、active-doc / authority validators、codebase-map policy 与 CLI 编排，职责明显过厚。
- `tests/meta/test_toolchain_truth.py` 同时承载 Python/toolchain pin、release identity、docs / terminology / public fast path、CI / lint / marker contract、testing/codebase/governance continuity 与 checker/path truth，failure radius 偏大。
- 直接 import `scripts.check_file_matrix` 的守卫至少覆盖 `tests/meta/test_governance_guards.py`、`tests/meta/test_evidence_pack_authority.py`、多份 hotspot/runtime budget guards 与 closeout guards；拆分时必须保证 import-facing compatibility。
- `Phase 59` 已先完成 verification localization，所以当前最正确的动作是 **拆 tooling hotspot 与 toolchain megasuite**，而不是再碰更重的 production root。

</canonical_refs>

<execution_shape>
## Recommended Execution Shape

- `60-01`：先把 `scripts/check_file_matrix.py` inward decomposition 成更清晰的 internal families，同时保留 outward contract；
- `60-02`：再把 `tests/meta/test_toolchain_truth.py` topicize 成 focused suites / thin roots；
- `60-03`：最后同步 `FILE_MATRIX / VERIFICATION_MATRIX / TESTING / current-story docs` 与相关 guards，冻结 tooling truth topology。

</execution_shape>
