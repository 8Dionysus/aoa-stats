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
    readme = read_text("README.md")
    changelog = read_text("CHANGELOG.md")
    payload = load_json("generated/summary_surface_catalog.min.json")

    assert "> Current release: `v0.1.1`" in readme
    assert "## [0.1.1] - 2026-04-12" in changelog
    assert "`v0.1.1`" in roadmap
    assert "Current release contour" in roadmap
    assert "derived-observability hardening" in roadmap
    assert "weaker than source-owned rollout history" in roadmap
    assert payload["schema_version"] == "aoa_stats_summary_surface_catalog_v2"
    assert payload["authority_ref"] == "docs/ARCHITECTURE.md"

    surface_names = {entry["name"] for entry in payload["surfaces"]}
    assert surface_names == set(ROADMAP_PHRASES)

    for surface_name, phrase in ROADMAP_PHRASES.items():
        assert surface_name in surface_names
        assert phrase in roadmap

    current_release_surfaces = [
        "docs/BOUNDARIES.md",
        "docs/ARCHITECTURE.md",
        "docs/LIVE_SESSION_USE.md",
        "docs/README.md",
        "schemas/stats-event-envelope.schema.json",
        "generated/summary_surface_catalog.min.json",
        "schemas/summary-surface-catalog.schema.json",
        "tests/test_summary_surface_catalog.py",
        "docs/CODEX_MCP.md",
        "scripts/aoa_stats_mcp_server.py",
        "src/aoa_stats_mcp/server.py",
        "src/aoa_stats_mcp/repo_state.py",
        "tests/test_aoa_stats_mcp_state.py",
        "requirements-mcp.txt",
        "docs/CODEX_PLANE_DEPLOYMENT_SUMMARIES.md",
        "docs/ROLLOUT_CAMPAIGN_SUMMARY.md",
        "docs/DRIFT_REVIEW_SUMMARY.md",
        "docs/CONTINUITY_WINDOW_SUMMARY.md",
        "docs/STRESS_RECOVERY_SUMMARIES_CHAOS_WAVE1.md",
        "examples/stress_recovery_window_summary.chaos-wave1.example.json",
        "generated/codex_rollout_operations_summary.min.json",
        "generated/codex_rollout_drift_summary.min.json",
        "generated/rollout_campaign_summary.min.json",
        "generated/drift_review_summary.min.json",
        "generated/continuity_window_summary.min.json",
        "scripts/build_views.py",
        "scripts/validate_repo.py",
        "scripts/release_check.py",
    ]
    for surface in current_release_surfaces:
        assert (REPO_ROOT / surface).exists(), surface
        assert surface in roadmap
