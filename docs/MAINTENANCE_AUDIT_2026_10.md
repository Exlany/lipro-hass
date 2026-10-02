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

## HA constraints and retained security findings

Minimum supported HA remains **2026.3.1**, Python **3.14.2**.
[HA's exact requirements](https://github.com/home-assistant/core/blob/2026.3.1/pyproject.toml)
and the pinned
[HA test plugin](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component/releases/tag/0.13.317)
constrain this environment. The existing aiohttp 3.14 override is advanced from
3.14.1 to the security patch 3.14.3; no new override is introduced. Pillow, PyJWT
and orjson overrides are unchanged. [aiohttp's patch notes](https://docs.aiohttp.org/en/stable/changes.html)
confirm redirect credential-header fixes. This patches the repository environment,
not the HA-managed aiohttp installed on users' systems: `manifest.json` does not
install aiohttp, and HA 2026.3.1 owns its native 3.13.3 dependency. [HA upgrade PR 69](https://github.com/Exlany/lipro-hass/pull/69)
remains on hold: a passing unit suite alone does not authorize raising the
supported HA floor.

A full installed-environment pip-audit returned 15 affected packages / 102 raw
advisory records before compatible updates, and 9 / 79 after the aiohttp patch.
The independently resolved runtime dependency audit now reports zero known vulnerabilities. These are
**local dependency-audit records, not GitHub alert counts**; aliases can duplicate
records. Remaining packages and currently reported fixed-version requirements:

| Package | Locked | Upstream remediation / condition |
|---|---|---|
| cryptography | 46.0.5 | Reported fixes span 46.0.6 through 50.0.0; HA exact pin and pyOpenSSL `<47` prevent wholesale resolution |
| homeassistant | 2026.3.1 | 2026.6.0 / 2026.7.0; requires approved supported-baseline change |
| Pillow | 12.2.0 | 12.3.0; existing override differs from HA native 12.1.1 |
| PyJWT | 2.12.0 | Reported fixes through 2.15.0; PYSEC-2026-4146 lists no fixed version |
| pyOpenSSL | 25.3.0 | 26.0.0; HA exact pin |
| pytest | 9.0.0 | 9.0.3; exact HA test-plugin pin |
| requests | 2.32.5 | 2.33.0; HA exact pin |
| uv | 0.10.6 | 0.11.6 / 0.11.15; HA exact pin |
| zeroconf | 0.148.0 | Reported fixes through 0.149.16; HA exact pin |

Resume when an approved HA/test-plugin baseline permits patched versions,
regenerate the lock without new incompatible overrides, rerun compatibility and
security checks, and verify actual GitHub alerts. For advisories with no fix,
wait for published upstream remediation and reassess exposure. No advisory was
dismissed or suppressed and no dependency-security threshold was reduced.

## External blockers

- Security/Dependabot/code-scanning alert APIs were inaccessible with the exposed
  connection (`Forbidden` / connector endpoint not allowed). An empty alert
  backlog cannot be asserted.
- Existing CodeQL jobs reject SARIF because advanced workflow configuration and
  GitHub default setup are enabled simultaneously. This is an administrative
  configuration conflict, not a successful scan. No repository security settings
  or scan workflows were disabled. Resolve the setup conflict through a separately
  authorized administrator action, then rerun the exact PR head.
- Runtime dependency security passes after patching aiohttp. The full HA/dev
  environment still has the retained findings above; runtime audit success does
  not mean the HA host or GitHub alert backlog is clear.
- Direct cloud CLI access to `repos/Exlany/lipro-hass/code-scanning/default-setup`
  also returns `Forbidden`. The available connector exposes no settings mutation.
  Retain advanced scanning (including tag/release coverage), have an authorized
  administrator remove the duplicate default setup, then rerun exact-head analysis.
  Do not remove the advanced workflow merely to make the check green.

## Local validation

- 2533 tests passed; coverage 96.62% versus baseline 96.10%.
- Every changed measured runtime file passes the 95% floor and non-regression.
- Full mypy: 641 source files, zero errors (baseline: 95 errors in 32 files).
- Ruff lint and formatting: pass (664 Python files formatted).
- `uv lock --check`, translations and configured Markdown links: pass.
- ShellCheck 0.11.0 and actionlint 1.7.7: pass.
- Hassfest container: 1 integration, 0 invalid integrations.
- Benchmark smoke: configured three-case manifest comparison passes.

GitHub CI must be evaluated separately on the submitted commit; local results do
not imply GitHub checks or unavailable security APIs passed.
