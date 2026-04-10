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
        [REPO_ROOT / "examples" / "session_harvest_family.receipts.example.json"]
    )
    outputs = module.build_all_views(receipts, ["session_harvest_family.receipts.example.json"])

    assert set(outputs) == {
        "object_summary.min.json",
        "core_skill_application_summary.min.json",
        "repeated_window_summary.min.json",
        "route_progression_summary.min.json",
        "fork_calibration_summary.min.json",
        "automation_pipeline_summary.min.json",
        "runtime_closeout_summary.min.json",
        "stress_recovery_window_summary.min.json",
        "surface_detection_summary.min.json",
        "summary_surface_catalog.min.json",
    }
    assert outputs["object_summary.min.json"]["generated_from"]["total_receipts"] == 14
    assert len(outputs["core_skill_application_summary.min.json"]["skills"]) == 1
    assert len(outputs["repeated_window_summary.min.json"]["windows"]) == 2
    assert len(outputs["route_progression_summary.min.json"]["routes"]) == 1
    assert len(outputs["fork_calibration_summary.min.json"]["routes"]) == 1
    assert len(outputs["automation_pipeline_summary.min.json"]["pipelines"]) == 1
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
    assert catalog["validation_refs"] == [
        "scripts/build_views.py",
        "scripts/validate_repo.py",
        "tests/test_summary_surface_catalog.py",
    ]
    assert [entry["surface_ref"] for entry in catalog["surfaces"]] == [
        "generated/core_skill_application_summary.min.json",
        "generated/object_summary.min.json",
        "generated/repeated_window_summary.min.json",
        "generated/route_progression_summary.min.json",
        "generated/fork_calibration_summary.min.json",
        "generated/automation_pipeline_summary.min.json",
        "generated/runtime_closeout_summary.min.json",
        "generated/stress_recovery_window_summary.min.json",
        "generated/surface_detection_summary.min.json",
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
    schema = json.loads((REPO_ROOT / "schemas" / "antifragility_vector_v1.json").read_text(encoding="utf-8"))
    payload = json.loads((REPO_ROOT / "examples" / "antifragility_vector.example.json").read_text(encoding="utf-8"))
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


def test_automation_pipeline_summary_tracks_seed_readiness() -> None:
    module = load_build_views_module()
    receipts = module.load_receipts(
        [REPO_ROOT / "examples" / "session_harvest_family.receipts.example.json"]
    )
    outputs = module.build_all_views(receipts, ["session_harvest_family.receipts.example.json"])
    pipeline = outputs["automation_pipeline_summary.min.json"]["pipelines"][0]

    assert pipeline["pipeline_ref"] == "pipeline:session-growth"
    assert pipeline["candidate_count"] == 2
    assert pipeline["seed_ready_count"] == 1
    assert pipeline["checkpoint_required_count"] == 1
    assert pipeline["next_artifact_hints"] == ["repair-prompt", "seed-pack"]


def test_validate_receipt_accepts_known_unsummarized_event_kind() -> None:
    module = load_build_views_module()
    receipt = {
        "event_kind": "memo_writeback_receipt",
        "event_id": "evt-memo-known-0001",
        "observed_at": "2026-04-06T09:00:00Z",
        "run_ref": "run-memo-001",
        "session_ref": "session:test-known-kind",
        "actor_ref": "aoa-memo:writeback",
        "object_ref": {
            "repo": "aoa-memo",
            "kind": "memory_object",
            "id": "memo.test.known-kind",
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


def test_automation_pipeline_summary_falls_back_to_manual_route_ref() -> None:
    module = load_build_views_module()
    receipts = [
        {
            "event_kind": "automation_candidate_receipt",
            "event_id": "evt-auto-manual-route-0001",
            "observed_at": "2026-04-06T09:00:00Z",
            "run_ref": "run-manual-route-001",
            "session_ref": "session:test-manual-route",
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
                "manual_route_ref": "route:manual-closeout-loop",
                "repeat_signal": "present",
                "deterministic_ready": True,
                "reversible_ready": True,
                "checkpoint_required": False,
                "seed_ready": True,
                "next_artifact_hint": "playbook_seed",
            },
        }
    ]

    summary = module.build_automation_pipeline_summary(
        receipts, {"receipt_input_paths": ["memory"], "total_receipts": len(receipts)}
    )

    assert summary["pipelines"][0]["pipeline_ref"] == "route:manual-closeout-loop"
    assert summary["pipelines"][0]["candidate_count"] == 1


def test_fork_calibration_summary_falls_back_to_branch_id_count() -> None:
    module = load_build_views_module()
    receipts = [
        {
            "event_kind": "decision_fork_receipt",
            "event_id": "evt-fork-test-0001",
            "observed_at": "2026-04-06T09:10:00Z",
            "run_ref": "run-fork-001",
            "session_ref": "session:test-fork-count",
            "actor_ref": "aoa-skills:session-route-forks",
            "object_ref": {
                "repo": "aoa-skills",
                "kind": "skill",
                "id": "aoa-session-route-forks",
                "version": "main",
            },
            "evidence_refs": [
                {
                    "kind": "skill",
                    "ref": "repo:aoa-skills/skills/aoa-session-route-forks/SKILL.md",
                }
            ],
            "payload": {
                "route_ref": "route:test-fork-calibration",
                "branch_ids": ["branch:keep", "branch:playbook", "branch:defer"],
                "chosen_branch": "branch:keep",
            },
        }
    ]

    summary = module.build_fork_calibration_summary(
        receipts, {"receipt_input_paths": ["memory"], "total_receipts": len(receipts)}
    )

    assert summary["routes"][0]["route_ref"] == "route:test-fork-calibration"
    assert summary["routes"][0]["max_option_count"] == 3


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
                    "ref": "/srv/abyss-stack/Logs/local-ai-trials/pilot-v1/W4-closeout.json",
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
                    "ref": "/srv/abyss-stack/Logs/local-ai-trials/pilot-v1/W4-closeout.submit.json",
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
