#!/usr/bin/env python3
"""Review one private stack-captured stats_catalog result as the stats owner."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG_SCHEMA = REPO_ROOT / "schemas" / "summary-surface-catalog.schema.json"
OWNER_PAYLOAD_SCHEMA_REF = "owner://aoa-stats/schema/payload"
COMMITTED_CATALOG = REPO_ROOT / "generated" / "summary_surface_catalog.min.json"
LIVE_CATALOG = REPO_ROOT / "state" / "generated" / "summary_surface_catalog.min.json"
MAX_INPUT_BYTES = 2 * 1024 * 1024
MAX_REVIEW_TTL_SECONDS = 300
CAPTURE_RECEIPT_SCHEMA = "abyss_stack_mcp_canary_receipt_v1"
RESULT_ARTIFACT_SCHEMA = "abyss_stack_mcp_canary_result_artifact_v1"
REVIEW_SCHEMA = "aoa_organ_owner_result_review_v1"
STATS_RESULT_SCHEMA = "aoa_stats_summary_surface_catalog_v2"
REVIEW_CLAIM_LIMIT = (
    "This owner-issued review proves only the named owner's schema grounding "
    "and freshness assessment for one content-addressed captured result. It "
    "does not prove owner acceptance, central proof, admission, cross-organ "
    "benefit, execution authorization, or rollback."
)


class StatsOwnerReviewError(ValueError):
    """The private capture cannot support an owner-bounded stats review."""


def _canonical_json_bytes(value: Any, *, ensure_ascii: bool) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=ensure_ascii,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _digest(value: Any, *, ensure_ascii: bool = False) -> str:
    return (
        "sha256:"
        + hashlib.sha256(
            _canonical_json_bytes(value, ensure_ascii=ensure_ascii)
        ).hexdigest()
    )


def _file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _aware_time(value: str | datetime, label: str) -> datetime:
    try:
        parsed = (
            value
            if isinstance(value, datetime)
            else datetime.fromisoformat(value.replace("Z", "+00:00"))
        )
    except ValueError as exc:
        raise StatsOwnerReviewError(f"{label} is not a valid timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise StatsOwnerReviewError(f"{label} must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def _require_regular_private_file(path: Path, label: str) -> Path:
    absolute = path.expanduser().absolute()
    for component in (*reversed(absolute.parents), absolute):
        if component.is_symlink():
            raise StatsOwnerReviewError(f"{label} cannot traverse a symlink")
    try:
        metadata = absolute.stat()
    except OSError as exc:
        raise StatsOwnerReviewError(f"{label} is unavailable") from exc
    if not stat.S_ISREG(metadata.st_mode):
        raise StatsOwnerReviewError(f"{label} must be a regular file")
    if stat.S_IMODE(metadata.st_mode) & 0o077:
        raise StatsOwnerReviewError(f"{label} must not be group/world accessible")
    if not 1 <= metadata.st_size <= MAX_INPUT_BYTES:
        raise StatsOwnerReviewError(f"{label} has an invalid bounded size")
    return absolute


def _read_private_json(path: Path, label: str) -> dict[str, Any]:
    absolute = _require_regular_private_file(path, label)
    try:
        value = json.loads(absolute.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise StatsOwnerReviewError(f"{label} is not valid JSON") from exc
    if not isinstance(value, dict):
        raise StatsOwnerReviewError(f"{label} must be a JSON object")
    return value


def _read_public_json(path: Path, label: str) -> dict[str, Any]:
    absolute = path.expanduser().resolve()
    try:
        value = json.loads(absolute.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise StatsOwnerReviewError(f"{label} is unavailable or invalid") from exc
    if not isinstance(value, dict):
        raise StatsOwnerReviewError(f"{label} must be a JSON object")
    return value


def _read_public_schema(path: Path, label: str) -> dict[str, Any]:
    value = _read_public_json(path, label)
    Draft202012Validator.check_schema(value)
    return value


def _relative_ref(root: Path, path: Path, label: str) -> str:
    root = root.expanduser().absolute()
    try:
        return path.expanduser().absolute().relative_to(root).as_posix()
    except ValueError as exc:
        raise StatsOwnerReviewError(f"{label} is outside the capture root") from exc


def _assert_content_address(payload: dict[str, Any], identity: str, label: str) -> None:
    claimed = payload.get(identity)
    body = dict(payload)
    body.pop(identity, None)
    if claimed != _digest(body):
        raise StatsOwnerReviewError(f"{label} content address does not match")


def _validate_capture(
    receipt: dict[str, Any],
    artifact: dict[str, Any],
    *,
    capture_root: Path,
    receipt_path: Path,
    artifact_path: Path,
) -> tuple[dict[str, Any], datetime, datetime, str, str]:
    if receipt.get("schema_version") != CAPTURE_RECEIPT_SCHEMA:
        raise StatsOwnerReviewError("capture receipt schema is unsupported")
    expected_receipt = {
        "issuer": "abyss-stack",
        "consumer_id": "abyss-stack-mcp-canary",
        "organ_id": "aoa-stats",
        "policy_family": "read",
        "tool_name": "stats_catalog",
        "call_succeeded": True,
        "result_contract_matched": True,
        "result_schema_identity": STATS_RESULT_SCHEMA,
        "contains_secrets": False,
        "content_trust": "untrusted_data",
        "instruction_authority": "none",
    }
    for field, expected in expected_receipt.items():
        if receipt.get(field) != expected:
            raise StatsOwnerReviewError(f"capture receipt {field} does not match")
    if receipt.get("reason_codes") not in ([], ()):
        raise StatsOwnerReviewError(
            "successful capture receipt carries failure reasons"
        )
    _assert_content_address(receipt, "receipt_id", "capture receipt")

    if artifact.get("schema_version") != RESULT_ARTIFACT_SCHEMA:
        raise StatsOwnerReviewError("result artifact schema is unsupported")
    expected_artifact = {
        "issuer": "abyss-stack",
        "organ_id": "aoa-stats",
        "policy_family": "read",
        "service_id": receipt.get("service_id"),
        "canary_route": receipt.get("canary_route"),
        "tool_name": "stats_catalog",
        "tool_arguments_digest": receipt.get("tool_arguments_digest"),
        "observed_at": receipt.get("observed_at"),
        "result_schema_identity": STATS_RESULT_SCHEMA,
        "result_digest": receipt.get("result_digest"),
        "contains_secrets": False,
        "content_trust": "untrusted_data",
        "instruction_authority": "none",
    }
    for field, expected in expected_artifact.items():
        if artifact.get(field) != expected:
            raise StatsOwnerReviewError(f"result artifact {field} does not match")
    _assert_content_address(artifact, "artifact_id", "result artifact")

    owner_payload = artifact.get("owner_payload")
    if not isinstance(owner_payload, dict):
        raise StatsOwnerReviewError("result artifact owner payload must be an object")
    if _digest(owner_payload) != receipt.get("result_digest"):
        raise StatsOwnerReviewError("owner payload digest does not match receipt")

    receipt_ref = _relative_ref(capture_root, receipt_path, "capture receipt")
    artifact_ref = _relative_ref(capture_root, artifact_path, "result artifact")
    if receipt.get("result_artifact_ref") != artifact_ref:
        raise StatsOwnerReviewError("result artifact path does not match receipt")
    if not receipt_ref.startswith("records/aoa-stats/"):
        raise StatsOwnerReviewError(
            "capture receipt is outside the aoa-stats record lane"
        )
    if not artifact_ref.startswith("results/aoa-stats/"):
        raise StatsOwnerReviewError(
            "result artifact is outside the aoa-stats result lane"
        )

    observed_at = _aware_time(str(receipt.get("observed_at") or ""), "observed_at")
    expires_at = _aware_time(str(receipt.get("expires_at") or ""), "expires_at")
    if expires_at <= observed_at:
        raise StatsOwnerReviewError("capture receipt expiry is invalid")
    return owner_payload, observed_at, expires_at, receipt_ref, artifact_ref


def _owner_runtime_root(path: Path | None) -> Path | None:
    if path is None:
        return None
    absolute = path.expanduser().absolute()
    for component in (*reversed(absolute.parents), absolute):
        if component.is_symlink():
            raise StatsOwnerReviewError("owner runtime root cannot traverse a symlink")
    if not absolute.is_dir():
        raise StatsOwnerReviewError("owner runtime root must be a directory")
    return absolute


def _catalog_source(
    payload: dict[str, Any],
    *,
    owner_runtime_root: Path | None,
) -> tuple[Path | None, str | None, Path | None, str | None]:
    identity = payload.get("artifact_identity")
    content_identity = (
        identity.get("content_identity") if isinstance(identity, dict) else None
    )
    if not isinstance(content_identity, str):
        return None, None, None, None
    if content_identity.startswith("state/generated/summary_surface_catalog.min.json "):
        runtime_root = _owner_runtime_root(owner_runtime_root)
        if runtime_root is None:
            return (
                None,
                "state/generated/summary_surface_catalog.min.json",
                None,
                "owner-runtime-root-required",
            )
        return (
            runtime_root / "state" / "generated" / "summary_surface_catalog.min.json",
            "state/generated/summary_surface_catalog.min.json",
            runtime_root,
            None,
        )
    if content_identity.startswith("generated/summary_surface_catalog.min.json "):
        return (
            COMMITTED_CATALOG,
            "generated/summary_surface_catalog.min.json",
            REPO_ROOT,
            None,
        )
    return None, None, None, None


def _git_revision(repo_root: Path) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise StatsOwnerReviewError("aoa-stats source revision is unavailable") from exc


def review_stats_capture(
    *,
    capture_root: Path,
    receipt_path: Path,
    artifact_path: Path,
    sdk_review_schema_path: Path,
    source_revision: str,
    reviewed_at: datetime,
    owner_runtime_root: Path | None = None,
    capability_id: str = "measurement-read",
    primitive_id: str = "inspect-measurement",
) -> dict[str, Any]:
    if source_revision != _git_revision(REPO_ROOT):
        raise StatsOwnerReviewError(
            "requested source revision is not current aoa-stats HEAD"
        )
    reviewed_at = _aware_time(reviewed_at, "reviewed_at")
    receipt = _read_private_json(receipt_path, "capture receipt")
    artifact = _read_private_json(artifact_path, "result artifact")
    (
        owner_payload,
        observed_at,
        capture_expires_at,
        receipt_ref,
        artifact_ref,
    ) = _validate_capture(
        receipt,
        artifact,
        capture_root=capture_root,
        receipt_path=receipt_path,
        artifact_path=artifact_path,
    )
    if reviewed_at < observed_at or reviewed_at >= capture_expires_at:
        raise StatsOwnerReviewError("review time is outside the live capture window")

    owner_schema = _read_public_schema(CATALOG_SCHEMA, "stats catalog schema")
    sdk_schema = _read_public_schema(
        sdk_review_schema_path,
        "SDK owner-review schema",
    )
    schema_errors = sorted(
        Draft202012Validator(
            owner_schema,
            format_checker=Draft202012Validator.FORMAT_CHECKER,
        ).iter_errors(owner_payload),
        key=lambda error: list(error.absolute_path),
    )
    reason_codes = ["owner-payload-schema-invalid"] if schema_errors else []
    grounding_state = "rejected" if schema_errors else "grounded"

    (
        owner_catalog_path,
        owner_catalog_ref,
        catalog_owner_root,
        catalog_resolution_reason,
    ) = _catalog_source(
        owner_payload,
        owner_runtime_root=owner_runtime_root,
    )
    if not schema_errors and catalog_resolution_reason is not None:
        grounding_state = "blocked"
        reason_codes.append(catalog_resolution_reason)
    elif not schema_errors and owner_catalog_path is None:
        grounding_state = "rejected"
        reason_codes.append("owner-catalog-source-unrecognized")
    elif not schema_errors:
        try:
            owner_catalog = _read_public_json(
                owner_catalog_path,
                "owner catalog source",
            )
        except StatsOwnerReviewError:
            grounding_state = "blocked"
            reason_codes.append("owner-catalog-source-unavailable")
        else:
            if _digest(owner_catalog) != _digest(owner_payload):
                grounding_state = "rejected"
                reason_codes.append("owner-catalog-content-mismatch")
            elif (
                catalog_owner_root is None
                or _git_revision(catalog_owner_root) != source_revision
            ):
                grounding_state = "blocked"
                reason_codes.append("owner-runtime-source-revision-drift")

    latest_observed_at: datetime | None = None
    generated_from = owner_payload.get("generated_from")
    if isinstance(generated_from, dict):
        raw_latest = generated_from.get("latest_observed_at")
        if isinstance(raw_latest, str):
            try:
                latest_observed_at = _aware_time(
                    raw_latest,
                    "generated_from.latest_observed_at",
                )
            except StatsOwnerReviewError:
                reason_codes.append("owner-catalog-watermark-invalid")
    if grounding_state == "grounded" and latest_observed_at is not None:
        age_seconds = (reviewed_at - latest_observed_at).total_seconds()
        if age_seconds < 0:
            freshness_state = "blocked"
            reason_codes.append("owner-catalog-watermark-in-future")
        elif age_seconds <= MAX_REVIEW_TTL_SECONDS:
            freshness_state = "exact"
        else:
            freshness_state = "blocked"
            reason_codes.append("owner-catalog-watermark-stale")
    else:
        freshness_state = "blocked"
        if latest_observed_at is None:
            reason_codes.append("owner-catalog-watermark-missing")

    provider_watermark = (
        (
            "aoa-stats-catalog:"
            f"{receipt['result_digest']}@{latest_observed_at.isoformat()}"
        )
        if latest_observed_at is not None
        else None
    )
    expires_at = min(
        capture_expires_at,
        reviewed_at + timedelta(seconds=MAX_REVIEW_TTL_SECONDS),
    )
    schema_digest = _file_digest(CATALOG_SCHEMA)
    evidence_refs = ["schemas/summary-surface-catalog.schema.json"]
    if grounding_state == "grounded" and owner_catalog_ref is not None:
        evidence_refs.append(owner_catalog_ref)
    statement = {
        "schema_version": REVIEW_SCHEMA,
        "review_owner": "aoa-stats",
        "organ_id": "aoa-stats",
        "capability_id": capability_id,
        "primitive_id": primitive_id,
        "owners": {
            "source_owner": "aoa-stats",
            "access_owner": "aoa-stats",
            "control_owner": "aoa-sdk",
            "runtime_owner": "abyss-stack",
            "proof_owner": "aoa-evals",
            "acceptance_owner": "aoa-stats",
        },
        "capture": {
            "capture_owner": "abyss-stack",
            "capture_receipt_ref": receipt_ref,
            "capture_receipt_id": receipt["receipt_id"],
            "result_artifact_ref": artifact_ref,
            "result_artifact_id": artifact["artifact_id"],
            "organ_id": "aoa-stats",
            "capability_id": capability_id,
            "primitive_id": primitive_id,
            "result_digest": receipt["result_digest"],
            "result_schema_identity": STATS_RESULT_SCHEMA,
            "server_schema_digest": receipt["server_schema_digest"],
            "primitive_schema_digest": receipt["selected_tool_schema_digest"],
            "observed_at": observed_at.isoformat(),
            "expires_at": capture_expires_at.isoformat(),
        },
        "source_revision": {
            "revision": source_revision,
            "schema_digest": schema_digest,
        },
        "owner_payload_schema_ref": OWNER_PAYLOAD_SCHEMA_REF,
        "owner_payload_schema_digest": schema_digest,
        "reviewed_at": reviewed_at.isoformat(),
        "expires_at": expires_at.isoformat(),
        "grounding_state": grounding_state,
        "freshness_state": freshness_state,
        "freshness_policy": {
            "policy_id": "stats-catalog-owner-watermark-v1",
            "max_age_seconds": MAX_REVIEW_TTL_SECONDS,
            "stale_readable_seconds": 0,
            "cache_scope": "task",
            "provider_watermark_required": True,
        },
        "provider_watermark": provider_watermark,
        "grounding_evidence": (
            [
                {
                    "owner": "aoa-stats",
                    "evidence_ref": evidence_ref,
                    "revision": source_revision,
                    "observed_at": reviewed_at.isoformat(),
                    "expires_at": expires_at.isoformat(),
                }
                for evidence_ref in evidence_refs
            ]
            if grounding_state == "grounded"
            else []
        ),
        "reason_codes": list(dict.fromkeys(reason_codes)),
        "owner_accepted": False,
        "central_proof_asserted": False,
        "admission_asserted": False,
        "cross_organ_proven": False,
        "rollback_proven": False,
        "contains_secrets": False,
        "self_report_is_security_authority": False,
        "claim_limit": REVIEW_CLAIM_LIMIT,
    }
    review = {
        **statement,
        "review_id": _digest(statement, ensure_ascii=True),
    }
    errors = sorted(
        Draft202012Validator(sdk_schema).iter_errors(review),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        raise StatsOwnerReviewError(
            "produced owner review does not satisfy the SDK contract"
        )
    return review


def _write_private_json(path: Path, payload: dict[str, Any]) -> None:
    absolute = path.expanduser().absolute()
    for component in reversed(absolute.parents):
        if component.is_symlink():
            raise StatsOwnerReviewError("review output cannot traverse a symlink")
    absolute.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(absolute.parent, 0o700)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{absolute.name}.",
        dir=absolute.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, absolute)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--sdk-review-schema", type=Path, required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--owner-runtime-root", type=Path)
    parser.add_argument("--reviewed-at")
    parser.add_argument("--capability-id", default="measurement-read")
    parser.add_argument("--primitive-id", default="inspect-measurement")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    reviewed_at = (
        _aware_time(args.reviewed_at, "reviewed_at")
        if args.reviewed_at
        else datetime.now(timezone.utc)
    )
    review = review_stats_capture(
        capture_root=args.capture_root,
        receipt_path=args.receipt,
        artifact_path=args.result,
        sdk_review_schema_path=args.sdk_review_schema,
        source_revision=args.source_revision,
        reviewed_at=reviewed_at,
        owner_runtime_root=args.owner_runtime_root,
        capability_id=args.capability_id,
        primitive_id=args.primitive_id,
    )
    _write_private_json(args.output, review)
    print(
        json.dumps(
            {
                "review_id": review["review_id"],
                "grounding_state": review["grounding_state"],
                "freshness_state": review["freshness_state"],
                "output": str(args.output.expanduser().absolute()),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
