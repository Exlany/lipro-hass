# Phase 23 Audit Coverage Checklist

**Purpose:** map every 2026-03-16 audit finding to an execution plan, addendum wave, or explicit defer.

| Audit Finding | Disposition | Notes |
|---|---|---|
| `fan.py` preset/options mismatch | `23-04` | 已补 `gentle_wind` / vent `off`，并完成对应平台回归。 |
| `runtime_access.py` side-effect injection | `23-04` | 已改为只读 projection，禁止污染 foreign object。 |
| default installer path must remain `latest` | `23-04`, `23-08` | 默认用户路径继续锁定 `ARCHIVE_TAG=latest`；pinned tag / `main` 仅作高级路径。 |
| entity -> coordinator write path drift | `23-05` | 命令派发优先 formal `command_service`。 |
| runtime compat normalization in `snapshot.py` | `23-05` | runtime 只保留最小 canonicalization，不再默默修 vendor 形态。 |
| broad catch / typed-failure hardening | `23-05` checklist | 已在 addendum 里登记，不作为 silent debt。 |
| `service_router.py` hotspot | `23-06` | developer-only 查询 helper 已集中化。 |
| `developer_report.py` hotspot | `23-06` | 本地视图组装与 upload-safe projection 已进一步分层。 |
| control/services bidirectional coupling | `23-06` | 已收口主要 helper home；更深 decouple 作为后续 follow-up。 |
| `.planning/codebase/TESTING.md` drift | `23-07` | 统计与口径已刷新，并由 meta guard 锁定。 |
| script ↔ tests coupling | `23-07` | 显式裁决为 helper-only / pull-only；禁止新增未登记例外。 |
| wording-guard brittleness | explicit follow-up | 继续向结构化守卫迁移，但本 phase 不假装一次性清零。 |
| giant tests / private-internal coupling | explicit follow-up | `tests/core/test_init.py`、`tests/core/api/test_api.py` 后续拆分，不在本轮 silent carry-forward。 |
| bug template vs troubleshooting tension | `23-08` | developer report 改为升级排障路径，不再作为公开 bug 的硬门槛。 |
| docs / internal planning exposure | `23-08` | 对外入口继续指向 README / troubleshooting / support / security / runbook；治理索引保持 maintainer-facing。 |
| release supply-chain hardening | `23-08` + explicit defer | 本 phase 明确当前已落地与 defer 项，不再停留于口头建议。 |
| firmware manifest metadata | explicit defer | 当前 trust root 继续是 `custom_components/lipro/firmware_support_manifest.json`；metadata 扩展不在本 phase 静默带过。 |
| bus factor / maintainer posture | `23-08` | 单维护者现实已在 support / security / codeowners / runbook 如实表达。 |

## Wave Mapping

- `23-04`：修复 preset/runtime-access/latest installer 三类直接用户与 control-surface 裂缝。
- `23-05`：收紧 entity command seam 与 runtime canonical row truth。
- `23-06`：收口 developer router / diagnostics helper / report projection hotspot。
- `23-07`：刷新测试图谱、脚本与 tests 边界裁决、补齐 audit coverage ledger。
- `23-08`：统一 public docs、support/security/release narrative 与显式 defer 说明。

## Explicit Follow-up / Defer Ledger

- **Wording guards:** 逐步把 wording-only assertions 迁移为结构化/AST/assert-shape guards；本 phase 仅要求显式登记，不假装全部完成。
- **Giant tests / private internals:** `tests/core/test_init.py` 与 `tests/core/api/test_api.py` 仍偏大，且部分回归依赖 private internals；后续需独立计划做测试分解。
- **Release supply-chain hardening beyond current gate:** 当前正式姿态是 pinned actions、CI 复用、tagged checkout、version match 与 `SHA256SUMS`；`provenance`、`SBOM`、artifact `signing`、把 `code scanning` 变成发版硬门槛，全部显式 defer 到后续 phase。
- **Firmware manifest metadata:** 当前只锁定本地 certified truth/root，不在本 phase 扩展更多 metadata 语义；若后续需要 richer metadata，必须新 phase 登记。

## Rules

- No item may be silently dropped.
- If an item is not executed in the current wave set, it must be named in the relevant plan's defer/follow-up section.
- Default installer UX remains `ARCHIVE_TAG=latest` unless the user explicitly changes that requirement in a future planning pass.
