# 28-02 Summary

## Outcome

- `.github/workflows/ci.yml` 把 runtime dependency audit 明确提升为 blocking runtime security gate，并把 release path 复用关系写进 CI summary。
- `.github/workflows/release.yml` 现在显式要求 `security_gate` 通过后才允许构建/发布 release assets，从而把 tagged source 上的 blocking runtime `pip-audit` 变成 repo-visible hard gate。
- `CONTRIBUTING.md` 与 runbook 已同步区分 blocking vs advisory gate，并明确 `code scanning` 仍是显式 defer，而不是被冒充为已落地事实。

## Key Files

- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `CONTRIBUTING.md`
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_version_sync.py`

## Validation

- `uv run pytest -q tests/meta/test_governance_guards.py -k "security or code or scanning or release"`
- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py -k "security or contributor or runbook"`

## Notes

- 本 plan 采用的是“更硬的等价 machine gate”而不是虚构 `code scanning` 已 blocking；仓库 truth 现诚实记录这一裁决。
