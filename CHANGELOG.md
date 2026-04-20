# Changelog

All notable changes to `aoa-stats` will be documented in this file.

The format is intentionally simple and human-first.
Tracking starts with the first public release-prep baseline for this repository.

## [Unreleased]

## [0.1.1] - 2026-04-12

### Summary

- this patch adds repo-local Codex MCP disclosure and new rollout/continuity
  summary surfaces
- release-audit continuity dependencies and rollout builder behavior are
  hardened across the derived observability lane
- `aoa-stats` remains a bounded derived layer rather than workflow authority

### Added

- narrow repo-local `aoa_stats` MCP surface for Codex under
  `src/aoa_stats_mcp/` and `scripts/aoa_stats_mcp_server.py`, scoped to the
  summary catalog, generated surfaces, source registry, and boundary bundle
- focused MCP state tests under `tests/test_aoa_stats_mcp_state.py`
- optional MCP dependency surface in `requirements-mcp.txt`

### Documentation

- repo-local MCP posture and launch guidance in `docs/CODEX_MCP.md`
- README, docs map, and AGENTS routing updates so the MCP stays bounded and
  visibly derived-only

### Changed

- added Codex rollout operations summaries, campaign cadence summaries, and
  continuity-window summaries to the derived observability layer.
- wired release-audit continuity dependencies, fixed continuity-summary
  discovery, and hardened rollout stats builders.

### Validation

- `python scripts/release_check.py`

### Notes

- detailed Codex MCP, rollout-summary, and continuity-summary changes for this patch remain enumerated below under `Added`, `Documentation`, and `Changed`

## [0.1.0] - 2026-04-10

First public release of `aoa-stats` as the derived observability layer in the
AoA public federation.

This changelog entry uses the release-prep merge date.

### Summary

- current public stats posture ships as a bounded derived layer rather than a
  dashboard authority or score empire
- the first public baseline includes the canonical shared receipt envelope,
  deterministic builders, local live-refresh helpers, and committed
  machine-first summary surfaces
- release messaging remains intentionally modest: counts, progression deltas,
  and summary capsules stay weaker than the source-owned receipts, verdicts,
  and workflow meaning they summarize

### Added

- first public release of `aoa-stats` as a repository for derived summary
  schemas, builders, validators, and generated observability surfaces
- canonical shared receipt-envelope and event-kind contracts under `schemas/`
- live receipt source registry plus local refresh, publisher-audit, and
  systemd watcher helpers under `config/`, `scripts/`, and `systemd/`
- committed generated summary surfaces under `generated/`, including the
  runtime-entry summary catalog capsule
- public-safe example receipt feeds and summary examples under `examples/`
- repo-level release, contribution, conduct, and security guidance for public
  release readiness

### Included in this release

- `10` committed generated summary surfaces under `generated/`
- current stats-layer docs under `docs/`
- current schemas, examples, scripts, tests, and live-refresh support files
- derived summary buildout across `generated/`, `schemas/`, `config/`,
  `scripts/`, `systemd/`, `examples/`, and `docs/`, including core-skill
  application summaries, supersedes-aware active views, surface-detection
  summaries, antifragility vectors, stress-recovery summaries, and the v2
  runtime capsule
- repo operating surfaces under `.agents/`, `.github/`, `AGENTS.md`,
  `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`,
  `tests/`, and `requirements-dev.txt`, including validate workflow, publisher
  audits, boundedness tightening, and release-ready community docs

### Validation

- `python scripts/build_views.py --check`
- `python scripts/validate_repo.py`
- `python -m pytest -q tests`

### Notes

- this remains a derived observability release, not a claim that `aoa-stats`
  now owns workflow, proof, route, or quest authority
- live local refresh stays operator-local under `state/`; the committed
  `generated/` directory remains the deterministic public repo surface
