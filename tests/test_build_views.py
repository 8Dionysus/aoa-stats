from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


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
        "owner_landing_summary.min.json",
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
        "titan_summon_summary.min.json",
        "runtime_closeout_summary.min.json",
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
    assert outputs["owner_landing_summary.min.json"]["owner_repo_counts"] == {
        "aoa-skills": 1,
    }
    assert outputs["owner_landing_summary.min.json"]["status_posture_counts"] == {
        "early": 1,
    }
    assert outputs["owner_landing_summary.min.json"]["landing_outcome_counts"] == {
        "landed_owner_status": 1,
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
    assert outputs["continuity_window_summary.min.json"]["continuity_ref"] == (
        "CONT-20260412-architect-01"
    )
    assert outputs["continuity_window_summary.min.json"]["current_status"] == "active"
    assert outputs["continuity_window_summary.min.json"]["open_revision_windows"] == 1
    assert outputs["continuity_window_summary.min.json"]["drift_flags"] == []
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
    assert len(outputs["runtime_closeout_summary.min.json"]["closeouts"]) == 1
    assert outputs["stress_recovery_window_summary.min.json"]["suppression"]["status"] == "low_sample"
    assert outputs["source_coverage_summary.min.json"]["source_mode"] == "registry_backed_receipt_feed"
    assert outputs["source_coverage_summary.min.json"]["missing_owner_repos"] == [
        "aoa-memo",
        "aoa-playbooks",
        "aoa-techniques",
    ]
    assert outputs["source_coverage_summary.min.json"]["unexpected_owner_repos"] == ["Dionysus"]
    assert outputs["source_coverage_summary.min.json"]["owner_repo_counts"]["aoa-skills"] == 12
    assert len(outputs["surface_detection_summary.min.json"]["windows"]) == 1
    assert outputs["core_skill_application_summary.min.json"]["skills"][0]["detail_event_kind_counts"] == {
        "diagnosis_packet_receipt": 1
    }
    assert outputs["runtime_closeout_summary.min.json"]["closeouts"][0]["wave_id"] == "W2"
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
    assert catalog["surface_strength_model_ref"] == "docs/SURFACE_STRENGTH_MODEL.md"
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
        "generated/owner_landing_summary.min.json",
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
        "generated/titan_summon_summary.min.json",
        "generated/runtime_closeout_summary.min.json",
        "generated/stress_recovery_window_summary.min.json",
        "generated/source_coverage_summary.min.json",
        "generated/surface_detection_summary.min.json",
    ]
    assert catalog["surfaces"][-2]["name"] == "source_coverage_summary"
    assert catalog["surfaces"][-2]["input_posture"] == "registry_backed_coverage_audit"


def test_continuity_window_summary_stays_derived_and_non_sovereign() -> None:
    module = load_build_views_module()

    summary = module.build_continuity_window_summary()

    assert summary["schema_version"] == "aoa_stats_continuity_window_summary_v1"
    assert summary["generated_from"]["receipt_input_paths"] == [
        "aoa-agents/mechanics/checkpoint/parts/continuity-lane/examples/self-agency-continuity-window.example.json",
        "aoa-playbooks/playbooks/continuity/session-growth/self-agency-continuity-cycle/PLAYBOOK.md",
        "aoa-memo/mechanics/writeback/parts/growth-and-continuity/examples/provenance_thread.self-agency-continuity.example.json",
        "aoa-evals/generated/eval_catalog.min.json",
    ]
    assert summary["current_status"] == "active"
    assert summary["successful_reanchors"] == 0
    assert summary["failed_reanchors"] == 0
    assert summary["last_anchor_artifact_ref"] == (
        "artifact:verification_result:AOA-VERIFY-20260412-0001"
    )
    assert summary["bounded_revision_count"] == 1


def test_component_refresh_summary_stays_derived_and_non_sovereign(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_views_module()
    sdk_root = tmp_path / ".deps" / "aoa-sdk"
    examples_root = (
        sdk_root
        / "mechanics"
        / "checkpoint"
        / "parts"
        / "reviewed-closeout-context-carry"
        / "examples"
    )
    examples_root.mkdir(parents=True)
    (examples_root / "component_drift_hints.example.json").write_text(
        json.dumps(
            {
                "schema_version": "aoa_component_drift_hint_set_v1",
                "session_ref": "session:component-refresh-test",
                "repo_root": "/srv/AbyssOS",
                "hints": [
                    {
                        "hint_ref": "hint:root",
                        "component_ref": "component:codex-plane:shared-root",
                        "owner_repo": "8Dionysus",
                        "observed_at": "2026-04-12T16:20:00Z",
                        "observed_by": "workspace_root",
                        "severity": "medium",
                        "signals": [
                            "doctor_fail_after_render",
                            "same_hand_patch_repeated"
                        ],
                        "repeat_count": 2,
                        "evidence_refs": ["artifact:root"],
                        "recommended_route_class": "regenerate",
                        "review_required": True
                    },
                    {
                        "hint_ref": "hint:stats",
                        "component_ref": "component:stats-derived-summaries:growth-refinery",
                        "owner_repo": "aoa-stats",
                        "observed_at": "2026-04-12T16:31:00Z",
                        "observed_by": "stats_reread",
                        "severity": "high",
                        "signals": [
                            "latest_observed_at_stale",
                            "summary_family_out_of_sync"
                        ],
                        "repeat_count": 1,
                        "evidence_refs": ["artifact:stats"],
                        "recommended_route_class": "rebuild",
                        "review_required": True
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (examples_root / "component_refresh_followthrough_decision.example.json").write_text(
        json.dumps(
            {
                "schema_version": "aoa_component_refresh_followthrough_decision_set_v1",
                "decision_ref": "decision:test",
                "reviewed": True,
                "session_ref": "session:component-refresh-test",
                "decisions": [
                    {
                        "component_ref": "component:codex-plane:shared-root",
                        "owner_repo": "8Dionysus",
                        "route_class": "regenerate",
                        "decision_status": "chosen",
                        "selected_refresh_path": ["python root.py"],
                        "reason": "root drift",
                        "evidence_refs": ["hint:root"],
                        "rollback_anchor": "docs/CODEX_PLANE_ROLLOUT.md",
                        "stats_should_refresh": True,
                        "memo_writeback_candidate": False
                    },
                    {
                        "component_ref": "component:stats-derived-summaries:growth-refinery",
                        "owner_repo": "aoa-stats",
                        "route_class": "rebuild",
                        "decision_status": "chosen",
                        "selected_refresh_path": ["python scripts/build_views.py"],
                        "reason": "stale summary",
                        "evidence_refs": ["hint:stats"],
                        "rollback_anchor": "docs/ARCHITECTURE.md",
                        "stats_should_refresh": True,
                        "memo_writeback_candidate": True
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("AOA_SDK_ROOT", str(sdk_root))

    summary = module.build_component_refresh_summary()

    assert summary["schema_version"] == "aoa_stats_component_refresh_summary_v1"
    assert summary["generated_from"]["receipt_input_paths"] == [
        "aoa-sdk/mechanics/checkpoint/parts/reviewed-closeout-context-carry/examples/component_drift_hints.example.json",
        "aoa-sdk/mechanics/checkpoint/parts/reviewed-closeout-context-carry/examples/component_refresh_followthrough_decision.example.json",
    ]
    assert summary["generated_from"]["total_receipts"] == 2
    assert summary["owner_repo_counts"] == {"8Dionysus": 1, "aoa-stats": 1}
    assert summary["status_counts"] == {
        "refresh_recommended": 1,
        "refresh_active": 1,
        "current": 0,
        "deferred": 0,
        "recovered": 0,
    }
    assert summary["drift_class_counts"] == {
        "doctor_drift": 1,
        "family_drift": 1,
        "manual_repeat": 1,
        "root_drift": 1,
        "staleness_window": 1,
    }


def test_component_refresh_summary_rejects_empty_hint_evidence_refs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_views_module()
    sdk_root = tmp_path / ".deps" / "aoa-sdk"
    examples_root = (
        sdk_root
        / "mechanics"
        / "checkpoint"
        / "parts"
        / "reviewed-closeout-context-carry"
        / "examples"
    )
    examples_root.mkdir(parents=True)
    (examples_root / "component_drift_hints.example.json").write_text(
        json.dumps(
            {
                "schema_version": "aoa_component_drift_hint_set_v1",
                "session_ref": "session:component-refresh-test",
                "repo_root": "/srv/AbyssOS",
                "hints": [
                    {
                        "hint_ref": "hint:root",
                        "component_ref": "component:codex-plane:shared-root",
                        "owner_repo": "8Dionysus",
                        "observed_at": "2026-04-12T16:20:00Z",
                        "observed_by": "workspace_root",
                        "severity": "medium",
                        "signals": ["doctor_fail_after_render"],
                        "repeat_count": 1,
                        "evidence_refs": [],
                        "recommended_route_class": "regenerate",
                        "review_required": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (examples_root / "component_refresh_followthrough_decision.example.json").write_text(
        json.dumps(
            {
                "schema_version": "aoa_component_refresh_followthrough_decision_set_v1",
                "decision_ref": "decision:test",
                "reviewed": True,
                "session_ref": "session:component-refresh-test",
                "decisions": [
                    {
                        "component_ref": "component:codex-plane:shared-root",
                        "owner_repo": "8Dionysus",
                        "route_class": "regenerate",
                        "decision_status": "chosen",
                        "selected_refresh_path": ["python root.py"],
                        "reason": "root drift",
                        "evidence_refs": ["hint:root"],
                        "rollback_anchor": "docs/CODEX_PLANE_ROLLOUT.md",
                        "stats_should_refresh": True,
                        "memo_writeback_candidate": False,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("AOA_SDK_ROOT", str(sdk_root))

    with pytest.raises(module.ReceiptValidationError, match="must expose at least one evidence_ref"):
        module.build_component_refresh_summary()


def test_component_refresh_summary_rejects_duplicate_decisions_for_component(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_views_module()
    sdk_root = tmp_path / ".deps" / "aoa-sdk"
    examples_root = (
        sdk_root
        / "mechanics"
        / "checkpoint"
        / "parts"
        / "reviewed-closeout-context-carry"
        / "examples"
    )
    examples_root.mkdir(parents=True)
    (examples_root / "component_drift_hints.example.json").write_text(
        json.dumps(
            {
                "schema_version": "aoa_component_drift_hint_set_v1",
                "session_ref": "session:component-refresh-test",
                "repo_root": "/srv/AbyssOS",
                "hints": [
                    {
                        "hint_ref": "hint:root",
                        "component_ref": "component:codex-plane:shared-root",
                        "owner_repo": "8Dionysus",
                        "observed_at": "2026-04-12T16:20:00Z",
                        "observed_by": "workspace_root",
                        "severity": "medium",
                        "signals": ["doctor_fail_after_render"],
                        "repeat_count": 1,
                        "evidence_refs": ["artifact:root"],
                        "recommended_route_class": "regenerate",
                        "review_required": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (examples_root / "component_refresh_followthrough_decision.example.json").write_text(
        json.dumps(
            {
                "schema_version": "aoa_component_refresh_followthrough_decision_set_v1",
                "decision_ref": "decision:test",
                "reviewed": True,
                "session_ref": "session:component-refresh-test",
                "decisions": [
                    {
                        "component_ref": "component:codex-plane:shared-root",
                        "owner_repo": "8Dionysus",
                        "route_class": "regenerate",
                        "decision_status": "chosen",
                        "selected_refresh_path": ["python root.py"],
                        "reason": "root drift",
                        "evidence_refs": ["hint:root"],
                        "rollback_anchor": "docs/CODEX_PLANE_ROLLOUT.md",
                        "stats_should_refresh": True,
                        "memo_writeback_candidate": False,
                    },
                    {
                        "component_ref": "component:codex-plane:shared-root",
                        "owner_repo": "8Dionysus",
                        "route_class": "repair",
                        "decision_status": "deferred",
                        "selected_refresh_path": ["python repair.py"],
                        "reason": "contradictory duplicate",
                        "evidence_refs": ["hint:root"],
                        "rollback_anchor": "docs/CODEX_PLANE_ROLLOUT.md",
                        "stats_should_refresh": False,
                        "memo_writeback_candidate": False,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("AOA_SDK_ROOT", str(sdk_root))

    with pytest.raises(module.ReceiptValidationError, match="must not duplicate component_ref"):
        module.build_component_refresh_summary()


def test_component_refresh_summary_uses_null_freshness_for_decision_only_component(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_views_module()
    sdk_root = tmp_path / ".deps" / "aoa-sdk"
    examples_root = (
        sdk_root
        / "mechanics"
        / "checkpoint"
        / "parts"
        / "reviewed-closeout-context-carry"
        / "examples"
    )
    examples_root.mkdir(parents=True)
    (examples_root / "component_drift_hints.example.json").write_text(
        json.dumps(
            {
                "schema_version": "aoa_component_drift_hint_set_v1",
                "session_ref": "session:component-refresh-test",
                "repo_root": "/srv/AbyssOS",
                "hints": [
                    {
                        "hint_ref": "hint:other",
                        "component_ref": "component:other",
                        "owner_repo": "repo-other",
                        "observed_at": "2026-04-12T10:00:00Z",
                        "observed_by": "workspace_root",
                        "severity": "medium",
                        "signals": ["doctor_fail_after_render"],
                        "repeat_count": 1,
                        "evidence_refs": ["artifact:other"],
                        "recommended_route_class": "regenerate",
                        "review_required": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (examples_root / "component_refresh_followthrough_decision.example.json").write_text(
        json.dumps(
            {
                "schema_version": "aoa_component_refresh_followthrough_decision_set_v1",
                "decision_ref": "decision:test",
                "reviewed": True,
                "session_ref": "session:component-refresh-test",
                "decisions": [
                    {
                        "component_ref": "component:no-hint",
                        "owner_repo": "repo-no-hint",
                        "route_class": "repair",
                        "decision_status": "chosen",
                        "selected_refresh_path": ["python repair.py"],
                        "reason": "reviewed decision exists without a matching per-component hint",
                        "evidence_refs": ["hint:other"],
                        "rollback_anchor": "docs/ROLLBACK.md",
                        "stats_should_refresh": True,
                        "memo_writeback_candidate": False,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("AOA_SDK_ROOT", str(sdk_root))

    summary = module.build_component_refresh_summary()
    schema = json.loads((REPO_ROOT / "schemas" / "component-refresh-summary.schema.json").read_text(encoding="utf-8"))
    decision_only = next(
        component for component in summary["components"] if component["component_ref"] == "component:no-hint"
    )

    Draft202012Validator(schema).validate(summary)
    assert summary["generated_from"]["latest_observed_at"] == "2026-04-12T10:00:00Z"
    assert decision_only["latest_decision_status"] == "chosen"
    assert decision_only["current_status"] == "refresh_active"
    assert decision_only["latest_route_class"] == "repair"
    assert decision_only["latest_observed_at"] is None


def test_component_refresh_summary_accepts_decision_evidence_without_hint_ref(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_views_module()
    sdk_root = tmp_path / ".deps" / "aoa-sdk"
    examples_root = (
        sdk_root
        / "mechanics"
        / "checkpoint"
        / "parts"
        / "reviewed-closeout-context-carry"
        / "examples"
    )
    examples_root.mkdir(parents=True)
    (examples_root / "component_drift_hints.example.json").write_text(
        json.dumps(
            {
                "schema_version": "aoa_component_drift_hint_set_v1",
                "session_ref": "session:component-refresh-test",
                "repo_root": "/srv/AbyssOS",
                "hints": [
                    {
                        "hint_ref": "hint:root",
                        "component_ref": "component:codex-plane:shared-root",
                        "owner_repo": "8Dionysus",
                        "observed_at": "2026-04-12T16:20:00Z",
                        "observed_by": "workspace_root",
                        "severity": "medium",
                        "signals": ["doctor_fail_after_render"],
                        "repeat_count": 1,
                        "evidence_refs": ["artifact:root"],
                        "recommended_route_class": "regenerate",
                        "review_required": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (examples_root / "component_refresh_followthrough_decision.example.json").write_text(
        json.dumps(
            {
                "schema_version": "aoa_component_refresh_followthrough_decision_set_v1",
                "decision_ref": "decision:test",
                "reviewed": True,
                "session_ref": "session:component-refresh-test",
                "decisions": [
                    {
                        "component_ref": "component:codex-plane:shared-root",
                        "owner_repo": "8Dionysus",
                        "route_class": "regenerate",
                        "decision_status": "chosen",
                        "selected_refresh_path": ["python root.py"],
                        "reason": "decision cites review evidence, not a route hint id",
                        "evidence_refs": ["repo:8Dionysus/docs/review.md"],
                        "rollback_anchor": "docs/CODEX_PLANE_ROLLOUT.md",
                        "stats_should_refresh": True,
                        "memo_writeback_candidate": False,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("AOA_SDK_ROOT", str(sdk_root))

    summary = module.build_component_refresh_summary()

    assert summary["components"][0]["latest_decision_status"] == "chosen"


def test_codex_plane_generated_from_uses_canonical_repo_labels(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_views_module()
    public_profile_root = tmp_path / ".deps" / "8Dionysus"
    sdk_root = tmp_path / ".deps" / "aoa-sdk"
    (public_profile_root / "examples").mkdir(parents=True)
    deploy_status_root = (
        sdk_root
        / "mechanics"
        / "codex-projection"
        / "parts"
        / "live-rollout-status-readout"
        / "examples"
    )
    deploy_status_root.mkdir(parents=True)
    (public_profile_root / "examples" / "codex_plane_trust_state.example.json").write_text(
        json.dumps(
            {
                "trust_state_id": "trust-1",
                "trust_posture": "trusted_ready",
                "captured_at": "2026-04-11T21:04:00Z",
            }
        ),
        encoding="utf-8",
    )
    (deploy_status_root / "live-rollout-status-snapshot.example.json").write_text(
        json.dumps(
            {
                "latest_trust_state_ref": "trust-1",
                "latest_rollout_receipt_ref": "receipt-1",
                "rollout_state": "verified",
                "observed_at": "2026-04-11T21:06:00Z",
            }
        ),
        encoding="utf-8",
    )
    (public_profile_root / "examples" / "codex_plane_rollout_receipt.example.json").write_text(
        json.dumps(
            {
                "rollout_receipt_id": "receipt-1",
                "verified_at": "2026-04-11T21:07:00Z",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("AOA_8DIONYSUS_ROOT", str(public_profile_root))
    monkeypatch.setenv("AOA_SDK_ROOT", str(sdk_root))

    source, _, _, _ = module.codex_plane_generated_from()

    assert source["receipt_input_paths"] == [
        "8Dionysus/examples/codex_plane_trust_state.example.json",
        "aoa-sdk/mechanics/codex-projection/parts/live-rollout-status-readout/examples/live-rollout-status-snapshot.example.json",
        "8Dionysus/examples/codex_plane_rollout_receipt.example.json",
    ]


def test_codex_trusted_rollout_generated_from_uses_any_parseable_timestamp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_views_module()
    public_profile_root = tmp_path / ".deps" / "8Dionysus"
    rollout_root = public_profile_root / "generated" / "codex" / "rollout"
    rollout_root.mkdir(parents=True)
    (rollout_root / "deploy_history.jsonl").write_text(
        json.dumps(
            {
                "rollout_campaign_ref": "ROLL-20260412-codex-plane-regen-03",
                "state": "prepared",
                "activated_at": "",
                "summary": "prepared rollout without activation timestamp yet",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (rollout_root / "regeneration_campaigns.min.json").write_text(
        json.dumps(
            {
                "campaigns": [
                    {
                        "rollout_campaign_ref": "ROLL-20260412-codex-plane-regen-03",
                        "state": "prepared",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (rollout_root / "rollback_windows.min.json").write_text(
        json.dumps(
            {
                "rollback_windows": [
                    {
                        "rollback_window_ref": "RBK-20260412-codex-plane-regen-03",
                        "opened_at": "2026-04-12T20:30:00Z",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (rollout_root / "rollout_latest.min.json").write_text(
        json.dumps(
            {
                "latest_rollout_campaign_ref": "ROLL-20260412-codex-plane-regen-03",
                "latest_state": "prepared",
                "latest_stable_rollout_campaign_ref": "ROLL-20260411-codex-plane-regen-01",
                "source_refs": [
                    "generated/codex/rollout/deploy_history.jsonl",
                    "generated/codex/rollout/regeneration_campaigns.min.json",
                    "generated/codex/rollout/rollback_windows.min.json",
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("AOA_8DIONYSUS_ROOT", str(public_profile_root))

    source, _, _, _, _ = module.codex_trusted_rollout_generated_from()

    assert source["latest_observed_at"] == "2026-04-12T20:30:00Z"


def test_codex_rollout_drift_summary_uses_history_row_matching_latest_campaign_ref(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_views_module()
    public_profile_root = tmp_path / ".deps" / "8Dionysus"
    rollout_root = public_profile_root / "generated" / "codex" / "rollout"
    rollout_root.mkdir(parents=True)
    (rollout_root / "deploy_history.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "rollout_campaign_ref": "ROLL-20260412-codex-hooks-tighten-02",
                        "state": "rolled_back",
                        "activated_at": "2026-04-12T21:00:00Z",
                        "drift_window_refs": ["DRIFT-20260412-codex-hooks-tighten-02"],
                        "rollback_window_refs": ["RBK-20260412-codex-hooks-tighten-02"],
                        "drift_state": "rolled_back",
                        "repair_attempted": True,
                    }
                ),
                json.dumps(
                    {
                        "rollout_campaign_ref": "ROLL-20260411-codex-plane-regen-01",
                        "state": "stabilized",
                        "activated_at": "2026-04-11T21:00:00Z",
                        "drift_window_refs": ["DRIFT-20260411-codex-plane-regen-01"],
                        "rollback_window_refs": [],
                        "drift_state": "quiet",
                        "repair_attempted": False,
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (rollout_root / "regeneration_campaigns.min.json").write_text(
        json.dumps({"campaigns": [{"rollout_campaign_ref": "ROLL-20260412-codex-hooks-tighten-02"}]}),
        encoding="utf-8",
    )
    (rollout_root / "rollback_windows.min.json").write_text(
        json.dumps(
            {
                "rollback_windows": [
                    {
                        "rollback_window_ref": "RBK-20260412-codex-hooks-tighten-02",
                        "closed_at": "2026-04-12T21:30:00Z",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (rollout_root / "rollout_latest.min.json").write_text(
        json.dumps(
            {
                "latest_rollout_campaign_ref": "ROLL-20260412-codex-hooks-tighten-02",
                "latest_state": "rolled_back",
                "latest_stable_rollout_campaign_ref": "ROLL-20260411-codex-plane-regen-01",
                "source_refs": [
                    "generated/codex/rollout/deploy_history.jsonl",
                    "generated/codex/rollout/regeneration_campaigns.min.json",
                    "generated/codex/rollout/rollback_windows.min.json",
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("AOA_8DIONYSUS_ROOT", str(public_profile_root))

    summary = module.build_codex_rollout_drift_summary()

    assert summary["latest_rollout_campaign_ref"] == "ROLL-20260412-codex-hooks-tighten-02"
    assert summary["drift_window_ref"] == "DRIFT-20260412-codex-hooks-tighten-02"
    assert summary["drift_state"] == "rolled_back"
    assert summary["rollback_required"] is True


def test_drift_review_summary_keeps_decision_counts_empty_when_decision_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_views_module()
    public_profile_root = tmp_path / ".deps" / "8Dionysus"
    examples_root = public_profile_root / "examples"
    examples_root.mkdir(parents=True)
    campaign = {
        "campaign_ref": "ROLL-20260412-codex-hooks-tighten-02",
        "state": "review_required",
        "window_opened_at": "2026-04-12T20:00:00Z",
        "lineage_refs": {"candidate_refs": ["candidate:rollout:hooks-tighten-02"]},
    }
    review = {
        "review_ref": "DRIFT-20260412-codex-hooks-tighten-02",
        "status": "review_required",
        "reviewed_at": "2026-04-12T20:15:00Z",
        "signals": {"doctor_clean": True, "hooks_active": False},
    }
    rollback = {
        "rollback_ref": "RBK-20260412-codex-hooks-tighten-02",
        "status": "ready_if_needed",
        "prepared_at": "2026-04-12T20:30:00Z",
    }
    (examples_root / "rollout_campaign_window.example.json").write_text(
        json.dumps(campaign), encoding="utf-8"
    )
    (examples_root / "drift_review_window.example.json").write_text(
        json.dumps(review), encoding="utf-8"
    )
    (examples_root / "rollback_followthrough_window.example.json").write_text(
        json.dumps(rollback), encoding="utf-8"
    )

    monkeypatch.setenv("AOA_8DIONYSUS_ROOT", str(public_profile_root))

    summary = module.build_drift_review_summary()

    assert summary["decision_counts"] == {}


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


def test_component_refresh_summary_selects_latest_hint_per_component(monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_build_views_module()

    def fake_generated_from():
        source = {
            "receipt_input_paths": ["hints", "decisions"],
            "total_receipts": 2,
            "latest_observed_at": "2026-04-12T16:20:00Z",
        }
        hints = [
            {
                "hint_ref": "hint:old",
                "component_ref": "component:test",
                "owner_repo": "aoa-stats",
                "observed_at": "2026-04-12T16:00:00Z",
                "recommended_route_class": "observe",
                "signals": ["missing_projection"],
            },
            {
                "hint_ref": "hint:new",
                "component_ref": "component:test",
                "owner_repo": "aoa-stats",
                "observed_at": "2026-04-12T16:20:00Z",
                "recommended_route_class": "repair",
                "signals": ["missing_projection"],
            },
        ]
        return source, hints, []

    monkeypatch.setattr(module, "component_refresh_generated_from", fake_generated_from)

    summary = module.build_component_refresh_summary()

    assert summary["components"] == [
        {
            "component_ref": "component:test",
            "owner_repo": "aoa-stats",
            "latest_decision_status": "unreviewed",
            "current_status": "refresh_recommended",
            "latest_route_class": "repair",
            "latest_observed_at": "2026-04-12T16:20:00Z",
        }
    ]


def test_stress_recovery_window_summary_resolves_eval_report_ref(tmp_path: Path) -> None:
    module = load_build_views_module()
    evals_root = tmp_path / "aoa-evals"
    report_path = (
        evals_root
        / "bundles"
        / "aoa-stress-recovery-window"
        / "reports"
        / "example-report.json"
    )
    report_path.parent.mkdir(parents=True)
    report_path.write_text(
        json.dumps(
            {
                "eval_name": "aoa-stress-recovery-window",
                "bundle_status": "draft",
                "object_under_evaluation": "ordered stress recovery posture on one named owner surface and adjacent evidence family",
                "comparison_mode": "longitudinal-window",
                "report_id": "eval-stress-window-test",
                "generated_at_utc": "2026-04-07T18:00:00Z",
                "window": {
                    "label": "window-test",
                    "start_utc": "2026-04-01T00:00:00Z",
                    "end_utc": "2026-04-07T00:00:00Z"
                },
                "scope": {
                    "stressor_family": "hybrid-query-kag-unhealthy",
                    "repo_roots": [
                        "ATM10-Agent",
                        "aoa-routing",
                        "aoa-memo"
                    ],
                    "owner_surface": "hybrid-query",
                    "surface_family": "kag-regrounding"
                },
                "inputs": {
                    "source_receipt_refs": [
                        "r1",
                        "r2"
                    ],
                    "handoff_refs": [
                        "h1"
                    ],
                    "playbook_lane_refs": [
                        "p1"
                    ],
                    "reentry_gate_refs": [
                        "g1"
                    ],
                    "projection_health_refs": [
                        "ph1"
                    ],
                    "regrounding_ticket_refs": [
                        "rt1"
                    ],
                    "route_hint_refs": [
                        "route1"
                    ],
                    "memo_context_refs": [
                        "memo1"
                    ]
                },
                "axes": {
                    "handoff_fidelity": {
                        "status": "pass",
                        "score": 0.9,
                        "rationale": "ok"
                    },
                    "route_discipline": {
                        "status": "pass",
                        "score": 0.88,
                        "rationale": "ok"
                    },
                    "reentry_quality": {
                        "status": "warn",
                        "score": 0.72,
                        "rationale": "ok"
                    },
                    "regrounding_effectiveness": {
                        "status": "warn",
                        "score": 0.69,
                        "rationale": "ok"
                    },
                    "evidence_continuity": {
                        "status": "pass",
                        "score": 0.91,
                        "rationale": "ok"
                    },
                    "false_promotion_prevention": {
                        "status": "pass",
                        "score": 0.93,
                        "rationale": "ok"
                    },
                    "operator_burden": {
                        "status": "warn",
                        "score": 0.64,
                        "rationale": "ok"
                    },
                    "trust_calibration": {
                        "status": "pass",
                        "score": 0.89,
                        "rationale": "ok"
                    }
                },
                "overall_posture": "mixed",
                "blind_spots": [
                    "one"
                ],
                "evidence_gaps": [
                    "two"
                ]
            },
            indent=2
        )
        + "\n",
        encoding="utf-8",
    )
    receipts = [
        {
            "event_kind": "eval_result_receipt",
            "event_id": "evt-stress-window-0001",
            "observed_at": "2026-04-07T18:01:00Z",
            "run_ref": "run-stress-window-001",
            "session_ref": "session:test-stress-window",
            "actor_ref": "aoa-evals:reviewer",
            "object_ref": {
                "repo": "aoa-evals",
                "kind": "eval_bundle",
                "id": "aoa-stress-recovery-window",
                "version": "draft"
            },
            "evidence_refs": [
                {
                    "kind": "bundle_report",
                    "ref": "repo:aoa-evals/bundles/aoa-stress-recovery-window/reports/example-report.json"
                }
            ],
            "payload": {
                "eval_name": "aoa-stress-recovery-window",
                "report_ref": "repo:aoa-evals/bundles/aoa-stress-recovery-window/reports/example-report.json"
            }
        }
    ]

    summary = module.build_stress_recovery_window_summary(
        receipts,
        {
            "receipt_input_paths": [
                "memory"
            ],
            "total_receipts": 1,
            "latest_observed_at": "2026-04-07T18:01:00Z"
        },
        evals_root=evals_root,
    )

    assert summary["suppression"]["status"] == "none"
    assert summary["scope"]["stressor_family"] == "hybrid-query-kag-unhealthy"
    assert summary["inputs"]["eval_report_refs"] == [
        "repo:aoa-evals/bundles/aoa-stress-recovery-window/reports/example-report.json"
    ]
    assert summary["summary"]["containment"] == 0.9
    assert summary["summary"]["adaptation_followthrough"] == 0.68


def test_stress_recovery_window_summary_suppresses_when_report_ref_is_missing(tmp_path: Path) -> None:
    module = load_build_views_module()
    receipts = [
        {
            "event_kind": "eval_result_receipt",
            "event_id": "evt-stress-window-0002",
            "observed_at": "2026-04-07T18:05:00Z",
            "run_ref": "run-stress-window-002",
            "session_ref": "session:test-stress-window-missing",
            "actor_ref": "aoa-evals:reviewer",
            "object_ref": {
                "repo": "aoa-evals",
                "kind": "eval_bundle",
                "id": "aoa-stress-recovery-window",
                "version": "draft"
            },
            "evidence_refs": [],
            "payload": {
                "eval_name": "aoa-stress-recovery-window",
                "report_ref": "repo:aoa-evals/bundles/aoa-stress-recovery-window/reports/missing-report.json"
            }
        }
    ]

    summary = module.build_stress_recovery_window_summary(
        receipts,
        {
            "receipt_input_paths": [
                "memory"
            ],
            "total_receipts": 1,
            "latest_observed_at": "2026-04-07T18:05:00Z"
        },
        evals_root=tmp_path / "aoa-evals",
    )

    assert summary["suppression"]["status"] == "insufficient_evidence"
    assert summary["summary"]["containment"] is None


def test_stress_recovery_window_summary_suppresses_on_malformed_report_json(tmp_path: Path) -> None:
    module = load_build_views_module()
    evals_root = tmp_path / "aoa-evals"
    report_path = (
        evals_root
        / "bundles"
        / "aoa-stress-recovery-window"
        / "reports"
        / "broken-report.json"
    )
    report_path.parent.mkdir(parents=True)
    report_path.write_text("{not valid json}\n", encoding="utf-8")
    receipts = [
        {
            "event_kind": "eval_result_receipt",
            "event_id": "evt-stress-window-0003",
            "observed_at": "2026-04-07T18:07:00Z",
            "run_ref": "run-stress-window-003",
            "session_ref": "session:test-stress-window-broken",
            "actor_ref": "aoa-evals:reviewer",
            "object_ref": {
                "repo": "aoa-evals",
                "kind": "eval_bundle",
                "id": "aoa-stress-recovery-window",
                "version": "draft",
            },
            "evidence_refs": [],
            "payload": {
                "eval_name": "aoa-stress-recovery-window",
                "report_ref": "repo:aoa-evals/bundles/aoa-stress-recovery-window/reports/broken-report.json",
            },
        }
    ]

    summary = module.build_stress_recovery_window_summary(
        receipts,
        {
            "receipt_input_paths": ["memory"],
            "total_receipts": 1,
            "latest_observed_at": "2026-04-07T18:07:00Z",
        },
        evals_root=evals_root,
    )

    assert summary["suppression"]["status"] == "insufficient_evidence"
    assert summary["summary"]["containment"] is None


def test_antifragility_vector_schema_requires_nonempty_source_refs() -> None:
    schema = json.loads(
        (
            REPO_ROOT
            / "mechanics"
            / "antifragility"
            / "parts"
            / "antifragility-vector"
            / "schemas"
            / "antifragility_vector_v1.json"
        ).read_text(encoding="utf-8")
    )
    payload = json.loads(
        (
            REPO_ROOT
            / "mechanics"
            / "antifragility"
            / "parts"
            / "antifragility-vector"
            / "examples"
            / "antifragility_vector.example.json"
        ).read_text(encoding="utf-8")
    )
    payload["inputs"]["receipt_refs"] = []
    payload["inputs"]["eval_report_refs"] = []

    errors = list(Draft202012Validator(schema).iter_errors(payload))

    assert any(list(error.absolute_path) == ["inputs", "receipt_refs"] for error in errors)
    assert any(list(error.absolute_path) == ["inputs", "eval_report_refs"] for error in errors)


def test_surface_detection_summary_tracks_second_wave_observability_signals() -> None:
    module = load_build_views_module()
    receipts = [
        {
            "event_kind": "core_skill_application_receipt",
            "event_id": "evt-surface-obs-0001",
            "observed_at": "2026-04-06T20:20:00Z",
            "run_ref": "run-surface-obs-001",
            "session_ref": "session:test-surface-obs",
            "actor_ref": "aoa-skills:session-donor-harvest",
            "object_ref": {
                "repo": "aoa-skills",
                "kind": "skill",
                "id": "aoa-session-donor-harvest",
                "version": "main",
            },
            "evidence_refs": [
                {"kind": "receipt", "ref": "repo:aoa-skills/tmp/HARVEST_PACKET_RECEIPT.json"}
            ],
            "payload": {
                "kernel_id": "project-core-session-growth-v1",
                "skill_name": "aoa-session-donor-harvest",
                "application_stage": "finish",
                "detail_event_kind": "harvest_packet_receipt",
                "detail_receipt_ref": "repo:aoa-skills/tmp/HARVEST_PACKET_RECEIPT.json",
                "surface_detection_context": {
                    "activation_truth": "manual-equivalent-adjacent",
                    "adjacent_owner_repos": ["aoa-playbooks", "aoa-techniques"],
                    "owner_layer_ambiguity": True,
                    "family_entry_refs": [
                        "aoa-playbooks.playbook_registry.min",
                        "aoa-techniques.technique_promotion_readiness.min"
                    ],
                    "candidate_counts": {
                        "candidate_now": 1,
                        "candidate_later": 2
                    },
                    "suggested_handoff_targets": [
                        "aoa-session-donor-harvest",
                        "aoa-quest-harvest"
                    ],
                    "repeated_pattern_signal": True,
                    "promotion_discussion_required": True
                },
            },
        }
    ]

    summary = module.build_surface_detection_summary(
        receipts, {"receipt_input_paths": ["memory"], "total_receipts": len(receipts)}
    )

    window = summary["windows"][0]
    assert window["manual_equivalent_adjacent_count"] == 1
    assert window["activated_count"] == 0
    assert window["candidate_now_count"] == 1
    assert window["candidate_later_count"] == 2
    assert window["owner_layer_ambiguity_count"] == 1
    assert window["adjacent_owner_repo_counts"] == {
        "aoa-playbooks": 1,
        "aoa-techniques": 1,
    }
    assert window["handoff_target_counts"] == {
        "aoa-quest-harvest": 1,
        "aoa-session-donor-harvest": 1,
    }
    assert window["repeated_pattern_signal_count"] == 1
    assert window["promotion_discussion_count"] == 1


def test_validate_receipt_accepts_known_unsummarized_event_kind() -> None:
    module = load_build_views_module()
    for event_kind, actor_ref, object_kind, object_id in (
        (
            "memo_writeback_receipt",
            "aoa-memo:writeback",
            "memory_object",
            "memo.test.known-kind",
        ),
        (
            "memo_growth_writeback_receipt",
            "aoa-memo:growth-refinery-writeback",
            "support_memory",
            "memo:test-growth-known-kind",
        ),
    ):
        receipt = {
            "event_kind": event_kind,
            "event_id": f"evt-{event_kind}-0001",
            "observed_at": "2026-04-06T09:00:00Z",
            "run_ref": "run-memo-001",
            "session_ref": "session:test-known-kind",
            "actor_ref": actor_ref,
            "object_ref": {
                "repo": "aoa-memo",
                "kind": object_kind,
                "id": object_id,
                "version": "main",
            },
            "evidence_refs": [{"kind": "memory_object", "ref": "repo:aoa-memo/generated/memory_object_catalog.min.json"}],
            "payload": {"target_kind": "decision"},
        }

        module.validate_receipt(receipt, location="memory")


def test_validate_receipt_rejects_unknown_event_kind_with_canonical_ref() -> None:
    module = load_build_views_module()
    receipt = {
        "event_kind": "memo_writeback_receipt_typo",
        "event_id": "evt-memo-typo-0001",
        "observed_at": "2026-04-06T09:00:00Z",
        "run_ref": "run-memo-002",
        "session_ref": "session:test-unknown-kind",
        "actor_ref": "aoa-memo:writeback",
        "object_ref": {
            "repo": "aoa-memo",
            "kind": "memory_object",
            "id": "memo.test.unknown-kind",
            "version": "main",
        },
        "evidence_refs": [{"kind": "memory_object", "ref": "repo:aoa-memo/generated/memory_object_catalog.min.json"}],
        "payload": {"target_kind": "decision"},
    }

    with pytest.raises(module.ReceiptValidationError, match="schemas/stats-event-envelope.schema.json"):
        module.validate_receipt(receipt, location="memory")


def test_runtime_closeout_summary_tracks_latest_handoff_posture() -> None:
    module = load_build_views_module()
    receipts = [
        {
            "event_kind": "runtime_wave_closeout_receipt",
            "event_id": "evt-runtime-closeout-0001",
            "observed_at": "2026-04-06T20:10:00Z",
            "run_ref": "run:abyss-stack:pilot:W4:closeout",
            "session_ref": "session:abyss-stack:pilot:W4:closeout",
            "actor_ref": "abyss-stack:aoa-local-ai-trials",
            "object_ref": {
                "repo": "abyss-stack",
                "kind": "runtime_wave_closeout",
                "id": "pilot-v1:W4",
                "version": "runtime",
            },
            "evidence_refs": [
                {
                    "kind": "wave_closeout_json",
                    "ref": "/srv/AbyssOS/abyss-stack/Logs/local-ai-trials/pilot-v1/W4-closeout.json",
                }
            ],
            "payload": {
                "program_id": "pilot-v1",
                "wave_id": "W4",
                "gate_result": "pass",
                "case_count": 3,
                "status_counts": {"pass": 3},
                "next_action": "continue-to-review",
                "truth_status": {
                    "source_authored": True,
                    "deployed": True,
                    "trial_proven": True,
                    "live_available": True,
                },
                "reviewed_closeout_handoff_status": "submitted",
                "reviewed_closeout_audit_only": True,
            },
        },
        {
            "event_kind": "runtime_wave_closeout_receipt",
            "event_id": "evt-runtime-closeout-0002",
            "observed_at": "2026-04-06T20:12:00Z",
            "run_ref": "run:abyss-stack:pilot:W4:closeout",
            "session_ref": "session:abyss-stack:pilot:W4:closeout",
            "actor_ref": "abyss-stack:aoa-local-ai-trials",
            "object_ref": {
                "repo": "abyss-stack",
                "kind": "runtime_wave_closeout",
                "id": "pilot-v1:W4",
                "version": "runtime",
            },
            "evidence_refs": [
                {
                    "kind": "closeout_submit_status",
                    "ref": "/srv/AbyssOS/abyss-stack/Logs/local-ai-trials/pilot-v1/W4-closeout.submit.json",
                }
            ],
            "payload": {
                "program_id": "pilot-v1",
                "wave_id": "W4",
                "gate_result": "pass",
                "case_count": 3,
                "status_counts": {"pass": 3},
                "next_action": "review-complete",
                "truth_status": {
                    "source_authored": True,
                    "deployed": True,
                    "trial_proven": True,
                    "live_available": True,
                },
                "reviewed_closeout_handoff_status": "submitted",
                "reviewed_closeout_audit_only": True,
            },
        },
    ]

    summary = module.build_runtime_closeout_summary(
        receipts, {"receipt_input_paths": ["memory"], "total_receipts": len(receipts)}
    )

    closeout = summary["closeouts"][0]
    assert closeout["program_id"] == "pilot-v1"
    assert closeout["wave_id"] == "W4"
    assert closeout["closeout_receipt_count"] == 2
    assert closeout["latest_gate_result"] == "pass"
    assert closeout["latest_next_action"] == "review-complete"
    assert closeout["latest_reviewed_closeout_handoff_status"] == "submitted"
    assert closeout["latest_reviewed_closeout_audit_only"] is True


def test_core_skill_application_summary_tracks_kernel_usage() -> None:
    module = load_build_views_module()
    receipts = [
        {
            "event_kind": "core_skill_application_receipt",
            "event_id": "evt-core-skill-test-0001",
            "observed_at": "2026-04-06T20:20:00Z",
            "run_ref": "run-core-skill-001",
            "session_ref": "session:test-core-kernel",
            "actor_ref": "aoa-skills:session-donor-harvest",
            "object_ref": {
                "repo": "aoa-skills",
                "kind": "skill",
                "id": "aoa-session-donor-harvest",
                "version": "main",
            },
            "evidence_refs": [
                {
                    "kind": "receipt",
                    "ref": "repo:aoa-skills/tmp/HARVEST_PACKET_RECEIPT.json",
                }
            ],
            "payload": {
                "kernel_id": "project-core-session-growth-v1",
                "skill_name": "aoa-session-donor-harvest",
                "application_stage": "finish",
                "detail_event_kind": "harvest_packet_receipt",
                "detail_receipt_ref": "repo:aoa-skills/tmp/HARVEST_PACKET_RECEIPT.json",
                "route_ref": "route:test-core-kernel",
            },
        },
        {
            "event_kind": "core_skill_application_receipt",
            "event_id": "evt-core-skill-test-0002",
            "observed_at": "2026-04-06T20:22:00Z",
            "run_ref": "run-core-skill-002",
            "session_ref": "session:test-core-kernel-2",
            "actor_ref": "aoa-skills:session-donor-harvest",
            "object_ref": {
                "repo": "aoa-skills",
                "kind": "skill",
                "id": "aoa-session-donor-harvest",
                "version": "main",
            },
            "evidence_refs": [
                {
                    "kind": "receipt",
                    "ref": "repo:aoa-skills/tmp/HARVEST_PACKET_RECEIPT_2.json",
                }
            ],
            "payload": {
                "kernel_id": "project-core-session-growth-v1",
                "skill_name": "aoa-session-donor-harvest",
                "application_stage": "finish",
                "detail_event_kind": "harvest_packet_receipt",
                "detail_receipt_ref": "repo:aoa-skills/tmp/HARVEST_PACKET_RECEIPT_2.json",
                "route_ref": "route:test-core-kernel",
            },
        },
    ]

    summary = module.build_core_skill_application_summary(
        receipts, {"receipt_input_paths": ["memory"], "total_receipts": len(receipts)}
    )

    assert summary["skills"][0]["kernel_id"] == "project-core-session-growth-v1"
    assert summary["skills"][0]["skill_name"] == "aoa-session-donor-harvest"
    assert summary["skills"][0]["application_count"] == 2
    assert summary["skills"][0]["latest_session_ref"] == "session:test-core-kernel-2"
    assert summary["skills"][0]["detail_event_kind_counts"] == {
        "harvest_packet_receipt": 2
    }


def test_core_skill_application_summary_ignores_non_finish_events() -> None:
    module = load_build_views_module()
    receipts = [
        {
            "event_kind": "core_skill_application_receipt",
            "event_id": "evt-core-skill-finish-0001",
            "observed_at": "2026-04-06T20:20:00Z",
            "run_ref": "run-core-skill-001",
            "session_ref": "session:test-core-kernel",
            "actor_ref": "aoa-skills:session-donor-harvest",
            "object_ref": {
                "repo": "aoa-skills",
                "kind": "skill",
                "id": "aoa-session-donor-harvest",
                "version": "main",
            },
            "evidence_refs": [{"kind": "receipt", "ref": "repo:aoa-skills/tmp/HARVEST_PACKET_RECEIPT.json"}],
            "payload": {
                "kernel_id": "project-core-session-growth-v1",
                "skill_name": "aoa-session-donor-harvest",
                "application_stage": "finish",
                "detail_event_kind": "harvest_packet_receipt",
                "detail_receipt_ref": "repo:aoa-skills/tmp/HARVEST_PACKET_RECEIPT.json",
            },
        },
        {
            "event_kind": "core_skill_application_receipt",
            "event_id": "evt-core-skill-start-0002",
            "observed_at": "2026-04-06T20:30:00Z",
            "run_ref": "run-core-skill-002",
            "session_ref": "session:test-core-kernel-start",
            "actor_ref": "aoa-skills:session-donor-harvest",
            "object_ref": {
                "repo": "aoa-skills",
                "kind": "skill",
                "id": "aoa-session-donor-harvest",
                "version": "main",
            },
            "evidence_refs": [{"kind": "receipt", "ref": "repo:aoa-skills/tmp/HARVEST_PACKET_RECEIPT_START.json"}],
            "payload": {
                "kernel_id": "project-core-session-growth-v1",
                "skill_name": "aoa-session-donor-harvest",
                "application_stage": "start",
                "detail_event_kind": "harvest_packet_receipt",
                "detail_receipt_ref": "repo:aoa-skills/tmp/HARVEST_PACKET_RECEIPT_START.json",
            },
        },
    ]

    summary = module.build_core_skill_application_summary(
        receipts, {"receipt_input_paths": ["memory"], "total_receipts": len(receipts)}
    )

    assert summary["skills"][0]["application_count"] == 1
    assert summary["skills"][0]["latest_session_ref"] == "session:test-core-kernel"
    assert summary["skills"][0]["detail_event_kind_counts"] == {
        "harvest_packet_receipt": 1
    }


def test_load_receipts_accepts_jsonl_and_deduplicates_event_ids(tmp_path: Path) -> None:
    module = load_build_views_module()
    jsonl_path = tmp_path / "live_receipts.jsonl"
    jsonl_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "event_kind": "automation_candidate_receipt",
                        "event_id": "evt-auto-test-0001",
                        "observed_at": "2026-04-05T10:20:00Z",
                        "run_ref": "run-test-001",
                        "session_ref": "session:test-001",
                        "actor_ref": "aoa-skills:automation-opportunity-scan",
                        "object_ref": {
                            "repo": "aoa-skills",
                            "kind": "skill",
                            "id": "aoa-automation-opportunity-scan",
                            "version": "main",
                        },
                        "evidence_refs": [
                            {
                                "kind": "skill",
                                "ref": "repo:aoa-skills/skills/aoa-automation-opportunity-scan/SKILL.md",
                            }
                        ],
                        "payload": {
                            "pipeline_ref": "pipeline:test",
                            "repeat_signal": "present",
                            "deterministic_ready": True,
                            "reversible_ready": True,
                            "checkpoint_required": False,
                            "seed_ready": True,
                            "next_artifact_hint": "seed-pack",
                        },
                    }
                ),
                json.dumps(
                    {
                        "event_kind": "automation_candidate_receipt",
                        "event_id": "evt-auto-test-0001",
                        "observed_at": "2026-04-05T10:19:00Z",
                        "run_ref": "run-test-001",
                        "session_ref": "session:test-001",
                        "actor_ref": "aoa-skills:automation-opportunity-scan",
                        "object_ref": {
                            "repo": "aoa-skills",
                            "kind": "skill",
                            "id": "aoa-automation-opportunity-scan",
                            "version": "main",
                        },
                        "evidence_refs": [
                            {
                                "kind": "skill",
                                "ref": "repo:aoa-skills/skills/aoa-automation-opportunity-scan/SKILL.md",
                            }
                        ],
                        "payload": {
                            "pipeline_ref": "pipeline:test",
                            "repeat_signal": "present",
                            "deterministic_ready": True,
                            "reversible_ready": True,
                            "checkpoint_required": False,
                            "seed_ready": True,
                            "next_artifact_hint": "seed-pack",
                        },
                    }
                ),
                json.dumps(
                    {
                        "event_kind": "automation_candidate_receipt",
                        "event_id": "evt-auto-test-0001",
                        "observed_at": "2026-04-05T10:21:00Z",
                        "run_ref": "run-test-001",
                        "session_ref": "session:test-001",
                        "actor_ref": "aoa-skills:automation-opportunity-scan",
                        "object_ref": {
                            "repo": "aoa-skills",
                            "kind": "skill",
                            "id": "aoa-automation-opportunity-scan",
                            "version": "main",
                        },
                        "evidence_refs": [
                            {
                                "kind": "skill",
                                "ref": "repo:aoa-skills/skills/aoa-automation-opportunity-scan/SKILL.md",
                            }
                        ],
                        "payload": {
                            "pipeline_ref": "pipeline:test",
                            "repeat_signal": "present",
                            "deterministic_ready": True,
                            "reversible_ready": True,
                            "checkpoint_required": False,
                            "seed_ready": True,
                            "next_artifact_hint": "seed-pack",
                        },
                    }
                ),
                json.dumps(
                    {
                        "event_kind": "automation_candidate_receipt",
                        "event_id": "evt-auto-test-0001",
                        "observed_at": "2026-04-05T10:18:00Z",
                        "run_ref": "run-test-001",
                        "session_ref": "session:test-001",
                        "actor_ref": "aoa-skills:automation-opportunity-scan",
                        "object_ref": {
                            "repo": "aoa-skills",
                            "kind": "skill",
                            "id": "aoa-automation-opportunity-scan",
                            "version": "main",
                        },
                        "evidence_refs": [
                            {
                                "kind": "skill",
                                "ref": "repo:aoa-skills/skills/aoa-automation-opportunity-scan/SKILL.md",
                            }
                        ],
                        "payload": {
                            "pipeline_ref": "pipeline:test",
                            "repeat_signal": "present",
                            "deterministic_ready": True,
                            "reversible_ready": True,
                            "checkpoint_required": False,
                            "seed_ready": True,
                            "next_artifact_hint": "seed-pack",
                        },
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    receipts = module.load_receipts([jsonl_path])

    assert len(receipts) == 1
    assert receipts[0]["observed_at"] == "2026-04-05T10:21:00Z"


def test_resolve_active_receipts_collapses_supersedes_chain() -> None:
    module = load_build_views_module()
    receipts = [
        {
            "event_kind": "automation_candidate_receipt",
            "event_id": "evt-auto-0001",
            "observed_at": "2026-04-06T10:00:00Z",
            "run_ref": "run-001",
            "session_ref": "session:test-supersedes",
            "actor_ref": "aoa-skills:automation-opportunity-scan",
            "object_ref": {"repo": "aoa-skills", "kind": "skill", "id": "aoa-automation-opportunity-scan"},
            "evidence_refs": [{"kind": "packet", "ref": "tmp/a.json"}],
            "payload": {"pipeline_ref": "pipeline:test", "seed_ready": False},
        },
        {
            "event_kind": "automation_candidate_receipt",
            "event_id": "evt-auto-0002",
            "observed_at": "2026-04-06T10:01:00Z",
            "run_ref": "run-002",
            "session_ref": "session:test-supersedes",
            "actor_ref": "aoa-skills:automation-opportunity-scan",
            "object_ref": {"repo": "aoa-skills", "kind": "skill", "id": "aoa-automation-opportunity-scan"},
            "evidence_refs": [{"kind": "packet", "ref": "tmp/b.json"}],
            "payload": {"pipeline_ref": "pipeline:test", "seed_ready": True},
            "supersedes": "evt-auto-0001",
        },
        {
            "event_kind": "automation_candidate_receipt",
            "event_id": "evt-auto-0003",
            "observed_at": "2026-04-06T10:02:00Z",
            "run_ref": "run-003",
            "session_ref": "session:test-supersedes",
            "actor_ref": "aoa-skills:automation-opportunity-scan",
            "object_ref": {"repo": "aoa-skills", "kind": "skill", "id": "aoa-automation-opportunity-scan"},
            "evidence_refs": [{"kind": "packet", "ref": "tmp/c.json"}],
            "payload": {"pipeline_ref": "pipeline:test", "seed_ready": True},
            "supersedes": "evt-auto-0002",
        },
    ]

    active = module.resolve_active_receipts(receipts)

    assert [receipt["event_id"] for receipt in active] == ["evt-auto-0003"]


def test_resolve_active_receipts_keeps_latest_sibling_correction_only() -> None:
    module = load_build_views_module()
    receipts = [
        {
            "event_kind": "harvest_packet_receipt",
            "event_id": "evt-harvest-0001",
            "observed_at": "2026-04-06T11:00:00Z",
            "run_ref": "run-001",
            "session_ref": "session:test-sibling",
            "actor_ref": "aoa-skills:session-donor-harvest",
            "object_ref": {"repo": "aoa-skills", "kind": "skill", "id": "aoa-session-donor-harvest"},
            "evidence_refs": [{"kind": "packet", "ref": "tmp/root.json"}],
            "payload": {"route_ref": "route:test"},
        },
        {
            "event_kind": "harvest_packet_receipt",
            "event_id": "evt-harvest-0002",
            "observed_at": "2026-04-06T11:01:00Z",
            "run_ref": "run-002",
            "session_ref": "session:test-sibling",
            "actor_ref": "aoa-skills:session-donor-harvest",
            "object_ref": {"repo": "aoa-skills", "kind": "skill", "id": "aoa-session-donor-harvest"},
            "evidence_refs": [{"kind": "packet", "ref": "tmp/older.json"}],
            "payload": {"route_ref": "route:test"},
            "supersedes": "evt-harvest-0001",
        },
        {
            "event_kind": "harvest_packet_receipt",
            "event_id": "evt-harvest-0003",
            "observed_at": "2026-04-06T11:02:00Z",
            "run_ref": "run-003",
            "session_ref": "session:test-sibling",
            "actor_ref": "aoa-skills:session-donor-harvest",
            "object_ref": {"repo": "aoa-skills", "kind": "skill", "id": "aoa-session-donor-harvest"},
            "evidence_refs": [{"kind": "packet", "ref": "tmp/newer.json"}],
            "payload": {"route_ref": "route:test"},
            "supersedes": "evt-harvest-0001",
        },
    ]

    active = module.resolve_active_receipts(receipts)

    assert [receipt["event_id"] for receipt in active] == ["evt-harvest-0003"]


def test_resolve_active_receipts_keeps_missing_target_and_cycle_receipts_active() -> None:
    module = load_build_views_module()
    receipts = [
        {
            "event_kind": "diagnosis_packet_receipt",
            "event_id": "evt-diagnose-0001",
            "observed_at": "2026-04-06T12:00:00Z",
            "run_ref": "run-001",
            "session_ref": "session:test-cycles",
            "actor_ref": "aoa-skills:session-self-diagnose",
            "object_ref": {"repo": "aoa-skills", "kind": "skill", "id": "aoa-session-self-diagnose"},
            "evidence_refs": [{"kind": "packet", "ref": "tmp/a.json"}],
            "payload": {"route_ref": "route:test"},
            "supersedes": "evt-missing-9999",
        },
        {
            "event_kind": "repair_cycle_receipt",
            "event_id": "evt-repair-0001",
            "observed_at": "2026-04-06T12:01:00Z",
            "run_ref": "run-002",
            "session_ref": "session:test-cycles",
            "actor_ref": "aoa-skills:session-self-repair",
            "object_ref": {"repo": "aoa-skills", "kind": "skill", "id": "aoa-session-self-repair"},
            "evidence_refs": [{"kind": "packet", "ref": "tmp/b.json"}],
            "payload": {"route_ref": "route:test"},
            "supersedes": "evt-repair-0002",
        },
        {
            "event_kind": "repair_cycle_receipt",
            "event_id": "evt-repair-0002",
            "observed_at": "2026-04-06T12:02:00Z",
            "run_ref": "run-003",
            "session_ref": "session:test-cycles",
            "actor_ref": "aoa-skills:session-self-repair",
            "object_ref": {"repo": "aoa-skills", "kind": "skill", "id": "aoa-session-self-repair"},
            "evidence_refs": [{"kind": "packet", "ref": "tmp/c.json"}],
            "payload": {"route_ref": "route:test"},
            "supersedes": "evt-repair-0001",
        },
    ]

    active = module.resolve_active_receipts(receipts)

    assert [receipt["event_id"] for receipt in active] == [
        "evt-diagnose-0001",
        "evt-repair-0001",
        "evt-repair-0002",
    ]


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
