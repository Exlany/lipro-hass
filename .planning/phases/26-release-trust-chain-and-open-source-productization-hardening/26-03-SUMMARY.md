# 26-03 Summary

## Outcome

- `SUPPORT.md`、`SECURITY.md` 与 `CONTRIBUTING.md` 现在对 supported install paths、preview/unsupported reality、single-maintainer model 与 public/private routing 讲同一条故事。
- `pyproject.toml` 已补齐 `Documentation` / `Support` / `Security` / `Discussions` URLs；`manifest.json` 的 documentation 也改为直接指向 README。
- `CODEOWNERS` 注释进一步诚实化：明确 backup maintainer 尚未建立，而不是假装已经冗余。

## Key Files

- `SUPPORT.md`
- `SECURITY.md`
- `CONTRIBUTING.md`
- `pyproject.toml`
- `.github/CODEOWNERS`
- `custom_components/lipro/manifest.json`
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_version_sync.py`

## Validation

- `uv run pytest -q tests/meta/test_governance_guards.py -k "support or security or codeowners or readme"`
- `uv run pytest -q tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py`

## Notes

- 本 tranche 诚实记录了“单维护者仍是现实”；并未伪造备用维护者或未实际存在的支持承诺。
