#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, SchemaError

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder.surface_catalog import (  # noqa: E402
    SurfaceProfileError,
    load_surface_profiles,
)

EXTRA_SCHEMA_ROUTES = (
    "schemas/stats-event-envelope.schema.json",
    "stats/read-models/surface-profile.schema.json",
)
REQUIRED_TEXT_FILES = (
    "README.md",
    "AGENTS.md",
    "DESIGN.md",
    "stats/README.md",
    "mechanics/README.md",
    "docs/README.md",
    "docs/BOUNDARIES.md",
    "docs/ARCHITECTURE.md",
    "docs/decisions/README.md",
    "docs/decisions/AGENTS.md",
    "docs/decisions/TEMPLATE.md",
    "docs/GROWTH_FUNNEL_SUMMARY.md",
    "docs/COMPONENT_REFRESH_SUMMARIES.md",
    "docs/RECURRENCE_DERIVED_SUMMARIES.md",
    "mechanics/growth-cycle/parts/session-growth-branch/docs/SESSION_GROWTH_BRANCH_SUMMARY.md",
    "mechanics/growth-cycle/parts/automation-followthrough/docs/AUTOMATION_FOLLOWTHROUGH_SUMMARY.md",
    "mechanics/release-support/parts/codex-deployment-rollout/docs/CODEX_PLANE_DEPLOYMENT_SUMMARIES.md",
    "mechanics/release-support/parts/rollout-campaign/docs/ROLLOUT_CAMPAIGN_SUMMARY.md",
    "mechanics/audit/parts/drift-shadow-review/docs/DRIFT_REVIEW_SUMMARY.md",
    "mechanics/recurrence/parts/continuity-window/docs/CONTINUITY_WINDOW_SUMMARY.md",
    "mechanics/recurrence/parts/component-refresh/docs/COMPONENT_REFRESH_SUMMARIES.md",
    "mechanics/boundary-bridge/parts/memory-owner-handoff/docs/MEMORY_MOVEMENT_SUMMARY.md",
    "mechanics/method-growth/parts/supersession-pruning/docs/SUPERSESSION_DROP_SUMMARY.md",
    "stats/surface-catalog/CODEX_MCP.md",
    "mechanics/recurrence/parts/live-receipt-refresh/docs/LIVE_SESSION_USE.md",
    "stats/intake-contract/RECEIPT_ABI.md",
    "docs/SURFACE_STRENGTH_MODEL.md",
    "mechanics/audit/parts/source-coverage/docs/SOURCE_COVERAGE_SUMMARY.md",
    "stats/surface-catalog/CONSUMER_REGROUNDING.md",
)


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def profile_schema_inventory() -> tuple[dict[str, str], set[str]]:
    """Derive output/schema validation routes from the authored source profiles."""

    active, deferred, retired = load_surface_profiles(
        REPO_ROOT / "stats" / "read-models"
    )
    generated_schemas = {
        Path(profile["surface_ref"]).name: profile["schema_ref"] for profile in active
    }
    generated_schemas["summary_surface_catalog.min.json"] = (
        "schemas/summary-surface-catalog.schema.json"
    )
    schema_routes = {
        *(profile["schema_ref"] for profile in [*active, *deferred, *retired]),
        *EXTRA_SCHEMA_ROUTES,
        "schemas/summary-surface-catalog.schema.json",
    }
    return generated_schemas, schema_routes


def main() -> int:
    errors: list[str] = []

    try:
        generated_schemas, schema_routes = profile_schema_inventory()
    except SurfaceProfileError as exc:
        errors.append(f"could not load authored read-model profiles: {exc}")
        generated_schemas = {}
        schema_routes = set(EXTRA_SCHEMA_ROUTES)

    for relative_path in REQUIRED_TEXT_FILES:
        path = REPO_ROOT / relative_path
        if not path.exists():
            errors.append(f"missing required text surface: {relative_path}")

    for schema_ref in sorted(schema_routes):
        schema_path = REPO_ROOT / schema_ref
        if not schema_path.exists():
            errors.append(f"missing schema: {schema_ref}")
            continue
        try:
            schema_payload = load_json(schema_path)
            if not isinstance(schema_payload, dict):
                errors.append(f"schema must be a JSON object: {schema_ref}")
                continue
            Draft202012Validator.check_schema(schema_payload)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON in {schema_ref}: {exc}")
        except SchemaError as exc:
            errors.append(f"invalid JSON schema in {schema_ref}: {exc.message}")

    try:
        build_views_command = [sys.executable, "scripts/build_views.py", "--check"]
        configured_evals_root = os.environ.get("AOA_EVALS_ROOT")
        if configured_evals_root:
            build_views_command.extend(["--evals-root", configured_evals_root])
        result = subprocess.run(
            build_views_command,
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        errors.append(f"could not run build_views --check: {exc}")
    else:
        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip() or "unknown error"
            errors.append(f"build_views --check failed: {message}")

    for label, command in (
        (
            "validate_nested_agents",
            [
                sys.executable,
                "scripts/validate_nested_agents.py",
                "--fail-on-untracked",
            ],
        ),
        (
            "validate_mechanics_topology",
            [sys.executable, "scripts/validate_mechanics_topology.py"],
        ),
        (
            "validate_stats_source_home",
            [sys.executable, "scripts/validate_stats_source_home.py"],
        ),
        (
            "check_agon_kag_stats_observability_registry",
            [
                sys.executable,
                "mechanics/agon/parts/kag-observability/scripts/build_agon_kag_stats_observability_registry.py",
                "--check",
            ],
        ),
        (
            "validate_agon_kag_stats_observability_registry",
            [
                sys.executable,
                "mechanics/agon/parts/kag-observability/scripts/validate_agon_kag_stats_observability_registry.py",
            ],
        ),
        (
            "generate_decision_indexes",
            [sys.executable, "scripts/generate_decision_indexes.py", "--check"],
        ),
        (
            "validate_decision_records",
            [sys.executable, "scripts/validate_decision_records.py"],
        ),
        ("validate_receipt_abi", [sys.executable, "scripts/validate_receipt_abi.py"]),
        (
            "validate_downstream_canaries",
            [sys.executable, "scripts/validate_downstream_canaries.py"],
        ),
    ):
        try:
            result = subprocess.run(
                command,
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError as exc:
            errors.append(f"could not run {label}: {exc}")
            continue
        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip() or "unknown error"
            errors.append(f"{label} failed: {message}")

    for generated_name, schema_ref in generated_schemas.items():
        schema_path = REPO_ROOT / schema_ref
        generated_path = REPO_ROOT / "generated" / generated_name
        if not generated_path.exists() or not schema_path.exists():
            continue
        try:
            payload = load_json(generated_path)
            schema = load_json(schema_path)
            validator = Draft202012Validator(schema)
            for issue in validator.iter_errors(payload):
                path = ".".join(str(part) for part in issue.absolute_path)
                prefix = f"{generated_name}:{'.' + path if path else ''}"
                errors.append(f"{prefix} {issue.message}")
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON in generated/{generated_name}: {exc}")

    if errors:
        print("Validation failed for aoa-stats.")
        for error in errors:
            print(f"- {error}")
        return 1

    print("[ok] validated aoa-stats repo surfaces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
