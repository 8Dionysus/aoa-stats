from __future__ import annotations

import importlib.util
import json
from pathlib import Path


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
        "summary_surface_catalog.min.json",
    }
    assert outputs["object_summary.min.json"]["generated_from"]["total_receipts"] == 11
    assert outputs["core_skill_application_summary.min.json"]["skills"] == []
    assert len(outputs["repeated_window_summary.min.json"]["windows"]) == 2
    assert len(outputs["route_progression_summary.min.json"]["routes"]) == 1
    assert len(outputs["fork_calibration_summary.min.json"]["routes"]) == 1
    assert len(outputs["automation_pipeline_summary.min.json"]["pipelines"]) == 1
    assert outputs["runtime_closeout_summary.min.json"]["closeouts"] == []


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
            "event_kind": "skill_run_receipt",
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
