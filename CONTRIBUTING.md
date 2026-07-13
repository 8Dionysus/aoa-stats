# Contributing to aoa-stats

Thank you for contributing.

## What belongs here

Good contributions:

- shared measurement compatibility that preserves local owner meaning
- owner-local port interoperability and cross-repo validation
- derived summary schemas and summary-shape improvements
- deterministic builder or validator improvements
- better receipt-envelope or event-kind contract clarity
- public-safe example feeds and summary examples
- live-refresh or publisher-audit improvements that preserve owner boundaries
- docs that clarify how stats stay downstream from source-owned meaning

Bad contributions:

- workflow meaning that belongs in `aoa-skills`
- proof or verdict interpretation that belongs in `aoa-evals`
- scenario or live quest authority that belongs in `aoa-playbooks`
- role or checkpoint meaning that belongs in `aoa-agents`
- memory semantics that belong in `aoa-memo`
- runtime authority that belongs in `abyss-stack`
- secret-bearing logs, paths, hostnames, or private topology
- one universal score that flattens bounded evidence into fake certainty

## Before opening a PR

Please make sure:

- the changed summary, schema, or builder stays explicitly derived
- owner-local measurement questions and definitions remain with their owner
- population, unit, dimensions, missingness, uncertainty, provenance, and
  live/reference posture stay explicit where applicable
- owner repos supplying the input facts are named clearly
- output-shape changes are intentional and documented
- generated surfaces are current when tracked outputs changed
- public examples stay sanitized and reusable
- route, progression, stress, and closeout summaries remain descriptive rather
  than authoritative
- changes do not move workflow, proof, role, or runtime ownership into this repo

Before opening a PR, run local validation for:

- generated-view parity
- schema and example integrity
- repository validation
- test coverage for the changed derivation path

## Local development setup

Dependency manifests live at the repository root. Run the repository gate from
[`AGENTS.md#verify`](AGENTS.md#verify), then the
nearest changed family's `AGENTS.md` and mechanic part's `VALIDATION.md`.

If your change touches live receipt source registration, watcher behavior, or
owner-local intake, also follow the
[`live-receipt-refresh` operator guide](mechanics/recurrence/parts/live-receipt-refresh/docs/LIVE_SESSION_USE.md)
and its adjacent
[`VALIDATION.md`](mechanics/recurrence/parts/live-receipt-refresh/VALIDATION.md).

## Preferred PR scope

Prefer:

- 1 summary family or schema improvement per PR
- or 1 focused builder / validator improvement
- or 1 bounded live-refresh or publisher-audit change
- or 1 focused docs and release-guidance improvement

Keep public-share changes small enough that a reviewer can still see the owner
boundaries without reconstructing the whole federation.
