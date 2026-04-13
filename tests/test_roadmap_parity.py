from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

ROADMAP_PHRASES = {
    "core_skill_application_summary": "core-skill application",
    "object_summary": "object",
    "candidate_lineage_summary": "candidate-lineage",
    "owner_landing_summary": "owner-landing",
    "supersession_drop_summary": "supersession-drop",
    "repeated_window_summary": "repeated-window",
    "route_progression_summary": "route-progression",
    "fork_calibration_summary": "fork-calibration",
    "session_growth_branch_summary": "session-growth branch",
    "automation_pipeline_summary": "automation-pipeline",
    "automation_followthrough_summary": "automation-followthrough",
    "codex_plane_deployment_summary": "Codex-plane deployment",
    "codex_rollout_operations_summary": "rollout-operations",
    "codex_rollout_drift_summary": "rollout-drift",
    "rollout_campaign_summary": "rollout-campaign",
    "drift_review_summary": "drift-review",
    "continuity_window_summary": "continuity-window",
    "component_refresh_summary": "component-refresh",
    "runtime_closeout_summary": "runtime-closeout",
    "stress_recovery_window_summary": "stress-recovery",
    "surface_detection_summary": "surface-detection",
}


def read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def load_json(relative_path: str) -> object:
    return json.loads((REPO_ROOT / relative_path).read_text(encoding="utf-8"))


def test_roadmap_names_current_catalog_summary_families() -> None:
    roadmap = read_text("ROADMAP.md")
    payload = load_json("generated/summary_surface_catalog.min.json")

    surface_names = {entry["name"] for entry in payload["surfaces"]}
    assert surface_names == set(ROADMAP_PHRASES)

    for surface_name, phrase in ROADMAP_PHRASES.items():
        assert surface_name in surface_names
        assert phrase in roadmap
