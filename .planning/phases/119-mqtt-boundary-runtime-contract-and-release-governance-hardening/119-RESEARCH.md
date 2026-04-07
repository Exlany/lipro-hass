# Phase 119 Research

## Problem Statement

`v1.33` 不是业务扩张 phase，而是当前仓内剩余 architecture / governance residual 的一次性收口：

- MQTT ingress 仍残留 boundary ↔ transport reverse import / lazy-import folklore。
- runtime/service typing 仍在 `runtime_types.py` 之外保留平行 Protocol / concrete drift。
- release / governance 当前故事仍允许旧 tag namespace、硬编码 route contract 与过期 changelog/docs 文案并存。

## Ground Truth

- `custom_components/lipro/coordinator_entry.py` 继续是 runtime public home；`custom_components/lipro/core/coordinator/` 只是 internal implementation family。
- `.planning/PROJECT.md` 的 machine-readable `governance-route` contract 是 canonical current-truth source；其余 live planning docs 必须与之完全对齐。
- public release story 只承认 semver tag namespace 与 tagged release security gates，不承认内部里程碑 tag 作为 public release signal。

## Decisions

1. MQTT payload-size / biz-id normalization / topic decode support 真源回收到 `protocol.boundary` family。
2. `runtime_types.py` 成为 service-facing runtime typing 的 single source of truth。
3. `release.yml` / `codeql.yml` 同时收窄到 semver tag namespace。
4. `tests/meta/governance_current_truth.py` 改为从 `.planning/PROJECT.md` 读取 canonical contract，而不是维护第二份 Python dict。
5. `v1.33` 当前收口状态写成 `active / phase 119 complete; closeout-ready (2026-04-01)`，默认下一步为 `$gsd-complete-milestone v1.33`。

## Execution Mapping

- `119-01`：MQTT boundary 单向 authority + focused guards + dependency/public-surface truth。
- `119-02`：runtime/service contract 真源统一 + focused typing guards。
- `119-03`：semver-only release namespace + canonical governance route helper + docs/changelog freshness。
