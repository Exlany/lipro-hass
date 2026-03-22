# v1.12 Milestone Seed

> Snapshot: `2026-03-22`
> Identity: proposal-only / pull-only planning seed for the next formal milestone.
> Authority: this seed does **not** override `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`; it exists so the next formal `$gsd-plan-phase 59` / `$gsd-execute-phase 59` can start from refreshed route evidence instead of conversation memory.

## 1. Arbitration Summary

`Phase 58` 已经完成 refreshed 全仓审阅，并把结论压成 `Phase 59+` remediation route。下一步最高价值工作不是重做 broad audit，也不是立刻跳进 `Phase 60` 的 tooling hotspot surgery，而是先把当前最大的验证维护成本——megaguards / megasuites 的 failure radius——收窄到更诚实的 topical suites。

换言之，`v1.12` 不是第二轮审计，而是 **把 refreshed audit 的第一优先级 follow-up 变成可执行、可验证、可维护的 verification-localization tranche**。

## 2. Candidate Milestone

**Name:** `v1.12 Verification Localization & Governance Guard Topicization`

**Why now:**

1. `58-REMEDIATION-ROADMAP.md` 已把 `Phase 59` 明确标成最高杠杆 next tranche；
2. 当前主风险已从“错架构”转向“验证定位半径过大、守卫巨石文件过厚”；
3. 若不先缩小验证半径，后续 `Phase 60+` 的 tooling / production hotspot follow-through 会继续建立在高噪声守卫上。

**North-star fit:**

- does not reopen protocol/runtime/control second-root stories
- does not add new public surfaces or maintenance folklore
- localizes verification only along existing truth families and focused concern seams
- keeps docs / matrices / route truth in sync with the new topology

## 3. Candidate Requirement Basket

- `TST-11` — public-surface / governance-history / follow-up-route megaguards 与 `test_device_refresh.py` 必须按 stable truth family / concern boundary topicize，避免继续维持 giant buckets。
- `QLT-19` — localized verification topology 必须提供更小、更可单独运行的 focused suites，同时保留现有 guard semantics 与 coverage honesty。
- `GOV-43` — current-story docs、verification matrix 与 related review truth 必须显式记录 `Phase 59` 的 localized verification topology、ownership boundary 与 no-growth contract。

## 4. Proposed Phase Seed

### Phase 59 — Verification localization and governance guard topicization

**Why first**
- it is the highest-priority route explicitly named by `Phase 58`
- it improves maintainer/debug efficiency without touching production architecture truth
- it reduces the chance that later hotspot work regresses behind giant, all-or-nothing verification files

**Primary outcomes**
- topicize governance/public-surface/follow-up-route megaguards into narrower suites
- split `tests/core/test_device_refresh.py` by parsing/filter/runtime concerns
- write back the new verification topology into planning truth and verification guidance

**Core files / areas**
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_governance_phase_history.py`
- `tests/meta/test_governance_followup_route.py`
- `tests/core/test_device_refresh.py`
- `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`（如 execution 需要 truth sync）

## 5. Non-Goals for Phase 59

- 不直接拆 `scripts/check_file_matrix.py`（那是 `Phase 60`）
- 不借题发挥去重写 production formal homes（那更接近 `Phase 61`）
- 不新增长期 public helper root，只为 test split 服务的最小局部抽取必须保持私有且有边界

## 6. Next Formal Steps

1. promote `v1.12` and `Phase 59` into `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`
2. run `$gsd-plan-phase 59 --prd .planning/phases/59-verification-localization-and-governance-guard-topicization/59-PRD.md --skip-research`
3. execute `$gsd-execute-phase 59`
4. route remaining tooling / production hotspot work into `Phase 60+`
