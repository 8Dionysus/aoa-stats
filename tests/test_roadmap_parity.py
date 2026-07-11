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
    "memory_movement_summary": "memory-movement",
    "titan_incarnation_summary": "Titan-incarnation",
    "titan_summon_summary": "Titan-summon",
    "runtime_closeout_summary": "runtime-closeout",
    "stress_recovery_window_summary": "stress-recovery",
    "source_coverage_summary": "source-coverage",
    "surface_detection_summary": "surface-detection",
}


def read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def load_json(relative_path: str) -> dict:
    payload = json.loads((REPO_ROOT / relative_path).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_roadmap_names_current_catalog_summary_families() -> None:
    roadmap = read_text("ROADMAP.md")
    readme = read_text("README.md")
    changelog = read_text("CHANGELOG.md")
    catalog = load_json("generated/summary_surface_catalog.min.json")

    assert "> Current release: `v0.1.3`" in readme
    assert "## [0.1.3] - 2026-04-23" in changelog
    assert "`v0.1.3`" in roadmap
    assert "Current release contour" in roadmap
    assert "derived-observability hardening" in roadmap
    assert "weaker than source-owned rollout history" in roadmap
    assert catalog["schema_version"] == "aoa_stats_summary_surface_catalog_v2"
    assert catalog["authority_ref"] == "docs/ARCHITECTURE.md"

    surface_names = {entry["name"] for entry in catalog["surfaces"]}
    assert surface_names == set(ROADMAP_PHRASES)
    for phrase in ROADMAP_PHRASES.values():
        assert phrase in roadmap


def test_roadmap_routes_to_authored_profiles_and_localized_operations() -> None:
    roadmap = read_text("ROADMAP.md")
    catalog = load_json("generated/summary_surface_catalog.min.json")
    profile_names = {
        load_json(path.relative_to(REPO_ROOT).as_posix())["name"]
        for path in (REPO_ROOT / "stats/read-models/active").glob("*.profile.json")
    }
    assert profile_names == {entry["name"] for entry in catalog["surfaces"]}

    current_routes = [
        "docs/BOUNDARIES.md",
        "docs/ARCHITECTURE.md",
        "stats/intake-contract/RECEIPT_ABI.md",
        "stats/intake-contract/event-kind-registry.json",
        "stats/read-models/README.md",
        "stats/surface-catalog/CODEX_MCP.md",
        "mechanics/recurrence/parts/live-receipt-refresh/config/live_receipt_sources.json",
        "mechanics/recurrence/parts/live-receipt-refresh/docs/LIVE_SESSION_USE.md",
        "mechanics/audit/parts/source-coverage/docs/SOURCE_COVERAGE_SUMMARY.md",
        "mechanics/release-support/parts/codex-deployment-rollout/docs/CODEX_PLANE_DEPLOYMENT_SUMMARIES.md",
        "mechanics/release-support/parts/rollout-campaign/docs/ROLLOUT_CAMPAIGN_SUMMARY.md",
        "mechanics/audit/parts/drift-shadow-review/docs/DRIFT_REVIEW_SUMMARY.md",
        "mechanics/recurrence/parts/continuity-window/docs/CONTINUITY_WINDOW_SUMMARY.md",
        "mechanics/recurrence/parts/component-refresh/docs/COMPONENT_REFRESH_SUMMARIES.md",
        "mechanics/antifragility/parts/stress-recovery-windows/examples/stress_recovery_window_summary.chaos-wave1.example.json",
        "mechanics/boundary-bridge/parts/memory-owner-handoff/docs/MEMORY_MOVEMENT_SUMMARY.md",
        "generated/summary_surface_catalog.min.json",
        "schemas/summary-surface-catalog.schema.json",
        "scripts/build_views.py",
        "scripts/validate_repo.py",
        "scripts/release_check.py",
    ]
    for route in current_routes:
        assert (REPO_ROOT / route).exists(), route
        assert route in roadmap
