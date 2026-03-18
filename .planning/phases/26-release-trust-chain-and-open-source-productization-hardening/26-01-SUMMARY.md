# 26-01 Summary

## Outcome

- `install.sh` 现在把 verified release assets 作为一等安装路径：支持 `--archive-file` / `--checksum-file`，并用 Python `hashlib` 校验 release zip，而不是依赖宿主机是否安装 `sha256sum`。
- 对 tag release 资产缺失或校验失败的路径已改为 fail-closed；`ARCHIVE_TAG=main` / branch fallback / mirror 现在只以 preview / unsupported 口径保留。
- README / README_zh / troubleshooting 已把默认 shell/manual story 切到“下载 release 资产 → 校验 → 本地运行 installer”。

## Key Files

- `install.sh`
- `README.md`
- `README_zh.md`
- `docs/TROUBLESHOOTING.md`
- `tests/meta/test_install_sh_guards.py`
- `tests/meta/test_governance_guards.py`

## Validation

- `uv run pytest -q tests/meta/test_install_sh_guards.py`
- `uv run pytest -q tests/meta/test_governance_guards.py -k "installer or latest or release"`

## Notes

- 本 tranche 明确把远程 `wget | bash` 从“默认支持路径”降级为 advanced preview/unsupported story。
