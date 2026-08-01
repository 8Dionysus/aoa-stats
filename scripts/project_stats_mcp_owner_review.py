#!/usr/bin/env python3
"""Project one exact stats owner review into a stack evidence overlay."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

try:
    from scripts.review_stats_mcp_result import (
        CAPTURE_RECEIPT_SCHEMA,
        REVIEW_SCHEMA,
        STATS_RESULT_SCHEMA,
        StatsOwnerReviewError,
        _assert_content_address,
        _aware_time,
        _digest,
        _git_revision,
        _read_private_json,
        _read_public_schema,
        _trusted_stack_signer,
        _verify_capture_attestation,
        _write_private_json,
    )
except ModuleNotFoundError:  # direct `python scripts/...` entrypoint
    from review_stats_mcp_result import (
        CAPTURE_RECEIPT_SCHEMA,
        REVIEW_SCHEMA,
        STATS_RESULT_SCHEMA,
        StatsOwnerReviewError,
        _assert_content_address,
        _aware_time,
        _digest,
        _git_revision,
        _read_private_json,
        _read_public_schema,
        _trusted_stack_signer,
        _verify_capture_attestation,
        _write_private_json,
    )


REPO_ROOT = Path(__file__).resolve().parents[1]
MAX_FUTURE_SKEW_SECONDS = 30


class StatsOwnerReviewProjectionError(ValueError):
    """The stats owner review cannot support a usable stack overlay."""


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _capture_path(capture_root: Path, relative_ref: Any) -> Path:
    if not isinstance(relative_ref, str) or not relative_ref:
        raise StatsOwnerReviewProjectionError("capture receipt ref is unavailable")
    ref = PurePosixPath(relative_ref)
    if ref.is_absolute() or ".." in ref.parts:
        raise StatsOwnerReviewProjectionError("capture receipt ref is not bounded")
    try:
        root = capture_root.expanduser().resolve(strict=True)
        candidate = (root / Path(*ref.parts)).resolve(strict=True)
        candidate.relative_to(root)
    except (OSError, ValueError) as exc:
        raise StatsOwnerReviewProjectionError(
            "capture receipt ref escapes the capture root"
        ) from exc
    return candidate


def _validate_review(review: dict[str, Any], sdk_schema_path: Path) -> None:
    schema = _read_public_schema(sdk_schema_path, "SDK owner-review schema")
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            review
        ),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        raise StatsOwnerReviewProjectionError(
            "owner review does not satisfy the SDK contract"
        )
    statement = dict(review)
    claimed = statement.pop("review_id", None)
    if claimed != _digest(statement, ensure_ascii=True):
        raise StatsOwnerReviewProjectionError("owner review content address is invalid")
    required = {
        "schema_version": REVIEW_SCHEMA,
        "review_owner": "aoa-stats",
        "organ_id": "aoa-stats",
        "capability_id": "measurement-read",
        "primitive_id": "inspect-measurement",
        "grounding_state": "grounded",
        "freshness_state": "exact",
        "owner_accepted": False,
        "central_proof_asserted": False,
        "admission_asserted": False,
        "cross_organ_proven": False,
        "rollback_proven": False,
        "contains_secrets": False,
        "self_report_is_security_authority": False,
    }
    if any(review.get(field) != value for field, value in required.items()):
        raise StatsOwnerReviewProjectionError(
            "owner review exceeds or does not meet the projection claim boundary"
        )
    if review.get("owners") != {
        "source_owner": "aoa-stats",
        "access_owner": "aoa-stats",
        "control_owner": "aoa-sdk",
        "runtime_owner": "abyss-stack",
        "proof_owner": "aoa-evals",
        "acceptance_owner": "aoa-stats",
    }:
        raise StatsOwnerReviewProjectionError("owner review roles do not match stats")
    if review.get("reason_codes") not in ([], ()):
        raise StatsOwnerReviewProjectionError("exact owner review carries reasons")
    watermark = review.get("provider_watermark")
    if not isinstance(watermark, str) or not watermark.startswith(
        "aoa-stats-catalog:"
    ):
        raise StatsOwnerReviewProjectionError("owner freshness watermark is invalid")


def project_owner_review(
    *,
    review_path: Path,
    capture_root: Path,
    sdk_schema_path: Path,
    clock: Callable[[], datetime] = _utc_now,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    review = _read_private_json(review_path, "owner review")
    source = review.get("source_revision")
    source_revision = source.get("revision") if isinstance(source, dict) else None
    if not isinstance(source_revision, str) or source_revision != _git_revision(
        repo_root
    ):
        raise StatsOwnerReviewProjectionError(
            "owner review is not bound to the current stats source revision"
        )
    _validate_review(review, sdk_schema_path)
    now = clock().astimezone(timezone.utc)
    reviewed_at = _aware_time(review["reviewed_at"], "reviewed_at")
    expires_at = _aware_time(review["expires_at"], "review expires_at")
    if reviewed_at > now and (reviewed_at - now).total_seconds() > (
        MAX_FUTURE_SKEW_SECONDS
    ):
        raise StatsOwnerReviewProjectionError("owner review is causally future-dated")
    if expires_at <= now:
        raise StatsOwnerReviewProjectionError("owner review is expired")

    capture = review.get("capture")
    if not isinstance(capture, dict):
        raise StatsOwnerReviewProjectionError("owner review capture binding is absent")
    receipt_path = _capture_path(capture_root, capture.get("capture_receipt_ref"))
    receipt = _read_private_json(receipt_path, "capture receipt")
    _assert_content_address(receipt, "receipt_id", "capture receipt")
    signer_id, public_key = _trusted_stack_signer(source_revision)
    _verify_capture_attestation(
        receipt,
        identity="receipt_id",
        label="capture receipt",
        trusted_signer_id=signer_id,
        public_key=public_key,
    )
    expected_receipt = {
        "schema_version": CAPTURE_RECEIPT_SCHEMA,
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
    if any(receipt.get(field) != value for field, value in expected_receipt.items()):
        raise StatsOwnerReviewProjectionError(
            "capture receipt does not support a grounded stats canary"
        )
    for review_field, receipt_field in {
        "capture_receipt_id": "receipt_id",
        "result_digest": "result_digest",
        "result_schema_identity": "result_schema_identity",
        "server_schema_digest": "server_schema_digest",
    }.items():
        if capture.get(review_field) != receipt.get(receipt_field):
            raise StatsOwnerReviewProjectionError(
                "owner review and capture receipt identities differ"
            )
    receipt_observed_at = _aware_time(receipt["observed_at"], "receipt observed_at")
    receipt_expires_at = _aware_time(receipt["expires_at"], "receipt expires_at")
    if (
        _aware_time(capture["observed_at"], "review capture observed_at")
        != receipt_observed_at
        or _aware_time(capture["expires_at"], "review capture expires_at")
        != receipt_expires_at
    ):
        raise StatsOwnerReviewProjectionError(
            "owner review and capture receipt timestamps differ"
        )
    effective_expiry = min(expires_at, receipt_expires_at)
    if effective_expiry <= now:
        raise StatsOwnerReviewProjectionError("owner-reviewed canary is expired")

    receipt_ref = receipt_path.as_posix()
    review_ref = review_path.expanduser().absolute().as_posix()
    canary_evidence = {
        "state": "exact",
        "observed_at": reviewed_at.isoformat(),
        "expires_at": effective_expiry.isoformat(),
        "evidence_refs": [
            {
                "owner": "abyss-stack",
                "evidence_ref": receipt_ref,
                "revision": receipt["receipt_id"],
                "observed_at": receipt_observed_at.isoformat(),
                "expires_at": receipt_expires_at.isoformat(),
            },
            {
                "owner": "aoa-stats",
                "evidence_ref": review_ref,
                "revision": review["review_id"],
                "observed_at": reviewed_at.isoformat(),
                "expires_at": expires_at.isoformat(),
            },
        ],
        "reason_codes": [],
    }
    return {
        "schema_version": "abyss_stack_runtime_evidence_overlay_v1",
        "generated_at": reviewed_at.isoformat(),
        "expires_at": effective_expiry.isoformat(),
        "contains_secrets": False,
        "subjects": [
            {
                "organ_id": "aoa-stats",
                "policy_family": "read",
                "endpoint": {
                    "transport": "streamable-http",
                    "endpoint_ref": receipt["endpoint_ref"],
                    "protocol_versions": [receipt["protocol_version"]],
                    "ready": True,
                    "server_schema_digest": receipt["server_schema_digest"],
                    "evidence": {
                        "state": "exact",
                        "observed_at": receipt_observed_at.isoformat(),
                        "expires_at": receipt_expires_at.isoformat(),
                        "evidence_refs": [canary_evidence["evidence_refs"][0]],
                        "reason_codes": [],
                    },
                },
                "freshness": {
                    "state": "exact",
                    "observed_at": reviewed_at.isoformat(),
                    "expires_at": expires_at.isoformat(),
                    "evidence_refs": [canary_evidence["evidence_refs"][1]],
                    "reason_codes": [],
                    "provider_watermark": review["provider_watermark"],
                },
                "canary": {
                    "succeeded": True,
                    "result_grounded": True,
                    "canary_route": receipt["canary_route"],
                    "canary_ref": receipt_ref,
                    "evidence": canary_evidence,
                },
            }
        ],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--sdk-review-schema", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        overlay = project_owner_review(
            review_path=args.review,
            capture_root=args.capture_root,
            sdk_schema_path=args.sdk_review_schema,
        )
        _write_private_json(args.output, overlay)
    except (StatsOwnerReviewError, StatsOwnerReviewProjectionError) as exc:
        print(f"aoa-stats MCP owner-review projection: {exc}", file=sys.stderr)
        return 1
    subject = overlay["subjects"][0]
    print(f"overlay_path={args.output.expanduser().absolute()}")
    print(f"canary_ref={subject['canary']['canary_ref']}")
    print(f"expires_at={overlay['expires_at']}")
    print("result_grounded=true")
    print("freshness_state=exact")
    print("owner_accepted=false")
    print("central_proof_asserted=false")
    print("contains_secrets=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
