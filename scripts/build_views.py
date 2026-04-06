#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "examples" / "session_harvest_family.receipts.example.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "generated"

AXES = (
    "boundary_integrity",
    "execution_reliability",
    "change_legibility",
    "review_sharpness",
    "proof_discipline",
    "provenance_hygiene",
    "deep_readiness",
)


class ReceiptValidationError(ValueError):
    pass


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build aoa-stats derived views.")
    parser.add_argument(
        "--input",
        action="append",
        default=[],
        help="Path to a JSON file containing an array of receipt envelopes.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where generated summary JSON files should live.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate that generated outputs are current instead of rewriting them.",
    )
    return parser.parse_args(argv)


def load_receipts(paths: list[Path]) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ReceiptValidationError(f"{path}: receipt feed must be a JSON array")
        for index, item in enumerate(payload):
            if not isinstance(item, dict):
                raise ReceiptValidationError(f"{path}[{index}]: receipt must be an object")
            validate_receipt(item, location=f"{path}[{index}]")
            receipts.append(item)
    receipts.sort(key=lambda receipt: (receipt["observed_at"], receipt["event_id"]))
    return receipts


def validate_receipt(receipt: dict[str, Any], *, location: str) -> None:
    required_fields = (
        "event_kind",
        "event_id",
        "observed_at",
        "run_ref",
        "session_ref",
        "actor_ref",
        "object_ref",
        "evidence_refs",
        "payload",
    )
    for field in required_fields:
        if field not in receipt:
            raise ReceiptValidationError(f"{location}: missing field '{field}'")

    for field in ("event_kind", "event_id", "run_ref", "session_ref", "actor_ref"):
        if not isinstance(receipt[field], str) or not receipt[field]:
            raise ReceiptValidationError(f"{location}.{field}: must be a non-empty string")

    try:
        datetime.fromisoformat(receipt["observed_at"].replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ReceiptValidationError(
            f"{location}.observed_at: must be an ISO datetime"
        ) from exc

    object_ref = receipt["object_ref"]
    if not isinstance(object_ref, dict):
        raise ReceiptValidationError(f"{location}.object_ref: must be an object")
    for field in ("repo", "kind", "id"):
        if not isinstance(object_ref.get(field), str) or not object_ref[field]:
            raise ReceiptValidationError(
                f"{location}.object_ref.{field}: must be a non-empty string"
            )

    evidence_refs = receipt["evidence_refs"]
    if not isinstance(evidence_refs, list):
        raise ReceiptValidationError(f"{location}.evidence_refs: must be a list")
    for index, item in enumerate(evidence_refs):
        if not isinstance(item, dict):
            raise ReceiptValidationError(
                f"{location}.evidence_refs[{index}]: must be an object"
            )
        for field in ("kind", "ref"):
            if not isinstance(item.get(field), str) or not item[field]:
                raise ReceiptValidationError(
                    f"{location}.evidence_refs[{index}].{field}: must be a non-empty string"
                )

    if not isinstance(receipt["payload"], dict):
        raise ReceiptValidationError(f"{location}.payload: must be an object")


def generated_from(receipts: list[dict[str, Any]], input_paths: list[str]) -> dict[str, Any]:
    latest_observed_at = max(receipt["observed_at"] for receipt in receipts)
    return {
        "receipt_input_paths": input_paths,
        "total_receipts": len(receipts),
        "latest_observed_at": latest_observed_at,
    }


def object_key(object_ref: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        object_ref["repo"],
        object_ref["kind"],
        object_ref["id"],
        object_ref.get("version", ""),
    )


def build_object_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        grouped[object_key(receipt["object_ref"])].append(receipt)

    objects: list[dict[str, Any]] = []
    for key in sorted(grouped):
        group = grouped[key]
        by_kind = Counter(receipt["event_kind"] for receipt in group)
        latest = max(group, key=lambda receipt: (receipt["observed_at"], receipt["event_id"]))
        latest_eval = None
        latest_progression = None
        automation_total = 0
        automation_seed_ready = 0
        automation_checkpoint_required = 0
        for receipt in group:
            payload = receipt["payload"]
            if receipt["event_kind"] == "eval_result_receipt":
                latest_eval = payload.get("verdict")
            if receipt["event_kind"] == "progression_delta_receipt":
                latest_progression = payload.get("verdict")
            if receipt["event_kind"] == "automation_candidate_receipt":
                automation_total += 1
                if payload.get("seed_ready") is True:
                    automation_seed_ready += 1
                if payload.get("checkpoint_required") is True:
                    automation_checkpoint_required += 1

        object_ref = dict(latest["object_ref"])
        objects.append(
            {
                "object_ref": object_ref,
                "receipt_count_total": len(group),
                "receipt_counts_by_event_kind": dict(sorted(by_kind.items())),
                "first_observed_at": group[0]["observed_at"],
                "last_observed_at": latest["observed_at"],
                "latest_session_ref": latest["session_ref"],
                "latest_run_ref": latest["run_ref"],
                "evidence_ref_count": sum(len(receipt["evidence_refs"]) for receipt in group),
                "latest_eval_verdict": latest_eval,
                "latest_progression_verdict": latest_progression,
                "automation_candidate_counts": {
                    "total": automation_total,
                    "seed_ready": automation_seed_ready,
                    "checkpoint_required": automation_checkpoint_required,
                },
            }
        )

    return {
        "schema_version": "aoa_stats_object_summary_v1",
        "generated_from": source,
        "objects": objects,
    }


def build_repeated_window_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        grouped[receipt["observed_at"][:10]].append(receipt)

    windows: list[dict[str, Any]] = []
    for window_date in sorted(grouped):
        group = grouped[window_date]
        event_counts = Counter(receipt["event_kind"] for receipt in group)
        unique_objects = {object_key(receipt["object_ref"]) for receipt in group}
        windows.append(
            {
                "window_id": f"window:{window_date}",
                "window_date": window_date,
                "total_receipts": len(group),
                "unique_objects": len(unique_objects),
                "event_counts_by_kind": dict(sorted(event_counts.items())),
                "eval_result_count": event_counts.get("eval_result_receipt", 0),
                "progression_delta_count": event_counts.get("progression_delta_receipt", 0),
                "automation_candidate_count": event_counts.get(
                    "automation_candidate_receipt", 0
                ),
                "evidence_ref_count": sum(len(receipt["evidence_refs"]) for receipt in group),
            }
        )

    return {
        "schema_version": "aoa_stats_repeated_window_summary_v1",
        "generated_from": source,
        "windows": windows,
    }


def axis_template() -> dict[str, int]:
    return {axis: 0 for axis in AXES}


def build_route_progression_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        if receipt["event_kind"] != "progression_delta_receipt":
            continue
        route_ref = receipt["payload"].get("route_ref") or receipt["session_ref"]
        grouped[route_ref].append(receipt)

    routes: list[dict[str, Any]] = []
    for route_ref in sorted(grouped):
        group = grouped[route_ref]
        latest = max(group, key=lambda receipt: (receipt["observed_at"], receipt["event_id"]))
        cumulative = axis_template()
        caution_count = 0
        for receipt in group:
            payload = receipt["payload"]
            axis_deltas = payload.get("axis_deltas", {})
            if isinstance(axis_deltas, dict):
                for axis in AXES:
                    value = axis_deltas.get(axis, 0)
                    if isinstance(value, int):
                        cumulative[axis] += value
            cautions = payload.get("cautions", [])
            if isinstance(cautions, list):
                caution_count += len(cautions)
        routes.append(
            {
                "route_ref": route_ref,
                "total_progression_receipts": len(group),
                "latest_verdict": latest["payload"].get("verdict", "unknown"),
                "latest_observed_at": latest["observed_at"],
                "cumulative_axis_deltas": cumulative,
                "caution_count": caution_count,
                "evidence_ref_count": sum(len(receipt["evidence_refs"]) for receipt in group),
            }
        )

    return {
        "schema_version": "aoa_stats_route_progression_summary_v1",
        "generated_from": source,
        "routes": routes,
    }


def build_fork_calibration_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        if receipt["event_kind"] != "decision_fork_receipt":
            continue
        route_ref = receipt["payload"].get("route_ref") or receipt["session_ref"]
        grouped[route_ref].append(receipt)

    routes: list[dict[str, Any]] = []
    for route_ref in sorted(grouped):
        group = grouped[route_ref]
        latest = max(group, key=lambda receipt: (receipt["observed_at"], receipt["event_id"]))
        branch_counts: Counter[str] = Counter()
        max_options = 0
        realized_outcome_link_count = 0
        for receipt in group:
            payload = receipt["payload"]
            branch = payload.get("chosen_branch") or "unrecorded"
            branch_counts[str(branch)] += 1
            option_count = payload.get("branch_options_count", 0)
            if isinstance(option_count, int) and option_count > max_options:
                max_options = option_count
            realized_refs = payload.get("realized_outcome_refs", [])
            if isinstance(realized_refs, list):
                realized_outcome_link_count += len(realized_refs)
        routes.append(
            {
                "route_ref": route_ref,
                "decision_count": len(group),
                "chosen_branch_counts": dict(sorted(branch_counts.items())),
                "max_option_count": max_options,
                "realized_outcome_link_count": realized_outcome_link_count,
                "evidence_ref_count": sum(len(receipt["evidence_refs"]) for receipt in group),
                "latest_observed_at": latest["observed_at"],
            }
        )

    return {
        "schema_version": "aoa_stats_fork_calibration_summary_v1",
        "generated_from": source,
        "routes": routes,
    }


def build_automation_pipeline_summary(
    receipts: list[dict[str, Any]], source: dict[str, Any]
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        if receipt["event_kind"] != "automation_candidate_receipt":
            continue
        pipeline_ref = receipt["payload"].get("pipeline_ref") or receipt["session_ref"]
        grouped[pipeline_ref].append(receipt)

    pipelines: list[dict[str, Any]] = []
    for pipeline_ref in sorted(grouped):
        group = grouped[pipeline_ref]
        latest = max(group, key=lambda receipt: (receipt["observed_at"], receipt["event_id"]))
        next_artifact_hints: set[str] = set()
        seed_ready_count = 0
        checkpoint_required_count = 0
        deterministic_ready_count = 0
        reversible_ready_count = 0
        for receipt in group:
            payload = receipt["payload"]
            if payload.get("seed_ready") is True:
                seed_ready_count += 1
            if payload.get("checkpoint_required") is True:
                checkpoint_required_count += 1
            if payload.get("deterministic_ready") is True:
                deterministic_ready_count += 1
            if payload.get("reversible_ready") is True:
                reversible_ready_count += 1
            next_hint = payload.get("next_artifact_hint")
            if isinstance(next_hint, str) and next_hint:
                next_artifact_hints.add(next_hint)
        pipelines.append(
            {
                "pipeline_ref": pipeline_ref,
                "candidate_count": len(group),
                "seed_ready_count": seed_ready_count,
                "checkpoint_required_count": checkpoint_required_count,
                "deterministic_ready_count": deterministic_ready_count,
                "reversible_ready_count": reversible_ready_count,
                "next_artifact_hints": sorted(next_artifact_hints),
                "evidence_ref_count": sum(len(receipt["evidence_refs"]) for receipt in group),
                "latest_observed_at": latest["observed_at"],
            }
        )

    return {
        "schema_version": "aoa_stats_automation_pipeline_summary_v1",
        "generated_from": source,
        "pipelines": pipelines,
    }


def build_summary_surface_catalog(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "aoa_stats_summary_surface_catalog_v1",
        "generated_from": source,
        "surfaces": [
            {
                "name": "object_summary",
                "path": "generated/object_summary.min.json",
                "schema_ref": "schemas/object-summary.schema.json",
                "primary_question": "How often and how broadly is each source object showing up in the current receipt feed?",
                "derivation_rule": "group receipts by object_ref and keep counts, latest timestamps, and bounded posture flags",
            },
            {
                "name": "repeated_window_summary",
                "path": "generated/repeated_window_summary.min.json",
                "schema_ref": "schemas/repeated-window-summary.schema.json",
                "primary_question": "What changed across bounded date windows without turning the result into one global score?",
                "derivation_rule": "group receipts by observed_at date and keep counts plus bounded window signals",
            },
            {
                "name": "route_progression_summary",
                "path": "generated/route_progression_summary.min.json",
                "schema_ref": "schemas/route-progression-summary.schema.json",
                "primary_question": "What bounded multi-axis movement is visible on each named route?",
                "derivation_rule": "aggregate progression_delta_receipt payloads by route_ref and sum axis deltas",
            },
            {
                "name": "fork_calibration_summary",
                "path": "generated/fork_calibration_summary.min.json",
                "schema_ref": "schemas/fork-calibration-summary.schema.json",
                "primary_question": "How are route forks actually being chosen and how often do they carry realized outcome refs?",
                "derivation_rule": "aggregate decision_fork_receipt payloads by route_ref and chosen_branch",
            },
            {
                "name": "automation_pipeline_summary",
                "path": "generated/automation_pipeline_summary.min.json",
                "schema_ref": "schemas/automation-pipeline-summary.schema.json",
                "primary_question": "How close is a named automation pipeline to seed-ready bounded use?",
                "derivation_rule": "aggregate automation_candidate_receipt payloads by pipeline_ref and readiness flags",
            },
        ],
    }


def build_all_views(
    receipts: list[dict[str, Any]], input_paths: list[str]
) -> dict[str, dict[str, Any]]:
    source = generated_from(receipts, input_paths)
    return {
        "object_summary.min.json": build_object_summary(receipts, source),
        "repeated_window_summary.min.json": build_repeated_window_summary(receipts, source),
        "route_progression_summary.min.json": build_route_progression_summary(receipts, source),
        "fork_calibration_summary.min.json": build_fork_calibration_summary(receipts, source),
        "automation_pipeline_summary.min.json": build_automation_pipeline_summary(
            receipts, source
        ),
        "summary_surface_catalog.min.json": build_summary_surface_catalog(source),
    }


def stable_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_paths = [Path(path).expanduser().resolve() for path in args.input] or [DEFAULT_INPUT]
    output_dir = Path(args.output_dir).expanduser().resolve()
    receipts = load_receipts(input_paths)
    outputs = build_all_views(receipts, [path.name for path in input_paths])

    if args.check:
        mismatches: list[str] = []
        for name, payload in outputs.items():
            target = output_dir / name
            expected = stable_json(payload)
            if not target.exists() or target.read_text(encoding="utf-8") != expected:
                mismatches.append(name)
        if mismatches:
            print(
                "Generated views are out of date: " + ", ".join(sorted(mismatches)),
                file=sys.stderr,
            )
            return 1
        print("[ok] generated views are current")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in outputs.items():
        (output_dir / name).write_text(stable_json(payload), encoding="utf-8")
    print(f"[ok] wrote {len(outputs)} derived summary surfaces to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

