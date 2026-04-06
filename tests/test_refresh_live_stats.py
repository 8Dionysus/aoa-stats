from __future__ import annotations

import importlib.util
import json
from pathlib import Path


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


def test_refresh_live_state_combines_playbook_technique_and_memo_sources(tmp_path: Path) -> None:
    module = load_refresh_module()
    federation_root = tmp_path / "srv"
    skills_dir = federation_root / "aoa-skills" / ".aoa" / "live_receipts"
    evals_dir = federation_root / "aoa-evals" / ".aoa" / "live_receipts"
    playbooks_dir = federation_root / "aoa-playbooks" / ".aoa" / "live_receipts"
    techniques_dir = federation_root / "aoa-techniques" / ".aoa" / "live_receipts"
    memo_dir = federation_root / "aoa-memo" / ".aoa" / "live_receipts"
    for path in (skills_dir, evals_dir, playbooks_dir, techniques_dir, memo_dir):
        path.mkdir(parents=True)

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
        memo_dir / "memo-writeback-receipts.jsonl": {
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
    }
    for path, receipt in receipts_by_path.items():
        path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")

    registry_path = tmp_path / "live_receipt_sources.json"
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "sources": [
                    {"name": "skills", "repo": "aoa-skills", "relative_path": ".aoa/live_receipts/session-harvest-family.jsonl"},
                    {"name": "evals", "repo": "aoa-evals", "relative_path": ".aoa/live_receipts/eval-result-receipts.jsonl"},
                    {"name": "playbooks", "repo": "aoa-playbooks", "relative_path": ".aoa/live_receipts/playbook-receipts.jsonl"},
                    {"name": "techniques", "repo": "aoa-techniques", "relative_path": ".aoa/live_receipts/technique-receipts.jsonl"},
                    {"name": "memo", "repo": "aoa-memo", "relative_path": ".aoa/live_receipts/memo-writeback-receipts.jsonl"},
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

    assert len(source_labels) == 5
    assert receipt_count == 5

    feed = json.loads(feed_output.read_text(encoding="utf-8"))
    assert len(feed) == 5

    repeated = json.loads(
        (summary_output_dir / "repeated_window_summary.min.json").read_text(encoding="utf-8")
    )
    counts = repeated["windows"][0]["event_counts_by_kind"]
    assert counts["playbook_review_harvest_receipt"] == 1
    assert counts["technique_promotion_receipt"] == 1
    assert counts["memo_writeback_receipt"] == 1

    objects = json.loads(
        (summary_output_dir / "object_summary.min.json").read_text(encoding="utf-8")
    )["objects"]
    by_repo = {entry["object_ref"]["repo"]: entry for entry in objects}
    assert by_repo["aoa-playbooks"]["receipt_counts_by_event_kind"]["playbook_review_harvest_receipt"] == 1
    assert by_repo["aoa-techniques"]["receipt_counts_by_event_kind"]["technique_promotion_receipt"] == 1
    assert by_repo["aoa-memo"]["receipt_counts_by_event_kind"]["memo_writeback_receipt"] == 1
