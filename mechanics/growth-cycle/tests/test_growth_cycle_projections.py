from __future__ import annotations

import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
MODULE_PATH = REPO_ROOT / "scripts" / "build_views.py"
RECEIPT_FIXTURE_REF = (
    "stats/intake-contract/examples/session_harvest_family.receipts.example.json"
)
RECEIPT_FIXTURE_PATH = REPO_ROOT / RECEIPT_FIXTURE_REF
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder import growth_cycle  # noqa: E402
from aoa_stats_builder.receipt_abi import generated_from, load_receipts  # noqa: E402


def load_build_views_module():
    spec = importlib.util.spec_from_file_location("build_views", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_checked_receipt_fixture() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    receipts = load_receipts([RECEIPT_FIXTURE_PATH])
    return receipts, generated_from(receipts, [RECEIPT_FIXTURE_REF])


def test_build_views_reexports_growth_cycle_core() -> None:
    facade = load_build_views_module()

    for name in (
        "build_fork_calibration_summary",
        "build_session_growth_branch_summary",
        "build_automation_pipeline_summary",
        "build_automation_followthrough_summary",
    ):
        assert getattr(facade, name) is getattr(growth_cycle, name)


def test_growth_cycle_core_is_schema_valid_and_does_not_mutate_inputs() -> None:
    receipts, source = load_checked_receipt_fixture()
    original_receipts = deepcopy(receipts)
    original_source = deepcopy(source)
    projections = (
        (
            growth_cycle.build_fork_calibration_summary,
            "fork-calibration-summary.schema.json",
        ),
        (
            growth_cycle.build_session_growth_branch_summary,
            "session-growth-branch-summary.schema.json",
        ),
        (
            growth_cycle.build_automation_pipeline_summary,
            "automation-pipeline-summary.schema.json",
        ),
        (
            growth_cycle.build_automation_followthrough_summary,
            "automation-followthrough-summary.schema.json",
        ),
    )

    for builder, schema_name in projections:
        summary = builder(receipts, source)
        schema = json.loads(
            (REPO_ROOT / "schemas" / schema_name).read_text(encoding="utf-8")
        )
        Draft202012Validator(schema).validate(summary)

    assert receipts == original_receipts
    assert source == original_source


def test_growth_cycle_core_is_stable_across_bounded_receipt_permutations() -> None:
    receipts, source = load_checked_receipt_fixture()
    split = len(receipts) // 2
    permutations = (
        receipts,
        list(reversed(receipts)),
        receipts[split:] + receipts[:split],
        receipts[::2] + receipts[1::2],
    )

    for builder in (
        growth_cycle.build_fork_calibration_summary,
        growth_cycle.build_session_growth_branch_summary,
        growth_cycle.build_automation_pipeline_summary,
        growth_cycle.build_automation_followthrough_summary,
    ):
        expected = builder(receipts, source)
        assert all(builder(permutation, source) == expected for permutation in permutations)


def test_automation_pipeline_summary_tracks_seed_readiness() -> None:
    receipts, source = load_checked_receipt_fixture()

    summary = growth_cycle.build_automation_pipeline_summary(receipts, source)
    pipeline = summary["pipelines"][0]

    assert pipeline["pipeline_ref"] == "pipeline:session-growth"
    assert pipeline["candidate_count"] == 2
    assert pipeline["seed_ready_count"] == 1
    assert pipeline["checkpoint_required_count"] == 1
    assert pipeline["next_artifact_hints"] == ["playbook_seed", "repair-prompt"]


def test_session_growth_branch_summary_tracks_reviewed_followthrough_hints() -> None:
    receipts, source = load_checked_receipt_fixture()

    summary = growth_cycle.build_session_growth_branch_summary(receipts, source)

    assert summary["schema_version"] == "aoa_stats_session_growth_branch_summary_v1"
    assert summary["window_ref"] == "window:2026-04"
    assert "total_score" not in summary
    assert summary["counts_by_recommended_next_skill"] == {
        "aoa-automation-opportunity-scan": 1,
        "aoa-session-route-forks": 1,
    }
    assert summary["defer_count"] == 1
    assert summary["counts_by_owner_target"] == {
        "aoa-playbooks": 1,
        "aoa-skills": 1,
    }
    assert summary["counts_by_status_posture"] == {
        "reanchor": 1,
        "thin-evidence": 1,
    }
    assert summary["reason_code_aggregates"] == {
        "approval_ambiguity": 1,
        "multiple_plausible_next_moves": 1,
        "repeated_manual_route": 1,
    }


def test_automation_followthrough_summary_tracks_blockers_and_real_run_review() -> (
    None
):
    receipts, source = load_checked_receipt_fixture()

    summary = growth_cycle.build_automation_followthrough_summary(receipts, source)

    assert summary["schema_version"] == "aoa_stats_automation_followthrough_summary_v1"
    assert summary["window_ref"] == "window:2026-04"
    assert "total_score" not in summary
    assert summary["automation_candidate_count"] == 2
    assert summary["seed_ready_count"] == 1
    assert summary["not_now_count"] == 1
    assert summary["checkpoint_required_count"] == 1
    assert summary["playbook_seed_candidate_count"] == 1
    assert summary["real_run_reviewed_count"] == 1
    assert summary["defer_count"] == 1
    assert summary["blocker_aggregates"] == {
        "approval_ambiguity": 1,
        "schedule_out_of_scope": 2,
    }


def test_automation_pipeline_summary_falls_back_to_manual_route_ref() -> None:
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

    summary = growth_cycle.build_automation_pipeline_summary(
        receipts, {"receipt_input_paths": ["memory"], "total_receipts": len(receipts)}
    )

    assert summary["pipelines"][0]["pipeline_ref"] == "route:manual-closeout-loop"
    assert summary["pipelines"][0]["candidate_count"] == 1


def test_fork_calibration_summary_falls_back_to_branch_id_count() -> None:
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

    summary = growth_cycle.build_fork_calibration_summary(
        receipts, {"receipt_input_paths": ["memory"], "total_receipts": len(receipts)}
    )

    assert summary["routes"][0]["route_ref"] == "route:test-fork-calibration"
    assert summary["routes"][0]["max_option_count"] == 3
