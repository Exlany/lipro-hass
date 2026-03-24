# Phase 71 Context

## Phase

- **Number:** `71`
- **Title:** `Audit-driven final hotspot decomposition, governance truth projection, and closeout routing`
- **Milestone:** `v1.19 Audit-Driven Final Hotspot Decomposition & Governance Truth Projection`
- **Starting baseline:** `v1.18 archived / evidence-ready`

## Why This Phase Exists

`v1.18` 已把 support-seam、anonymous-share / OTA helper convergence、archive/current version truth freeze 与 governance topicization 收口到归档态；但 repo-wide 终审仍指出一组“高收益但仍安全可落地”的 residual hotspots：

- OTA diagnostics / firmware install orchestration
- anonymous-share submit outcome loop
- request pacing / command-runtime long-flow density
- current-route / latest-archive truth 的多点字面同步

本 phase 的目标不是重开大规模架构迁移，而是把这些热点继续 inward split，并把 current route 切到 `v1.19 / Phase 71 complete / closeout-ready`。

## In Scope

- `custom_components/lipro/entities/firmware_update.py`
- `custom_components/lipro/core/api/diagnostics_api_ota.py`
- `custom_components/lipro/core/anonymous_share/share_client_submit.py`
- `custom_components/lipro/core/api/request_policy_support.py`
- `custom_components/lipro/core/coordinator/runtime/command_runtime.py`
- `tests/meta/*` touched current-route / archive-pointer guards
- `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`
- `.planning/baseline/{PUBLIC_SURFACES,AUTHORITY_MATRIX,VERIFICATION_MATRIX}.md`
- `docs/README.md`

## Constraints

- 不新增 outward roots / public surfaces
- latest archived baseline 仍是 `v1.18`
- current route 必须 machine-checkable，不能只靠 prose
- 所有 Python / test / script 命令统一 `uv run ...`
