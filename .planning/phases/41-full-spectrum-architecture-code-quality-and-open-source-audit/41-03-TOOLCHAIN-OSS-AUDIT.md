# Phase 41 Toolchain & Open-Source Audit Shard

## Test and Toolchain Verdict

- Strengths: governance/meta guards are unusually strong; replay/fixture chain is coherent; release trust chain is first-class.
- `High`: release/install path lacks artifact-level smoke execution, see `tests/meta/test_governance_release_contract.py:40`, `tests/meta/test_install_sh_guards.py:10`, `.github/workflows/release.yml:177`.
- `High`: coverage policy is total-coverage heavy and diff-coverage weak, see `scripts/coverage_diff.py:34`, `scripts/coverage_diff.py:43`.
- `Medium`: local lint flow is looser than CI, see `scripts/lint:12`, `scripts/lint:51`, `scripts/lint:74`.
- `Medium`: `release.yml` security gate lacks explicit `setup-python`, see `.github/workflows/release.yml:33`.

## Open-Source Experience Verdict

- Strengths: HACS + devcontainer + support/security paths are present; contributor environment is runnable.
- `High`: single-maintainer continuity remains the biggest governance risk, see `SUPPORT.md:32`, `SECURITY.md:33`, `.github/CODEOWNERS:1`.
- `Medium`: contributor fast-path is too mixed with maintainer governance vocabulary, see `CONTRIBUTING.md:73`, `docs/README.md:24`, `.github/pull_request_template.md:8`.
- `Medium`: bilingual promise is not fully credible yet, see `README.md:19`, `CHANGELOG.md:1`, `SUPPORT.md:1`, `docs/README.md:1`.
- `Medium`: security disclosure has no documented fallback outside GitHub private advisory, see `SECURITY.md:58`, `SECURITY.md:64`, `SECURITY.md:75`.

## Repo Hygiene Verdict

- Tracked caches are clean; ignored-cache discipline is good.
- The largest hygiene issue is still `.planning/phases/**` over-tracking versus its stated execution-trace identity.
