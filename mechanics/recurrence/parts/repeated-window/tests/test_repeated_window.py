from __future__ import annotations

from copy import deepcopy
import importlib.util
from itertools import permutations
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parents[5]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder import receipt_abi, repeated_window  # noqa: E402
from aoa_stats_builder.object_observation import object_key  # noqa: E402


def load_build_views_module():
    script_path = REPO_ROOT / "scripts" / "build_views.py"
    spec = importlib.util.spec_from_file_location("build_views_repeated_window", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def public_source(total_receipts: int) -> dict[str, Any]:
    return {
        "receipt_input_paths": ["stats/intake-contract/examples/test-receipts.json"],
        "total_receipts": total_receipts,
        "latest_observed_at": "2026-04-06T23:59:59Z",
    }


def receipt(
    event_id: str,
    observed_at: str,
    *,
    event_kind: str,
    object_id: str,
    object_version: str | None = None,
    evidence_count: int = 1,
) -> dict[str, Any]:
    object_ref = {
        "repo": "aoa-owner",
        "kind": "candidate",
        "id": object_id,
    }
    if object_version is not None:
        object_ref["version"] = object_version
    return {
        "event_kind": event_kind,
        "event_id": event_id,
        "observed_at": observed_at,
        "run_ref": f"run:{event_id}",
        "session_ref": "session:repeated-window",
        "actor_ref": "aoa-owner:publisher",
        "object_ref": object_ref,
        "evidence_refs": [
            {"kind": "receipt", "ref": f"repo:aoa-owner/{event_id}/{index}"}
            for index in range(evidence_count)
        ],
        "payload": {},
    }


def varied_receipts() -> list[dict[str, Any]]:
    return [
        receipt(
            "evt-eval-v1",
            "2026-04-06T10:00:00Z",
            event_kind="eval_result_receipt",
            object_id="alpha",
            object_version="v1",
            evidence_count=2,
        ),
        receipt(
            "evt-automation",
            "2026-04-05T23:59:59Z",
            event_kind="automation_candidate_receipt",
            object_id="beta",
        ),
        receipt(
            "evt-progression",
            "2026-04-06T11:00:00Z",
            event_kind="progression_delta_receipt",
            object_id="alpha",
            object_version="v1",
            evidence_count=3,
        ),
        receipt(
            "evt-eval-v2",
            "2026-04-06T12:00:00Z",
            event_kind="eval_result_receipt",
            object_id="alpha",
            object_version="v2",
        ),
    ]


def assert_public_schema_valid(summary: dict[str, Any]) -> None:
    schema = json.loads(
        (REPO_ROOT / "schemas" / "repeated-window-summary.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(summary)


def test_root_builder_delegates_to_core_with_compatibility_identity_hook() -> None:
    facade = load_build_views_module()
    calls: list[tuple[list[dict[str, Any]], dict[str, Any], Any]] = []
    admitted = varied_receipts()[:1]
    source = public_source(1)

    def tracked_core(
        receipts: list[dict[str, Any]],
        generated_from: dict[str, Any],
        *,
        object_identity: Any,
    ) -> dict[str, Any]:
        calls.append((receipts, generated_from, object_identity))
        return repeated_window.build_repeated_window_summary(
            receipts, generated_from, object_identity=object_identity
        )

    facade.build_repeated_window_summary_from_inputs = tracked_core
    summary = facade.build_repeated_window_summary(admitted, source)

    assert calls == [(admitted, source, facade.object_key)]
    assert summary == repeated_window.build_repeated_window_summary(admitted, source)


def test_groups_observed_calendar_dates_without_inventing_change() -> None:
    receipts = varied_receipts()
    source = public_source(len(receipts))

    summary = repeated_window.build_repeated_window_summary(receipts, source)

    assert summary == {
        "schema_version": "aoa_stats_repeated_window_summary_v1",
        "generated_from": source,
        "windows": [
            {
                "window_id": "window:2026-04-05",
                "window_date": "2026-04-05",
                "total_receipts": 1,
                "unique_objects": 1,
                "event_counts_by_kind": {"automation_candidate_receipt": 1},
                "eval_result_count": 0,
                "progression_delta_count": 0,
                "automation_candidate_count": 1,
                "evidence_ref_count": 1,
            },
            {
                "window_id": "window:2026-04-06",
                "window_date": "2026-04-06",
                "total_receipts": 3,
                "unique_objects": 2,
                "event_counts_by_kind": {
                    "eval_result_receipt": 2,
                    "progression_delta_receipt": 1,
                },
                "eval_result_count": 2,
                "progression_delta_count": 1,
                "automation_candidate_count": 0,
                "evidence_ref_count": 6,
            },
        ],
    }
    assert_public_schema_valid(summary)


def test_projection_is_invariant_across_bounded_input_permutations() -> None:
    receipts = varied_receipts()
    source = public_source(len(receipts))
    expected = repeated_window.build_repeated_window_summary(receipts, source)

    for permuted in permutations(receipts):
        assert repeated_window.build_repeated_window_summary(list(permuted), source) == expected


def test_projection_conserves_receipts_events_objects_and_evidence() -> None:
    receipts = varied_receipts()
    summary = repeated_window.build_repeated_window_summary(
        receipts, public_source(len(receipts))
    )

    assert sum(window["total_receipts"] for window in summary["windows"]) == len(receipts)
    assert sum(window["evidence_ref_count"] for window in summary["windows"]) == sum(
        len(item["evidence_refs"]) for item in receipts
    )
    for window in summary["windows"]:
        date_receipts = [
            item for item in receipts if item["observed_at"][:10] == window["window_date"]
        ]
        assert sum(window["event_counts_by_kind"].values()) == window["total_receipts"]
        assert window["unique_objects"] == len(
            {object_key(item["object_ref"]) for item in date_receipts}
        )
        assert list(window["event_counts_by_kind"]) == sorted(
            window["event_counts_by_kind"]
        )
        assert window["eval_result_count"] == window["event_counts_by_kind"].get(
            "eval_result_receipt", 0
        )
        assert window["progression_delta_count"] == window[
            "event_counts_by_kind"
        ].get("progression_delta_receipt", 0)
        assert window["automation_candidate_count"] == window[
            "event_counts_by_kind"
        ].get("automation_candidate_receipt", 0)


def test_projection_does_not_mutate_admitted_receipts_or_source() -> None:
    receipts = varied_receipts()
    source = public_source(len(receipts))
    original_receipts = deepcopy(receipts)
    original_source = deepcopy(source)

    repeated_window.build_repeated_window_summary(receipts, source)

    assert receipts == original_receipts
    assert source == original_source


def test_committed_fixture_preserves_schema_and_exact_public_bytes() -> None:
    input_path = (
        REPO_ROOT
        / "stats"
        / "intake-contract"
        / "examples"
        / "session_harvest_family.receipts.example.json"
    )
    receipts = receipt_abi.resolve_active_receipts(
        receipt_abi.load_receipts([input_path])
    )
    source = receipt_abi.generated_from(
        receipts,
        [input_path.relative_to(REPO_ROOT).as_posix()],
    )
    summary = repeated_window.build_repeated_window_summary(receipts, source)
    facade = load_build_views_module()

    assert facade.stable_json(summary) == (
        REPO_ROOT / "generated" / "repeated_window_summary.min.json"
    ).read_text(encoding="utf-8")
    assert_public_schema_valid(summary)
