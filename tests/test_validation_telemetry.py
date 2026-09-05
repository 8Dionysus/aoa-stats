from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from functools import cache
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder.schema_validation import schema_issues  # noqa: E402
from aoa_stats_builder.validation_telemetry import (  # noqa: E402
    ValidationTelemetryAdmission,
    ValidationTelemetryAdmissionError,
    VALIDATION_TELEMETRY_FIELDS,
    admit_validation_telemetry_packet,
    build_validation_telemetry_baseline,
    validate_validation_telemetry_packet,
    validate_validation_telemetry_port,
    validate_validation_telemetry_port_schema,
)

PROTOCOL_PATH = REPO_ROOT / "scripts/validate_stats_protocol.py"
SPEC = importlib.util.spec_from_file_location("validation_telemetry_protocol", PROTOCOL_PATH)
assert SPEC is not None and SPEC.loader is not None
protocol = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = protocol
SPEC.loader.exec_module(protocol)


def load_json(relative_path: str) -> dict[str, object]:
    payload = json.loads((REPO_ROOT / relative_path).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


@cache
def _validated_fixture_schemas():
    # These authored inputs are immutable for the packet/admission scenarios.
    # Keep the real loader and schema-validity check, but perform them once.
    schemas, issues = protocol._load_schemas(REPO_ROOT)
    assert issues == []
    return schemas


def prepared_schemas():
    # Each scenario gets independent mutable schemas and a fresh context epoch.
    # Loader/currentness tests below deliberately still call the real loader.
    schemas = deepcopy(_validated_fixture_schemas())
    protocol._install_canonical_validation_telemetry_port_schema(
        schemas[protocol.VALIDATION_TELEMETRY_PORT_SCHEMA_PATH.as_posix()]
    )
    return schemas


def load_stats_protocol_test_module():
    path = REPO_ROOT / "tests/test_stats_protocol.py"
    spec = importlib.util.spec_from_file_location("validation_telemetry_stats_protocol_fixture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def telemetry_port() -> dict[str, object]:
    port = deepcopy(load_stats_protocol_test_module().local_port())
    port["central_contract_refs"] = [
        *port["central_contract_refs"],
        "aoa-stats:stats/measurement-contract/validation-telemetry-packet.schema.json",
    ]
    port["validation_telemetry"] = {
        "schema_version": "aoa_stats_validation_telemetry_port_v1",
        "contract_version": "1.0.0",
        "packet_schema_ref": "aoa-stats:stats/measurement-contract/validation-telemetry-packet.schema.json",
        "required_fields": sorted(VALIDATION_TELEMETRY_FIELDS),
        "node_lanes": [
            {
                "id": "stats-protocol",
                "lane": "local-protocol",
                "semantic_class": "contract_abi_api",
                "budget_tier": "contextual",
                "validator_ref": "scripts/validate_stats_protocol.py",
                "timing_contract": {
                    "scope": "contextual_validator_process",
                    "measurement_ref": "reports/stats-protocol-timing.json",
                    "sample_count": 3,
                    "p95_budget_ms": None,
                },
                "cacheability": "read_only",
                "parallel_safety": "serialized",
                "claim_refs": ["claim:stats-protocol"],
                "evidence_refs": ["reports/stats-protocol.json"],
                "acceptance_barrier": "owner stats protocol contract remains green",
            }
        ],
        "exports": [
            {
                "id": "validation-telemetry",
                "posture": "reference",
                "packet_refs": ["reports/stats-protocol.json"],
                "evidence_refs": ["reports/stats-protocol.json"],
            }
        ],
    }
    return port


def valid_packet() -> dict[str, object]:
    return {
        "schema_version": "aoa_stats_validation_telemetry_packet_v1",
        "contract_version": "1.0.0",
        "owner_repo": "aoa-evals",
        "telemetry_port_ref": "stats/port.manifest.json#/validation_telemetry",
        "observation_id": "aoa-evals:stats-protocol:2026-08-21T12:00:00Z",
        "observed_at": "2026-08-21T12:00:00Z",
        "node": {
            "node_id": "stats-protocol",
            "lane": "local-protocol",
            "semantic_class": "contract_abi_api",
            "budget_tier": "contextual",
            "validator_ref": "scripts/validate_stats_protocol.py",
            "claim_refs": ["claim:stats-protocol"],
            "evidence_refs": ["reports/stats-protocol.json"],
            "acceptance_barrier": "owner stats protocol contract remains green",
        },
        "result": {
            "status": "pass",
            "exit_code": 0,
            "result_ref": "reports/stats-protocol.json",
        },
        "candidate_identity": {
            "kind": "git-tree",
            "source": "aoa-evals:working-tree",
            "digest": "sha256:" + "1" * 64,
        },
        "environment_identity": {
            "kind": "validation-environment",
            "source": "owner:aoa-evals",
            "digest": "sha256:" + "2" * 64,
        },
        "metrics": {
            "wall_ms": {"status": "observed", "value": 64580},
            "cpu_ms": {"status": "observed", "value": 50750},
            "peak_rss_bytes": {"status": "observed", "value": 164704256},
            "io_read_bytes": {"status": "observed", "value": 1024},
            "io_write_bytes": {"status": "observed", "value": 2048},
        },
        "cache_posture": {
            "status": "miss",
            "key_digest": "sha256:" + "3" * 64,
            "receipt_ref": "reports/cache-receipt.json",
        },
        "receipt_posture": {
            "status": "emitted",
            "receipt_ref": "reports/stats-protocol-receipt.json",
        },
        "first_failure": {
            "status": "none",
            "time_to_first_failure_ms": {"status": "not_applicable"},
        },
        "rerun_amplification": {
            "status": "observed",
            "attempt_count": 3,
            "distinct_operation_count": 2,
            "repeated_attempt_count": 1,
            "validation_attempt_count": 2,
            "validation_rerun_after_repair_count": 1,
            "attempts_per_distinct_operation": 1.5,
        },
        "source_coverage": {
            "status": "complete",
            "expected_owner_count": 23,
            "observed_owner_count": 23,
        },
        "cost": {
            "status": "observed",
            "measurement_ref": "reports/validation-cost-measurement.json",
        },
        "provenance": {
            "evidence_refs": [
                {"kind": "owner-report", "ref": "reports/stats-protocol.json"}
            ],
            "derivation_ref": "owner:aoa-evals/stats-protocol",
            "source_revision": "git:abcdef1",
        },
        "posture": {
            "freshness": "reference",
            "live_state": "reference",
            "privacy": "public",
            "raw_content_included": False,
        },
    }


def validated_port_schema(port: dict[str, object]):
    schemas = prepared_schemas()
    return validate_validation_telemetry_port_schema(
        port["validation_telemetry"],
        label="telemetry port",
        registry=protocol._registry(schemas),
    )


def admitted_packet(
    packet: dict[str, object] | None = None,
    *,
    owner_port: dict[str, object] | None = None,
) -> ValidationTelemetryAdmission:
    payload = valid_packet() if packet is None else packet
    owner = str(payload["owner_repo"])
    owner_port = telemetry_port() if owner_port is None else deepcopy(owner_port)
    owner_port["owner_repo"] = owner
    owner_source_ref = f"{owner}:stats/port.manifest.json"
    schemas = prepared_schemas()
    registry = protocol._registry(schemas)
    schema_findings = schema_issues(
        schemas[protocol.VALIDATION_TELEMETRY_PACKET_SCHEMA_PATH.as_posix()],
        payload,
        label="packet",
        registry=registry,
    )
    return admit_validation_telemetry_packet(
        payload,
        schema_issues=schema_findings,
        telemetry_port_schema_validation=validate_validation_telemetry_port_schema(
            owner_port["validation_telemetry"],
            label="telemetry port",
            registry=registry,
        ),
        telemetry_port=owner_port["validation_telemetry"],
        owner_port=owner_port,
        expected_owner_repo=owner,
        expected_telemetry_port_ref="stats/port.manifest.json#/validation_telemetry",
        expected_port_ref="stats/port.manifest.json",
        expected_packet_ref="reports/stats-protocol.json",
        owner_source_ref=owner_source_ref,
    )


def owner_input(owner: str) -> dict[str, object]:
    port = telemetry_port()
    port["owner_repo"] = owner
    return {
        "owner_repo": owner,
        "source_kind": "direct_owner_source",
        "source_ref": f"{owner}:stats/port.manifest.json",
        "port_ref": "stats/port.manifest.json",
        "payload": port,
        "input_status": "observed",
    }


def test_telemetry_schemas_and_semantics_accept_complete_reference_packet() -> None:
    schemas, issues = protocol._load_schemas(REPO_ROOT)
    assert issues == []
    registry = protocol._registry(schemas)
    port = telemetry_port()
    packet = valid_packet()

    assert protocol.validate_port_payload(
        port,
        label="aoa-evals:stats/port.manifest.json",
        port_schema=schemas[protocol.PORT_SCHEMA_PATH.as_posix()],
        registry=registry,
    ) == []
    assert validate_validation_telemetry_port(port["validation_telemetry"]) == []
    assert schema_issues(
        schemas[protocol.VALIDATION_TELEMETRY_PACKET_SCHEMA_PATH.as_posix()],
        packet,
        label="packet",
        registry=registry,
    ) == []
    assert validate_validation_telemetry_packet(packet) == []


def test_protocol_resolves_owner_telemetry_packet_refs(tmp_path: Path) -> None:
    owner_root = tmp_path / "aoa-evals"
    packet_path = owner_root / "reports" / "validation-telemetry.json"
    port_path = owner_root / "stats" / "port.manifest.json"
    packet_path.parent.mkdir(parents=True)
    port_path.parent.mkdir(parents=True)
    port = telemetry_port()
    port["validation_telemetry"]["exports"][0] = {
        "id": "validation-telemetry",
        "posture": "reference",
        "packet_refs": ["reports/validation-telemetry.json"],
        "evidence_refs": ["reports/validation-telemetry.json"],
    }
    packet_path.write_text(json.dumps(valid_packet()), encoding="utf-8")
    port_path.write_text(json.dumps(port), encoding="utf-8")

    assert protocol.validate(REPO_ROOT, port_paths=[port_path]) == []


def test_owner_port_route_rejects_missing_telemetry_schema_field(tmp_path: Path) -> None:
    owner_root = tmp_path / "aoa-evals"
    port_path = owner_root / "stats" / "port.manifest.json"
    port_path.parent.mkdir(parents=True)
    port = telemetry_port()
    del port["validation_telemetry"]["required_fields"]
    port_path.write_text(json.dumps(port), encoding="utf-8")

    issues = protocol.validate(REPO_ROOT, port_paths=[port_path])

    assert any(
        "validation_telemetry:" in issue
        and "required_fields" in issue
        and "required property" in issue
        for issue in issues
    )


@pytest.mark.parametrize(
    "telemetry_port_ref",
    (
        "stats/port.manifest.json#/validation_telemetry",
        "aoa-evals:stats/port.manifest.json#/validation_telemetry",
    ),
)
def test_baseline_script_binds_packet_to_owner_root_and_current_port(
    tmp_path: Path,
    telemetry_port_ref: str,
) -> None:
    owner_root = tmp_path / "aoa-evals"
    port_path = owner_root / "stats" / "port.manifest.json"
    packet_path = owner_root / "reports" / "stats-protocol.json"
    port_path.parent.mkdir(parents=True)
    packet_path.parent.mkdir(parents=True)
    port = telemetry_port()
    packet = valid_packet()
    packet["telemetry_port_ref"] = telemetry_port_ref
    port_path.write_text(json.dumps(port), encoding="utf-8")
    packet_path.write_text(json.dumps(packet), encoding="utf-8")
    output_path = tmp_path / "baseline.json"

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts/build_validation_telemetry_baseline.py"),
            "--port",
            str(port_path),
            "--packet",
            str(packet_path),
            "--output",
            str(output_path),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    baseline = json.loads(output_path.read_text(encoding="utf-8"))
    record = next(
        item for item in baseline["owner_records"] if item["owner_repo"] == "aoa-evals"
    )
    assert record["telemetry_status"] == "reference"
    assert record["identity_barrier_status"] == "compatible"
    assert record["identity_group_count"] == 1


def test_unknown_metric_cannot_carry_zero_as_a_proxy() -> None:
    schemas = prepared_schemas()
    packet = valid_packet()
    packet["metrics"]["wall_ms"] = {"status": "unknown", "value": 0}

    schema_findings = schema_issues(
        schemas[protocol.VALIDATION_TELEMETRY_PACKET_SCHEMA_PATH.as_posix()],
        packet,
        label="packet",
        registry=protocol._registry(schemas),
    )
    assert schema_findings
    assert any("wall_ms" in finding for finding in schema_findings)
    assert any("must not carry a value" in finding for finding in validate_validation_telemetry_packet(packet))


def test_incomplete_nested_packet_is_not_admitted_by_pure_validation() -> None:
    packet = valid_packet()
    del packet["provenance"]["source_revision"]
    del packet["metrics"]["io_write_bytes"]

    issues = validate_validation_telemetry_packet(packet)

    assert any("provenance: required field 'source_revision' is missing" in issue for issue in issues)
    assert any("metrics: required field 'io_write_bytes' is missing" in issue for issue in issues)


def test_result_and_first_failure_coherence_is_fail_closed() -> None:
    packet = valid_packet()
    packet["result"] = {
        "status": "fail",
        "exit_code": 1,
        "result_ref": "reports/stats-protocol.json",
    }

    issues = validate_validation_telemetry_packet(packet)

    assert any(
        "fail result cannot have first_failure.status=none" in issue
        for issue in issues
    )


def test_direct_admission_requires_schema_validation_precondition() -> None:
    owner_port = telemetry_port()
    with pytest.raises(
        ValidationTelemetryAdmissionError,
        match="canonical JSON Schema validation is a required precondition",
    ):
        admit_validation_telemetry_packet(
            valid_packet(),
            telemetry_port=owner_port["validation_telemetry"],
            owner_port=owner_port,
            expected_owner_repo="aoa-evals",
            expected_telemetry_port_ref="stats/port.manifest.json#/validation_telemetry",
            expected_port_ref="stats/port.manifest.json",
            expected_packet_ref="reports/stats-protocol.json",
            owner_source_ref="aoa-evals:stats/port.manifest.json",
        )


def test_direct_admission_preserves_nested_schema_findings() -> None:
    packet = valid_packet()
    packet["node"] = dict(packet["node"])
    packet["node"]["unexpected"] = True
    schemas = prepared_schemas()
    schema_findings = schema_issues(
        schemas[protocol.VALIDATION_TELEMETRY_PACKET_SCHEMA_PATH.as_posix()],
        packet,
        label="packet",
        registry=protocol._registry(schemas),
    )
    assert schema_findings

    owner_port = telemetry_port()
    with pytest.raises(ValidationTelemetryAdmissionError, match="unexpected"):
        admit_validation_telemetry_packet(
            packet,
            schema_issues=schema_findings,
            telemetry_port_schema_validation=validate_validation_telemetry_port_schema(
                owner_port["validation_telemetry"],
                label="telemetry port",
                registry=protocol._registry(schemas),
            ),
            telemetry_port=owner_port["validation_telemetry"],
            owner_port=owner_port,
            expected_owner_repo="aoa-evals",
            expected_telemetry_port_ref="stats/port.manifest.json#/validation_telemetry",
            expected_port_ref="stats/port.manifest.json",
            expected_packet_ref="reports/stats-protocol.json",
            owner_source_ref="aoa-evals:stats/port.manifest.json",
        )


@pytest.mark.parametrize(
    "missing_field",
    (
        "schema_version",
        "contract_version",
        "packet_schema_ref",
        "required_fields",
        "node_lanes",
        "exports",
    ),
)
def test_direct_admission_rejects_missing_telemetry_port_schema_fields(
    missing_field: str,
) -> None:
    owner_port = telemetry_port()
    del owner_port["validation_telemetry"][missing_field]
    schemas = prepared_schemas()
    registry = protocol._registry(schemas)
    port_schema_validation = validate_validation_telemetry_port_schema(
        owner_port["validation_telemetry"],
        label="telemetry port",
        registry=registry,
    )
    assert any(missing_field in finding for finding in port_schema_validation.issues)

    with pytest.raises(ValidationTelemetryAdmissionError, match=missing_field):
        admit_validation_telemetry_packet(
            valid_packet(),
            schema_issues=[],
            telemetry_port_schema_validation=port_schema_validation,
            telemetry_port=owner_port["validation_telemetry"],
            owner_port=owner_port,
            expected_owner_repo="aoa-evals",
            expected_telemetry_port_ref="stats/port.manifest.json#/validation_telemetry",
            expected_port_ref="stats/port.manifest.json",
            expected_packet_ref="reports/stats-protocol.json",
            owner_source_ref="aoa-evals:stats/port.manifest.json",
        )


@pytest.mark.parametrize(
    "missing_field",
    (
        "schema_version",
        "contract_version",
        "packet_schema_ref",
        "required_fields",
        "node_lanes",
        "exports",
    ),
)
def test_direct_admission_rejects_forged_empty_telemetry_port_schema_findings(
    missing_field: str,
) -> None:
    owner_port = telemetry_port()
    del owner_port["validation_telemetry"][missing_field]

    with pytest.raises(
        ValidationTelemetryAdmissionError,
        match="content-bound canonical telemetry-port JSON Schema validation",
    ):
        admit_validation_telemetry_packet(
            valid_packet(),
            schema_issues=[],
            telemetry_port_schema_issues=[],
            telemetry_port=owner_port["validation_telemetry"],
            owner_port=owner_port,
            expected_owner_repo="aoa-evals",
            expected_telemetry_port_ref="stats/port.manifest.json#/validation_telemetry",
            expected_port_ref="stats/port.manifest.json",
            expected_packet_ref="reports/stats-protocol.json",
            owner_source_ref="aoa-evals:stats/port.manifest.json",
        )


def test_direct_admission_rejects_port_schema_validation_bound_to_different_bytes() -> None:
    owner_port = telemetry_port()
    validation = validated_port_schema(owner_port)
    changed_owner_port = deepcopy(owner_port)
    changed_owner_port["validation_telemetry"] = dict(
        changed_owner_port["validation_telemetry"]
    )
    changed_owner_port["validation_telemetry"]["contract_version"] = "1.0.1"

    with pytest.raises(
        ValidationTelemetryAdmissionError,
        match="stale or bound to different port/schema content",
    ):
        admit_validation_telemetry_packet(
            valid_packet(),
            schema_issues=[],
            telemetry_port_schema_validation=validation,
            telemetry_port=changed_owner_port["validation_telemetry"],
            owner_port=changed_owner_port,
            expected_owner_repo="aoa-evals",
            expected_telemetry_port_ref="stats/port.manifest.json#/validation_telemetry",
            expected_port_ref="stats/port.manifest.json",
            expected_packet_ref="reports/stats-protocol.json",
            owner_source_ref="aoa-evals:stats/port.manifest.json",
        )


def test_direct_admission_does_not_trust_forged_empty_validation_diagnostics() -> None:
    owner_port = telemetry_port()
    del owner_port["validation_telemetry"]["required_fields"]
    validation = validated_port_schema(owner_port)
    forged = replace(validation, issues=())

    with pytest.raises(ValidationTelemetryAdmissionError, match="required_fields"):
        admit_validation_telemetry_packet(
            valid_packet(),
            schema_issues=[],
            telemetry_port_schema_validation=forged,
            telemetry_port=owner_port["validation_telemetry"],
            owner_port=owner_port,
            expected_owner_repo="aoa-evals",
            expected_telemetry_port_ref="stats/port.manifest.json#/validation_telemetry",
            expected_port_ref="stats/port.manifest.json",
            expected_packet_ref="reports/stats-protocol.json",
            owner_source_ref="aoa-evals:stats/port.manifest.json",
        )


def test_direct_admission_rejects_stale_port_schema_context() -> None:
    owner_port = telemetry_port()
    validation = validated_port_schema(owner_port)
    schemas, issues = protocol._load_schemas(REPO_ROOT)
    assert issues == []
    schema = schemas[protocol.VALIDATION_TELEMETRY_PORT_SCHEMA_PATH.as_posix()]
    original_schema_id = schema["$id"]
    schema["$id"] = "https://aoa-stats/stats/federation/other.schema.json"
    try:
        with pytest.raises(
            ValidationTelemetryAdmissionError,
            match="stale or bound to different port/schema content",
        ):
            admit_validation_telemetry_packet(
                valid_packet(),
                schema_issues=[],
                telemetry_port_schema_validation=validation,
                telemetry_port=owner_port["validation_telemetry"],
                owner_port=owner_port,
                expected_owner_repo="aoa-evals",
                expected_telemetry_port_ref="stats/port.manifest.json#/validation_telemetry",
                expected_port_ref="stats/port.manifest.json",
                expected_packet_ref="reports/stats-protocol.json",
                owner_source_ref="aoa-evals:stats/port.manifest.json",
            )
    finally:
        schema["$id"] = original_schema_id
        protocol._load_schemas(REPO_ROOT)


def test_result_and_observed_first_failure_coherence_is_fail_closed() -> None:
    packet = valid_packet()
    packet["first_failure"] = {
        "status": "observed",
        "node_id": "stats-protocol",
        "failure_class": "validator_failure",
        "evidence_ref": "reports/stats-protocol.json",
        "time_to_first_failure_ms": {"status": "observed", "value": 1},
    }

    issues = validate_validation_telemetry_packet(packet)

    assert any("pass result cannot have an observed first_failure" in issue for issue in issues)


def test_qualified_absolute_alias_and_traversal_refs_fail_closed() -> None:
    for bad_ref in (
        "/etc/passwd",
        "owner-a:/etc/passwd",
        "owner-a:~/.ssh/config",
        "@alias/reports/result.json",
        "owner-a:../../outside.json",
    ):
        packet = valid_packet()
        packet["candidate_identity"] = {
            "kind": "git-tree",
            "source": bad_ref,
            "digest": "sha256:" + "1" * 64,
        }
        assert any(
            "candidate_identity.source" in issue
            for issue in validate_validation_telemetry_packet(packet)
        ), bad_ref


def test_owner_port_without_extension_is_a_visible_nearest_collision() -> None:
    inventory = load_json("stats/federation/owner-inventory.json")
    baseline = build_validation_telemetry_baseline(
        inventory["owners"],
        port_inputs={
            "aoa-stats": {
                "owner_repo": "aoa-stats",
                "source_kind": "central_source_home",
                "source_ref": "aoa-stats:stats/source_home.manifest.json",
                "port_ref": "stats/source_home.manifest.json",
                "payload": {
                    "owner_repo": "aoa-stats",
                    "source_home_input": True,
                    "source_home_ref": "stats/source_home.manifest.json",
                    "source_home_schema_version": "aoa_stats_source_home_v3",
                    "source_home_status": "active_source_home",
                    "source_home_digest": "sha256:"
                    + "ad1b87e31004990c7a3421b80bcc70b19f603d33e647610447d52ee1f9dd6703",
                },
            },
            "aoa-kag": {
                "owner_repo": "aoa-kag",
                "source_kind": "direct_owner_source",
                "source_ref": "aoa-kag:stats/port.manifest.json",
                "port_ref": "stats/port.manifest.json",
                "payload": {"owner_repo": "aoa-kag"},
            },
        },
        inventory_ref="stats/federation/owner-inventory.json",
    )

    assert baseline["summary"]["expected_owner_count"] == 23
    assert baseline["summary"]["port_present_count"] == 2
    assert baseline["summary"]["port_missing_count"] == 21
    assert baseline["summary"]["telemetry_declared_owner_count"] == 0
    assert baseline["summary"]["telemetry_packet_owner_count"] == 0
    kag = next(record for record in baseline["owner_records"] if record["owner_repo"] == "aoa-kag")
    assert kag["port_status"] == "observed"
    assert kag["telemetry_status"] == "port_without_telemetry"
    assert all(
        kag["field_coverage"][field]["status"] == "missing"
        for field in VALIDATION_TELEMETRY_FIELDS
    )

    baseline_schema = load_json("schemas/validation-telemetry-baseline.schema.json")
    Draft202012Validator.check_schema(baseline_schema)
    assert schema_issues(baseline_schema, baseline, label="baseline") == []


def test_unknown_and_stale_states_survive_owner_projection() -> None:
    inventory = load_json("stats/federation/owner-inventory.json")
    packet = valid_packet()
    packet["owner_repo"] = "aoa-kag"
    packet["metrics"] = {
        field: {"status": "unknown", "reason": "owner did not expose this field"}
        for field in ("wall_ms", "cpu_ms", "peak_rss_bytes", "io_read_bytes", "io_write_bytes")
    }
    packet["cache_posture"] = {"status": "unknown"}
    packet["receipt_posture"] = {"status": "unknown"}
    packet["first_failure"] = {"status": "stale", "reason": "receipt predates source revision"}
    packet["rerun_amplification"] = {"status": "unknown", "reason": "no correlated attempt set"}
    packet["source_coverage"] = {"status": "unknown", "reason": "owner graph unavailable"}
    packet["cost"] = {"status": "unknown", "reason": "owner did not expose cost"}
    assert validate_validation_telemetry_packet(packet) == []

    admitted = admitted_packet(packet)

    baseline = build_validation_telemetry_baseline(
        inventory["owners"],
        port_inputs={
            "aoa-kag": owner_input("aoa-kag")
        },
        packets=[admitted],
    )
    kag = next(record for record in baseline["owner_records"] if record["owner_repo"] == "aoa-kag")
    assert kag["telemetry_status"] == "reference"
    assert kag["field_coverage"]["wall_ms"]["status"] == "unknown"
    assert kag["field_coverage"]["wall_ms"]["owner_count"] == 0
    assert kag["field_coverage"]["first_failure"]["status"] == "stale"
    assert kag["field_coverage"]["time_to_first_failure_ms"]["status"] == "stale"


def test_cost_and_first_failure_timing_reject_tampering() -> None:
    packet = valid_packet()
    packet["candidate_identity"]["source"] = "../outside-owner.json"
    packet["cost"] = {
        "status": "observed",
        "measurement_ref": "/tmp/owner-cost.json",
    }
    packet["first_failure"]["time_to_first_failure_ms"] = {
        "status": "observed",
        "value": -1,
    }

    issues = validate_validation_telemetry_packet(packet)
    assert any("cost.measurement_ref" in issue for issue in issues)
    assert any("candidate_identity.source" in issue for issue in issues)
    assert any("time_to_first_failure_ms.value" in issue for issue in issues)


def test_non_finite_observation_is_not_numeric_telemetry() -> None:
    packet = valid_packet()
    packet["metrics"]["wall_ms"] = {"status": "observed", "value": float("nan")}

    issues = validate_validation_telemetry_packet(packet)

    assert any("metrics.wall_ms" in issue for issue in issues)


def test_builder_is_deterministic_and_sorts_owner_projection() -> None:
    owners = [
        {"repo_id": "owner-b", "classification": "implemented"},
        {"repo_id": "owner-a", "classification": "implemented"},
    ]
    inputs = {
        "owner-b": {
            "owner_repo": "owner-b",
            "source_kind": "direct_owner_source",
            "source_ref": "owner-b:stats/port.manifest.json",
            "port_ref": "stats/port.manifest.json",
            "payload": {"owner_repo": "owner-b"},
        },
        "owner-a": {
            "owner_repo": "owner-a",
            "source_kind": "direct_owner_source",
            "source_ref": "owner-a:stats/port.manifest.json",
            "port_ref": "stats/port.manifest.json",
            "payload": {"owner_repo": "owner-a"},
        },
    }

    first = build_validation_telemetry_baseline(owners, port_inputs=inputs)
    second = build_validation_telemetry_baseline(list(reversed(owners)), port_inputs=inputs)

    assert first == second
    assert [record["owner_repo"] for record in first["owner_records"]] == [
        "owner-a",
        "owner-b",
    ]
    assert list(first["summary"]["field_coverage"]) == list(VALIDATION_TELEMETRY_FIELDS)


def test_owner_authenticated_direct_input_overrides_inventory_classification() -> None:
    expected_owners = [
        {
            "repo_id": "owner-a",
            "classification": "routed_to_stronger_owner",
        }
    ]
    telemetry = {
        "node_lanes": [{"id": "node"}],
    }
    baseline = build_validation_telemetry_baseline(
        expected_owners,
        port_inputs={
            "owner-a": {
                "owner_repo": "owner-a",
                "source_kind": "direct_owner_source",
                "source_ref": "owner-a:stats/port.manifest.json",
                "port_ref": "stats/port.manifest.json",
                "payload": {"owner_repo": "owner-a", "validation_telemetry": telemetry},
            }
        },
    )

    record = baseline["owner_records"][0]
    assert record["port_status"] == "observed"
    assert record["telemetry_status"] == "declared_only"


def test_unqualified_generated_input_is_invalid_not_owner_truth() -> None:
    baseline = build_validation_telemetry_baseline(
        [{"repo_id": "owner-a", "classification": "implemented"}],
        port_inputs={
            "owner-a": {
                "owner_repo": "owner-a",
                "source_kind": "generated_inventory",
                "source_ref": "owner-a:generated/port.json",
                "port_ref": "stats/port.manifest.json",
                "payload": {"owner_repo": "owner-a"},
            }
        },
    )

    record = baseline["owner_records"][0]
    assert record["port_status"] == "invalid"
    assert record["telemetry_status"] == "invalid"
    assert baseline["summary"]["port_invalid_count"] == 1


def test_raw_packet_cannot_bypass_typed_admission() -> None:
    packet = valid_packet()
    packet["admitted"] = True

    with pytest.raises(TypeError, match="raw packets cannot bypass admission"):
        build_validation_telemetry_baseline(
            [{"repo_id": "aoa-evals", "classification": "implemented"}],
            port_inputs={},
            packets=[packet],  # type: ignore[list-item]
        )


def test_admission_receipt_binds_lane_and_keeps_acceptance_unproven() -> None:
    admission = admitted_packet()

    assert admission.is_intact()
    assert admission.receipt.acceptance_evidenced is False
    tampered = deepcopy(dict(admission.packet))
    tampered["node"] = dict(tampered["node"])
    tampered["node"]["claim_refs"] = ["claim:other"]
    owner_port = telemetry_port()
    validation = validated_port_schema(owner_port)
    with pytest.raises(ValidationTelemetryAdmissionError, match="declared telemetry lane"):
        admit_validation_telemetry_packet(
            tampered,
            schema_issues=[],
            telemetry_port_schema_validation=validation,
            telemetry_port=owner_port["validation_telemetry"],
            owner_port=owner_port,
            expected_owner_repo="aoa-evals",
            expected_telemetry_port_ref="stats/port.manifest.json#/validation_telemetry",
        )


def test_admission_requires_explicit_owner_and_port_bindings() -> None:
    owner_port = telemetry_port()
    with pytest.raises(ValidationTelemetryAdmissionError, match="expected_owner_repo"):
        admit_validation_telemetry_packet(
            valid_packet(),
            schema_issues=[],
            telemetry_port_schema_validation=validated_port_schema(owner_port),
            telemetry_port=owner_port["validation_telemetry"],
        )


def test_tampered_admission_receipt_blocks_projection() -> None:
    admission = admitted_packet()
    admission.packet["metrics"] = dict(admission.packet["metrics"])
    admission.packet["metrics"]["wall_ms"] = {"status": "observed", "value": -1}

    with pytest.raises(ValueError, match="receipt no longer binds"):
        build_validation_telemetry_baseline(
            [{"repo_id": "aoa-evals", "classification": "implemented"}],
            port_inputs={},
            packets=[admission],
        )


def test_current_owner_port_content_digest_is_a_projection_barrier() -> None:
    admission = admitted_packet()
    current = owner_input("aoa-evals")
    current["payload"] = deepcopy(current["payload"])
    current["payload"]["validation_telemetry"]["node_lanes"][0]["acceptance_barrier"] = (
        "changed after packet export"
    )

    with pytest.raises(ValueError, match="port content digest"):
        build_validation_telemetry_baseline(
            [{"repo_id": "aoa-evals", "classification": "implemented"}],
            port_inputs={"aoa-evals": current},
            packets=[admission],
        )


def test_incompatible_candidate_posture_groups_are_not_aggregated() -> None:
    first = admitted_packet()
    second_packet = valid_packet()
    second_packet["observation_id"] = "aoa-evals:stats-protocol:2026-08-21T12:01:00Z"
    second_packet["candidate_identity"] = dict(second_packet["candidate_identity"])
    second_packet["candidate_identity"]["digest"] = "sha256:" + "4" * 64
    second = admitted_packet(second_packet)
    baseline = build_validation_telemetry_baseline(
        [{"repo_id": "aoa-evals", "classification": "implemented"}],
        port_inputs={"aoa-evals": owner_input("aoa-evals")},
        packets=[first, second],
    )

    record = baseline["owner_records"][0]
    assert record["telemetry_status"] == "identity_incompatible"
    assert record["identity_barrier_status"] == "blocked"
    assert record["identity_group_count"] == 2
    assert baseline["summary"]["telemetry_incompatible_owner_count"] == 1
    assert baseline["summary"]["identity_barrier_owner_repos"] == ["aoa-evals"]
    assert record["field_coverage"]["wall_ms"]["status"] == "missing"


def test_duplicate_observation_is_not_projected_twice() -> None:
    with pytest.raises(ValueError, match="duplicate validation telemetry observation"):
        build_validation_telemetry_baseline(
            [{"repo_id": "aoa-evals", "classification": "implemented"}],
            port_inputs={"aoa-evals": owner_input("aoa-evals")},
            packets=[admitted_packet(), admitted_packet()],
        )


def test_first_failure_identity_and_strict_rfc3339_are_coherent() -> None:
    bad_timestamp = valid_packet()
    bad_timestamp["observed_at"] = "2026-99-99T99:99:99Z"
    assert any("strict RFC3339" in issue for issue in validate_validation_telemetry_packet(bad_timestamp))

    bad_failure = valid_packet()
    bad_failure["first_failure"] = {
        "status": "observed",
        "node_id": "other-node",
        "failure_class": "none",
        "evidence_ref": "reports/stats-protocol.json",
        "time_to_first_failure_ms": {"status": "observed", "value": 1},
    }
    issues = validate_validation_telemetry_packet(bad_failure)
    assert any("must identify an observed failure" in issue for issue in issues)
    assert any("must match packet.node.node_id" in issue for issue in issues)


def test_qualified_traversal_and_central_source_identity_fail_closed(tmp_path: Path) -> None:
    packet = valid_packet()
    packet["candidate_identity"] = {
        "kind": "git-tree",
        "source": "owner-a:../outside",
        "digest": "sha256:" + "1" * 64,
    }
    assert any("candidate_identity.source" in issue for issue in validate_validation_telemetry_packet(packet))

    fake_source_home = tmp_path / "source_home.manifest.json"
    fake_source_home.write_text(json.dumps({"not_an_aoa_stats_manifest": True}), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts/build_validation_telemetry_baseline.py"),
            "--source-home",
            str(fake_source_home),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "canonical" in result.stderr


def test_all_not_applicable_survives_aggregate_projection() -> None:
    baseline = build_validation_telemetry_baseline(
        [
            {"repo_id": "owner-a", "classification": "routed_to_stronger_owner"},
            {"repo_id": "owner-b", "classification": "not_applicable"},
        ],
        port_inputs={},
    )

    assert baseline["summary"]["owner_coverage_status"] == "not_applicable"
    assert baseline["summary"]["telemetry_coverage_status"] == "not_applicable"
    assert baseline["summary"]["telemetry_gap_owner_repos"] == []
    assert all(
        entry["status"] == "not_applicable"
        for entry in baseline["summary"]["field_coverage"].values()
    )


def test_reference_projection_does_not_claim_live_telemetry() -> None:
    packet = valid_packet()
    packet["posture"] = dict(packet["posture"])
    packet["posture"]["live_state"] = "live"
    live_owner_port = telemetry_port()
    live_owner_port["owner_repo"] = "aoa-evals"
    live_owner_port["evidence_posture"] = dict(live_owner_port["evidence_posture"])
    live_owner_port["evidence_posture"]["live_state"] = "live_capable"
    live_owner_port["validation_telemetry"]["exports"][0]["posture"] = "live"
    admission = admitted_packet(packet, owner_port=live_owner_port)
    current = owner_input("aoa-evals")
    current["payload"] = live_owner_port
    baseline = build_validation_telemetry_baseline(
        [{"repo_id": "aoa-evals", "classification": "implemented"}],
        port_inputs={"aoa-evals": current},
        packets=[admission],
        input_posture="reference_only",
    )
    assert baseline["owner_records"][0]["telemetry_status"] == "reference"


@pytest.mark.parametrize(
    ("freshness", "input_status", "expected_status"),
    (
        ("stale", "observed", "reference"),
        ("current", "not_observed", "reference"),
        ("current", "observed", "live"),
    ),
)
def test_mixed_live_projection_requires_current_observed_owner_binding(
    freshness: str,
    input_status: str,
    expected_status: str,
) -> None:
    packet = valid_packet()
    packet["posture"] = dict(packet["posture"])
    packet["posture"]["freshness"] = freshness
    packet["posture"]["live_state"] = "live"
    live_owner_port = telemetry_port()
    live_owner_port["owner_repo"] = "aoa-evals"
    live_owner_port["evidence_posture"] = dict(live_owner_port["evidence_posture"])
    live_owner_port["evidence_posture"]["live_state"] = "live_capable"
    live_owner_port["validation_telemetry"]["exports"][0]["posture"] = "live"
    admission = admitted_packet(packet, owner_port=live_owner_port)
    current = owner_input("aoa-evals")
    current["payload"] = live_owner_port
    current["input_status"] = input_status

    baseline = build_validation_telemetry_baseline(
        [{"repo_id": "aoa-evals", "classification": "implemented"}],
        port_inputs={"aoa-evals": current},
        packets=[admission],
        input_posture="mixed",
    )

    assert baseline["owner_records"][0]["telemetry_status"] == expected_status


def test_validation_telemetry_timing_measures_the_declared_validator_process() -> None:
    lane = telemetry_port()["validation_telemetry"]["node_lanes"][0]
    assert lane["validator_ref"] == "scripts/validate_stats_protocol.py"
    timing_contract = lane["timing_contract"]
    assert timing_contract["scope"] == "contextual_validator_process"
    assert timing_contract["p95_budget_ms"] is None

    samples_ms: list[float] = []
    for _ in range(timing_contract["sample_count"]):
        started = time.perf_counter()
        result = subprocess.run(
            [sys.executable, str(PROTOCOL_PATH)],
            cwd=REPO_ROOT,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            check=False,
            capture_output=True,
            text=True,
        )
        samples_ms.append((time.perf_counter() - started) * 1000)
        assert result.returncode == 0, result.stderr

    p95_ms = sorted(samples_ms)[-1]
    assert p95_ms >= 0
