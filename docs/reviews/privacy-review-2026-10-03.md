# Privacy boundary review progress — 2026-10-03

This is an incomplete manual review, performed only in an independent cloud
checkout. It does not establish that every repository file or security alert is
resolved. No real Home Assistant instance or device was accessed.

The [file ledger](file-review-privacy-2026-10-03.tsv) covers all 766 tracked blobs
at code commit `bdce1cc96834be5aab1e969ada311a58d19599b7`. Of these, 64 files
have been read completely and 702 remain unread or only partly read. Every row
records the source commit and blob. This snapshot predates these review documents
and excludes files that exist only on other open PR branches. Automated tests,
searches and downloads are not counted as complete manual reading.

## Confirmed findings and fixes

- [PR #80](https://github.com/Exlany/lipro-hass/pull/80): replacing exception args
  did not prevent private details in causes, notes, filenames or custom string
  formatting from reaching upload logs. Three synthetic cases failed before the
  fix. Logging now retains only the error type without mutating the exception.
  Full regression: 2545 tests and 5 snapshots passed; full mypy and Ruff passed;
  modified module coverage 100%. Exact commit
  `956e0c4bd3f603e7bb12d34d18f8a4aaf3ae3ac7` passed
  [CI](https://github.com/Exlany/lipro-hass/actions/runs/37091245019) and
  [default CodeQL](https://github.com/Exlany/lipro-hass/actions/runs/37091242932).
- [PR #81](https://github.com/Exlany/lipro-hass/pull/81): quoted JSON secrets in
  arbitrary text were not masked, and truncation before sanitization left token
  fragments. Seven regression cases failed before the fix. Text redaction now
  shares the API JSON matcher, with sanitization before the message limit.
  Full regression: 2552 tests and 5 snapshots passed. Three additional boundary
  cases were then added; the final seven-test utility module passed. Full mypy
  (643 files) and Ruff passed on the final code. Combined coverage: redaction
  97.30%, API response safety 100%, collector 99%, with no changed-file regression.
  Remote CI must be checked again against this PR's final head.

## Remaining work and blockers

Both PRs remain draft. Advanced CodeQL still fails because default setup is
enabled; the configuration switch is authorized but the available administration
interface returned Forbidden. No settings retries, alternate privileged workflow,
scan disabling, alert dismissal or gate bypass was used.

Continue manual reading beyond the current ledger. The utility and request-policy
review identified follow-up candidates that are not fixed by these PRs:

- Validate non-finite numeric options and Retry-After values with regression tests.
- Check whether all sanitized strings and feedback projections obey size/depth
  limits before recursive traversal.
- Review debug exception traces and arbitrary exception `code` values for privacy.
- Review token persistence when only expiry changes, and cache-load task ownership.

These are investigation candidates, not claims that every path is exploitable.
Home Assistant's pinned development dependencies remain unchanged; upstream
compatibility constraints and inaccessible security alert inventories still need
to be reflected in the final maintenance report.
