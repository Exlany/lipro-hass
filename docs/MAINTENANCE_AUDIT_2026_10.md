# October 2026 maintenance audit

Baseline: `444ce7f75bad360597ab967989d2e1bbc8d1935f` (main).
All execution used an isolated cloud checkout, with no live HA instance or device.

## Scope and evidence limits

The baseline inventory contains 758 tracked files, including 326 runtime Python
files and 304 test Python files. Every tracked file was inventoried and hashed;
Python AST, JSON, TOML and YAML syntax were checked across the inventory.
Repository-wide Ruff and configured full mypy checks cover the Python surface;
the full non-benchmark pytest suite exercises integration behavior. Targeted manual
review covered changed runtime contracts, redaction, REST/MQTT boundaries,
authentication, sharing, installer, dependencies, CI and release workflows.
This is **not a claim that every line of all 758 files received manual review**.
Markdown validation covers only the repository checker's configured links.
Governance checks report skips because `.governance` is absent; they do not provide
an independent architecture-policy assurance. Physical devices, live cloud
accounts, actual HA upgrades and releases were not exercised.

## Repairs

- Share one sensitive-key policy across invalid-response and MQTT redaction;
  mask escaped/truncated secrets and mask schedule payloads before truncation.
- Correct protocol, coordinator, entity and service typing contracts. Full mypy
  replaces a three-file CI subset and stale pre-commit references to `tests/meta`.
- Preserve scoped anonymous-sharing clients with explicitly typed accessors.
- Resolve relative offline installer paths before changing directories; verify
  successful installation and checksum rejection in temporary fake configurations.
- Fix Hassfest's integration mount to `custom_components/lipro`.
- Check lock freshness and full repository formatting in CI. Compare all PR
  commits against merge-base, rather than checking only the latest commit.
- Fail closed when release or PR code-scanning evidence cannot be read.
- Incorporate compatible dependency and pinned Action updates from PRs
  [62](https://github.com/Exlany/lipro-hass/pull/62),
  [66](https://github.com/Exlany/lipro-hass/pull/66),
  [67](https://github.com/Exlany/lipro-hass/pull/67),
  [68](https://github.com/Exlany/lipro-hass/pull/68),
  [70](https://github.com/Exlany/lipro-hass/pull/70), and
  [71](https://github.com/Exlany/lipro-hass/pull/71).
  Final locks include pip 26.2.1, virtualenv 21.14.3, anyio 4.14.2,
  urllib3 2.8.0 and Pygments 2.21.0. Original PRs remain open until the
  consolidated changes can satisfy blocking checks and merge.

## Latest stable HA baseline and retained upstream findings

The authorized support baseline is now **Home Assistant 2026.9.4**, verified from
[the official latest stable release](https://github.com/home-assistant/core/releases/tag/2026.9.4).
Python remains **>=3.14.2**, exactly as required by the upstream release.
The test plugin is pinned to **0.13.367**, whose package metadata requires HA
2026.9.4. Plugin 0.13.368 targets 2026.10.0b0 and is intentionally not selected.
HACS metadata, both READMEs, troubleshooting, bug templates and the development
pin agree on the new minimum. This upgrades the repository, not a user's live HA.

All four old uv overrides (aiohttp, Pillow, PyJWT and orjson) and the old pycares
cap are removed. The environment resolves against
[HA's native exact requirements](https://github.com/home-assistant/core/blob/2026.9.4/pyproject.toml),
including aiohttp 3.14.3, Pillow 12.3.0, orjson 3.11.9, pytest 9.0.3 via the matching
test plugin, requests 2.34.2, uv 0.12.5 and zeroconf 0.151.1.
`uv pip check` reports all installed packages compatible.

The full installed-environment audit improves from **15 affected packages / 102
raw records** to **2 packages / 19 raw records**. These are local audit results,
not GitHub alert counts; aliases can duplicate records. The separately resolved
runtime dependency audit reports zero known vulnerabilities.

| Package | Native HA pin | Remaining remediation constraints |
|---|---|---|
| cryptography | 48.0.1 | PYSEC-2026-3554 and -3553 require 49.0.0; -3552 requires 50.0.0 |
| PyJWT | 2.13.0 | Reported fixes require 2.14.0 / 2.15.0; PYSEC-2026-4146 lists no fixed version |

Resume when a stable HA release permits these fixed versions, and when upstream
publishes remediation for the no-fix advisory. Update the matched HA/test-plugin
pair, regenerate the lock without incompatible overrides, run tests and audit,
and verify GitHub alerts through an authorized connection. No advisory is
suppressed or dismissed. [PR 69](https://github.com/Exlany/lipro-hass/pull/69)'s
2026.7.0 proposal is superseded by the newer stable baseline once this change merges.

The stricter HA test plugin detected four tests leaving debounce timers alive.
They now execute the entity's normal removal lifecycle and assert the debouncer
is released, preserving the upstream leak checks.

## External blockers

- Security/Dependabot/code-scanning alert APIs were inaccessible with the exposed
  connection (`Forbidden` / connector endpoint not allowed). An empty alert
  backlog cannot be asserted.
- Existing CodeQL jobs reject SARIF because advanced workflow configuration and
  GitHub default setup are enabled simultaneously. This is an administrative
  configuration conflict, not a successful scan. No repository security settings
  or scan workflows were disabled. Resolve the setup conflict through a separately
  authorized administrator action, then rerun the exact PR head.
- Runtime dependency security passes; the full HA/dev environment still has the
  two upstream packages above. Success does not mean the GitHub alert backlog is clear.
- Direct cloud CLI access to `repos/Exlany/lipro-hass/code-scanning/default-setup`
  also returns `Forbidden`. The available connector exposes no settings mutation.
  Retain advanced scanning (including tag/release coverage), have an authorized
  administrator remove the duplicate default setup, then rerun exact-head analysis.
  Do not remove the advanced workflow merely to make the check green.

## Local validation

- 2533 tests and 5 snapshots passed under HA 2026.9.4; coverage 96.62%
  versus baseline 96.10%.
- Every changed measured runtime file passes the 95% floor and non-regression.
- Full mypy: 641 source files, zero errors (baseline: 95 errors in 32 files).
- Ruff lint and formatting: pass (664 Python files formatted).
- `uv lock --check`, translations and configured Markdown links: pass.
- ShellCheck 0.11.0 and actionlint 1.7.7: pass.
- Hassfest container: 1 integration, 0 invalid integrations.
- Full benchmark suite: 9 cases pass, and all configured manifest thresholds pass
  under HA 2026.9.4.

GitHub CI must be evaluated separately on the submitted commit; local results do
not imply GitHub checks or unavailable security APIs passed.
