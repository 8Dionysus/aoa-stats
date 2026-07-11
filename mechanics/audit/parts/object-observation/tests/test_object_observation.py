from __future__ import annotations

import importlib.util
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[5]
SRC_ROOT = REPO_ROOT / "src"
BUILD_VIEWS_PATH = REPO_ROOT / "scripts" / "build_views.py"
RECEIPT_FIXTURE_REF = (
    "stats/intake-contract/examples/session_harvest_family.receipts.example.json"
)
RECEIPT_FIXTURE_PATH = REPO_ROOT / RECEIPT_FIXTURE_REF
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder import object_observation  # noqa: E402
from aoa_stats_builder.receipt_abi import (  # noqa: E402
    generated_from,
    load_receipts,
    resolve_active_receipts,
)


_MISSING = object()


def load_build_views_module():
    spec = importlib.util.spec_from_file_location("build_views", BUILD_VIEWS_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def receipt(
    event_kind: str,
    event_id: str,
    observed_at: str,
    *,
    repo: str = "aoa-skills",
    kind: str = "skill",
    object_id: str = "aoa-example",
    version: str | object = _MISSING,
    session_ref: str | None = None,
    run_ref: str | None = None,
    evidence_count: int = 0,
    payload: dict[str, Any] | None = None,
    object_extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    object_ref: dict[str, Any] = {
        "repo": repo,
        "kind": kind,
        "id": object_id,
    }
    if version is not _MISSING:
        object_ref["version"] = version
    if object_extra:
        object_ref.update(object_extra)
    return {
        "event_kind": event_kind,
        "event_id": event_id,
        "observed_at": observed_at,
        "run_ref": run_ref or f"run:{event_id}",
        "session_ref": session_ref or f"session:{event_id}",
        "object_ref": object_ref,
        "evidence_refs": [
            {"kind": "test", "ref": f"evidence:{event_id}:{index}"}
            for index in range(evidence_count)
        ],
        "payload": payload or {},
    }


def test_projection_preserves_root_result_schema_committed_bytes_and_inputs() -> None:
    receipts = load_receipts([RECEIPT_FIXTURE_PATH])
    active_receipts = resolve_active_receipts(receipts)
    source = generated_from(active_receipts, [RECEIPT_FIXTURE_REF])
    original_receipts = deepcopy(active_receipts)
    original_source = deepcopy(source)
    facade = load_build_views_module()

    projected = object_observation.build_object_summary(active_receipts, source)

    assert facade.build_object_summary is object_observation.build_object_summary
    assert facade.object_key is object_observation.object_key
    assert projected == facade.build_object_summary(active_receipts, source)
    schema = facade.json.loads(
        (REPO_ROOT / "schemas" / "object-summary.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator(schema).validate(projected)
    assert facade.stable_json(projected).encode() == (
        REPO_ROOT / "generated" / "object_summary.min.json"
    ).read_bytes()
    assert active_receipts == original_receipts
    assert source == original_source


def test_repeated_window_uses_root_object_key_compatibility_alias() -> None:
    facade = load_build_views_module()
    observed_refs: list[dict[str, Any]] = []
    admitted = receipt(
        "observation_receipt",
        "evt-repeated-window-alias",
        "2026-04-05T12:00:00Z",
    )

    def tracked_object_key(
        object_ref: dict[str, Any],
    ) -> tuple[str, str, str, str]:
        observed_refs.append(object_ref)
        return object_observation.object_key(object_ref)

    facade.object_key = tracked_object_key
    summary = facade.build_repeated_window_summary([admitted], {})

    assert observed_refs == [admitted["object_ref"]]
    assert observed_refs[0] is admitted["object_ref"]
    assert summary["windows"][0]["unique_objects"] == 1


def test_grouping_uses_full_object_identity_and_keeps_sorted_counters() -> None:
    receipts = [
        receipt(
            "eval_result_receipt",
            "evt-z-unversioned",
            "2026-04-01T00:00:00Z",
            repo="z-repo",
            object_id="shared",
            evidence_count=2,
            payload={"verdict": "review"},
        ),
        receipt(
            "automation_candidate_receipt",
            "evt-z-empty-version",
            "2026-04-01T00:01:00Z",
            repo="z-repo",
            object_id="shared",
            version="",
            evidence_count=1,
        ),
        receipt(
            "progression_delta_receipt",
            "evt-z-v1",
            "2026-04-01T00:02:00Z",
            repo="z-repo",
            object_id="shared",
            version="v1",
            payload={"verdict": "hold"},
        ),
        receipt(
            "eval_result_receipt",
            "evt-a",
            "2026-04-01T00:03:00Z",
            repo="a-repo",
            object_id="other",
            payload={"verdict": "pass"},
        ),
    ]

    summary = object_observation.build_object_summary(receipts, {"source": "test"})

    assert [
        object_observation.object_key(item["object_ref"])
        for item in summary["objects"]
    ] == [
        ("a-repo", "skill", "other", ""),
        ("z-repo", "skill", "shared", ""),
        ("z-repo", "skill", "shared", "v1"),
    ]
    unversioned = summary["objects"][1]
    assert unversioned["receipt_count_total"] == 2
    assert unversioned["receipt_counts_by_event_kind"] == {
        "automation_candidate_receipt": 1,
        "eval_result_receipt": 1,
    }
    assert unversioned["evidence_ref_count"] == 3
    assert object_observation.object_key(receipts[0]["object_ref"]) == (
        "z-repo",
        "skill",
        "shared",
        "",
    )
    assert object_observation.object_key(receipts[1]["object_ref"]) == (
        "z-repo",
        "skill",
        "shared",
        "",
    )


def test_temporal_latest_and_input_order_verdicts_remain_distinct() -> None:
    receipts = [
        receipt(
            "observation_receipt",
            "evt-latest-z",
            "2026-04-05T12:00:00Z",
            session_ref="session:temporal-latest",
            run_ref="run:temporal-latest",
            object_extra={"label": "max-by-event-id"},
        ),
        receipt(
            "eval_result_receipt",
            "evt-eval-newer",
            "2026-04-05T11:00:00Z",
            payload={"verdict": "temporal-eval"},
        ),
        receipt(
            "progression_delta_receipt",
            "evt-progression-newer",
            "2026-04-05T10:00:00Z",
            payload={"verdict": "temporal-progression"},
        ),
        receipt(
            "observation_receipt",
            "evt-latest-a",
            "2026-04-05T12:00:00Z",
            session_ref="session:lower-event-id",
            run_ref="run:lower-event-id",
        ),
        receipt(
            "eval_result_receipt",
            "evt-eval-older",
            "2026-04-01T09:00:00Z",
            payload={"verdict": "input-last-eval"},
        ),
        receipt(
            "progression_delta_receipt",
            "evt-progression-older",
            "2026-04-01T08:00:00Z",
            payload={"verdict": "input-last-progression"},
        ),
    ]

    observed = object_observation.build_object_summary(receipts, {})["objects"][0]
    reversed_observed = object_observation.build_object_summary(
        list(reversed(receipts)), {}
    )["objects"][0]

    assert observed["first_observed_at"] == "2026-04-05T12:00:00Z"
    assert observed["last_observed_at"] == "2026-04-05T12:00:00Z"
    assert observed["latest_session_ref"] == "session:temporal-latest"
    assert observed["latest_run_ref"] == "run:temporal-latest"
    assert observed["object_ref"]["label"] == "max-by-event-id"
    assert observed["latest_eval_verdict"] == "input-last-eval"
    assert observed["latest_progression_verdict"] == "input-last-progression"
    assert reversed_observed["first_observed_at"] == "2026-04-01T08:00:00Z"
    assert reversed_observed["latest_session_ref"] == "session:temporal-latest"
    assert reversed_observed["latest_eval_verdict"] == "temporal-eval"
    assert reversed_observed["latest_progression_verdict"] == "temporal-progression"


def test_automation_counts_require_exact_boolean_truth() -> None:
    receipts = [
        receipt(
            "automation_candidate_receipt",
            "evt-auto-1",
            "2026-04-01T00:00:00Z",
            payload={"seed_ready": True, "checkpoint_required": False},
        ),
        receipt(
            "automation_candidate_receipt",
            "evt-auto-2",
            "2026-04-01T00:01:00Z",
            payload={"seed_ready": False, "checkpoint_required": True},
        ),
        receipt(
            "automation_candidate_receipt",
            "evt-auto-3",
            "2026-04-01T00:02:00Z",
            payload={"seed_ready": 1, "checkpoint_required": "true"},
        ),
        receipt(
            "automation_candidate_receipt",
            "evt-auto-4",
            "2026-04-01T00:03:00Z",
            payload={},
        ),
    ]

    observed = object_observation.build_object_summary(receipts, {})["objects"][0]

    assert observed["automation_candidate_counts"] == {
        "total": 4,
        "seed_ready": 1,
        "checkpoint_required": 1,
    }


def test_projection_shape_is_bounded_and_inputs_are_not_mutated() -> None:
    receipts = [
        receipt(
            "eval_result_receipt",
            "evt-pure",
            "2026-04-01T00:00:00Z",
            payload={"verdict": "pass"},
        )
    ]
    source = {"receipt_input_paths": ["memory"], "total_receipts": 1}
    original_receipts = deepcopy(receipts)
    original_source = deepcopy(source)

    projected = object_observation.build_object_summary(receipts, source)

    assert projected == {
        "schema_version": "aoa_stats_object_summary_v1",
        "generated_from": source,
        "objects": [
            {
                "object_ref": {
                    "repo": "aoa-skills",
                    "kind": "skill",
                    "id": "aoa-example",
                },
                "receipt_count_total": 1,
                "receipt_counts_by_event_kind": {"eval_result_receipt": 1},
                "first_observed_at": "2026-04-01T00:00:00Z",
                "last_observed_at": "2026-04-01T00:00:00Z",
                "latest_session_ref": "session:evt-pure",
                "latest_run_ref": "run:evt-pure",
                "evidence_ref_count": 0,
                "latest_eval_verdict": "pass",
                "latest_progression_verdict": None,
                "automation_candidate_counts": {
                    "total": 0,
                    "seed_ready": 0,
                    "checkpoint_required": 0,
                },
            }
        ],
    }
    assert receipts == original_receipts
    assert source == original_source
