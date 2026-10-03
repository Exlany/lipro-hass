# Maintenance review progress — 2026-10-03

Work has stayed in independent cloud checkouts. No user computer, real Home
Assistant configuration, device, credentials, tag or release was accessed or
changed. This is a progress report, not a complete repository/security clearance.

## Manual review coverage

The [ledger](file-review-current-2026-10-03.tsv) records all 765 tracked blobs at
`dd4320ae076fc17bf78513c11c384bd6cef8305d`, before these review files were added.
104 files have been read completely; 661 are unread or only partially read.
Tests/searches/downloads do not count as complete reading. Files found only on
other open PR branches are outside this baseline; their regressions are recorded
in their PRs. Earlier ledgers describe earlier commits and are historical snapshots.

Recent reading covered anonymous sharing, all shared utility modules, telemetry,
authentication/bootstrap and related tests, request policy, response safety,
workflow configuration and contributor/support documentation.

## Published fixes and exact-head results

All following PRs remain draft. Each listed CI run passed; default CodeQL also
passed. The Python and Actions advanced CodeQL jobs failed with the confirmed
default-setup conflict described below.

| PR | Head commit | Passing CI | Local verification |
| --- | --- | --- | --- |
| [#80](https://github.com/Exlany/lipro-hass/pull/80), private exception details in logs | `956e0c4bd3f603e7bb12d34d18f8a4aaf3ae3ac7` | [37091245019](https://github.com/Exlany/lipro-hass/actions/runs/37091245019) | 2545 tests, 5 snapshots; module 100% |
| [#81](https://github.com/Exlany/lipro-hass/pull/81), quoted secrets and truncation order | `210364d1685351a9bb683b2a066487277a95012c` | [37091703198](https://github.com/Exlany/lipro-hass/actions/runs/37091703198) | 2552 tests, 5 snapshots; final 7 utility tests after adding 3 cases |
| [#82](https://github.com/Exlany/lipro-hass/pull/82), non-finite option/retry inputs | `43068f8dc9fe8c142bc059587f001a7a2423f6e8` | [37092029697](https://github.com/Exlany/lipro-hass/actions/runs/37092029697) | 2549 tests, 5 snapshots; both modules 100% |
| [#83](https://github.com/Exlany/lipro-hass/pull/83), expiry-only token renewal | `3e181880d5e38e756c264d3a114dbcc07e0c14e9` | [37092271224](https://github.com/Exlany/lipro-hass/actions/runs/37092271224) | 2543 tests, 5 snapshots; module 97.65% |
| [#84](https://github.com/Exlany/lipro-hass/pull/84), complete local coverage surface | `c7411b7334e318bad23fb6119583eb58d7f83597` | [37092594845](https://github.com/Exlany/lipro-hass/actions/runs/37092594845) | 7 real-Git fixture tests; ShellCheck 0.11.0 |

Each code patch also passed Ruff lint/format and full mypy. Regressions reproduced
the original failures before fixes. No physical-device or live-HA testing occurred.

## Combined verification

A separate, unpublished cloud worktree merged the following exact PR heads without
conflicts, in order:

```text
75 ab2316f66b426de034829a19cb14caef662d5bd9
76 11eff0e176c65de6bdc94af07bb93e0898a599d0
77 507316d22811650c6b33bcc0fff6d6acc7be0f24
79 ccd991774586d27cf65c70dfd1621e6f3deb05f1 (includes #78)
80 956e0c4bd3f603e7bb12d34d18f8a4aaf3ae3ac7
81 210364d1685351a9bb683b2a066487277a95012c
82 43068f8dc9fe8c142bc059587f001a7a2423f6e8
83 3e181880d5e38e756c264d3a114dbcc07e0c14e9
84 c7411b7334e318bad23fb6119583eb58d7f83597
```

Local-only merge commit: `3603fb833617a423bed2ea1c87b406623ab67fbf`.
With the new lockfile dependencies: 2594 tests and 5 snapshots passed; Ruff,
full mypy (648 files), `uv lock --check` and `uv pip check` passed. Total coverage
96.75%; all 14 modified measured production modules exceed 95%. The combined
coverage check did not supply a baseline; individual PR CI runs provide their
own baseline comparisons. No combined branch was pushed or merged to main.

## Blockers and remaining work

- Advanced CodeQL uploads report: `CodeQL analyses from advanced configurations
  cannot be processed when the default setup is enabled`. Disabling default
  setup only has explicit user approval, but the connector settings interface
  returned Forbidden. No retries through alternate privileges, scan disabling,
  alert dismissals or gate bypasses occurred. Successful default scans do not
  authorize bypassing failed advanced gates.
- Security alert inventories are not fully accessible through the available
  connector; absence of retrieved alerts is not evidence of zero alerts.
- HA `2026.9.4` still pins PyJWT `2.13.0` and cryptography `48.0.1` in its
  development dependency set. Do not force incompatible overrides. Re-evaluate
  once a stable HA release and matching pytest integration release accept the
  relevant fixes. Sources: [HA metadata](https://pypi.org/pypi/homeassistant/2026.9.4/json)
  and [HA test plugin metadata](https://pypi.org/pypi/pytest-homeassistant-custom-component/0.13.367/json).
- Continue the 661 unfinished files and investigate bounded payload traversal,
  debug-log exception privacy, cache-load task ownership and manually dispatched
  release identity/SBOM binding. These are pending reviews, not completed fixes.

The associated documentation patch corrects stale HA versions, public repository
access wording and commands referring to absent `tests/meta/`/`.governance/` files.
Markdown links, translation checks, issue-template YAML, documented pytest paths,
ShellCheck and `scripts/lint --help` passed. Architecture/file-matrix helpers
reported their existing governance-data skips; those skips are not review coverage.
