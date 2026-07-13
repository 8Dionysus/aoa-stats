from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker
import pytest


REPO_ROOT = Path(__file__).resolve().parents[5]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder.measurement import (  # noqa: E402
    MeasurementError,
    aggregate_packets,
    evidence_identity,
    pass_estimate,
    semantic_identity,
    summarize_distribution,
    validate_contract_semantics,
    validate_packet_semantics,
    validate_packet_set,
)


def load_json(relative_path: str) -> dict[str, object]:
    payload = json.loads((REPO_ROOT / relative_path).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def measurement_contract() -> dict[str, object]:
    return {
        "schema_version": "aoa_stats_measurement_contract_v1",
        "measurement_id": "aoa-evals/reliability-ratio",
        "contract_version": "1.0.0",
        "owner_repo": "aoa-evals",
        "question_ref": "question:reliability",
        "semantic_class": "statistic",
        "statistic": "ratio",
        "object_kind": "eval-run",
        "unit": {"symbol": "1", "quantity": "ratio"},
        "population": {
            "subject": "bounded eval runs",
            "definition": "owner-admitted runs under one eval contract",
            "inclusion_rule": "run has an owner verdict and evidence refs",
            "exclusion_rule": "draft examples and missing verdicts",
            "sampling": "either",
        },
        "window": {"temporality": "interval", "clock": "event_time"},
        "dimensions": {
            "allowed": [
                {
                    "name": "model",
                    "max_cardinality": 1,
                    "sensitivity": "public",
                }
            ],
            "prohibited": ["session_id", "prompt"],
        },
        "aggregation": {
            "operator": "ratio_of_sums",
            "across": ["population", "window"],
        },
        "missingness": {
            "states": ["missing", "unknown", "stale"],
            "zero_is_observation": True,
        },
        "uncertainty": {"required": False, "methods": ["not_estimated"]},
        "provenance": {
            "evidence_refs_required": True,
            "source_revision_required": False,
        },
        "lifecycle": {"status": "active", "compatible_with": []},
        "privacy": {
            "classification": "public",
            "raw_content_allowed": False,
            "sensitive_dimensions_allowed": False,
        },
        "live_state": {"capability": "live_capable"},
        "authority_ceiling": "Weaker than aoa-evals verdicts and reports.",
    }


def measurement_packet(
    observation_id: str,
    *,
    start: str,
    end: str,
    numerator: int,
    denominator: int,
    model: str = "m1",
) -> dict[str, object]:
    return {
        "schema_version": "aoa_stats_measurement_packet_v1",
        "contract_ref": "aoa-evals:stats/port.manifest.json#/measurements/0",
        "contract_version": "1.0.0",
        "measurement_id": "aoa-evals/reliability-ratio",
        "writer_repo": "aoa-evals",
        "observation_id": observation_id,
        "observed_at": end,
        "object_ref": {
            "kind": "eval-run",
            "id": observation_id,
            "version": "v1",
        },
        "population": {
            "id": f"population:{observation_id}",
            "definition_ref": (
                "aoa-evals:stats/port.manifest.json#/measurements/0/population"
            ),
            "size": denominator,
        },
        "sample": {"size": denominator, "selection": "owner-admitted runs"},
        "cohort": {"id": "model:m1"},
        "window": {
            "id": f"window:{observation_id}",
            "start": start,
            "end": end,
            "temporality": "interval",
        },
        "dimensions": {"model": model},
        "value": {
            "status": "observed",
            "kind": "ratio",
            "unit": "1",
            "number": numerator / denominator,
            "numerator": numerator,
            "denominator": denominator,
        },
        "uncertainty": {
            "status": "not_estimated",
            "sample_size": denominator,
            "method": "not_estimated",
            "reason": "focused contract fixture",
        },
        "provenance": {
            "evidence_refs": [
                {
                    "kind": "eval-report",
                    "ref": f"repo:aoa-evals/reports/{observation_id}.json",
                }
            ],
            "derivation_ref": "aoa-evals:stats/port.manifest.json#/measurements/0",
            "source_revision": None,
        },
        "reporting_rule": {"id": "reliability-ratio", "version": "1.0.0"},
        "posture": {
            "freshness": "current",
            "live_state": "reference",
            "privacy": "public",
            "raw_content_included": False,
        },
        "progress": {
            "state": "terminal",
            "completed": denominator,
            "total": denominator,
        },
    }


def packet_pair() -> tuple[dict[str, object], dict[str, object]]:
    return (
        measurement_packet(
            "run-a",
            start="2026-07-01T00:00:00Z",
            end="2026-07-01T01:00:00Z",
            numerator=2,
            denominator=3,
        ),
        measurement_packet(
            "run-b",
            start="2026-07-02T00:00:00Z",
            end="2026-07-02T01:00:00Z",
            numerator=3,
            denominator=5,
        ),
    )


def test_source_schemas_and_positive_packets_are_valid() -> None:
    contract = measurement_contract()
    contract_schema = load_json(
        "stats/measurement-contract/measurement-contract.schema.json"
    )
    packet_schema = load_json(
        "stats/measurement-contract/measurement-packet.schema.json"
    )
    Draft202012Validator(
        contract_schema, format_checker=FormatChecker()
    ).validate(contract)
    assert validate_contract_semantics(contract) == []
    for packet in packet_pair():
        Draft202012Validator(
            packet_schema, format_checker=FormatChecker()
        ).validate(packet)
        assert validate_packet_semantics(contract, packet) == []


def test_ratio_aggregation_preserves_denominators_and_population() -> None:
    contract = measurement_contract()
    result = aggregate_packets(contract, list(packet_pair()))

    assert result["value"] == {
        "status": "observed",
        "kind": "ratio",
        "unit": "1",
        "number": 5 / 8,
        "numerator": 5,
        "denominator": 8,
    }
    assert result["sample"]["size"] == 8
    assert result["population"]["size"] == 8
    assert validate_packet_semantics(contract, result) == []


def test_aggregation_rejects_incompatible_unit_and_undeclared_axis() -> None:
    contract = measurement_contract()
    first, second = packet_pair()
    second["value"]["unit"] = "ms"

    with pytest.raises(MeasurementError, match="value.unit"):
        aggregate_packets(contract, [first, second])

    first, second = packet_pair()
    contract["aggregation"]["across"] = ["window"]
    with pytest.raises(MeasurementError, match="across population"):
        aggregate_packets(contract, [first, second])


def test_distribution_summary_and_pass_statistics_preserve_sample_meaning() -> None:
    distribution = summarize_distribution(
        [10, 20, 30, 40], quantiles=[0.5, 0.9]
    )

    assert distribution == {
        "count": 4,
        "minimum": 10.0,
        "maximum": 40.0,
        "quantiles": [
            {"q": 0.5, "value": 25.0},
            {"q": 0.9, "value": 37.0},
        ],
    }
    assert pass_estimate(
        successes=2, attempts=4, k=2, statistic="pass_at_k"
    ) == 5 / 6
    assert pass_estimate(
        successes=2, attempts=4, k=2, statistic="pass_all_k"
    ) == 1 / 6


def test_unknown_is_not_zero_and_cannot_enter_aggregation() -> None:
    contract = measurement_contract()
    packet, _ = packet_pair()
    packet["value"] = {
        "status": "unknown",
        "kind": "ratio",
        "unit": "1",
        "reason": "owner evidence unavailable",
    }
    packet["sample"]["size"] = 0
    packet["population"]["size"] = None
    packet["uncertainty"] = {
        "status": "not_estimated",
        "sample_size": 0,
        "method": "not_estimated",
        "reason": "unknown evidence",
    }
    packet["posture"]["freshness"] = "unknown"

    assert validate_packet_semantics(contract, packet) == []
    false_zero = deepcopy(packet)
    false_zero["value"]["number"] = 0
    assert any(
        "must not carry numeric" in issue
        for issue in validate_packet_semantics(contract, false_zero)
    )
    with pytest.raises(MeasurementError, match="cannot be coerced"):
        aggregate_packets(contract, [packet])


def test_packet_set_rejects_duplicate_writer_overlap_and_cardinality() -> None:
    contract = measurement_contract()
    first, second = packet_pair()
    duplicate = deepcopy(first)
    duplicate["writer_repo"] = "aoa-stats"

    issues = validate_packet_set(contract, [first, duplicate])
    assert any("duplicate observation_id" in issue for issue in issues)
    assert any("duplicate writers" in issue for issue in issues)

    second["dimensions"]["model"] = "m2"
    issues = validate_packet_set(contract, [first, second])
    assert any("cardinality" in issue for issue in issues)


def test_reference_privacy_and_raw_session_stop_lines_hold() -> None:
    contract = measurement_contract()
    contract["live_state"]["capability"] = "reference_only"
    packet, _ = packet_pair()
    packet["posture"]["live_state"] = "live"

    assert any(
        "reference-only" in issue
        for issue in validate_packet_semantics(contract, packet)
    )

    packet["posture"]["live_state"] = "reference"
    packet["posture"]["raw_content_included"] = True
    packet["provenance"]["evidence_refs"] = [
        {
            "kind": "raw",
            "ref": "/home/user/.aoa/sessions/transcript.jsonl",
        }
    ]
    issues = validate_packet_semantics(contract, packet)
    assert any("host-local path" in issue for issue in issues)
    assert any("raw session material" in issue for issue in issues)
    assert any("raw content" in issue for issue in issues)


def test_reporting_rule_changes_view_identity_not_evidence_identity() -> None:
    packet, _ = packet_pair()
    rerendered = deepcopy(packet)
    rerendered["reporting_rule"]["version"] = "2.0.0"

    assert evidence_identity(packet) == evidence_identity(rerendered)
    assert semantic_identity(packet) != semantic_identity(rerendered)


def test_partial_progress_is_not_terminal_and_required_uncertainty_is_not_lost() -> None:
    contract = measurement_contract()
    first, second = packet_pair()
    first["progress"] = {"state": "partial", "completed": 1, "total": 3}
    assert validate_packet_semantics(contract, first) == []

    false_partial = deepcopy(first)
    false_partial["progress"]["completed"] = 3
    assert any(
        "partial progress" in issue
        for issue in validate_packet_semantics(contract, false_partial)
    )

    contract["uncertainty"] = {
        "required": True,
        "methods": ["confidence_interval"],
    }
    for packet in (first, second):
        packet["uncertainty"] = {
            "status": "estimated",
            "sample_size": packet["sample"]["size"],
            "method": "confidence_interval",
            "lower": 0.1,
            "upper": 0.9,
        }
    with pytest.raises(MeasurementError, match="required uncertainty"):
        aggregate_packets(contract, [first, second])
