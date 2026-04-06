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
    skills_dir = federation_root / "aoa-skills" / "examples"
    evals_dir = federation_root / "aoa-evals" / "examples"
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

    (skills_dir / "session_harvest_family.receipts.example.json").write_text(
        json.dumps(skill_receipt, indent=2) + "\n",
        encoding="utf-8",
    )
    (evals_dir / "eval_result_receipt.example.json").write_text(
        json.dumps(eval_receipt, indent=2) + "\n",
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
                        "relative_path": "examples/session_harvest_family.receipts.example.json",
                    },
                    {
                        "name": "evals",
                        "repo": "aoa-evals",
                        "relative_path": "examples/eval_result_receipt.example.json",
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
        "aoa-skills/examples/session_harvest_family.receipts.example.json",
        "aoa-evals/examples/eval_result_receipt.example.json",
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
