#!/usr/bin/env python3
"""Validate the federated stats grammar, inventory, ports, and packets."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker, SchemaError
from referencing import Registry, Resource

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder.measurement import (  # noqa: E402
    validate_contract_semantics,
    validate_packet_semantics,
    validate_packet_set,
)

MEASUREMENT_SCHEMA_PATH = Path(
    "stats/measurement-contract/measurement-contract.schema.json"
)
PACKET_SCHEMA_PATH = Path("stats/measurement-contract/measurement-packet.schema.json")
PORT_SCHEMA_PATH = Path("stats/federation/local-port.schema.json")
INVENTORY_SCHEMA_PATH = Path("stats/federation/owner-inventory.schema.json")
INVENTORY_PATH = Path("stats/federation/owner-inventory.json")
CENTRAL_CONTRACT_REFS = {
    "aoa-stats:stats/measurement-contract/measurement-contract.schema.json",
    "aoa-stats:stats/measurement-contract/measurement-packet.schema.json",
}


def _load_object(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"{path}: file is missing"
    except json.JSONDecodeError as exc:
        return None, f"{path}: invalid JSON: {exc}"
    if not isinstance(payload, dict):
        return None, f"{path}: must be a JSON object"
    return payload, None


def _portable_ref(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    lowered = value.lower()
    return not (
        value.startswith(("/", "~"))
        or "/home/" in lowered
        or "/srv/" in lowered
        or ".aoa/sessions" in lowered
        or "transcript" in lowered
    )


def _schema_issues(
    schema: Mapping[str, Any], payload: Mapping[str, Any], *, label: str, registry: Registry[Any] | None = None
) -> list[str]:
    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
        registry=registry or Registry(),
    )
    issues: list[str] = []
    for error in sorted(validator.iter_errors(payload), key=lambda item: list(item.absolute_path)):
        location = ".".join(str(part) for part in error.absolute_path)
        suffix = f":{location}" if location else ""
        issues.append(f"{label}{suffix}: {error.message}")
    return issues


def _load_schemas(repo_root: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    schemas: dict[str, dict[str, Any]] = {}
    issues: list[str] = []
    for relative in (
        MEASUREMENT_SCHEMA_PATH,
        PACKET_SCHEMA_PATH,
        PORT_SCHEMA_PATH,
        INVENTORY_SCHEMA_PATH,
    ):
        schema, error = _load_object(repo_root / relative)
        if error:
            issues.append(error)
            continue
        assert schema is not None
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as exc:
            issues.append(f"{relative}: invalid JSON schema: {exc.message}")
            continue
        schemas[relative.as_posix()] = schema
    return schemas, issues


def _registry(schemas: Mapping[str, Mapping[str, Any]]) -> Registry[Any]:
    registry: Registry[Any] = Registry()
    for schema in schemas.values():
        schema_id = schema.get("$id")
        if isinstance(schema_id, str):
            registry = registry.with_resource(schema_id, Resource.from_contents(schema))
    return registry


def _validate_inventory(
    repo_root: Path,
    inventory_schema: Mapping[str, Any],
    *,
    registry: Registry[Any],
) -> list[str]:
    inventory, error = _load_object(repo_root / INVENTORY_PATH)
    if error:
        return [error]
    assert inventory is not None
    issues = _schema_issues(
        inventory_schema,
        inventory,
        label=INVENTORY_PATH.as_posix(),
        registry=registry,
    )
    owners = inventory.get("owners")
    if not isinstance(owners, list):
        return issues

    repo_ids: list[str] = []
    workspace_routes: set[str] = set()
    owner_by_id: dict[str, Mapping[str, Any]] = {}
    for index, entry in enumerate(owners):
        if not isinstance(entry, Mapping):
            continue
        repo_id = entry.get("repo_id")
        workspace_route = entry.get("workspace_route")
        if isinstance(repo_id, str):
            if repo_id in owner_by_id:
                issues.append(f"{INVENTORY_PATH}:owners[{index}]: duplicate repo_id {repo_id!r}")
            repo_ids.append(repo_id)
            owner_by_id[repo_id] = entry
        if isinstance(workspace_route, str):
            if workspace_route in workspace_routes:
                issues.append(
                    f"{INVENTORY_PATH}:owners[{index}]: duplicate workspace_route {workspace_route!r}"
                )
            workspace_routes.add(workspace_route)
        for field in ("workspace_route", "owner_boundary_ref", "port_ref"):
            value = entry.get(field)
            if value is not None and not _portable_ref(value):
                issues.append(
                    f"{INVENTORY_PATH}:owners[{index}]: {field} is not portable"
                )
        classification = entry.get("classification")
        if classification in {"routed_to_stronger_owner", "not_applicable", "blocked"} and not entry.get(
            "rationale"
        ):
            issues.append(
                f"{INVENTORY_PATH}:owners[{index}]: {classification} requires rationale"
            )

    if repo_ids != sorted(repo_ids):
        issues.append(f"{INVENTORY_PATH}: owners must be sorted by repo_id")
    central = owner_by_id.get("aoa-stats")
    if not central or central.get("classification") != "implemented":
        issues.append(f"{INVENTORY_PATH}: aoa-stats must be an implemented central owner")

    routed = inventory.get("routed_surfaces")
    routed_ids: set[str] = set()
    if isinstance(routed, list):
        for index, entry in enumerate(routed):
            if not isinstance(entry, Mapping):
                continue
            surface_id = entry.get("id")
            if isinstance(surface_id, str):
                if surface_id in routed_ids:
                    issues.append(
                        f"{INVENTORY_PATH}:routed_surfaces[{index}]: duplicate id {surface_id!r}"
                    )
                routed_ids.add(surface_id)
            if entry.get("owner_repo") not in owner_by_id:
                issues.append(
                    f"{INVENTORY_PATH}:routed_surfaces[{index}]: owner_repo is not inventoried"
                )
            if not _portable_ref(entry.get("owner_route")):
                issues.append(
                    f"{INVENTORY_PATH}:routed_surfaces[{index}]: owner_route is not portable"
                )
    return issues


def validate_port_payload(
    port: Mapping[str, Any],
    *,
    label: str,
    port_schema: Mapping[str, Any],
    registry: Registry[Any],
) -> list[str]:
    issues = _schema_issues(port_schema, port, label=label, registry=registry)
    owner_repo = port.get("owner_repo")
    refs = port.get("central_contract_refs")
    if isinstance(refs, list) and set(refs) != CENTRAL_CONTRACT_REFS:
        issues.append(f"{label}: central_contract_refs must contain both canonical schemas")

    questions = port.get("questions")
    question_ids: list[str] = []
    if isinstance(questions, list):
        question_ids = [
            entry["id"]
            for entry in questions
            if isinstance(entry, Mapping) and isinstance(entry.get("id"), str)
        ]
        if len(question_ids) != len(set(question_ids)):
            issues.append(f"{label}: question ids must be unique")
        for index, question in enumerate(questions):
            if not isinstance(question, Mapping):
                continue
            for ref in question.get("consumer_refs", []):
                if not _portable_ref(ref):
                    issues.append(
                        f"{label}:questions[{index}]: consumer_ref is not portable"
                    )

    measurements = port.get("measurements")
    measurement_ids: list[str] = []
    measurement_by_id: dict[str, Mapping[str, Any]] = {}
    if isinstance(measurements, list):
        for index, measurement in enumerate(measurements):
            if not isinstance(measurement, Mapping):
                continue
            measurement_id = measurement.get("measurement_id")
            if isinstance(measurement_id, str):
                measurement_ids.append(measurement_id)
                measurement_by_id[measurement_id] = measurement
            if measurement.get("owner_repo") != owner_repo:
                issues.append(
                    f"{label}:measurements[{index}]: owner_repo must match local port owner"
                )
            if measurement.get("question_ref") not in question_ids:
                issues.append(
                    f"{label}:measurements[{index}]: question_ref is not declared"
                )
            issues.extend(
                f"{label}:measurements[{index}]: {issue}"
                for issue in validate_contract_semantics(measurement)
            )
    if len(measurement_ids) != len(set(measurement_ids)):
        issues.append(f"{label}: measurement ids must be unique")

    exports = port.get("exports")
    export_ids: list[str] = []
    if isinstance(exports, list):
        for index, export in enumerate(exports):
            if not isinstance(export, Mapping):
                continue
            measurement_id = export.get("measurement_id")
            if isinstance(measurement_id, str):
                export_ids.append(measurement_id)
            measurement = measurement_by_id.get(measurement_id)
            if measurement is None:
                issues.append(
                    f"{label}:exports[{index}]: measurement_id is not declared"
                )
                continue
            posture = export.get("posture")
            packet_refs = export.get("packet_refs")
            if posture == "declaration_only" and packet_refs:
                issues.append(
                    f"{label}:exports[{index}]: declaration_only must not name packets"
                )
            if posture in {"reference", "live"} and not packet_refs:
                issues.append(
                    f"{label}:exports[{index}]: {posture} export requires packet_refs"
                )
            if posture == "live":
                live_state = measurement.get("live_state")
                capability = (
                    live_state.get("capability") if isinstance(live_state, Mapping) else None
                )
                if capability != "live_capable":
                    issues.append(
                        f"{label}:exports[{index}]: live export requires live-capable measurement"
                    )
            for field in ("packet_refs", "evidence_refs"):
                for ref in export.get(field, []):
                    if not _portable_ref(ref):
                        issues.append(
                            f"{label}:exports[{index}]: {field} contains a non-portable ref"
                        )
    if len(export_ids) != len(set(export_ids)):
        issues.append(f"{label}: one measurement may have at most one export record")
    return issues


def _owner_root_for_port(port_path: Path) -> Path:
    if port_path.name == "port.manifest.json" and port_path.parent.name == "stats":
        return port_path.parent.parent.resolve()
    return port_path.parent.resolve()


def _resolve_owner_packet_ref(
    port_path: Path,
    packet_ref: str,
    *,
    label: str,
) -> tuple[Path | None, str | None]:
    owner_root = _owner_root_for_port(port_path)
    candidate = (owner_root / packet_ref).resolve()
    try:
        candidate.relative_to(owner_root)
    except ValueError:
        return None, f"{label}: packet_ref {packet_ref!r} escapes owner root"
    return candidate, None


def _validate_port_packets(
    port_path: Path,
    port: Mapping[str, Any],
    *,
    packet_schema: Mapping[str, Any],
    registry: Registry[Any],
) -> list[str]:
    label = str(port_path)
    issues: list[str] = []
    owner_root = _owner_root_for_port(port_path)
    try:
        port_ref = port_path.relative_to(owner_root).as_posix()
    except ValueError:
        port_ref = port_path.name

    measurements = port.get("measurements")
    measurement_by_id: dict[str, tuple[int, Mapping[str, Any]]] = {}
    if isinstance(measurements, list):
        for index, measurement in enumerate(measurements):
            if not isinstance(measurement, Mapping):
                continue
            measurement_id = measurement.get("measurement_id")
            if isinstance(measurement_id, str):
                measurement_by_id[measurement_id] = (index, measurement)

    exports = port.get("exports")
    if not isinstance(exports, list):
        return issues
    for export_index, export in enumerate(exports):
        if not isinstance(export, Mapping):
            continue
        posture = export.get("posture")
        if posture not in {"reference", "live"}:
            continue
        measurement_entry = measurement_by_id.get(export.get("measurement_id"))
        if measurement_entry is None:
            continue
        measurement_index, contract = measurement_entry
        expected_contract_ref = f"{port_ref}#/measurements/{measurement_index}"
        packets: list[Mapping[str, Any]] = []
        for packet_ref in export.get("packet_refs", []):
            if not isinstance(packet_ref, str) or not _portable_ref(packet_ref):
                continue
            packet_path, resolve_error = _resolve_owner_packet_ref(
                port_path,
                packet_ref,
                label=f"{label}:exports[{export_index}]",
            )
            if resolve_error:
                issues.append(resolve_error)
                continue
            assert packet_path is not None
            packet, packet_error = _load_object(packet_path)
            if packet_error:
                issues.append(packet_error)
                continue
            assert packet is not None
            issues.extend(
                _schema_issues(
                    packet_schema,
                    packet,
                    label=str(packet_path),
                    registry=registry,
                )
            )
            if packet.get("contract_ref") != expected_contract_ref:
                issues.append(
                    f"{packet_path}: contract_ref must equal {expected_contract_ref!r}"
                )
            packet_posture = packet.get("posture")
            packet_live_state = (
                packet_posture.get("live_state")
                if isinstance(packet_posture, Mapping)
                else None
            )
            if packet_live_state != posture:
                issues.append(
                    f"{packet_path}: posture.live_state must match export posture {posture!r}"
                )
            packets.append(packet)
        issues.extend(
            f"{label}:exports[{export_index}]: {issue}"
            for issue in validate_packet_set(contract, packets)
        )
    return issues


def validate(
    repo_root: Path = REPO_ROOT,
    *,
    port_paths: list[Path] | None = None,
    contract_path: Path | None = None,
    packet_paths: list[Path] | None = None,
) -> list[str]:
    repo_root = repo_root.resolve()
    schemas, issues = _load_schemas(repo_root)
    if issues:
        return issues
    registry = _registry(schemas)
    issues.extend(
        _validate_inventory(
            repo_root,
            schemas[INVENTORY_SCHEMA_PATH.as_posix()],
            registry=registry,
        )
    )

    for raw_path in port_paths or []:
        path = raw_path.expanduser().resolve()
        port, error = _load_object(path)
        if error:
            issues.append(error)
            continue
        assert port is not None
        issues.extend(
            validate_port_payload(
                port,
                label=str(path),
                port_schema=schemas[PORT_SCHEMA_PATH.as_posix()],
                registry=registry,
            )
        )
        issues.extend(
            _validate_port_packets(
                path,
                port,
                packet_schema=schemas[PACKET_SCHEMA_PATH.as_posix()],
                registry=registry,
            )
        )

    if packet_paths and contract_path is None:
        issues.append("--packet requires --contract")
    if contract_path is not None:
        contract, error = _load_object(contract_path.expanduser().resolve())
        if error:
            issues.append(error)
        else:
            assert contract is not None
            issues.extend(
                _schema_issues(
                    schemas[MEASUREMENT_SCHEMA_PATH.as_posix()],
                    contract,
                    label=str(contract_path),
                    registry=registry,
                )
            )
            issues.extend(
                f"{contract_path}: {issue}"
                for issue in validate_contract_semantics(contract)
            )
            for raw_path in packet_paths or []:
                path = raw_path.expanduser().resolve()
                packet, packet_error = _load_object(path)
                if packet_error:
                    issues.append(packet_error)
                    continue
                assert packet is not None
                issues.extend(
                    _schema_issues(
                        schemas[PACKET_SCHEMA_PATH.as_posix()],
                        packet,
                        label=str(path),
                        registry=registry,
                    )
                )
                issues.extend(
                    f"{path}: {issue}"
                    for issue in validate_packet_semantics(contract, packet)
                )
    return issues


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the central stats protocol and optional owner-local artifacts."
    )
    parser.add_argument(
        "--port",
        action="append",
        default=[],
        type=Path,
        help="Owner-local stats/port.manifest.json to validate; may be repeated.",
    )
    parser.add_argument(
        "--contract",
        type=Path,
        help="Standalone measurement contract used to validate --packet inputs.",
    )
    parser.add_argument(
        "--packet",
        action="append",
        default=[],
        type=Path,
        help="Measurement packet to validate against --contract; may be repeated.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    issues = validate(
        port_paths=args.port,
        contract_path=args.contract,
        packet_paths=args.packet,
    )
    if issues:
        for issue in issues:
            print(f"[error] {issue}", file=sys.stderr)
        return 1
    print("[ok] federated stats protocol and requested artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
