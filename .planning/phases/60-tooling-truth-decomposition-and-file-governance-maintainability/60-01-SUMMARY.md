# Plan 60-01 Summary

- `scripts/check_file_matrix.py` 已收敛为 thin compatibility root，并 outward 保留 `repo_root` / `iter_python_files` / `classify_path` / `parse_file_matrix_paths` / `extract_reported_total` / `run_checks` / CLI contract。
- inventory、classification registry、markdown render/parse 与 validator passes 已 inward 分离到 `scripts/check_file_matrix_{inventory,registry,markdown,validation}.py`，不再把 file-governance truth 压在单个 giant script 中。
- `FILE_MATRIX.md` 现已 truthful 记录新 tooling topology，既有 importer 与 CLI story 保持不变。
