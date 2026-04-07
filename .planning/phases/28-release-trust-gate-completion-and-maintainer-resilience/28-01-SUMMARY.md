# 28-01 Summary

## Outcome

- `.github/workflows/release.yml` 继续复用 `validate -> build -> publish` 单链，但现在在 tagged source 上新增 `security_gate`，并把 artifact attestation 验证与 release identity manifest 提升为正式 release identity story。
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` 现明确要求 `gh attestation verify`、release identity manifest 与 tagged release security gate；attestation 与 signing 的真相仍被严格区分。
- `tests/meta/test_governance_guards.py` 与 `tests/meta/test_toolchain_truth.py` 已冻结新的 identity posture，防止 future drift 回落成“只有 attestation、没有 machine verification”的软叙事。

## Key Files

- `.github/workflows/release.yml`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_toolchain_truth.py`

## Validation

- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_toolchain_truth.py -k "release or attestation or provenance or signing"`

## Notes

- 本 plan 没有发明第二条 release path；强化全部仍 anchored 在 `.github/workflows/ci.yml -> .github/workflows/release.yml` 正式主链。
