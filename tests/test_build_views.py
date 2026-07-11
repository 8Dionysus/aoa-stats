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


def test_latest_rollout_history_row_preserves_legacy_missing_ref_fallback() -> None:
    module = load_build_views_module()
    history = [
        {"rollout_campaign_ref": "ROLL-20260411-first-01"},
        {"rollout_campaign_ref": "ROLL-20260412-second-02"},
    ]

    assert module.latest_rollout_history_row(history, {}) == history[-1]


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
        "generated/runtime_closeout_summary.min.json",
        "generated/stress_recovery_window_summary.min.json",
        "generated/source_coverage_summary.min.json",
        "generated/surface_detection_summary.min.json",
    ]
    assert "titan_summon_summary" not in {
        entry["name"] for entry in catalog["surfaces"]
    }
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
