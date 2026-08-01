from __future__ import annotations

import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from scripts.project_stats_mcp_owner_review import (
    REPO_ROOT,
    StatsOwnerReviewProjectionError,
    project_owner_review,
)
from scripts.review_stats_mcp_result import (
    REVIEW_CLAIM_LIMIT,
    STATS_RESULT_SCHEMA,
    _digest,
    _write_private_json,
)


NOW = datetime(2026, 8, 1, 6, 0, tzinfo=timezone.utc)
DIGEST_A = "sha256:" + ("a" * 64)
DIGEST_B = "sha256:" + ("b" * 64)


def _sdk_schema(path: Path) -> Path:
    path.write_text(
        json.dumps(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
            }
        ),
        encoding="utf-8",
    )
    return path


def _inputs(root: Path) -> tuple[Path, Path, Path]:
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    observed_at = NOW - timedelta(seconds=30)
    capture_expires = NOW + timedelta(minutes=10)
    receipt_body = {
        "schema_version": "abyss_stack_mcp_canary_receipt_v2",
        "issuer": "abyss-stack",
        "consumer_id": "abyss-stack-mcp-canary",
        "organ_id": "aoa-stats",
        "policy_family": "read",
        "service_id": "aoa-stats-mcp",
        "endpoint_ref": "http://127.0.0.1:5430/mcp",
        "canary_route": "runbook://mcp-canary/aoa-stats/read",
        "tool_name": "stats_catalog",
        "tool_arguments_digest": DIGEST_A,
        "observed_at": observed_at.isoformat(),
        "expires_at": capture_expires.isoformat(),
        "protocol_version": "2025-11-25",
        "server_schema_digest": DIGEST_A,
        "selected_tool_schema_digest": DIGEST_B,
        "call_succeeded": True,
        "result_contract_matched": True,
        "result_schema_identity": STATS_RESULT_SCHEMA,
        "result_digest": DIGEST_B,
        "reason_codes": [],
        "contains_secrets": False,
        "content_trust": "untrusted_data",
        "instruction_authority": "none",
        "signer_id": DIGEST_A,
        "attestation_algorithm": "ed25519",
    }
    receipt = {
        "receipt_id": _digest(receipt_body),
        **receipt_body,
        "attestation": "test-attestation",
    }
    receipt_ref = (
        "records/aoa-stats/"
        + receipt["receipt_id"].removeprefix("sha256:")
        + ".json"
    )
    receipt_path = root / receipt_ref
    _write_private_json(receipt_path, receipt)
    reviewed_at = NOW - timedelta(seconds=5)
    expires_at = NOW + timedelta(minutes=5)
    statement = {
        "schema_version": "aoa_organ_owner_result_review_v1",
        "review_owner": "aoa-stats",
        "organ_id": "aoa-stats",
        "capability_id": "measurement-read",
        "primitive_id": "inspect-measurement",
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
            "result_artifact_ref": "results/aoa-stats/result.json",
            "result_artifact_id": DIGEST_A,
            "organ_id": "aoa-stats",
            "capability_id": "measurement-read",
            "primitive_id": "inspect-measurement",
            "result_digest": DIGEST_B,
            "result_schema_identity": STATS_RESULT_SCHEMA,
            "server_schema_digest": DIGEST_A,
            "primitive_schema_digest": DIGEST_B,
            "observed_at": observed_at.isoformat(),
            "expires_at": capture_expires.isoformat(),
        },
        "source_revision": {"revision": revision, "schema_digest": DIGEST_A},
        "owner_payload_schema_ref": "owner://aoa-stats/schema/payload",
        "owner_payload_schema_digest": DIGEST_A,
        "reviewed_at": reviewed_at.isoformat(),
        "expires_at": expires_at.isoformat(),
        "grounding_state": "grounded",
        "freshness_state": "exact",
        "freshness_policy": {
            "policy_id": "stats-catalog-owner-watermark-v1",
            "max_age_seconds": 300,
            "stale_readable_seconds": 0,
            "cache_scope": "task",
            "provider_watermark_required": True,
        },
        "provider_watermark": f"aoa-stats-catalog:{DIGEST_B}@{observed_at.isoformat()}",
        "grounding_evidence": [],
        "reason_codes": [],
        "owner_accepted": False,
        "central_proof_asserted": False,
        "admission_asserted": False,
        "cross_organ_proven": False,
        "rollback_proven": False,
        "contains_secrets": False,
        "self_report_is_security_authority": False,
        "claim_limit": REVIEW_CLAIM_LIMIT,
    }
    review = {**statement, "review_id": _digest(statement, ensure_ascii=True)}
    review_path = root / "review.json"
    _write_private_json(review_path, review)
    return review_path, receipt_path, _sdk_schema(root / "sdk.schema.json")


def test_exact_owner_review_projects_only_grounded_read_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    review, _, schema = _inputs(tmp_path)
    monkeypatch.setattr(
        "scripts.project_stats_mcp_owner_review._trusted_stack_signer",
        lambda _revision: (DIGEST_A, b"x" * 32),
    )
    monkeypatch.setattr(
        "scripts.project_stats_mcp_owner_review._verify_capture_attestation",
        lambda *_args, **_kwargs: None,
    )

    overlay = project_owner_review(
        review_path=review,
        capture_root=tmp_path,
        sdk_schema_path=schema,
        clock=lambda: NOW,
    )

    subject = overlay["subjects"][0]
    assert subject["organ_id"] == "aoa-stats"
    assert subject["endpoint"]["ready"] is True
    assert subject["freshness"]["state"] == "exact"
    assert subject["canary"]["result_grounded"] is True
    assert "proof" not in subject
    assert "acceptance" not in subject
    assert "rollback" not in subject


def test_projection_rejects_owner_acceptance_promotion(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    review, _, schema = _inputs(tmp_path)
    payload = json.loads(review.read_text(encoding="utf-8"))
    payload["owner_accepted"] = True
    statement = dict(payload)
    statement.pop("review_id")
    payload["review_id"] = _digest(statement, ensure_ascii=True)
    _write_private_json(review, payload)
    monkeypatch.setattr(
        "scripts.project_stats_mcp_owner_review._trusted_stack_signer",
        lambda _revision: (DIGEST_A, b"x" * 32),
    )
    monkeypatch.setattr(
        "scripts.project_stats_mcp_owner_review._verify_capture_attestation",
        lambda *_args, **_kwargs: None,
    )

    with pytest.raises(
        StatsOwnerReviewProjectionError,
        match="claim boundary",
    ):
        project_owner_review(
            review_path=review,
            capture_root=tmp_path,
            sdk_schema_path=schema,
            clock=lambda: NOW,
        )
