# Reviews Workspace

本目录承载“全量文件治理矩阵”的正式工作产物。

## Files

- `FILE_MATRIX.md`：全部 Python 文件的分类矩阵
- `RESIDUAL_LEDGER.md`：历史残留、compat adapter、影子模块与删除条件
- `KILL_LIST.md`：明确待删除文件 / 层 / 适配器列表
- `PROMOTED_PHASE_ASSETS.md`：`.planning/phases/**` 的长期治理 / CI 证据 allowlist，也是 promoted phase assets 的唯一完整清单

## Promoted Evidence Notes

- 本目录中的 phase/package 列表不再按 README 穷举维护；请以 `PROMOTED_PHASE_ASSETS.md` 为准获取完整 allowlist。
- README 只负责解释 reviews workspace 的正式文件与 allowlist 角色，避免再因 phase 追加而产生 stale 列表漂移。
- 历史 promoted audit package 仍由 `PROMOTED_PHASE_ASSETS.md` 管理，其中 `46-AUDIT.md` 与 `46-REMEDIATION-ROADMAP.md` 继续作为 promoted audit package 的正式成员。
- 历史 promoted audit / closeout packages 仍通过 `PROMOTED_PHASE_ASSETS.md`、`VERIFICATION_MATRIX.md` 与 phase-history guards 追踪，而不是在本 README 中复制第二套清单。

## Governance Rules

- 所有 Python 文件必须被归类为：`保留 / 重构 / 迁移适配 / 删除`
- 每个 phase 都必须更新受影响文件簇
- 不允许存在“暂时留着、以后再看”的匿名残留
