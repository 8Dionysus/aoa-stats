from __future__ import annotations

import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[3]
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


def test_build_views_reexports_candidate_lifecycle_core() -> None:
    facade = load_build_views_module()
    core = load_candidate_lifecycle_module()

    for name in (
        "build_candidate_lineage_summary",
        "build_owner_landing_summary",
        "build_supersession_drop_summary",
    ):
        assert getattr(facade, name) is getattr(core, name)


def test_candidate_lifecycle_core_is_schema_valid_and_does_not_mutate_receipts() -> (
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
    projections = (
        (
            candidate_lifecycle.build_candidate_lineage_summary,
            "candidate_lineage_summary.schema.json",
        ),
        (
            candidate_lifecycle.build_owner_landing_summary,
            "owner-landing-summary.schema.json",
        ),
        (
            candidate_lifecycle.build_supersession_drop_summary,
            "supersession-drop-summary.schema.json",
        ),
    )

    for builder, schema_name in projections:
        summary = builder(receipts, source)
        schema = json.loads(
            (REPO_ROOT / "schemas" / schema_name).read_text(encoding="utf-8")
        )
        Draft202012Validator(schema).validate(summary)

    assert receipts == original_receipts


def test_candidate_lifecycle_core_is_stable_after_active_receipt_resolution() -> None:
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

    for builder in (
        candidate_lifecycle.build_candidate_lineage_summary,
        candidate_lifecycle.build_owner_landing_summary,
        candidate_lifecycle.build_supersession_drop_summary,
    ):
        assert builder(active, source) == builder(reordered_active, source)


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


def make_reviewed_owner_landing_receipt(
    *,
    event_id: str,
    observed_at: str,
    candidate_ref: str,
    owner_repo: str = "aoa-skills",
    owner_shape: str = "skill",
    status_posture: str = "early",
    supersedes: list[str] | None = None,
    superseded_by: str | None = None,
    merged_into: str | None = None,
    drop_reason: str | None = None,
    drop_stage: str | None = None,
) -> dict[str, object]:
    return {
        "event_kind": "reviewed_owner_landing_receipt",
        "event_id": event_id,
        "observed_at": observed_at,
        "run_ref": "run-test-owner-landing",
        "session_ref": "session:test-owner-landing",
        "actor_ref": "aoa-skills:reviewed-owner-landing",
        "object_ref": {
            "repo": "aoa-skills",
            "kind": "owner_status_surface",
            "id": "reviewed_owner_landing_bundle",
            "version": "v1",
        },
        "evidence_refs": [
            {
                "kind": "owner_landing_bundle",
                "ref": "repo:aoa-skills/examples/reviewed_owner_landing_bundle.example.json",
            }
        ],
        "payload": {
            "schema_version": "reviewed_owner_landing_bundle_v1",
            "bundle_kind": "reviewed_owner_landing_bundle",
            "cluster_ref": "cluster:growth:aoa-sdk-checkpoint-auto-capture-verify-green",
            "candidate_ref": candidate_ref,
            "owner_repo": owner_repo,
            "owner_shape": owner_shape,
            "nearest_wrong_target": "aoa-playbooks",
            "status_posture": status_posture,
            "reviewed_at": observed_at,
            "evidence_refs": [
                "repo:aoa-skills/examples/session_growth_artifacts/candidate_lineage_receipt.alpha.json"
            ],
            "status_note": "reviewed owner landing",
            "supersedes": supersedes or [],
            "superseded_by": superseded_by,
            "merged_into": merged_into,
            "drop_reason": drop_reason,
            "drop_stage": drop_stage,
            "drop_evidence_refs": [] if drop_reason is None else ["artifact:drop"],
        },
    }


def make_seed_owner_landing_trace_receipt(
    *,
    event_id: str,
    observed_at: str,
    candidate_ref: str,
    seed_ref: str,
    owner_repo: str = "aoa-skills",
    owner_shape: str = "skill",
    outcome: str = "landed_owner_status",
    merged_into: str | None = None,
    superseded_by: str | None = None,
    drop_reason: str | None = None,
) -> dict[str, object]:
    return {
        "event_kind": "seed_owner_landing_trace_receipt",
        "event_id": event_id,
        "observed_at": observed_at,
        "run_ref": "run-test-owner-landing",
        "session_ref": "session:test-owner-landing",
        "actor_ref": "Dionysus:seed-owner-landing-trace",
        "object_ref": {
            "repo": "Dionysus",
            "kind": "seed_owner_landing_trace",
            "id": "reviewed-donor-harvest",
            "version": "v1",
        },
        "evidence_refs": [
            {
                "kind": "seed_owner_landing_trace",
                "ref": "repo:Dionysus/examples/seed_owner_landing_trace.example.json",
            }
        ],
        "payload": {
            "schema_version": "dionysus_seed_owner_landing_trace_v1",
            "cluster_ref": "cluster:growth:aoa-sdk-checkpoint-auto-capture-verify-green",
            "candidate_ref": candidate_ref,
            "seed_ref": seed_ref,
            "owner_repo": owner_repo,
            "owner_shape": owner_shape,
            "outcome": outcome,
            "owner_status_ref": "repo:aoa-skills/examples/reviewed_owner_landing_bundle.example.json",
            "object_ref": None,
            "merged_into": merged_into,
            "superseded_by": superseded_by,
            "drop_reason": drop_reason,
            "observed_at": observed_at,
            "evidence_refs": [
                "repo:Dionysus/examples/seed_lineage_entry.example.json",
                "repo:aoa-skills/examples/reviewed_owner_landing_bundle.example.json",
            ],
        },
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


def test_owner_landing_summary_reads_reviewed_owner_landings_and_seed_traces() -> None:
    module = load_candidate_lifecycle_module()
    receipts = [
        make_reviewed_owner_landing_receipt(
            event_id="evt-owner-landing-test-0001",
            observed_at="2026-04-11T12:00:00Z",
            candidate_ref="candidate:session-growth:reviewed-donor-harvest",
            status_posture="thin-evidence",
        ),
        make_seed_owner_landing_trace_receipt(
            event_id="evt-seed-owner-trace-test-0001",
            observed_at="2026-04-11T12:10:00Z",
            candidate_ref="candidate:session-growth:reviewed-donor-harvest",
            seed_ref="seed:aoa:session-growth:reviewed-donor-harvest:v1",
            outcome="landed_owner_status",
        ),
    ]

    summary = module.build_owner_landing_summary(
        receipts,
        {
            "receipt_input_paths": ["owner-landing"],
            "total_receipts": len(receipts),
            "latest_observed_at": "2026-04-11T12:10:00Z",
        },
    )

    assert summary["schema_version"] == "aoa_stats_owner_landing_summary_v1"
    assert "total_score" not in summary
    assert summary["owner_repo_counts"] == {"aoa-skills": 1}
    assert summary["owner_shape_counts"] == {"skill": 1}
    assert summary["status_posture_counts"] == {"thin-evidence": 1}
    assert summary["landing_outcome_counts"] == {"landed_owner_status": 1}
    assert summary["time_to_outcome_median_days"]["landed_owner_status"] == 0.01
    assert summary["time_to_outcome_median_days"]["merged"] is None


def test_owner_landing_summary_keeps_earliest_review_for_outcome_duration() -> None:
    module = load_candidate_lifecycle_module()
    receipts = [
        make_reviewed_owner_landing_receipt(
            event_id="evt-owner-landing-test-early",
            observed_at="2026-04-11T12:00:00Z",
            candidate_ref="candidate:session-growth:reviewed-donor-harvest",
            status_posture="thin-evidence",
        ),
        make_reviewed_owner_landing_receipt(
            event_id="evt-owner-landing-test-late",
            observed_at="2026-04-12T12:00:00Z",
            candidate_ref="candidate:session-growth:reviewed-donor-harvest",
            status_posture="reviewed",
        ),
        make_reviewed_owner_landing_receipt(
            event_id="evt-owner-landing-test-middle-arrives-late",
            observed_at="2026-04-11T18:00:00Z",
            candidate_ref="candidate:session-growth:reviewed-donor-harvest",
            status_posture="middle",
        ),
        make_seed_owner_landing_trace_receipt(
            event_id="evt-seed-owner-trace-test-late",
            observed_at="2026-04-13T12:00:00Z",
            candidate_ref="candidate:session-growth:reviewed-donor-harvest",
            seed_ref="seed:aoa:session-growth:reviewed-donor-harvest:v1",
            outcome="landed_owner_status",
        ),
    ]

    summary = module.build_owner_landing_summary(
        receipts,
        {
            "receipt_input_paths": ["owner-landing"],
            "total_receipts": len(receipts),
            "latest_observed_at": "2026-04-13T12:00:00Z",
        },
    )

    assert summary["status_posture_counts"] == {"reviewed": 1}
    assert summary["time_to_outcome_median_days"]["landed_owner_status"] == 2.0


def test_owner_landing_summary_counts_unknown_outcome_without_duration_bucket() -> None:
    module = load_candidate_lifecycle_module()
    receipts = [
        make_reviewed_owner_landing_receipt(
            event_id="evt-owner-landing-test-unknown",
            observed_at="2026-04-11T12:00:00Z",
            candidate_ref="candidate:session-growth:experimental",
        ),
        make_seed_owner_landing_trace_receipt(
            event_id="evt-seed-owner-trace-test-unknown",
            observed_at="2026-04-12T12:00:00Z",
            candidate_ref="candidate:session-growth:experimental",
            seed_ref="seed:aoa:session-growth:experimental:v1",
            outcome="experimental_outcome",
        ),
    ]

    summary = module.build_owner_landing_summary(
        receipts,
        {
            "receipt_input_paths": ["owner-landing"],
            "total_receipts": len(receipts),
            "latest_observed_at": "2026-04-12T12:00:00Z",
        },
    )

    assert summary["landing_outcome_counts"] == {"experimental_outcome": 1}
    assert "experimental_outcome" not in summary["time_to_outcome_median_days"]


def test_supersession_drop_summary_uses_explicit_turnover_only() -> None:
    module = load_candidate_lifecycle_module()
    receipts = [
        make_harvest_packet_receipt(
            event_id="evt-harvest-test-0001",
            observed_at="2026-04-11T12:00:00Z",
            candidate_lineage_entries=[
                make_lineage_entry(
                    candidate_ref="candidate:session-growth:nearest-wrong-playbook-route",
                    cluster_ref="cluster:growth:aoa-sdk-checkpoint-auto-capture-verify-green",
                    owner_hypothesis="aoa-playbooks",
                    owner_shape="recurring-playbook-route",
                    nearest_wrong_target="aoa-playbooks",
                    status_posture="reanchor",
                    stages={
                        "observed": "2026-04-11T11:40:00Z",
                        "checkpointed": "2026-04-11T11:45:00Z",
                        "reviewed": "2026-04-11T11:52:00Z",
                        "harvested": None,
                        "seeded": None,
                        "planted": None,
                        "proved": None,
                        "promoted": None,
                        "superseded_or_dropped": "2026-04-11T12:00:00Z",
                    },
                    drop_reason="nearest_wrong_target_rejected_during_reviewed_harvest",
                )
            ],
        ),
        make_reviewed_owner_landing_receipt(
            event_id="evt-owner-landing-test-0002",
            observed_at="2026-04-11T12:02:00Z",
            candidate_ref="candidate:session-growth:replacement",
            supersedes=["candidate:session-growth:older"],
        ),
        make_seed_owner_landing_trace_receipt(
            event_id="evt-seed-owner-trace-test-0002",
            observed_at="2026-04-11T12:08:00Z",
            candidate_ref="candidate:session-growth:replacement",
            seed_ref="seed:aoa:session-growth:replacement:v1",
            merged_into="object:aoa-skills:aoa-session-donor-harvest:v1",
        ),
    ]

    summary = module.build_supersession_drop_summary(
        receipts,
        {
            "receipt_input_paths": ["turnover"],
            "total_receipts": len(receipts),
            "latest_observed_at": "2026-04-11T12:08:00Z",
        },
    )

    assert summary["schema_version"] == "aoa_stats_supersession_drop_summary_v1"
    assert summary["drop_reason_counts"] == {
        "nearest_wrong_target_rejected_during_reviewed_harvest": 1,
    }
    assert summary["supersession_counts"] == {
        "superseded_total": 0,
        "replacing_total": 1,
        "dropped_total": 1,
    }
    assert summary["merge_counts"] == {
        "total": 1,
        "by_owner_repo": {
            "aoa-skills": 1,
        },
    }
    assert summary["owner_repo_counts"] == {
        "aoa-playbooks": 1,
        "aoa-skills": 1,
    }
    assert summary["reanchor_after_drop_counts"] == {
        "aoa-playbooks": 1,
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
