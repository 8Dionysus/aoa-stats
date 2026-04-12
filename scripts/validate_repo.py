#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, SchemaError

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVALS_ROOT = REPO_ROOT.parent / "aoa-evals"
SCHEMAS = {
    "object_summary.min.json": "object-summary.schema.json",
    "candidate_lineage_summary.min.json": "candidate_lineage_summary.schema.json",
    "owner_landing_summary.min.json": "owner-landing-summary.schema.json",
    "supersession_drop_summary.min.json": "supersession-drop-summary.schema.json",
    "core_skill_application_summary.min.json": "core-skill-application-summary.schema.json",
    "repeated_window_summary.min.json": "repeated-window-summary.schema.json",
    "route_progression_summary.min.json": "route-progression-summary.schema.json",
    "fork_calibration_summary.min.json": "fork-calibration-summary.schema.json",
    "session_growth_branch_summary.min.json": "session-growth-branch-summary.schema.json",
    "automation_pipeline_summary.min.json": "automation-pipeline-summary.schema.json",
    "automation_followthrough_summary.min.json": "automation-followthrough-summary.schema.json",
    "continuity_window_summary.min.json": "continuity-window-summary.schema.json",
    "codex_plane_deployment_summary.min.json": "codex-plane-deployment-summary.schema.json",
    "codex_rollout_operations_summary.min.json": "codex-rollout-operations-summary.schema.json",
    "codex_rollout_drift_summary.min.json": "codex-rollout-drift-summary.schema.json",
    "rollout_campaign_summary.min.json": "rollout-campaign-summary.schema.json",
    "drift_review_summary.min.json": "drift-review-summary.schema.json",
    "runtime_closeout_summary.min.json": "runtime-closeout-summary.schema.json",
    "stress_recovery_window_summary.min.json": "stress-recovery-window-summary.schema.json",
    "surface_detection_summary.min.json": "surface-detection-summary.schema.json",
    "summary_surface_catalog.min.json": "summary-surface-catalog.schema.json",
}
EXTRA_SCHEMA_FILES = (
    "stats-event-envelope.schema.json",
    "stress_recovery_window_summary_v1.json",
)
REQUIRED_TEXT_FILES = (
    "README.md",
    "AGENTS.md",
    "docs/README.md",
    "docs/BOUNDARIES.md",
    "docs/ARCHITECTURE.md",
    "docs/GROWTH_FUNNEL_SUMMARY.md",
    "docs/SESSION_GROWTH_BRANCH_SUMMARY.md",
    "docs/AUTOMATION_FOLLOWTHROUGH_SUMMARY.md",
    "docs/CODEX_PLANE_DEPLOYMENT_SUMMARIES.md",
    "docs/ROLLOUT_CAMPAIGN_SUMMARY.md",
    "docs/DRIFT_REVIEW_SUMMARY.md",
    "docs/CONTINUITY_WINDOW_SUMMARY.md",
    "docs/OWNER_LANDING_SUMMARY.md",
    "docs/SUPERSESSION_DROP_SUMMARY.md",
    "docs/CODEX_MCP.md",
    "docs/LIVE_SESSION_USE.md",
)


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []

    for relative_path in REQUIRED_TEXT_FILES:
        path = REPO_ROOT / relative_path
        if not path.exists():
            errors.append(f"missing required text surface: {relative_path}")

    for schema_name in sorted({*SCHEMAS.values(), *EXTRA_SCHEMA_FILES}):
        schema_path = REPO_ROOT / "schemas" / schema_name
        if not schema_path.exists():
            errors.append(f"missing schema: schemas/{schema_name}")
            continue
        try:
            schema_payload = load_json(schema_path)
            if not isinstance(schema_payload, dict):
                errors.append(f"schema must be a JSON object: schemas/{schema_name}")
                continue
            Draft202012Validator.check_schema(schema_payload)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON in schemas/{schema_name}: {exc}")
        except SchemaError as exc:
            errors.append(f"invalid JSON schema in schemas/{schema_name}: {exc.message}")

    try:
        build_views_command = [sys.executable, "scripts/build_views.py", "--check"]
        configured_evals_root = os.environ.get("AOA_EVALS_ROOT")
        if configured_evals_root:
            build_views_command.extend(["--evals-root", configured_evals_root])
        elif DEFAULT_EVALS_ROOT.exists():
            build_views_command.extend(["--evals-root", str(DEFAULT_EVALS_ROOT)])
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

    for generated_name, schema_name in SCHEMAS.items():
        schema_path = REPO_ROOT / "schemas" / schema_name
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
