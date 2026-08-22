from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder.schema_validation import schema_issues  # noqa: E402
from aoa_stats_builder.validation_telemetry import (  # noqa: E402
    VALIDATION_TELEMETRY_FIELDS,
    build_validation_telemetry_baseline,
    validate_validation_telemetry_packet,
    validate_validation_telemetry_port,
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
                "id": "release-check",
                "lane": "local-release",
                "semantic_class": "contract_abi_api",
                "budget_tier": "fast",
                "validator_ref": "scripts/release_check.py",
                "cacheability": "read_only",
                "parallel_safety": "serialized",
                "claim_refs": ["claim:release-contract"],
            }
        ],
        "exports": [
            {
                "id": "validation-telemetry",
                "posture": "declaration_only",
                "packet_refs": [],
                "evidence_refs": ["reports/validation-telemetry.json"],
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
        "observation_id": "aoa-evals:release-check:2026-08-21T12:00:00Z",
        "observed_at": "2026-08-21T12:00:00Z",
        "node": {
            "node_id": "release-check",
            "lane": "local-release",
            "semantic_class": "contract_abi_api",
            "budget_tier": "fast",
            "validator_ref": "scripts/release_check.py",
            "claim_refs": ["claim:release-contract"],
        },
        "result": {
            "status": "pass",
            "exit_code": 0,
            "result_ref": "reports/release-check.json",
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
            "receipt_ref": "reports/release-check-receipt.json",
        },
        "first_failure": {"status": "none"},
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
        "provenance": {
            "evidence_refs": [
                {"kind": "owner-report", "ref": "reports/release-check.json"}
            ],
            "derivation_ref": "owner:aoa-evals/release-check",
            "source_revision": "git:abcdef1",
        },
        "posture": {
            "freshness": "reference",
            "live_state": "reference",
            "privacy": "public",
            "raw_content_included": False,
        },
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


def test_unknown_metric_cannot_carry_zero_as_a_proxy() -> None:
    schemas, issues = protocol._load_schemas(REPO_ROOT)
    assert issues == []
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


def test_owner_port_without_extension_is_a_visible_nearest_collision() -> None:
    inventory = load_json("stats/federation/owner-inventory.json")
    baseline = build_validation_telemetry_baseline(
        inventory["owners"],
        port_inputs={
            "aoa-stats": {
                "port_ref": "stats/source_home.manifest.json",
                "payload": {"owner_repo": "aoa-stats", "source_home_input": True},
            },
            "aoa-kag": {
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
    assert validate_validation_telemetry_packet(packet) == []

    baseline = build_validation_telemetry_baseline(
        inventory["owners"],
        port_inputs={
            "aoa-kag": {
                "port_ref": "stats/port.manifest.json",
                "payload": {
                    "owner_repo": "aoa-kag",
                    "validation_telemetry": {
                        "node_lanes": [{"id": "node"}],
                    },
                },
            }
        },
        packets=[packet],
    )
    kag = next(record for record in baseline["owner_records"] if record["owner_repo"] == "aoa-kag")
    assert kag["telemetry_status"] == "reference"
    assert kag["field_coverage"]["wall_ms"]["status"] == "unknown"
    assert kag["field_coverage"]["wall_ms"]["owner_count"] == 0
    assert kag["field_coverage"]["first_failure"]["status"] == "stale"
