from __future__ import annotations

import importlib.util
import json
import sys
from copy import deepcopy
from itertools import permutations
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


def committed_receipts() -> list[dict[str, object]]:
    return load_receipts(
        [
            REPO_ROOT
            / "stats"
            / "intake-contract"
            / "examples"
            / "session_harvest_family.receipts.example.json"
        ]
    )


def test_build_views_reexports_supersession_pruning_core() -> None:
    facade = load_build_views_module()

    assert (
        facade.build_supersession_drop_summary
        is candidate_lifecycle.build_supersession_drop_summary
    )


def test_supersession_pruning_core_is_schema_valid_and_non_mutating() -> None:
    receipts = committed_receipts()
    original_receipts = deepcopy(receipts)
    source = {
        "receipt_input_paths": [
            "stats/intake-contract/examples/session_harvest_family.receipts.example.json"
        ],
        "total_receipts": len(receipts),
        "latest_observed_at": max(receipt["observed_at"] for receipt in receipts),
    }

    summary = candidate_lifecycle.build_supersession_drop_summary(receipts, source)
    schema = json.loads(
        (
            REPO_ROOT / "schemas" / "supersession-drop-summary.schema.json"
        ).read_text(encoding="utf-8")
    )
    Draft202012Validator(schema).validate(summary)

    assert receipts == original_receipts


def test_supersession_pruning_is_stable_after_active_receipt_resolution() -> None:
    receipts = committed_receipts()
    active = resolve_active_receipts(receipts)
    reordered_active = resolve_active_receipts(list(reversed(receipts)))
    source = {
        "receipt_input_paths": ["canonical-active-receipts"],
        "total_receipts": len(active),
        "latest_observed_at": max(receipt["observed_at"] for receipt in active),
    }

    assert active == reordered_active
    assert candidate_lifecycle.build_supersession_drop_summary(
        active, source
    ) == candidate_lifecycle.build_supersession_drop_summary(
        reordered_active, source
    )


def explicit_turnover_receipts() -> list[dict[str, object]]:
    return [
        {
            "event_kind": "harvest_packet_receipt",
            "observed_at": "2026-04-11T12:00:00Z",
            "payload": {
                "evidence_density_summary": "reviewed",
                "candidate_lineage_entries": [
                    {
                        "candidate_ref": "candidate:session-growth:discarded",
                        "cluster_ref": "cluster:growth:reviewed-turnover",
                        "owner_hypothesis": "aoa-playbooks",
                        "owner_shape": "recurring-playbook-route",
                        "nearest_wrong_target": "aoa-playbooks",
                        "status_posture": "reanchor",
                        "axis_pressure": [],
                        "supersedes": [],
                        "merged_into": None,
                        "drop_reason": "nearest_wrong_target_rejected_during_review",
                        "evidence_refs": ["artifact:reviewed-turnover"],
                        "stages": {
                            "observed": "2026-04-11T11:40:00Z",
                            "reviewed": "2026-04-11T11:52:00Z",
                            "superseded_or_dropped": "2026-04-11T12:00:00Z",
                        },
                    }
                ],
            },
        },
        {
            "event_kind": "reviewed_owner_landing_receipt",
            "observed_at": "2026-04-11T12:02:00Z",
            "payload": {
                "candidate_ref": "candidate:session-growth:replacement",
                "owner_repo": "aoa-skills",
                "owner_shape": "skill",
                "status_posture": "reviewed",
                "reviewed_at": "2026-04-11T12:02:00Z",
                "evidence_refs": ["artifact:reviewed-owner-landing"],
                "supersedes": ["candidate:session-growth:older"],
            },
        },
        {
            "event_kind": "seed_owner_landing_trace_receipt",
            "observed_at": "2026-04-11T12:08:00Z",
            "payload": {
                "candidate_ref": "candidate:session-growth:replacement",
                "seed_ref": "seed:aoa:session-growth:replacement:v1",
                "owner_repo": "aoa-skills",
                "owner_shape": "skill",
                "outcome": "landed_owner_status",
                "merged_into": "object:aoa-skills:replacement:v1",
                "observed_at": "2026-04-11T12:08:00Z",
                "evidence_refs": ["artifact:seed-owner-landing-trace"],
            },
        },
    ]


def test_supersession_pruning_uses_only_explicit_turnover_in_any_receipt_order() -> (
    None
):
    receipts = explicit_turnover_receipts()
    original_receipts = deepcopy(receipts)
    source = {
        "receipt_input_paths": ["turnover"],
        "total_receipts": len(receipts),
        "latest_observed_at": "2026-04-11T12:08:00Z",
    }
    summaries = [
        candidate_lifecycle.build_supersession_drop_summary(list(order), source)
        for order in permutations(receipts)
    ]

    assert all(summary == summaries[0] for summary in summaries[1:])
    assert receipts == original_receipts
    summary = summaries[0]
    assert summary["drop_reason_counts"] == {
        "nearest_wrong_target_rejected_during_review": 1,
    }
    assert summary["supersession_counts"] == {
        "superseded_total": 0,
        "replacing_total": 1,
        "dropped_total": 1,
    }
    assert summary["merge_counts"] == {
        "total": 1,
        "by_owner_repo": {"aoa-skills": 1},
    }
    assert summary["owner_repo_counts"] == {
        "aoa-playbooks": 1,
        "aoa-skills": 1,
    }
    assert summary["reanchor_after_drop_counts"] == {"aoa-playbooks": 1}
