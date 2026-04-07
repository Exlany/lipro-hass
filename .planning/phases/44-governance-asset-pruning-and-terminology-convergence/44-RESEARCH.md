# Phase 44 Research

**Date:** 2026-03-20
**Status:** Final
**Plans / Waves:** 4 plans / 4 waves

## What The Review Confirmed

- `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 已明确把 `.planning/phases/**` 定义为 `execution-trace`，但 active docs、review ledgers 与 meta guards 仍有大量 promotion / authority 相关耦合断言，治理噪声仍高；
- `.planning/baseline/AUTHORITY_MATRIX.md`、`docs/README.md` 与 `AGENTS.md` 已建立 phase asset identity、authority order 与 promoted-evidence contract，说明 Phase 44 更像“统一 current story”，而不是从零定义新制度；
- `README.md` / `README_zh.md` / `docs/README.md` / `CONTRIBUTING.md` 已有 public navigation 主链，但 contributor fast-path、maintainer-only governance 说明与 bilingual boundary 仍混写在长文中，外部贡献者入口噪声偏高；
- repo 当前仍可搜到大量 `client` / `mixin` / `forwarding` 术语命中；其中一部分属于历史 ADR、residual 账本与基线裁决文本，另一部分则仍位于 current docs / baseline / comments / tests 的活跃叙事层；
- `tests/meta/test_governance_closeout_guards.py`、`tests/meta/test_governance_phase_history.py`、`tests/meta/test_toolchain_truth.py` 已对 promoted phase assets、authority boundary 与 current-doc story 建立机器守卫，因此任何治理降噪都必须同步 guards，而不能只改文案。

## Risk Notes

- 若对全仓库直接做术语替换，容易破坏 ADR 历史语义、review evidence 与 residual ledger 的归档价值；
- 若只在文档层“宣告” `.planning/phases/**` 是 trace，而不补 allowlist / guard / index / contributor入口，旧 phase 资产仍会在未来被误提升为 authority；
- contributor fast-path 与 maintainer appendix 若拆分不干净，仓库会出现“对外一套导航、对内另一套未链接真相”的双主链；
- bilingual policy 若只停留在 README 口头约定，而没有入口级守卫与文档范围定义，后续极易再度漂移。

## Chosen Strategy

1. 先收紧 `.planning/phases/**` 的 promoted-asset / authority / allowlist story，让 execution trace 与长期治理真相的边界可链接、可守卫；
2. 再对 current docs、baseline、active comments 中的 `client / mixin / forwarding` 做 scoped terminology convergence，把允许保留的历史用法显式下沉到 archive / residual ledger；
3. 然后重构 contributor fast-path、maintainer appendix 与 bilingual boundary policy，使 public navigation 更短、更清晰，同时把 maintainer-only governance 说明收进附录；
4. 最后同步 README / docs index / governance guards / review ledgers，确保对外入口、维护者治理与 CI 证据使用同一套语义。

## Validation Focus

- `uv run pytest tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_phase_history_runtime.py tests/meta/test_governance_phase_history_topology.py -q`
- `uv run pytest tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py -q`
- `uv run python scripts/check_translations.py`
- `uv run python scripts/check_file_matrix.py --check`
