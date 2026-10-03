# Submission review follow-up, 2026-10-03

The [commit/blob ledger](file-review-submission-2026-10-03.tsv) covers the 766
tracked files at code commit `1bf1d237c8ca52d4f2a768d4c460f7b7f9593cfb`.
42 files have been completely read; **724 remain not completely read**.
Generated inventories, syntax checks, dependency scans and tests are not counted
as complete manual reading. This supersedes the earlier reading-count snapshot
in PR 77 without claiming completion of the requested whole-repository review.

## Delivered review slices

- [PR 77](https://github.com/Exlany/lipro-hass/pull/77),
  `507316d22811650c6b33bcc0fff6d6acc7be0f24`: cache/token boundary validation.
  [Exact CI](https://github.com/Exlany/lipro-hass/actions/runs/37089142854) succeeds;
  [default CodeQL](https://github.com/Exlany/lipro-hass/actions/runs/37089140634)
  succeeds. Advanced upload remains blocked.
- [PR 78](https://github.com/Exlany/lipro-hass/pull/78),
  `0db697f006e803c3ff5c33d1cb5393c054bed969`: queued submission consent/data checks
  inside the existing scope lock. Both deterministic regressions failed before
  the patch; 2544 tests and 5 snapshots pass after it.
  [Exact CI](https://github.com/Exlany/lipro-hass/actions/runs/37089595670) and
  [default CodeQL](https://github.com/Exlany/lipro-hass/actions/runs/37089593878)
  succeed. Advanced upload remains blocked.
- This patch: acknowledge a snapshot of delivered records on the event loop;
  preserve newly collected devices/errors, replacement device records and records
  omitted from a lite report; pass a detached cache copy to the disk worker.
  The data-loss regression failed before the patch. 2548 tests and 5 snapshots
  pass after it; full mypy checks 643 files. Changed runtime coverage is
  96.67% / 98.99% / 99.34% / 96.92%, each above 95% and non-regressing.
  Second-pass diff review checked identity retention, error-count subtraction,
  cancellation, lite-report limits, scope lock ownership and copied disk arguments.
  Final-commit GitHub checks must still be evaluated separately.

## Dependency PRs and blockers

[PR 76](https://github.com/Exlany/lipro-hass/pull/76) now has mypy-2.3 compatibility
repairs at `11eff0e176c65de6bdc94af07bb93e0898a599d0`, without ignores or relaxed
gates. The command-code value has an explicit object contract; test assertions
use snapshots of mutable attributes and retain the original mock handle.
The updated locked environment passes pip check, full mypy (642 files), 2542 tests
and 5 snapshots. [Exact CI](https://github.com/Exlany/lipro-hass/actions/runs/37089801862)
and [default CodeQL](https://github.com/Exlany/lipro-hass/actions/runs/37089799693)
succeed; advanced upload remains blocked. New dependencies ast-serialize and
py-cpuinfo2 come from mypy and pytest-benchmark's declared requirements. This is
compatibility verification, not a complete upstream source audit.

PR 75 was automatically rebuilt at `ab2316f66b426de034829a19cb14caef662d5bd9`.
The diff is still the same three pinned Action updates reviewed in the prior
slice. [CI](https://github.com/Exlany/lipro-hass/actions/runs/37088515376) succeeds,
but CodeQL upload fails; no successful matching default PR scan was found.
The existing Codecov dynamic-CLI-version risk remains documented. The official
CLI release metadata reports v11.3.1, but a read-only CDN availability check from
this cloud environment returned 403, so no unverified download configuration
was committed.

No failed security check is bypassed. No scanning/settings request was repeated;
no alert was dismissed. The authorized CodeQL setup switch still requires an
administrator connection that can change that setting. HA/PyJWT constraints
remain as recorded in PR 77; these PRs do not force incompatible upgrades.

## Next review scope

The 21 anonymous-share runtime files have been read, but not every finding is
closed. Next inspect shared logging/redaction and payload size/depth handling,
then the remaining protocol, runtime, entity, test, script and configuration
files shown as unread in the ledger. In particular, examine error text before
truncation, exception chains/custom exception formatting, thread-boundary cache
loads and nested developer-feedback projection. Do not treat these hypotheses
as confirmed vulnerabilities without deterministic evidence.

No live HA instance, physical device, account or release was exercised.
