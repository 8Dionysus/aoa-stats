#!/usr/bin/env python3
"""Build a deterministic validation-telemetry coverage baseline.

The command consumes an inventory plus explicitly named owner inputs.  It does
not discover repositories, infer missing measurements, or turn a green local
validator into a cross-owner sufficiency decision.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import validate_stats_protocol as protocol  # noqa: E402
from aoa_stats_builder.schema_validation import schema_issues  # noqa: E402
from aoa_stats_builder.validation_telemetry import (  # noqa: E402
    ValidationTelemetryAdmission,
    ValidationTelemetryAdmissionError,
    admit_validation_telemetry_packet,
    build_validation_telemetry_baseline,
    validate_central_source_home_identity,
)

BASELINE_SCHEMA_PATH = REPO_ROOT / "schemas/validation-telemetry-baseline.schema.json"


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"{path}: file is missing"
    except json.JSONDecodeError as exc:
        return None, f"{path}: invalid JSON: {exc}"
    if not isinstance(payload, dict):
        return None, f"{path}: must be a JSON object"
    return payload, None


def _owner_port_ref(path: Path) -> str:
    if path.name == "port.manifest.json" and path.parent.name == "stats":
        return path.relative_to(path.parent.parent).as_posix()
    return path.name


def _source_home_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _content_digest(payload: Mapping[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _load_inventory(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    inventory, error = _load_json(path)
    if error:
        return None, [error]
    assert inventory is not None
    schemas, schema_errors = protocol._load_schemas(REPO_ROOT)
    if schema_errors:
        return None, schema_errors
    registry = protocol._registry(schemas)
    issues = protocol._schema_issues(
        schemas[protocol.INVENTORY_SCHEMA_PATH.as_posix()],
        inventory,
        label=str(path),
        registry=registry,
    )
    issues.extend(
        protocol._validate_inventory(
            REPO_ROOT,
            schemas[protocol.INVENTORY_SCHEMA_PATH.as_posix()],
            registry=registry,
        )
        if path.resolve() == (REPO_ROOT / protocol.INVENTORY_PATH).resolve()
        else []
    )
    return inventory, issues


def _load_port(
    path: Path,
    *,
    schemas: dict[str, dict[str, Any]],
    registry: Any,
) -> tuple[str | None, dict[str, Any] | None, list[str]]:
    payload, error = _load_json(path)
    if error:
        return None, None, [error]
    assert payload is not None
    owner_repo = payload.get("owner_repo")
    port_ref = _owner_port_ref(path)
    label = str(path)
    issues: list[str] = []
    if path.name != "port.manifest.json" or path.parent.name != "stats":
        issues.append(
            f"{label}: owner port must be supplied as stats/port.manifest.json"
        )
    issues.extend(
        protocol.validate_port_payload(
            payload,
            label=label,
            port_schema=schemas[protocol.PORT_SCHEMA_PATH.as_posix()],
            registry=registry,
        )
    )
    issues.extend(
        protocol._validate_port_packets(
            path,
            payload,
            packet_schema=schemas[protocol.PACKET_SCHEMA_PATH.as_posix()],
            registry=registry,
        )
    )
    issues.extend(
        protocol._validate_validation_telemetry_packets(
            path,
            payload,
            packet_schema=schemas[protocol.VALIDATION_TELEMETRY_PACKET_SCHEMA_PATH.as_posix()],
            registry=registry,
        )
    )
    if not isinstance(owner_repo, str) or not owner_repo:
        issues.append(f"{label}: owner_repo must be non-empty")
        return None, payload, issues
    return owner_repo, {
        "owner_repo": owner_repo,
        "source_kind": "direct_owner_source",
        "source_ref": f"{owner_repo}:{port_ref}",
        "port_ref": port_ref,
        "payload": payload,
        "port_content_digest": _content_digest(payload),
        "_owner_root": str(path.parent.parent.resolve()),
        "input_status": "invalid" if issues else "observed",
        "telemetry_port_ref": f"{port_ref}#/validation_telemetry"
        if isinstance(payload.get("validation_telemetry"), dict)
        else None,
    }, issues


def _load_packet(
    path: Path,
    *,
    schemas: dict[str, dict[str, Any]],
    registry: Any,
    telemetry_port: Mapping[str, Any] | None,
    owner_port: Mapping[str, Any] | None,
    expected_owner_repo: str | None,
    expected_telemetry_port_ref: str | None,
    expected_port_ref: str | None,
    expected_packet_ref: str | None,
    owner_source_ref: str | None,
) -> tuple[ValidationTelemetryAdmission | None, list[str]]:
    packet, error = _load_json(path)
    if error:
        return None, [error]
    assert packet is not None
    schema_findings = protocol._schema_issues(
        schemas[protocol.VALIDATION_TELEMETRY_PACKET_SCHEMA_PATH.as_posix()],
        packet,
        label=str(path),
        registry=registry,
    )
    try:
        admission = admit_validation_telemetry_packet(
            packet,
            schema_issues=[f"{path}: {issue}" for issue in schema_findings],
            telemetry_port=telemetry_port,
            owner_port=owner_port,
            expected_owner_repo=expected_owner_repo,
            expected_telemetry_port_ref=expected_telemetry_port_ref,
            expected_port_ref=expected_port_ref,
            expected_packet_ref=expected_packet_ref,
            owner_source_ref=owner_source_ref,
            label=str(path),
        )
    except ValidationTelemetryAdmissionError as exc:
        return None, list(exc.issues)
    return admission, []


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build an explicit-input validation telemetry coverage baseline."
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=REPO_ROOT / "stats/federation/owner-inventory.json",
    )
    parser.add_argument(
        "--source-home",
        type=Path,
        default=REPO_ROOT / "stats/source_home.manifest.json",
        help="Central aoa-stats source-home input; it is not treated as an owner port.",
    )
    parser.add_argument(
        "--port",
        action="append",
        type=Path,
        default=[],
        help="Explicit owner stats/port.manifest.json; may be repeated.",
    )
    parser.add_argument(
        "--packet",
        action="append",
        type=Path,
        default=[],
        help="Explicit validation telemetry packet; may be repeated.",
    )
    parser.add_argument("--source-revision", default=None)
    parser.add_argument(
        "--output",
        type=Path,
        help="Write the derived baseline here instead of printing it.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    inventory_path = args.inventory.expanduser().resolve()
    inventory, issues = _load_inventory(inventory_path)
    if inventory is None:
        for issue in issues:
            print(f"[error] {issue}", file=sys.stderr)
        return 1

    schemas, schema_errors = protocol._load_schemas(REPO_ROOT)
    issues.extend(schema_errors)
    if schema_errors:
        for issue in schema_errors:
            print(f"[error] {issue}", file=sys.stderr)
        return 1
    registry = protocol._registry(schemas)

    expected_owners = inventory.get("owners")
    routed_surfaces = inventory.get("routed_surfaces", [])
    if not isinstance(expected_owners, list) or not all(
        isinstance(owner, dict) for owner in expected_owners
    ):
        print("[error] inventory owners must be an object list", file=sys.stderr)
        return 1
    routed_surface_ids = [
        entry.get("id")
        for entry in routed_surfaces
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    ]
    expected_owner_repos = {
        owner.get("repo_id")
        for owner in expected_owners
        if isinstance(owner.get("repo_id"), str)
    }

    port_inputs: dict[str, dict[str, Any]] = {}
    source_home_path = args.source_home.expanduser().resolve()
    canonical_source_home_path = (REPO_ROOT / "stats/source_home.manifest.json").resolve()
    if source_home_path != canonical_source_home_path:
        issues.append(
            f"{source_home_path}: source-home input must be the canonical "
            f"{canonical_source_home_path}"
        )
        source_home = None
    else:
        source_home, source_home_error = _load_json(source_home_path)
        if source_home_error:
            issues.append(source_home_error)
        elif source_home is not None:
            source_home_digest = _source_home_digest(source_home_path)
            source_home_issues = validate_central_source_home_identity(
                source_home,
                content_digest=source_home_digest,
                label=str(source_home_path),
            )
            issues.extend(source_home_issues)
            if not source_home_issues:
                port_inputs["aoa-stats"] = {
                    "owner_repo": "aoa-stats",
                    "source_kind": "central_source_home",
                    "source_ref": "aoa-stats:stats/source_home.manifest.json",
                    "port_ref": "stats/source_home.manifest.json",
                    "payload": {
                        "owner_repo": "aoa-stats",
                        "source_home_input": True,
                        "source_home_ref": "stats/source_home.manifest.json",
                        "source_home_schema_version": source_home.get("schema_version"),
                        "source_home_status": source_home.get("status"),
                        "source_home_digest": source_home_digest,
                    },
                    "input_status": "observed",
                }

    for raw_path in args.port:
        path = raw_path.expanduser().resolve()
        owner_repo, input_entry, port_issues = _load_port(
            path,
            schemas=schemas,
            registry=registry,
        )
        issues.extend(port_issues)
        if owner_repo is None or input_entry is None:
            continue
        if owner_repo not in expected_owner_repos:
            issues.append(f"{path}: owner_repo {owner_repo!r} is not in the supplied inventory")
            continue
        if owner_repo in port_inputs:
            issues.append(f"{path}: duplicate explicit input for owner {owner_repo!r}")
            continue
        port_inputs[owner_repo] = input_entry

    packets: list[ValidationTelemetryAdmission] = []
    for raw_path in args.packet:
        path = raw_path.expanduser().resolve()
        packet_owner: str | None = None
        packet_preview, packet_preview_error = _load_json(path)
        if packet_preview_error:
            issues.append(packet_preview_error)
            continue
        if packet_preview is not None:
            packet_owner_value = packet_preview.get("owner_repo")
            if isinstance(packet_owner_value, str):
                packet_owner = packet_owner_value
        owner_input = port_inputs.get(packet_owner or "")
        telemetry_port = (
            owner_input.get("payload", {}).get("validation_telemetry")
            if isinstance(owner_input, Mapping)
            and isinstance(owner_input.get("payload"), Mapping)
            else None
        )
        expected_telemetry_port_ref = (
            owner_input.get("telemetry_port_ref")
            if isinstance(owner_input, Mapping)
            else None
        )
        owner_port = (
            owner_input.get("payload")
            if isinstance(owner_input, Mapping)
            and isinstance(owner_input.get("payload"), Mapping)
            else None
        )
        expected_port_ref = (
            owner_input.get("port_ref")
            if isinstance(owner_input, Mapping)
            else None
        )
        owner_source_ref = (
            owner_input.get("source_ref")
            if isinstance(owner_input, Mapping)
            else None
        )
        expected_packet_ref: str | None = None
        if isinstance(owner_input, Mapping):
            owner_root_value = owner_input.get("_owner_root")
            if isinstance(owner_root_value, str):
                owner_root = Path(owner_root_value).resolve()
                try:
                    expected_packet_ref = path.relative_to(owner_root).as_posix()
                except ValueError:
                    issues.append(
                        f"{path}: packet must be contained by the explicit owner root "
                        f"{owner_root}"
                    )
        packet, packet_issues = _load_packet(
            path,
            schemas=schemas,
            registry=registry,
            telemetry_port=telemetry_port if isinstance(telemetry_port, Mapping) else None,
            owner_port=owner_port,
            expected_owner_repo=packet_owner,
            expected_telemetry_port_ref=(
                expected_telemetry_port_ref
                if isinstance(expected_telemetry_port_ref, str)
                else None
            ),
            expected_port_ref=(
                expected_port_ref if isinstance(expected_port_ref, str) else None
            ),
            expected_packet_ref=expected_packet_ref,
            owner_source_ref=(
                owner_source_ref if isinstance(owner_source_ref, str) else None
            ),
        )
        issues.extend(packet_issues)
        if packet is not None:
            owner_repo = packet.packet.get("owner_repo")
            if owner_repo not in expected_owner_repos:
                issues.append(
                    f"{path}: owner_repo {owner_repo!r} is not in the supplied inventory"
                )
            else:
                packets.append(packet)

    baseline = build_validation_telemetry_baseline(
        expected_owners,
        port_inputs=port_inputs,
        packets=packets,
        inventory_ref=_owner_port_ref(inventory_path),
        routed_surface_ids=routed_surface_ids,
        source_revision=args.source_revision,
        input_posture="reference_only",
    )
    baseline_schema = json.loads(BASELINE_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(baseline_schema)
    baseline_issues = schema_issues(
        baseline_schema,
        baseline,
        label="validation telemetry baseline",
    )
    issues.extend(baseline_issues)

    rendered = json.dumps(baseline, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        output_path = args.output.expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        print(f"[ok] wrote {output_path}")
    else:
        print(rendered, end="")

    if issues:
        print("[error] explicit input issues:", file=sys.stderr)
        for issue in sorted(set(issues)):
            print(f"- {issue}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
