from __future__ import annotations

import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[5]
SRC_ROOT = REPO_ROOT / "src"
MODULE_PATH = REPO_ROOT / "scripts" / "build_views.py"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder import candidate_lifecycle  # noqa: E402
from aoa_stats_builder.receipt_abi import (  # noqa: E402
    load_receipts,
    resolve_active_receipts,
)


def load_build_views_module():
    spec = importlib.util.spec_from_file_location("build_views", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_candidate_lifecycle_module():
    return candidate_lifecycle


def test_build_views_reexports_candidate_lineage_core() -> None:
    facade = load_build_views_module()
    core = load_candidate_lifecycle_module()

    assert (
        facade.build_candidate_lineage_summary
        is core.build_candidate_lineage_summary
    )


def test_candidate_lineage_core_is_schema_valid_and_does_not_mutate_receipts() -> (
    None
):
    receipts = load_receipts(
        [
            REPO_ROOT
            / "stats"
            / "intake-contract"
            / "examples"
            / "session_harvest_family.receipts.example.json"
        ]
    )
    original_receipts = deepcopy(receipts)
    source = {
        "receipt_input_paths": [
            "stats/intake-contract/examples/session_harvest_family.receipts.example.json"
        ],
        "total_receipts": len(receipts),
        "latest_observed_at": max(receipt["observed_at"] for receipt in receipts),
    }
    summary = candidate_lifecycle.build_candidate_lineage_summary(receipts, source)
    schema = json.loads(
        (
            REPO_ROOT / "schemas" / "candidate_lineage_summary.schema.json"
        ).read_text(encoding="utf-8")
    )
    Draft202012Validator(schema).validate(summary)

    assert receipts == original_receipts


def test_candidate_lineage_core_is_stable_after_active_receipt_resolution() -> None:
    receipts = load_receipts(
        [
            REPO_ROOT
            / "stats"
            / "intake-contract"
            / "examples"
            / "session_harvest_family.receipts.example.json"
        ]
    )
    source = {
        "receipt_input_paths": ["canonical-active-receipts"],
        "total_receipts": len(receipts),
        "latest_observed_at": max(receipt["observed_at"] for receipt in receipts),
    }
    active = resolve_active_receipts(receipts)
    reordered_active = resolve_active_receipts(list(reversed(receipts)))

    assert active == reordered_active

    assert candidate_lifecycle.build_candidate_lineage_summary(
        active, source
    ) == candidate_lifecycle.build_candidate_lineage_summary(
        reordered_active, source
    )


def make_harvest_packet_receipt(
    *,
    event_id: str,
    observed_at: str,
    candidate_lineage_entries: list[dict[str, object]],
    evidence_density_summary: str = "reviewed",
) -> dict[str, object]:
    return {
        "event_kind": "harvest_packet_receipt",
        "event_id": event_id,
        "observed_at": observed_at,
        "run_ref": "run-test-growth-lineage",
        "session_ref": "session:test-growth-lineage",
        "actor_ref": "aoa-skills:session-donor-harvest",
        "object_ref": {
            "repo": "aoa-skills",
            "kind": "skill",
            "id": "aoa-session-donor-harvest",
            "version": "main",
        },
        "evidence_refs": [
            {
                "kind": "candidate_lineage_receipt",
                "ref": "repo:aoa-skills/examples/session_growth_artifacts/candidate_lineage_receipt.alpha.json",
                "role": "primary",
            }
        ],
        "payload": {
            "evidence_density_summary": evidence_density_summary,
            "candidate_lineage_entries": candidate_lineage_entries,
        },
    }


def make_lineage_entry(
    *,
    candidate_ref: str,
    cluster_ref: str,
    owner_hypothesis: str,
    owner_shape: str,
    nearest_wrong_target: str | None,
    status_posture: str,
    stages: dict[str, str | None],
    axis_pressure: list[str] | None = None,
    supersedes: list[str] | None = None,
    merged_into: str | None = None,
    drop_reason: str | None = None,
) -> dict[str, object]:
    return {
        "candidate_ref": candidate_ref,
        "cluster_ref": cluster_ref,
        "owner_hypothesis": owner_hypothesis,
        "owner_shape": owner_shape,
        "nearest_wrong_target": nearest_wrong_target,
        "status_posture": status_posture,
        "axis_pressure": axis_pressure or [],
        "supersedes": supersedes or [],
        "merged_into": merged_into,
        "drop_reason": drop_reason,
        "evidence_refs": [
            "repo:aoa-skills/examples/session_growth_artifacts/candidate_lineage_receipt.alpha.json"
        ],
        "stages": stages,
    }


def test_candidate_lineage_summary_stays_reviewed_only_and_no_score() -> None:
    module = load_candidate_lifecycle_module()
    receipts = load_receipts(
        [
            REPO_ROOT
            / "stats"
            / "intake-contract"
            / "examples"
            / "session_harvest_family.receipts.example.json"
        ]
    )

    summary = module.build_candidate_lineage_summary(
        receipts,
        {
            "receipt_input_paths": [
                "stats/intake-contract/examples/session_harvest_family.receipts.example.json"
            ],
            "total_receipts": len(receipts),
            "latest_observed_at": max(receipt["observed_at"] for receipt in receipts),
        },
    )

    assert summary["schema_version"] == "aoa_stats_candidate_lineage_summary_v1"
    assert "total_score" not in summary
    assert summary["status_posture_counts"] == {
        "early": 1,
        "reanchor": 1,
    }
    assert summary["misroute_counts"] == {
        "total": 1,
        "by_target": {
            "aoa-playbooks": 1,
        },
        "owner_ambiguity_total": 0,
    }
    assert summary["supersession_counts"] == {
        "superseded_total": 0,
        "dropped_total": 1,
    }


def test_candidate_lineage_summary_orders_mixed_timezone_timestamps() -> None:
    module = load_candidate_lifecycle_module()
    receipts = [
        {
            "event_kind": "harvest_packet_receipt",
            "observed_at": "2026-04-11T12:00:00",
            "payload": {
                "evidence_density_summary": "reviewed",
                "candidate_lineage_entries": [
                    {
                        "candidate_ref": "candidate:growth:mixed-timezone",
                        "cluster_ref": "cluster:growth:mixed-timezone",
                        "owner_hypothesis": "aoa-skills",
                        "owner_shape": "skill",
                        "nearest_wrong_target": "aoa-playbooks",
                        "status_posture": "early",
                        "axis_pressure": ["change_legibility"],
                        "supersedes": [],
                        "merged_into": None,
                        "drop_reason": None,
                        "evidence_refs": [
                            "repo:aoa-skills/examples/session_growth_artifacts/harvest_packet.alpha.json"
                        ],
                        "stages": {
                            "observed": "2026-04-11T12:00:00",
                            "checkpointed": "2026-04-11T12:05:00Z",
                        },
                    }
                ],
            },
        }
    ]

    summary = module.build_candidate_lineage_summary(
        receipts,
        {
            "receipt_input_paths": ["mixed-timezone"],
            "total_receipts": len(receipts),
            "latest_observed_at": "2026-04-11T12:00:00",
        },
    )

    assert summary["stage_counts"]["observed"] == 1
    assert summary["stage_counts"]["checkpointed"] == 1


def test_candidate_lineage_summary_richer_reviewed_fixture_keeps_stage_and_aggregate_truth() -> (
    None
):
    module = load_candidate_lifecycle_module()
    receipts = load_receipts(
        [
            REPO_ROOT
            / "mechanics/method-growth/parts/candidate-lineage/examples/reviewed_candidate_lineage_receipts.example.json"
        ]
    )

    summary = module.build_candidate_lineage_summary(
        receipts,
        {
            "receipt_input_paths": [
                "mechanics/method-growth/parts/candidate-lineage/examples/reviewed_candidate_lineage_receipts.example.json"
            ],
            "total_receipts": len(receipts),
            "latest_observed_at": max(receipt["observed_at"] for receipt in receipts),
        },
    )

    assert summary["stage_counts"] == {
        "observed": 3,
        "checkpointed": 3,
        "reviewed": 3,
        "harvested": 3,
        "seeded": 2,
        "planted": 1,
        "proved": 1,
        "promoted": 1,
        "superseded_or_dropped": 2,
    }
    assert summary["owner_target_counts"] == {
        "aoa-evals": 1,
        "aoa-playbooks": 2,
    }
    assert summary["status_posture_counts"] == {
        "reanchor": 1,
        "stable": 2,
    }
    assert summary["time_to_stage_median_days"] == {
        "checkpointed": 0.5,
        "reviewed": 1.0,
        "harvested": 1.5,
        "seeded": 2.5,
        "planted": 3.0,
        "proved": 4.0,
        "promoted": 5.0,
    }
    assert summary["misroute_counts"] == {
        "total": 1,
        "by_target": {
            "aoa-skills": 1,
        },
        "owner_ambiguity_total": 0,
    }
    assert summary["supersession_counts"] == {
        "superseded_total": 1,
        "dropped_total": 1,
    }


def test_candidate_lineage_summary_ignores_unreviewed_checkpoint_like_receipts() -> (
    None
):
    module = load_candidate_lifecycle_module()
    receipts = [
        make_harvest_packet_receipt(
            event_id="evt-harvest-checkpoint-like",
            observed_at="2026-04-12T10:00:00Z",
            evidence_density_summary="checkpoint",
            candidate_lineage_entries=[
                make_lineage_entry(
                    candidate_ref="candidate:growth:checkpoint-like",
                    cluster_ref="cluster:growth:checkpoint-like",
                    owner_hypothesis="aoa-skills",
                    owner_shape="skill",
                    nearest_wrong_target="aoa-playbooks",
                    status_posture="early",
                    axis_pressure=["change_legibility"],
                    stages={
                        "observed": "2026-04-12T09:00:00Z",
                        "checkpointed": "2026-04-12T09:05:00Z",
                        "reviewed": "2026-04-12T09:10:00Z",
                        "harvested": "2026-04-12T09:15:00Z",
                        "seeded": "2026-04-12T09:20:00Z",
                        "planted": "2026-04-12T09:25:00Z",
                        "proved": "2026-04-12T09:30:00Z",
                        "promoted": "2026-04-12T09:35:00Z",
                        "superseded_or_dropped": None,
                    },
                )
            ],
        )
    ]

    summary = module.build_candidate_lineage_summary(
        receipts,
        {
            "receipt_input_paths": ["checkpoint-like"],
            "total_receipts": len(receipts),
            "latest_observed_at": "2026-04-12T10:00:00Z",
        },
    )

    assert summary["stage_counts"] == {stage: 0 for stage in module.FUNNEL_STAGES}
    assert summary["owner_target_counts"] == {}
    assert summary["misroute_counts"] == {
        "total": 0,
        "by_target": {},
        "owner_ambiguity_total": 0,
    }
    assert summary["supersession_counts"] == {
        "superseded_total": 0,
        "dropped_total": 0,
    }
    assert summary["time_to_stage_median_days"] == {
        stage: None for stage in module.TIME_TO_STAGE_KEYS
    }


def test_candidate_lineage_summary_does_not_infer_seeded_from_harvested_only() -> None:
    module = load_candidate_lifecycle_module()
    receipts = [
        make_harvest_packet_receipt(
            event_id="evt-harvested-only",
            observed_at="2026-04-12T12:00:00Z",
            candidate_lineage_entries=[
                make_lineage_entry(
                    candidate_ref="candidate:growth:harvested-only",
                    cluster_ref="cluster:growth:harvested-only",
                    owner_hypothesis="aoa-skills",
                    owner_shape="skill",
                    nearest_wrong_target="aoa-playbooks",
                    status_posture="early",
                    stages={
                        "observed": "2026-04-12T09:00:00Z",
                        "checkpointed": "2026-04-12T09:15:00Z",
                        "reviewed": "2026-04-12T09:30:00Z",
                        "harvested": "2026-04-12T10:00:00Z",
                        "seeded": None,
                        "planted": None,
                        "proved": None,
                        "promoted": None,
                        "superseded_or_dropped": None,
                    },
                )
            ],
        )
    ]

    summary = module.build_candidate_lineage_summary(
        receipts,
        {
            "receipt_input_paths": ["harvested-only"],
            "total_receipts": len(receipts),
            "latest_observed_at": "2026-04-12T12:00:00Z",
        },
    )

    assert summary["stage_counts"]["harvested"] == 1
    assert summary["stage_counts"]["seeded"] == 0
    assert summary["stage_counts"]["planted"] == 0
    assert summary["time_to_stage_median_days"]["seeded"] is None
    assert summary["time_to_stage_median_days"]["planted"] is None


def test_candidate_lineage_summary_does_not_infer_planted_from_seeded_only() -> None:
    module = load_candidate_lifecycle_module()
    receipts = [
        make_harvest_packet_receipt(
            event_id="evt-seeded-only",
            observed_at="2026-04-12T16:00:00Z",
            candidate_lineage_entries=[
                make_lineage_entry(
                    candidate_ref="candidate:growth:seeded-only",
                    cluster_ref="cluster:growth:seeded-only",
                    owner_hypothesis="aoa-skills",
                    owner_shape="skill",
                    nearest_wrong_target="aoa-playbooks",
                    status_posture="stable",
                    stages={
                        "observed": "2026-04-12T09:00:00Z",
                        "checkpointed": "2026-04-12T09:30:00Z",
                        "reviewed": "2026-04-12T10:00:00Z",
                        "harvested": "2026-04-12T11:00:00Z",
                        "seeded": "2026-04-12T12:00:00Z",
                        "planted": None,
                        "proved": None,
                        "promoted": None,
                        "superseded_or_dropped": None,
                    },
                )
            ],
        )
    ]

    summary = module.build_candidate_lineage_summary(
        receipts,
        {
            "receipt_input_paths": ["seeded-only"],
            "total_receipts": len(receipts),
            "latest_observed_at": "2026-04-12T16:00:00Z",
        },
    )

    assert summary["stage_counts"]["seeded"] == 1
    assert summary["stage_counts"]["planted"] == 0
    assert summary["stage_counts"]["proved"] == 0
    assert summary["stage_counts"]["promoted"] == 0
    assert summary["time_to_stage_median_days"]["planted"] is None
    assert summary["time_to_stage_median_days"]["proved"] is None
    assert summary["time_to_stage_median_days"]["promoted"] is None
