# Reviews Workspace

本目录承载“全量文件治理矩阵”的正式工作产物。

## Files

- `FILE_MATRIX.md`：全部 Python 文件的分类矩阵
- `RESIDUAL_LEDGER.md`：历史残留、compat adapter、影子模块与删除条件
- `KILL_LIST.md`：明确待删除文件 / 层 / 适配器列表

## Governance Rules

- 所有 Python 文件必须被归类为：`保留 / 重构 / 迁移适配 / 删除`
- 每个 phase 都必须更新受影响文件簇
- 不允许存在“暂时留着、以后再看”的匿名残留
