from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "refresh_live_stats.py"


def load_refresh_module():
    spec = importlib.util.spec_from_file_location("refresh_live_stats", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_refresh_live_state_combines_repo_relative_sources(tmp_path: Path) -> None:
    module = load_refresh_module()
    federation_root = tmp_path / "srv"
    skills_dir = federation_root / "aoa-skills" / ".aoa" / "live_receipts"
    evals_dir = federation_root / "aoa-evals" / ".aoa" / "live_receipts"
    skills_dir.mkdir(parents=True)
    evals_dir.mkdir(parents=True)

    skill_receipt = [
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
            "evidence_refs": [{"kind": "skill", "ref": "repo:aoa-skills/skills/aoa-automation-opportunity-scan/SKILL.md"}],
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
    ]
    eval_receipt = {
        "event_kind": "eval_result_receipt",
        "event_id": "evt-eval-test-0001",
        "observed_at": "2026-04-05T10:35:00Z",
        "run_ref": "eval-run-test-001",
        "session_ref": "session:test-001",
        "actor_ref": "aoa-evals:reviewer",
        "object_ref": {
            "repo": "aoa-evals",
            "kind": "eval_bundle",
            "id": "aoa-bounded-change-quality",
            "version": "portable",
        },
        "evidence_refs": [{"kind": "bundle_report", "ref": "repo:aoa-evals/bundles/aoa-bounded-change-quality/reports/example-report.json"}],
        "payload": {
            "eval_name": "aoa-bounded-change-quality",
            "bundle_status": "portable",
            "report_format": "summary",
            "verdict": "supports bounded claim",
            "claim_scope": "bundle_scoped",
            "bundle_ref": "repo:aoa-evals/bundles/aoa-bounded-change-quality/EVAL.md",
            "report_ref": "repo:aoa-evals/bundles/aoa-bounded-change-quality/reports/example-report.json",
            "case_count": 3,
            "score": None,
            "interpretation_bound": "Bounded example only.",
        },
    }

    (skills_dir / "session-harvest-family.jsonl").write_text(
        "\n".join(json.dumps(item) for item in skill_receipt) + "\n",
        encoding="utf-8",
    )
    (evals_dir / "eval-result-receipts.jsonl").write_text(
        json.dumps(eval_receipt) + "\n",
        encoding="utf-8",
    )

    registry_path = tmp_path / "live_receipt_sources.example.json"
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "sources": [
                    {
                        "name": "skills",
                        "repo": "aoa-skills",
                        "relative_path": ".aoa/live_receipts/session-harvest-family.jsonl",
                    },
                    {
                        "name": "evals",
                        "repo": "aoa-evals",
                        "relative_path": ".aoa/live_receipts/eval-result-receipts.jsonl",
                    },
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    feed_output = tmp_path / "state" / "live_receipts.min.json"
    summary_output_dir = tmp_path / "state" / "generated"
    source_labels, receipt_count = module.refresh_live_state(
        registry_path=registry_path,
        federation_root=federation_root,
        feed_output=feed_output,
        summary_output_dir=summary_output_dir,
    )

    assert source_labels == [
        "aoa-skills/.aoa/live_receipts/session-harvest-family.jsonl",
        "aoa-evals/.aoa/live_receipts/eval-result-receipts.jsonl",
    ]
    assert receipt_count == 2

    feed = json.loads(feed_output.read_text(encoding="utf-8"))
    assert len(feed) == 2
    pipeline_summary = json.loads(
        (summary_output_dir / "automation_pipeline_summary.min.json").read_text(encoding="utf-8")
    )
    assert pipeline_summary["generated_from"]["receipt_input_paths"] == source_labels
    assert pipeline_summary["generated_from"]["total_receipts"] == 2
    assert pipeline_summary["pipelines"][0]["pipeline_ref"] == "pipeline:test"
    stress_summary = json.loads(
        (summary_output_dir / "stress_recovery_window_summary.min.json").read_text(encoding="utf-8")
    )
    assert stress_summary["suppression"]["status"] == "insufficient_evidence"


def test_refresh_live_state_clears_previous_outputs_when_sources_are_empty(tmp_path: Path) -> None:
    module = load_refresh_module()
    federation_root = tmp_path / "srv"
    skills_log = federation_root / "aoa-skills" / ".aoa" / "live_receipts"
    evals_log = federation_root / "aoa-evals" / ".aoa" / "live_receipts"
    skills_log.mkdir(parents=True)
    evals_log.mkdir(parents=True)
    (skills_log / "session-harvest-family.jsonl").write_text("", encoding="utf-8")
    (evals_log / "eval-result-receipts.jsonl").write_text("", encoding="utf-8")

    registry_path = tmp_path / "live_receipt_sources.json"
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "sources": [
                    {
                        "name": "skills",
                        "repo": "aoa-skills",
                        "relative_path": ".aoa/live_receipts/session-harvest-family.jsonl",
                    },
                    {
                        "name": "evals",
                        "repo": "aoa-evals",
                        "relative_path": ".aoa/live_receipts/eval-result-receipts.jsonl",
                    },
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    feed_output = tmp_path / "state" / "live_receipts.min.json"
    summary_output_dir = tmp_path / "state" / "generated"
    summary_output_dir.mkdir(parents=True)
    feed_output.write_text("[]\n", encoding="utf-8")
    (summary_output_dir / "summary_surface_catalog.min.json").write_text(
        '{"schema_version":"aoa_stats_summary_surface_catalog_v1"}\n', encoding="utf-8"
    )
    (summary_output_dir / "codex_plane_deployment_summary.min.json").write_text(
        '{"schema_version":"aoa_stats_codex_plane_deployment_summary_v1"}\n',
        encoding="utf-8",
    )

    source_labels, receipt_count = module.refresh_live_state(
        registry_path=registry_path,
        federation_root=federation_root,
        feed_output=feed_output,
        summary_output_dir=summary_output_dir,
    )

    assert source_labels == [
        "aoa-skills/.aoa/live_receipts/session-harvest-family.jsonl",
        "aoa-evals/.aoa/live_receipts/eval-result-receipts.jsonl",
    ]
    assert receipt_count == 0
    assert feed_output.exists() is False
    assert (summary_output_dir / "summary_surface_catalog.min.json").exists() is False
    assert (summary_output_dir / "codex_plane_deployment_summary.min.json").exists() is False
    assert (summary_output_dir / "stress_recovery_window_summary.min.json").exists() is False


def test_refresh_live_state_removes_stale_optional_outputs_when_builder_omits_them(tmp_path: Path) -> None:
    module = load_refresh_module()
    federation_root = tmp_path / "srv"
    skills_dir = federation_root / "aoa-skills" / ".aoa" / "live_receipts"
    evals_dir = federation_root / "aoa-evals" / ".aoa" / "live_receipts"
    skills_dir.mkdir(parents=True)
    evals_dir.mkdir(parents=True)

    (skills_dir / "session-harvest-family.jsonl").write_text(
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
                "evidence_refs": [{"kind": "skill", "ref": "repo:aoa-skills/skills/aoa-automation-opportunity-scan/SKILL.md"}],
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
        )
        + "\n",
        encoding="utf-8",
    )
    (evals_dir / "eval-result-receipts.jsonl").write_text("", encoding="utf-8")

    registry_path = tmp_path / "live_receipt_sources.json"
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "sources": [
                    {
                        "name": "skills",
                        "repo": "aoa-skills",
                        "relative_path": ".aoa/live_receipts/session-harvest-family.jsonl",
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    feed_output = tmp_path / "state" / "live_receipts.min.json"
    summary_output_dir = tmp_path / "state" / "generated"
    summary_output_dir.mkdir(parents=True)
    stale_path = summary_output_dir / "codex_plane_deployment_summary.min.json"
    stale_path.write_text("stale\n", encoding="utf-8")

    with patch.object(
        module,
        "build_all_views",
        return_value={
            "automation_pipeline_summary.min.json": {"schema_version": "test"},
            "summary_surface_catalog.min.json": {"schema_version": "test"},
        },
    ), patch.object(module, "stable_json", side_effect=lambda payload: json.dumps(payload) + "\n"):
        _, receipt_count = module.refresh_live_state(
            registry_path=registry_path,
            federation_root=federation_root,
            feed_output=feed_output,
            summary_output_dir=summary_output_dir,
        )

    assert receipt_count == 1
    assert stale_path.exists() is False


def test_refresh_live_state_resolves_stress_report_from_federation_root(tmp_path: Path) -> None:
    module = load_refresh_module()
    federation_root = tmp_path / "srv"
    evals_dir = federation_root / "aoa-evals" / ".aoa" / "live_receipts"
    evals_dir.mkdir(parents=True)
    report_path = (
        federation_root
        / "aoa-evals"
        / "bundles"
        / "aoa-stress-recovery-window"
        / "reports"
        / "example-report.json"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(
            {
                "eval_name": "aoa-stress-recovery-window",
                "bundle_status": "draft",
                "object_under_evaluation": "ordered stress recovery posture",
                "comparison_mode": "longitudinal-window",
                "report_id": "eval-stress-window-live",
                "generated_at_utc": "2026-04-07T18:00:00Z",
                "window": {
                    "label": "window-live",
                    "start_utc": "2026-04-01T00:00:00Z",
                    "end_utc": "2026-04-07T00:00:00Z",
                },
                "scope": {
                    "stressor_family": "hybrid-query-kag-unhealthy",
                    "repo_roots": ["aoa-routing", "aoa-memo"],
                    "owner_surface": "hybrid-query",
                    "surface_family": "kag-regrounding",
                },
                "inputs": {
                    "source_receipt_refs": ["r1"],
                    "handoff_refs": ["h1"],
                    "playbook_lane_refs": ["p1"],
                    "reentry_gate_refs": ["g1"],
                    "projection_health_refs": ["ph1"],
                    "regrounding_ticket_refs": ["rt1"],
                    "route_hint_refs": ["route1"],
                    "memo_context_refs": ["memo1"],
                },
                "axes": {
                    "handoff_fidelity": {"status": "pass", "score": 0.9, "rationale": "ok"},
                    "route_discipline": {"status": "pass", "score": 0.88, "rationale": "ok"},
                    "reentry_quality": {"status": "warn", "score": 0.72, "rationale": "ok"},
                    "regrounding_effectiveness": {"status": "warn", "score": 0.69, "rationale": "ok"},
                    "evidence_continuity": {"status": "pass", "score": 0.91, "rationale": "ok"},
                    "false_promotion_prevention": {"status": "pass", "score": 0.93, "rationale": "ok"},
                    "operator_burden": {"status": "warn", "score": 0.64, "rationale": "ok"},
                    "trust_calibration": {"status": "pass", "score": 0.89, "rationale": "ok"},
                },
                "overall_posture": "mixed",
                "blind_spots": ["one"],
                "evidence_gaps": ["two"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (evals_dir / "eval-result-receipts.jsonl").write_text(
        json.dumps(
            {
                "event_kind": "eval_result_receipt",
                "event_id": "evt-stress-live-0001",
                "observed_at": "2026-04-07T18:01:00Z",
                "run_ref": "run-stress-live-001",
                "session_ref": "session:test-stress-live",
                "actor_ref": "aoa-evals:reviewer",
                "object_ref": {
                    "repo": "aoa-evals",
                    "kind": "eval_bundle",
                    "id": "aoa-stress-recovery-window",
                    "version": "draft",
                },
                "evidence_refs": [
                    {
                        "kind": "bundle_report",
                        "ref": "repo:aoa-evals/bundles/aoa-stress-recovery-window/reports/example-report.json",
                    }
                ],
                "payload": {
                    "eval_name": "aoa-stress-recovery-window",
                    "report_ref": "repo:aoa-evals/bundles/aoa-stress-recovery-window/reports/example-report.json",
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    registry_path = tmp_path / "live_receipt_sources.stress.json"
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "sources": [
                    {
                        "name": "evals",
                        "repo": "aoa-evals",
                        "relative_path": ".aoa/live_receipts/eval-result-receipts.jsonl",
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    feed_output = tmp_path / "state" / "live_receipts.min.json"
    summary_output_dir = tmp_path / "state" / "generated"
    source_labels, receipt_count = module.refresh_live_state(
        registry_path=registry_path,
        federation_root=federation_root,
        feed_output=feed_output,
        summary_output_dir=summary_output_dir,
    )

    assert source_labels == ["aoa-evals/.aoa/live_receipts/eval-result-receipts.jsonl"]
    assert receipt_count == 1
    stress_summary = json.loads(
        (summary_output_dir / "stress_recovery_window_summary.min.json").read_text(encoding="utf-8")
    )
    assert stress_summary["suppression"]["status"] == "low_sample"
    assert stress_summary["scope"]["stressor_family"] == "hybrid-query-kag-unhealthy"
    assert stress_summary["inputs"]["eval_report_refs"] == [
        "repo:aoa-evals/bundles/aoa-stress-recovery-window/reports/example-report.json"
    ]


def test_refresh_live_state_prefers_vendored_evals_root_when_present(tmp_path: Path) -> None:
    module = load_refresh_module()
    federation_root = tmp_path / "srv"
    evals_dir = federation_root / "aoa-evals" / ".aoa" / "live_receipts"
    evals_dir.mkdir(parents=True)
    vendored_repo_root = tmp_path / "repo" / "aoa-stats"
    vendored_report_path = (
        vendored_repo_root
        / "aoa-evals"
        / "bundles"
        / "aoa-stress-recovery-window"
        / "reports"
        / "vendored-report.json"
    )
    vendored_report_path.parent.mkdir(parents=True, exist_ok=True)
    vendored_report_path.write_text(
        json.dumps(
            {
                "eval_name": "aoa-stress-recovery-window",
                "bundle_status": "draft",
                "object_under_evaluation": "ordered stress recovery posture",
                "comparison_mode": "longitudinal-window",
                "report_id": "eval-stress-window-vendored",
                "generated_at_utc": "2026-04-07T18:00:00Z",
                "window": {
                    "label": "window-live",
                    "start_utc": "2026-04-01T00:00:00Z",
                    "end_utc": "2026-04-07T00:00:00Z",
                },
                "scope": {
                    "stressor_family": "hybrid-query-kag-unhealthy",
                    "repo_roots": ["aoa-routing", "aoa-memo"],
                    "owner_surface": "hybrid-query",
                    "surface_family": "kag-regrounding",
                },
                "inputs": {
                    "source_receipt_refs": ["r1"],
                    "handoff_refs": ["h1"],
                    "playbook_lane_refs": ["p1"],
                    "reentry_gate_refs": ["g1"],
                    "projection_health_refs": ["ph1"],
                    "regrounding_ticket_refs": ["rt1"],
                    "route_hint_refs": ["route1"],
                    "memo_context_refs": ["memo1"],
                },
                "axes": {
                    "handoff_fidelity": {"status": "pass", "score": 0.9, "rationale": "ok"},
                    "route_discipline": {"status": "pass", "score": 0.88, "rationale": "ok"},
                    "reentry_quality": {"status": "warn", "score": 0.72, "rationale": "ok"},
                    "regrounding_effectiveness": {"status": "warn", "score": 0.69, "rationale": "ok"},
                    "evidence_continuity": {"status": "pass", "score": 0.91, "rationale": "ok"},
                    "false_promotion_prevention": {"status": "pass", "score": 0.93, "rationale": "ok"},
                    "operator_burden": {"status": "warn", "score": 0.64, "rationale": "ok"},
                    "trust_calibration": {"status": "pass", "score": 0.89, "rationale": "ok"},
                },
                "overall_posture": "mixed",
                "blind_spots": ["one"],
                "evidence_gaps": ["two"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (evals_dir / "eval-result-receipts.jsonl").write_text(
        json.dumps(
            {
                "event_kind": "eval_result_receipt",
                "event_id": "evt-stress-live-0001",
                "observed_at": "2026-04-07T18:01:00Z",
                "run_ref": "run-stress-live-001",
                "session_ref": "session:test-stress-live",
                "actor_ref": "aoa-evals:reviewer",
                "object_ref": {
                    "repo": "aoa-evals",
                    "kind": "eval_bundle",
                    "id": "aoa-stress-recovery-window",
                    "version": "draft",
                },
                "evidence_refs": [
                    {
                        "kind": "bundle_report",
                        "ref": "repo:aoa-evals/bundles/aoa-stress-recovery-window/reports/vendored-report.json",
                    }
                ],
                "payload": {
                    "eval_name": "aoa-stress-recovery-window",
                    "report_ref": "repo:aoa-evals/bundles/aoa-stress-recovery-window/reports/vendored-report.json",
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    registry_path = tmp_path / "live_receipt_sources.stress.json"
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "sources": [
                    {
                        "name": "evals",
                        "repo": "aoa-evals",
                        "relative_path": ".aoa/live_receipts/eval-result-receipts.jsonl",
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    feed_output = tmp_path / "state" / "live_receipts.min.json"
    summary_output_dir = tmp_path / "state" / "generated"
    with patch.object(module, "REPO_ROOT", vendored_repo_root):
        source_labels, receipt_count = module.refresh_live_state(
            registry_path=registry_path,
            federation_root=federation_root,
            feed_output=feed_output,
            summary_output_dir=summary_output_dir,
        )

    assert source_labels == ["aoa-evals/.aoa/live_receipts/eval-result-receipts.jsonl"]
    assert receipt_count == 1
    stress_summary = json.loads(
        (summary_output_dir / "stress_recovery_window_summary.min.json").read_text(encoding="utf-8")
    )
    assert stress_summary["scope"]["stressor_family"] == "hybrid-query-kag-unhealthy"
    assert stress_summary["inputs"]["eval_report_refs"] == [
        "repo:aoa-evals/bundles/aoa-stress-recovery-window/reports/vendored-report.json"
    ]


def test_refresh_live_state_combines_playbook_technique_memo_and_runtime_sources(
    tmp_path: Path,
) -> None:
    module = load_refresh_module()
    federation_root = tmp_path / "srv"
    skills_dir = federation_root / "aoa-skills" / ".aoa" / "live_receipts"
    skills_core_dir = federation_root / "aoa-skills" / ".aoa" / "live_receipts"
    evals_dir = federation_root / "aoa-evals" / ".aoa" / "live_receipts"
    playbooks_dir = federation_root / "aoa-playbooks" / ".aoa" / "live_receipts"
    techniques_dir = federation_root / "aoa-techniques" / ".aoa" / "live_receipts"
    memo_dir = federation_root / "aoa-memo" / ".aoa" / "live_receipts"
    runtime_dir = federation_root / "abyss-stack" / ".aoa" / "live_receipts"
    for path in (
        skills_dir,
        skills_core_dir,
        evals_dir,
        playbooks_dir,
        techniques_dir,
        memo_dir,
        runtime_dir,
    ):
        path.mkdir(parents=True, exist_ok=True)

    receipts_by_path = {
        skills_dir / "session-harvest-family.jsonl": {
            "event_kind": "harvest_packet_receipt",
            "event_id": "evt-skill-test-0001",
            "observed_at": "2026-04-06T20:00:00Z",
            "run_ref": "run-skill-001",
            "session_ref": "session:test-002",
            "actor_ref": "aoa-skills:session-donor-harvest",
            "object_ref": {
                "repo": "aoa-skills",
                "kind": "skill",
                "id": "aoa-session-donor-harvest",
                "version": "main",
            },
            "evidence_refs": [{"kind": "skill", "ref": "repo:aoa-skills/skills/aoa-session-donor-harvest/SKILL.md"}],
            "payload": {"route_ref": "route:test-multi-owner"},
        },
        skills_core_dir / "core-skill-applications.jsonl": {
            "event_kind": "core_skill_application_receipt",
            "event_id": "evt-core-skill-test-0001",
            "observed_at": "2026-04-06T20:00:30Z",
            "run_ref": "run-skill-001",
            "session_ref": "session:test-002",
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
                "route_ref": "route:test-multi-owner",
            },
        },
        evals_dir / "eval-result-receipts.jsonl": {
            "event_kind": "eval_result_receipt",
            "event_id": "evt-eval-test-0002",
            "observed_at": "2026-04-06T20:01:00Z",
            "run_ref": "run-eval-002",
            "session_ref": "session:test-002",
            "actor_ref": "aoa-evals:reviewer",
            "object_ref": {
                "repo": "aoa-evals",
                "kind": "eval_bundle",
                "id": "aoa-bounded-change-quality",
                "version": "portable",
            },
            "evidence_refs": [{"kind": "bundle_report", "ref": "repo:aoa-evals/generated/eval_catalog.min.json"}],
            "payload": {"verdict": "supports bounded claim"},
        },
        playbooks_dir / "playbook-receipts.jsonl": {
            "event_kind": "playbook_review_harvest_receipt",
            "event_id": "evt-playbook-test-0001",
            "observed_at": "2026-04-06T20:02:00Z",
            "run_ref": "run-playbook-001",
            "session_ref": "session:test-002",
            "actor_ref": "aoa-playbooks:owner-first-capability-landing",
            "object_ref": {
                "repo": "aoa-playbooks",
                "kind": "playbook",
                "id": "AOA-P-0021",
                "version": "main",
            },
            "evidence_refs": [{"kind": "reviewed_run", "ref": "repo:aoa-playbooks/docs/real-runs/2026-04-06.owner-first-capability-landing.md"}],
            "payload": {"gate_verdict": "composition-landed"},
        },
        techniques_dir / "technique-receipts.jsonl": {
            "event_kind": "technique_promotion_receipt",
            "event_id": "evt-technique-test-0001",
            "observed_at": "2026-04-06T20:03:00Z",
            "run_ref": "run-technique-001",
            "session_ref": "session:test-002",
            "actor_ref": "aoa-techniques:promotion-wave",
            "object_ref": {
                "repo": "aoa-techniques",
                "kind": "technique",
                "id": "AOA-T-0089",
                "version": "main",
            },
            "evidence_refs": [{"kind": "technique_bundle", "ref": "repo:aoa-techniques/TECHNIQUE_INDEX.md#AOA-T-0089"}],
            "payload": {"promotion_state": "promoted"},
        },
        memo_dir / "memo-writeback-receipts.jsonl": [
            {
                "event_kind": "memo_writeback_receipt",
                "event_id": "evt-memo-test-0001",
                "observed_at": "2026-04-06T20:04:00Z",
                "run_ref": "run-memo-001",
                "session_ref": "session:test-002",
                "actor_ref": "aoa-memo:writeback",
                "object_ref": {
                    "repo": "aoa-memo",
                    "kind": "memory_object",
                    "id": "memo.decision.2026-04-06.session-closeout",
                    "version": "main",
                },
                "evidence_refs": [{"kind": "memory_object", "ref": "repo:aoa-memo/generated/memory_object_catalog.min.json"}],
                "payload": {"target_kind": "decision"},
            },
            {
                "event_kind": "memo_growth_writeback_receipt",
                "event_id": "evt-memo-growth-test-0001",
                "observed_at": "2026-04-06T20:04:30Z",
                "run_ref": "run-memo-growth-001",
                "session_ref": "session:test-002",
                "actor_ref": "aoa-memo:growth-refinery-writeback",
                "object_ref": {
                    "repo": "aoa-memo",
                    "kind": "support_memory",
                    "id": "memo:session-growth-cycle-owner-reanchor-first",
                    "version": "main",
                },
                "evidence_refs": [{"kind": "support_memory", "ref": "repo:aoa-memo/generated/growth_refinery_writeback_lanes.min.json#growth_refinery_failure_lesson"}],
                "payload": {"target_kind": "failure_lesson"},
            },
        ],
        runtime_dir / "runtime-wave-closeouts.jsonl": {
            "event_kind": "runtime_wave_closeout_receipt",
            "event_id": "evt-runtime-closeout-test-0001",
            "observed_at": "2026-04-06T20:05:00Z",
            "run_ref": "run:abyss-stack:pilot-v1:W4:closeout",
            "session_ref": "session:abyss-stack:pilot-v1:W4:closeout",
            "actor_ref": "abyss-stack:aoa-local-ai-trials",
            "object_ref": {
                "repo": "abyss-stack",
                "kind": "runtime_wave_closeout",
                "id": "pilot-v1:W4",
                "version": "runtime",
            },
            "evidence_refs": [{"kind": "wave_closeout_json", "ref": "/srv/abyss-stack/Logs/local-ai-trials/pilot-v1/W4-closeout.json"}],
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
    }
    for path, receipt in receipts_by_path.items():
        if isinstance(receipt, list):
            payload = "\n".join(json.dumps(item) for item in receipt) + "\n"
        else:
            payload = json.dumps(receipt) + "\n"
        path.write_text(payload, encoding="utf-8")

    registry_path = tmp_path / "live_receipt_sources.json"
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "sources": [
                    {"name": "skills", "repo": "aoa-skills", "relative_path": ".aoa/live_receipts/session-harvest-family.jsonl"},
                    {"name": "skills-core", "repo": "aoa-skills", "relative_path": ".aoa/live_receipts/core-skill-applications.jsonl"},
                    {"name": "evals", "repo": "aoa-evals", "relative_path": ".aoa/live_receipts/eval-result-receipts.jsonl"},
                    {"name": "playbooks", "repo": "aoa-playbooks", "relative_path": ".aoa/live_receipts/playbook-receipts.jsonl"},
                    {"name": "techniques", "repo": "aoa-techniques", "relative_path": ".aoa/live_receipts/technique-receipts.jsonl"},
                    {"name": "memo", "repo": "aoa-memo", "relative_path": ".aoa/live_receipts/memo-writeback-receipts.jsonl"},
                    {"name": "runtime", "repo": "abyss-stack", "relative_path": ".aoa/live_receipts/runtime-wave-closeouts.jsonl"},
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    feed_output = tmp_path / "state" / "live_receipts.min.json"
    summary_output_dir = tmp_path / "state" / "generated"
    source_labels, receipt_count = module.refresh_live_state(
        registry_path=registry_path,
        federation_root=federation_root,
        feed_output=feed_output,
        summary_output_dir=summary_output_dir,
    )

    assert len(source_labels) == 7
    assert receipt_count == 8

    feed = json.loads(feed_output.read_text(encoding="utf-8"))
    assert len(feed) == 8

    repeated = json.loads(
        (summary_output_dir / "repeated_window_summary.min.json").read_text(encoding="utf-8")
    )
    counts = repeated["windows"][0]["event_counts_by_kind"]
    assert counts["core_skill_application_receipt"] == 1
    assert counts["playbook_review_harvest_receipt"] == 1
    assert counts["technique_promotion_receipt"] == 1
    assert counts["memo_growth_writeback_receipt"] == 1
    assert counts["memo_writeback_receipt"] == 1

    objects = json.loads(
        (summary_output_dir / "object_summary.min.json").read_text(encoding="utf-8")
    )["objects"]
    by_repo = {entry["object_ref"]["repo"]: entry for entry in objects if entry["object_ref"]["repo"] != "aoa-memo"}
    memo_writeback_total = sum(
        entry["receipt_counts_by_event_kind"].get("memo_writeback_receipt", 0)
        for entry in objects
        if entry["object_ref"]["repo"] == "aoa-memo"
    )
    memo_growth_total = sum(
        entry["receipt_counts_by_event_kind"].get("memo_growth_writeback_receipt", 0)
        for entry in objects
        if entry["object_ref"]["repo"] == "aoa-memo"
    )
    assert by_repo["aoa-playbooks"]["receipt_counts_by_event_kind"]["playbook_review_harvest_receipt"] == 1
    assert by_repo["aoa-techniques"]["receipt_counts_by_event_kind"]["technique_promotion_receipt"] == 1
    assert by_repo["abyss-stack"]["receipt_counts_by_event_kind"]["runtime_wave_closeout_receipt"] == 1
    assert memo_writeback_total == 1
    assert memo_growth_total == 1

    core_summary = json.loads(
        (summary_output_dir / "core_skill_application_summary.min.json").read_text(encoding="utf-8")
    )
    assert core_summary["skills"][0]["kernel_id"] == "project-core-session-growth-v1"
    assert core_summary["skills"][0]["skill_name"] == "aoa-session-donor-harvest"
    assert core_summary["skills"][0]["application_count"] == 1

    runtime_summary = json.loads(
        (summary_output_dir / "runtime_closeout_summary.min.json").read_text(encoding="utf-8")
    )
    assert runtime_summary["closeouts"][0]["program_id"] == "pilot-v1"
    assert runtime_summary["closeouts"][0]["wave_id"] == "W4"
    assert runtime_summary["closeouts"][0]["latest_gate_result"] == "pass"


def test_refresh_live_state_applies_supersedes_before_summary_counts(tmp_path: Path) -> None:
    module = load_refresh_module()
    federation_root = tmp_path / "srv"
    skills_dir = federation_root / "aoa-skills" / ".aoa" / "live_receipts"
    skills_dir.mkdir(parents=True)

    receipts = [
        {
            "event_kind": "core_skill_application_receipt",
            "event_id": "evt-core-0001",
            "observed_at": "2026-04-06T14:00:00Z",
            "run_ref": "run-001",
            "session_ref": "session:test-supersedes-refresh",
            "actor_ref": "aoa-skills:session-donor-harvest",
            "object_ref": {
                "repo": "aoa-skills",
                "kind": "skill",
                "id": "aoa-session-donor-harvest",
                "version": "main",
            },
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
            "observed_at": "2026-04-06T14:01:00Z",
            "run_ref": "run-002",
            "session_ref": "session:test-supersedes-refresh",
            "actor_ref": "aoa-skills:session-donor-harvest",
            "object_ref": {
                "repo": "aoa-skills",
                "kind": "skill",
                "id": "aoa-session-donor-harvest",
                "version": "main",
            },
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
    (skills_dir / "core-skill-applications.jsonl").write_text(
        "\n".join(json.dumps(item) for item in receipts) + "\n",
        encoding="utf-8",
    )

    registry_path = tmp_path / "live_receipt_sources.json"
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "sources": [
                    {"name": "skills-core", "repo": "aoa-skills", "relative_path": ".aoa/live_receipts/core-skill-applications.jsonl"},
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    feed_output = tmp_path / "state" / "live_receipts.min.json"
    summary_output_dir = tmp_path / "state" / "generated"
    source_labels, receipt_count = module.refresh_live_state(
        registry_path=registry_path,
        federation_root=federation_root,
        feed_output=feed_output,
        summary_output_dir=summary_output_dir,
    )

    assert source_labels == ["aoa-skills/.aoa/live_receipts/core-skill-applications.jsonl"]
    assert receipt_count == 1
    feed = json.loads(feed_output.read_text(encoding="utf-8"))
    assert [item["event_id"] for item in feed] == ["evt-core-0002"]
    summary = json.loads(
        (summary_output_dir / "core_skill_application_summary.min.json").read_text(encoding="utf-8")
    )
    assert summary["generated_from"]["total_receipts"] == 1
    assert summary["skills"][0]["application_count"] == 1
