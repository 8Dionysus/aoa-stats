from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "build_views.py"


def load_build_views_module():
    spec = importlib.util.spec_from_file_location("build_views", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module

def test_build_views_produces_expected_surface_counts() -> None:
    module = load_build_views_module()
    receipts = module.load_receipts(
        [REPO_ROOT / "stats" / "intake-contract" / "examples" / "session_harvest_family.receipts.example.json"]
    )
    outputs = module.build_all_views(receipts, ["stats/intake-contract/examples/session_harvest_family.receipts.example.json"])

    assert set(outputs) == {
        "object_summary.min.json",
        "candidate_lineage_summary.min.json",
        "supersession_drop_summary.min.json",
        "core_skill_application_summary.min.json",
        "repeated_window_summary.min.json",
        "route_progression_summary.min.json",
        "fork_calibration_summary.min.json",
        "session_growth_branch_summary.min.json",
        "automation_pipeline_summary.min.json",
        "automation_followthrough_summary.min.json",
        "codex_plane_deployment_summary.min.json",
        "codex_rollout_operations_summary.min.json",
        "codex_rollout_drift_summary.min.json",
        "rollout_campaign_summary.min.json",
        "drift_review_summary.min.json",
        "continuity_window_summary.min.json",
        "component_refresh_summary.min.json",
        "memory_movement_summary.min.json",
        "titan_incarnation_summary.min.json",
        "stress_recovery_window_summary.min.json",
        "source_coverage_summary.min.json",
        "surface_detection_summary.min.json",
        "summary_surface_catalog.min.json",
    }
    assert outputs["object_summary.min.json"]["generated_from"]["total_receipts"] == 16
    assert outputs["candidate_lineage_summary.min.json"]["stage_counts"] == {
        "observed": 2,
        "checkpointed": 2,
        "reviewed": 2,
        "harvested": 1,
        "seeded": 0,
        "planted": 0,
        "proved": 0,
        "promoted": 0,
        "superseded_or_dropped": 1,
    }
    assert outputs["candidate_lineage_summary.min.json"]["owner_target_counts"] == {
        "aoa-playbooks": 1,
        "aoa-skills": 1,
    }
    assert outputs["supersession_drop_summary.min.json"]["drop_reason_counts"] == {
        "nearest_wrong_target_rejected_during_reviewed_harvest": 1,
    }
    assert outputs["supersession_drop_summary.min.json"]["reanchor_after_drop_counts"] == {
        "aoa-playbooks": 1,
    }
    assert outputs["rollout_campaign_summary.min.json"]["campaign_ref"] == "CAMP-20260412-codex-cadence-01"
    assert outputs["rollout_campaign_summary.min.json"]["pending_reviews"] == 1
    assert outputs["drift_review_summary.min.json"]["review_ref"] == "DREV-20260412-codex-cadence-01"
    assert outputs["drift_review_summary.min.json"]["signals_seen"]["hook_drift"] == 1
    assert outputs["component_refresh_summary.min.json"]["owner_repo_counts"] == {
        "8Dionysus": 1,
        "aoa-agents": 1,
        "aoa-skills": 1,
        "aoa-stats": 1,
    }
    assert outputs["component_refresh_summary.min.json"]["status_counts"] == {
        "refresh_recommended": 1,
        "refresh_active": 2,
        "current": 0,
        "deferred": 1,
        "recovered": 0,
    }
    assert len(outputs["core_skill_application_summary.min.json"]["skills"]) == 1
    assert len(outputs["repeated_window_summary.min.json"]["windows"]) == 2
    assert len(outputs["route_progression_summary.min.json"]["routes"]) == 1
    assert len(outputs["fork_calibration_summary.min.json"]["routes"]) == 1
    assert outputs["session_growth_branch_summary.min.json"]["counts_by_recommended_next_skill"] == {
        "aoa-automation-opportunity-scan": 1,
        "aoa-session-route-forks": 1,
    }
    assert len(outputs["automation_pipeline_summary.min.json"]["pipelines"]) == 1
    assert outputs["automation_followthrough_summary.min.json"]["playbook_seed_candidate_count"] == 1
    assert outputs["automation_followthrough_summary.min.json"]["real_run_reviewed_count"] == 1
    assert outputs["codex_plane_deployment_summary.min.json"]["latest_rollout_state"] == "verified"
    assert outputs["codex_rollout_operations_summary.min.json"]["latest_state"] == "rolled_back"
    assert outputs["codex_rollout_operations_summary.min.json"]["counts_by_state"] == {
        "rolled_back": 1,
        "stabilized": 1,
    }
    assert outputs["codex_rollout_drift_summary.min.json"]["drift_window_ref"] == (
        "DRIFT-20260411-codex-hooks-tighten-02"
    )
    assert outputs["codex_rollout_drift_summary.min.json"]["rollback_required"] is True
    assert outputs["codex_plane_deployment_summary.min.json"]["trust_posture_counts"] == {
        "unknown": 0,
        "root_mismatch": 0,
        "config_inactive": 0,
        "trusted_ready": 1,
        "rollout_active": 0,
        "rollback_recommended": 0,
    }
    assert outputs["stress_recovery_window_summary.min.json"]["suppression"]["status"] == "low_sample"
    assert len(outputs["surface_detection_summary.min.json"]["windows"]) == 1
    assert outputs["core_skill_application_summary.min.json"]["skills"][0]["detail_event_kind_counts"] == {
        "diagnosis_packet_receipt": 1
    }
    catalog = outputs["summary_surface_catalog.min.json"]
    assert catalog["schema_version"] == "aoa_stats_summary_surface_catalog_v2"
    assert catalog["schema_ref"] == "schemas/summary-surface-catalog.schema.json"
    assert catalog["owner_repo"] == "aoa-stats"
    assert catalog["surface_kind"] == "runtime_surface"
    assert catalog["authority_ref"] == "docs/ARCHITECTURE.md"
    assert catalog["artifact_identity"]["artifact_class"] == "derived_observability_readmodel_catalog"
    assert catalog["artifact_identity"]["abi_epoch"] == "aoa_stats_summary_surface_catalog_v2"
    assert catalog["artifact_identity"]["contract_version"] == (
        "summary-surface-catalog.schema.json@aoa_stats_summary_surface_catalog_v2#artifact_identity"
    )
    assert catalog["artifact_identity"]["trust_layer"] == [
        "abi_contract_signature",
        "w3c_prov_lineage",
    ]
    assert catalog["surface_strength_model_ref"] == (
        "stats/surface-catalog/SURFACE_STRENGTH_MODEL.md"
    )
    assert catalog["validation_refs"] == [
        "scripts/build_views.py",
        "scripts/validate_repo.py",
        "tests/test_summary_surface_catalog.py",
    ]
    assert catalog["deferred_contract_surfaces"][0]["name"] == "antifragility_vector"
    assert [entry["surface_ref"] for entry in catalog["surfaces"]] == [
        "generated/core_skill_application_summary.min.json",
        "generated/object_summary.min.json",
        "generated/candidate_lineage_summary.min.json",
        "generated/supersession_drop_summary.min.json",
        "generated/repeated_window_summary.min.json",
        "generated/route_progression_summary.min.json",
        "generated/fork_calibration_summary.min.json",
        "generated/session_growth_branch_summary.min.json",
        "generated/automation_pipeline_summary.min.json",
        "generated/automation_followthrough_summary.min.json",
        "generated/codex_plane_deployment_summary.min.json",
        "generated/codex_rollout_operations_summary.min.json",
        "generated/codex_rollout_drift_summary.min.json",
        "generated/rollout_campaign_summary.min.json",
        "generated/drift_review_summary.min.json",
        "generated/continuity_window_summary.min.json",
        "generated/component_refresh_summary.min.json",
        "generated/memory_movement_summary.min.json",
        "generated/titan_incarnation_summary.min.json",
        "generated/stress_recovery_window_summary.min.json",
        "generated/source_coverage_summary.min.json",
        "generated/surface_detection_summary.min.json",
    ]
    assert {
        "owner_landing_summary",
        "runtime_closeout_summary",
        "titan_summon_summary",
    }.isdisjoint({
        entry["name"] for entry in catalog["surfaces"]
    })
    assert catalog["surfaces"][-2]["name"] == "source_coverage_summary"
    assert catalog["surfaces"][-2]["input_posture"] == "registry_backed_coverage_audit"


def test_build_all_views_skips_missing_optional_sibling_surfaces(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_views_module()
    receipts = module.load_receipts(
        [REPO_ROOT / "stats" / "intake-contract" / "examples" / "session_harvest_family.receipts.example.json"]
    )
    for env_name in (
        "AOA_8DIONYSUS_ROOT",
        "AOA_SDK_ROOT",
        "AOA_AGENTS_ROOT",
        "AOA_PLAYBOOKS_ROOT",
        "AOA_MEMO_ROOT",
    ):
        monkeypatch.setenv(env_name, str(tmp_path / env_name.lower()))

    outputs = module.build_all_views(receipts, ["stats/intake-contract/examples/session_harvest_family.receipts.example.json"])

    assert "codex_plane_deployment_summary.min.json" not in outputs
    assert "codex_rollout_operations_summary.min.json" not in outputs
    assert "codex_rollout_drift_summary.min.json" not in outputs
    assert "rollout_campaign_summary.min.json" not in outputs
    assert "drift_review_summary.min.json" not in outputs
    assert "continuity_window_summary.min.json" not in outputs
    assert "component_refresh_summary.min.json" not in outputs
    catalog_surface_refs = [
        entry["surface_ref"] for entry in outputs["summary_surface_catalog.min.json"]["surfaces"]
    ]
    assert "generated/codex_plane_deployment_summary.min.json" not in catalog_surface_refs
    assert "generated/continuity_window_summary.min.json" not in catalog_surface_refs
    assert "generated/component_refresh_summary.min.json" not in catalog_surface_refs

def test_build_all_views_uses_active_receipt_count_after_supersedes() -> None:
    module = load_build_views_module()
    receipts = [
        {
            "event_kind": "core_skill_application_receipt",
            "event_id": "evt-core-0001",
            "observed_at": "2026-04-06T13:00:00Z",
            "run_ref": "run-001",
            "session_ref": "session:test-active-count",
            "actor_ref": "aoa-skills:session-donor-harvest",
            "object_ref": {"repo": "aoa-skills", "kind": "skill", "id": "aoa-session-donor-harvest"},
            "evidence_refs": [{"kind": "receipt", "ref": "tmp/a.json"}],
            "payload": {
                "kernel_id": "project-core-session-growth-v1",
                "skill_name": "aoa-session-donor-harvest",
                "application_stage": "finish",
                "detail_event_kind": "harvest_packet_receipt",
                "detail_receipt_ref": "tmp/a.json",
            },
        },
        {
            "event_kind": "core_skill_application_receipt",
            "event_id": "evt-core-0002",
            "observed_at": "2026-04-06T13:01:00Z",
            "run_ref": "run-002",
            "session_ref": "session:test-active-count",
            "actor_ref": "aoa-skills:session-donor-harvest",
            "object_ref": {"repo": "aoa-skills", "kind": "skill", "id": "aoa-session-donor-harvest"},
            "evidence_refs": [{"kind": "receipt", "ref": "tmp/b.json"}],
            "payload": {
                "kernel_id": "project-core-session-growth-v1",
                "skill_name": "aoa-session-donor-harvest",
                "application_stage": "finish",
                "detail_event_kind": "harvest_packet_receipt",
                "detail_receipt_ref": "tmp/b.json",
            },
            "supersedes": "evt-core-0001",
        },
    ]

    outputs = module.build_all_views(receipts, ["memory"])

    assert outputs["core_skill_application_summary.min.json"]["generated_from"]["total_receipts"] == 1
    assert outputs["core_skill_application_summary.min.json"]["skills"][0]["application_count"] == 1
