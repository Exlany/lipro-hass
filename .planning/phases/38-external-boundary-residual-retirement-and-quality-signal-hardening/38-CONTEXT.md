# Phase 38 Context

**Phase:** `38 External-boundary residual retirement and quality-signal hardening`
**Milestone:** `v1.4 continuation — Fresh-audit residual & signal hardening`
**Date:** `2026-03-18`
**Status:** `planned — context captured, ready for execution planning`
**Source:** `.planning/{ROADMAP,REQUIREMENTS,STATE,PROJECT}.md` + `.planning/reviews/{RESIDUAL_LEDGER,KILL_LIST}.md` + `.planning/codebase/TESTING.md` + external-boundary / governance guard audit

## Why Phase 38 Exists

`Phase 34 -> 37` 已把 release trust、protocol/runtime hotspots 与 test topology 主线推进到全绿；当前若继续按 10 分质量推进，最该优先收口的已是更窄但仍真实存在的三类尾债：

1. `External-boundary advisory naming` 仍是仓库唯一 active residual family。
2. benchmark / coverage-diff / pytest marker registry 这组 quality signals 仍偏“解释型”，machine truth 还不够硬。
3. governance closeout / phase-history truth 已明显改善，但少量 guard 仍依赖 prose fragments，噪音还可再降。

因此 `Phase 38` 不再做大规模架构重排，而是把最后 residual、剩余 assurance signal gap 与 closeout noise 一次性路由到更硬的正式合同。

## Goal

1. 退掉最后一条 active residual family：`External-boundary advisory naming`。
2. 收紧 benchmark / coverage-diff / marker registry 的质量信号语义，使其 machine-checkable。
3. 进一步降低 governance closeout 断言噪音，让 future audit 建立在更结构化的 truth anchors 上。

## Decisions (Locked)

- 不改变 external-boundary authority contract：`local trust root + remote advisory` 仍是正式真相，只收口命名与 generated payload 语义。
- benchmark 继续保持 advisory posture，不擅自升级为 blocking gate；但预算/基线语义必须可审计。
- 不虚构 backup maintainer、emergency delegate 或未存在的人治冗余。
- structured truth anchors 只能辅助守卫与 closeout，不得反向取代 `ROADMAP / REQUIREMENTS / STATE`。
- phase 只收口最后 residual 与 assurance truth，不重开 protocol/runtime 大拆分。

## Non-Negotiable Constraints

- 不得把 remote firmware advisory 重新洗成 certification truth。
- 不得用“文档解释”替代 machine guard；质量信号的诚实化必须有自动化证据。
- 不得新增第二套 phase-history / closeout authority source。
- 不得为了降低噪音而削弱外部边界、governance 或 public-surface guard 的约束力。

## Canonical References

### Residual / Authority Truth
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `tests/meta/test_external_boundary_authority.py`
- `tests/meta/test_external_boundary_fixtures.py`
- `tests/meta/test_firmware_support_manifest_repo_asset.py`

### Quality Signal Truth
- `.planning/codebase/TESTING.md`
- `CONTRIBUTING.md`
- `.github/workflows/ci.yml`
- `scripts/coverage_diff.py`
- `pyproject.toml`
- `tests/meta/test_toolchain_truth.py`
- `tests/meta/test_governance_release_contract.py`

### Governance Closeout Truth
- `tests/meta/test_governance_closeout_guards.py`
- `tests/meta/test_governance_phase_history.py`
- `tests/meta/test_governance_phase_history_runtime.py`
- `tests/meta/test_governance_phase_history_topology.py`
- `.planning/{ROADMAP,REQUIREMENTS,STATE}.md`

## Expected Scope

### In scope
- external-boundary naming honesty cleanup
- benchmark / coverage diff / marker registry quality-signal hardening
- lower-noise structured governance closeout anchors

### Out of scope
- protocol/runtime hotspot slimming
- new release trust story or maintainer fiction
- changing benchmark from advisory to blocking
- reopening v1.3 audit verdict

## Open Planning Questions

1. external-boundary naming 应该统一到哪些 canonical terms，才能既诚实又不破坏 trust contract？
2. quality-signal hardening 最优解是新增 baseline artifact、重命名脚本语义，还是删掉 dead marker/claim？
3. closeout guards 最适合抽成哪种结构化 truth anchor，才能降噪但不多立真源？

---

*Phase directory: `38-external-boundary-residual-retirement-and-quality-signal-hardening`*
*Context gathered: 2026-03-18 from residual-ledger review, testing-map audit, and governance closeout truth scan.*
