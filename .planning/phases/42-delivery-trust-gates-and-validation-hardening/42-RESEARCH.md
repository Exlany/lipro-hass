# Phase 42 Research

**Date:** 2026-03-20
**Status:** Final
**Plans / Waves:** 4 plans / 4 waves

## What The Review Confirmed

- `.github/workflows/release.yml` 已具备 reused CI、tagged security gate、CodeQL gate、attestation / cosign / release-identity 基础链路，但仍未验证“release zip + install.sh”对用户真的可安装；
- `security_gate` 只有 `setup-uv`，未像 `ci.yml` 的 Python jobs 一样显式 `setup-python`；
- `ci.yml` 目前维持 total coverage floor，并允许显式 baseline diff，但尚未形成 changed-surface dual gate，也还没有把 local-vs-CI parity 锁进同一个 machine-checkable story；
- `SUPPORT.md`、`SECURITY.md`、`.github/CODEOWNERS`、runbook 目前都诚实承认“没有已文档化 delegate”，但安全 fallback / custody escalation 仍偏维护者内部语义，对外入口与模板联动不够强；
- 仓库尚无明确的 compatibility / deprecation preview lane；benchmark lane 是 advisory，但不等于 compatibility 预警。

## Risk Notes

- continuity 修复不能伪造并不存在的 delegate；若当前现实仍是单维护者，phase 交付必须把 fallback path 设计为“诚实且可执行”的文档/流程合同；
- release smoke 若直接在源码树验证，容易误判“产物可用”；应尽量贴近 release asset 的真实分发形态；
- diff coverage 若只依赖可选 baseline，仍可能让 touched low-coverage 代码漏网；
- preview lane 不能模糊 stable support contract，避免让用户误以为 preview / deprecation lane 也是稳定支持路径。

## Chosen Strategy

1. 先收 continuity / security fallback / template / runbook truth，让 maintainer custody 与 fallback escalation 变成统一合同；
2. 再为 release pipeline 增加 artifact install smoke，并顺手修正 tagged security gate 的 Python parity；
3. 然后收 coverage dual gate 与 local-vs-CI parity，把 `ci.yml`、`scripts/lint`、PR template 与 contributor docs 拉回单一故事；
4. 最后引入 compatibility / deprecation preview lane，并把 stable-vs-preview 语义回写到 runbook / docs / guards。

## Validation Focus

- `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py`
- `uv run pytest -q tests/meta/test_toolchain_truth.py tests/test_refactor_tools.py`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_public_surface_guards.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py`
