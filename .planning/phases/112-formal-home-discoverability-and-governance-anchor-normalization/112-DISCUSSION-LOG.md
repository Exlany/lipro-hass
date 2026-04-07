# Phase 112: Formal-home discoverability and governance-anchor normalization - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-31
**Phase:** 112-formal-home-discoverability-and-governance-anchor-normalization
**Areas discussed:** formal-home ownership, governance-anchor normalization, public-vs-maintainer docs boundary, discoverability wording

---

## Formal-home ownership

| Option | Description | Selected |
|--------|-------------|----------|
| Register sanctioned homes in docs/baselines | Keep `runtime_infra.py`, `runtime_types.py`, `entry_auth.py` in place for now; explain ownership clearly and avoid risky moves in Phase 112 | ✓ |
| Physically relocate/merge now | Move or rename the root-level files during Phase 112 so topology looks cleaner immediately | |
| Defer ownership clarification | Leave root-level files as-is and revisit discoverability in a later phase | |

**User's choice:** `[auto]` Register sanctioned homes in docs/baselines
**Notes:** 推荐此项，因为 `ARC-29` 明确允许“归并或正式登记”；当前最小风险路径是先消除 discoverability ambiguity，而不是在治理归一化阶段引入高风险文件搬迁。

---

## Governance-anchor normalization

| Option | Description | Selected |
|--------|-------------|----------|
| Normalize maintainer-facing docs and planning truth now | Update `developer_architecture`, runbook, planning/baseline docs, and guards to the live `v1.31` route while keeping archive history separate | ✓ |
| Patch planning docs only | 仅修 `.planning/*` 当前 selector，不同步 developer/runbook docs | |
| Push all stale-anchor cleanup to later phases | 保留 archived-only wording，先做别的事情 | |

**User's choice:** `[auto]` Normalize maintainer-facing docs and planning truth now
**Notes:** 推荐此项，因为 `GOV-72` 目标正是清理 stale anchors；只修 planning truth 会让 maintainer docs 继续误导审阅路径。

---

## Public-vs-maintainer docs boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Keep public docs public-first; sync wording only | `SUPPORT.md` / `SECURITY.md` / docs index 继续做 first hop，不承载 internal route ledger，只同步 honest wording 与 appendix linkage | ✓ |
| Expand public docs with active route truth | 把 current route / phase / archived pointer 直接写进 public-facing docs | |
| Defer all support/security wording to Phase 114 | 让当前 public docs 继续保留 stale anchor，等开源可达性阶段再统一 | |

**User's choice:** `[auto]` Keep public docs public-first; sync wording only
**Notes:** 推荐此项，因为 public docs 的职责是 guaranteed first hop 与 honest caveats；把 internal route truth 塞回去会制造第二条 authority chain。

---

## Discoverability wording

| Option | Description | Selected |
|--------|-------------|----------|
| Update existing authoritative docs/tables | 在现有 north-star / developer / baseline / planning docs 中清理 `coordinator.coordinator` 等折返叙事，不新增新 registry | ✓ |
| Add a new standalone formal-home registry | 新建一份统一 registry 专门解释 root-level homes | |
| Rename files/symbols immediately | 直接通过 code rename 解决 discoverability，而不是先修文档 | |

**User's choice:** `[auto]` Update existing authoritative docs/tables
**Notes:** 推荐此项，因为 authority order 已存在；新增 registry 会制造 second truth，立即 rename 则把文档归一化阶段变成高风险实现阶段。

---

## the agent's Discretion

- sanctioned-home mapping 最终落在哪个文档 section
- stale-anchor cleanup 的具体 wording 和 cross-link 组织方式
- 是否增加 focused governance guards，以及它们落在哪个 `tests/meta` family

## Deferred Ideas

- 更激进的 root-level file move / rename（如 docs normalization 仍不足）
- `Phase 113` hotspot burn-down / no-regrowth hardening
- `Phase 114` public reachability / security fallback / delegate identity closure
