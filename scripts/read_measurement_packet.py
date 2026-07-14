#!/usr/bin/env python3
"""Read one measurement contract and packet through the public stats boundary."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator, SchemaError


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder.packet_read import build_packet_read_result  # noqa: E402
from aoa_stats_builder.schema_validation import schema_issues  # noqa: E402


CONTRACT_SCHEMA_PATH = Path(
    "stats/measurement-contract/measurement-contract.schema.json"
)
PACKET_SCHEMA_PATH = Path(
    "stats/measurement-contract/measurement-packet.schema.json"
)
REQUEST_SCHEMA_PATH = Path(
    "stats/measurement-contract/packet-read-request.schema.json"
)
RESULT_SCHEMA_PATH = Path(
    "stats/measurement-contract/packet-read-result.schema.json"
)


def _load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: must be a JSON object")
    return payload


def _load_schema(path: Path) -> dict[str, Any]:
    schema = _load_object(REPO_ROOT / path)
    Draft202012Validator.check_schema(schema)
    return schema


def _read_request() -> tuple[dict[str, Any] | None, list[str]]:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        return None, [f"request: invalid JSON: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, ["request: must be a JSON object"]
    try:
        request_schema = _load_schema(REQUEST_SCHEMA_PATH)
    except (OSError, ValueError, json.JSONDecodeError, SchemaError) as exc:
        return None, [f"request contract unavailable: {exc}"]
    issues = schema_issues(request_schema, payload, label="request")
    return (payload if not issues else None), issues


def main() -> int:
    request, request_issues = _read_request()
    if request_issues:
        for issue in request_issues:
            print(f"[error] {issue}", file=sys.stderr)
        return 2
    assert request is not None

    try:
        contract_schema = _load_schema(CONTRACT_SCHEMA_PATH)
        packet_schema = _load_schema(PACKET_SCHEMA_PATH)
        result_schema = _load_schema(RESULT_SCHEMA_PATH)
    except (OSError, ValueError, json.JSONDecodeError, SchemaError) as exc:
        print(f"[error] read contract unavailable: {exc}", file=sys.stderr)
        return 3

    result = build_packet_read_result(
        request["contract"],
        request["packet"],
        contract_schema=contract_schema,
        packet_schema=packet_schema,
    )
    result_issues = schema_issues(result_schema, result, label="result")
    if result_issues:
        for issue in result_issues:
            print(f"[error] internal {issue}", file=sys.stderr)
        return 3
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
