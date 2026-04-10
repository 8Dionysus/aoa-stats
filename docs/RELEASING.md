# Releasing `aoa-stats`

This guide defines the bounded publication flow for `aoa-stats`.

`aoa-stats` is released as a repository of derived summary schemas,
deterministic builders, committed machine-first summary surfaces, and local
live-refresh support files.

See also:

- [Documentation Map](README.md)
- [CHANGELOG](../CHANGELOG.md)
- [Contributing](../CONTRIBUTING.md)

## Release goals

A release should make it easy to answer:

- what changed
- why it matters
- how it was validated
- which owner repos were involved
- what is intentionally still outside stats-layer authority

## Recommended release flow

1. Confirm the release scope stays bounded.
2. Update `CHANGELOG.md` with the section that will anchor the human release narrative.
3. Run the repo-level validation loop:
   - `python -m pip install -r requirements-dev.txt`
   - `python scripts/build_views.py --check`
   - `python scripts/validate_repo.py`
   - `python -m pytest -q tests`
4. If the release touches live intake, watcher behavior, or owner-local source registration, also run:
   - `python scripts/check_live_publishers.py`
   - `python scripts/refresh_live_stats.py`
5. Confirm generated surfaces are current when the release touches derivation rules, schemas, examples, or committed `generated/` outputs.
6. Review public-safety hygiene:
   - no secrets
   - no private topology
   - no raw sensitive logs or payload dumps
   - no owner-local meaning copied into stats as if it were stats-owned truth
7. If the release depends on a new upstream owner-owned surface, merge that upstream source first and rerun local validation against the landed source.
8. Merge the release-prep PR to `main`.
9. Create a Git tag such as `v0.1.0`.
10. Publish GitHub release notes from the matching changelog section or a clearly equivalent human-first shape.

## Release note shape

Recommended changelog and GitHub release-note sections:

- summary
- added
- changed
- included in this release
- validation
- notes

Exact headings do not need to be rigid, but the changelog entry and the
published GitHub release should answer the same questions in roughly the same
shape.

## Live-intake changes

If the release changes `config/live_receipt_sources.json`, the shared receipt
envelope, or watcher installation behavior, also confirm:

- required owner-local sources still resolve under the supported workspace layouts
- live-refresh output remains local under `state/`
- committed `generated/` outputs still reflect deterministic repo-owned builds
- publisher audits remain descriptive and do not imply authority over owner repos

## Final publication check

Before finalizing a release:

- confirm the repo still reads as a derived observability layer rather than a
  workflow or proof authority
- confirm summary wording does not overstate what counts, deltas, or verdict
  echoes can prove
- confirm owner-boundary language in `README.md`, `AGENTS.md`, and `docs/`
  still matches the current implementation
- confirm public examples remain sanitized and reusable
- confirm release scope is small enough that reviewers can reason about it directly

## Versioning guidance

Suggested interpretation:

- `0.x.y` for early public baselines, summary-shape hardening, and live-refresh
  discipline
- `1.0.0` only when the repository structure, release path, and evidence posture
  feel stable enough to promise a durable public baseline

## What not to optimize yet

For now, avoid:

- dashboard or scorecard theater that exceeds current validation
- release automation that promises stronger guarantees than the repo actually proves
- per-surface version metadata that duplicates changelog or tag identity
- release claims that make stats sound like source-owned workflow or proof truth

## Current stance

Right now, `aoa-stats` is best released as:

- a bounded derived observability repository
- a repo with deterministic committed summary surfaces plus local live-refresh helpers
- a public surface whose release identity lives in `CHANGELOG.md`, the Git tag,
  and the GitHub release body rather than in a package registry
