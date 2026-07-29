from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from scripts.review_stats_mcp_result import (
    REPO_ROOT,
    STATS_RESULT_SCHEMA,
    StatsOwnerReviewError,
    _digest,
    _write_private_json,
    review_stats_capture,
)


NOW = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)


def _sdk_schema() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": [
            "schema_version",
            "review_id",
            "review_owner",
            "capture",
            "grounding_state",
            "freshness_state",
            "owner_accepted",
            "central_proof_asserted",
            "admission_asserted",
        ],
        "properties": {
            "schema_version": {"const": "aoa_organ_owner_result_review_v1"},
            "review_id": {
                "type": "string",
                "pattern": "^sha256:[0-9a-f]{64}$",
            },
            "review_owner": {"const": "aoa-stats"},
            "capture": {"type": "object"},
            "grounding_state": {"enum": ["grounded", "rejected", "blocked"]},
            "freshness_state": {
                "enum": [
                    "exact",
                    "compatible_drift",
                    "stale_readable",
                    "blocked",
                    "unknown",
                ]
            },
            "owner_accepted": {"const": False},
            "central_proof_asserted": {"const": False},
            "admission_asserted": {"const": False},
        },
    }


def _capture(root: Path, payload: dict) -> tuple[Path, Path]:
    result_digest = _digest(payload)
    result_ref = f"results/aoa-stats/{result_digest.removeprefix('sha256:')}.json"
    receipt_body = {
        "schema_version": "abyss_stack_mcp_canary_receipt_v1",
        "issuer": "abyss-stack",
        "consumer_id": "abyss-stack-mcp-canary",
        "organ_id": "aoa-stats",
        "policy_family": "read",
        "service_id": "aoa-stats-mcp",
        "endpoint_ref": "http://127.0.0.1:5430/mcp",
        "canary_route": "runbook://mcp-canary/aoa-stats/read",
        "tool_name": "stats_catalog",
        "tool_arguments_digest": "sha256:" + ("d" * 64),
        "observed_at": NOW.isoformat(),
        "expires_at": (NOW + timedelta(minutes=10)).isoformat(),
        "protocol_version": "2025-11-25",
        "server_name": "aoa-stats-mcp",
        "server_version": "0.1.0",
        "server_schema_digest": "sha256:" + ("a" * 64),
        "selected_tool_schema_digest": "sha256:" + ("b" * 64),
        "inventory_counts": {
            "tools": 5,
            "resources": 0,
            "resource_templates": 0,
            "prompts": 0,
        },
        "call_succeeded": True,
        "result_contract_matched": True,
        "result_schema_identity": STATS_RESULT_SCHEMA,
        "result_digest": result_digest,
        "result_artifact_ref": result_ref,
        "call_latency_ms": 3,
        "total_latency_ms": 10,
        "reason_codes": [],
        "contains_secrets": False,
        "content_trust": "untrusted_data",
        "instruction_authority": "none",
        "claim_limit": "stack capture only",
    }
    receipt = {"receipt_id": _digest(receipt_body), **receipt_body}
    artifact_body = {
        "schema_version": "abyss_stack_mcp_canary_result_artifact_v1",
        "issuer": "abyss-stack",
        "organ_id": "aoa-stats",
        "policy_family": "read",
        "service_id": receipt["service_id"],
        "canary_route": receipt["canary_route"],
        "tool_name": receipt["tool_name"],
        "tool_arguments_digest": receipt["tool_arguments_digest"],
        "observed_at": receipt["observed_at"],
        "result_schema_identity": STATS_RESULT_SCHEMA,
        "result_digest": result_digest,
        "owner_payload": payload,
        "contains_secrets": False,
        "content_trust": "untrusted_data",
        "instruction_authority": "none",
        "claim_limit": "capture is not owner review",
    }
    artifact = {"artifact_id": _digest(artifact_body), **artifact_body}
    receipt_path = (
        root
        / "records"
        / "aoa-stats"
        / f"{receipt['receipt_id'].removeprefix('sha256:')}.json"
    )
    result_path = root / result_ref
    _write_private_json(receipt_path, receipt)
    _write_private_json(result_path, artifact)
    return receipt_path, result_path


def _review(
    tmp_path: Path,
    payload: dict,
    reviewed_at: datetime,
    *,
    owner_runtime_root: Path | None = None,
) -> dict:
    receipt, result = _capture(tmp_path, payload)
    sdk_schema = tmp_path / "sdk-review.schema.json"
    sdk_schema.write_text(json.dumps(_sdk_schema()), encoding="utf-8")
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return review_stats_capture(
        capture_root=tmp_path,
        receipt_path=receipt,
        artifact_path=result,
        sdk_review_schema_path=sdk_schema,
        source_revision=revision,
        reviewed_at=reviewed_at,
        owner_runtime_root=owner_runtime_root,
    )


def test_owner_catalog_is_grounded_but_old_watermark_is_blocked(
    tmp_path: Path,
) -> None:
    payload = json.loads(
        (REPO_ROOT / "generated" / "summary_surface_catalog.min.json").read_text(
            encoding="utf-8"
        )
    )
    review = _review(tmp_path, payload, NOW + timedelta(seconds=1))
    assert review["grounding_state"] == "grounded"
    assert review["freshness_state"] == "blocked"
    assert "owner-catalog-watermark-stale" in review["reason_codes"]
    assert review["provider_watermark"].startswith("aoa-stats-catalog:")
    assert review["owner_accepted"] is False
    assert review["central_proof_asserted"] is False
    assert review["admission_asserted"] is False


def test_current_owner_watermark_can_be_exact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = json.loads(
        (REPO_ROOT / "generated" / "summary_surface_catalog.min.json").read_text(
            encoding="utf-8"
        )
    )
    payload["generated_from"]["latest_observed_at"] = NOW.isoformat()
    owner_catalog = tmp_path / "owner-catalog.json"
    owner_catalog.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(
        "scripts.review_stats_mcp_result.COMMITTED_CATALOG",
        owner_catalog,
    )
    review = _review(tmp_path / "capture", payload, NOW + timedelta(seconds=1))
    assert review["grounding_state"] == "grounded"
    assert review["freshness_state"] == "exact"
    assert review["reason_codes"] == []


def test_explicit_live_owner_root_binds_runtime_catalog_revision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = json.loads(
        (REPO_ROOT / "generated" / "summary_surface_catalog.min.json").read_text(
            encoding="utf-8"
        )
    )
    payload["artifact_identity"]["content_identity"] = (
        "state/generated/summary_surface_catalog.min.json rebuilt from the "
        "active live receipt feed and written by refresh_live_stats"
    )
    runtime_root = tmp_path / "runtime-owner"
    runtime_catalog = (
        runtime_root / "state" / "generated" / "summary_surface_catalog.min.json"
    )
    runtime_catalog.parent.mkdir(parents=True)
    runtime_catalog.write_text(json.dumps(payload), encoding="utf-8")
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    monkeypatch.setattr(
        "scripts.review_stats_mcp_result._git_revision",
        lambda _: revision,
    )

    review = _review(
        tmp_path / "capture",
        payload,
        NOW + timedelta(seconds=1),
        owner_runtime_root=runtime_root,
    )

    assert review["grounding_state"] == "grounded"
    assert "owner-runtime-source-revision-drift" not in review["reason_codes"]


def test_live_catalog_requires_an_explicit_runtime_root(tmp_path: Path) -> None:
    payload = json.loads(
        (REPO_ROOT / "generated" / "summary_surface_catalog.min.json").read_text(
            encoding="utf-8"
        )
    )
    payload["artifact_identity"]["content_identity"] = (
        "state/generated/summary_surface_catalog.min.json rebuilt from the "
        "active live receipt feed and written by refresh_live_stats"
    )

    review = _review(
        tmp_path / "capture",
        payload,
        NOW + timedelta(seconds=1),
    )

    assert review["grounding_state"] == "blocked"
    assert review["freshness_state"] == "blocked"
    assert "owner-runtime-root-required" in review["reason_codes"]
    assert "state/generated/summary_surface_catalog.min.json" not in {
        evidence["evidence_ref"] for evidence in review["grounding_evidence"]
    }


def test_live_catalog_rejects_runtime_source_revision_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = json.loads(
        (REPO_ROOT / "generated" / "summary_surface_catalog.min.json").read_text(
            encoding="utf-8"
        )
    )
    payload["artifact_identity"]["content_identity"] = (
        "state/generated/summary_surface_catalog.min.json rebuilt from the "
        "active live receipt feed and written by refresh_live_stats"
    )
    runtime_root = tmp_path / "runtime-owner"
    runtime_catalog = (
        runtime_root / "state" / "generated" / "summary_surface_catalog.min.json"
    )
    runtime_catalog.parent.mkdir(parents=True)
    runtime_catalog.write_text(json.dumps(payload), encoding="utf-8")
    source_revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    def revision_for(path: Path) -> str:
        return "f" * 40 if path == runtime_root else source_revision

    monkeypatch.setattr(
        "scripts.review_stats_mcp_result._git_revision",
        revision_for,
    )

    review = _review(
        tmp_path / "capture",
        payload,
        NOW + timedelta(seconds=1),
        owner_runtime_root=runtime_root,
    )

    assert review["grounding_state"] == "blocked"
    assert review["freshness_state"] == "blocked"
    assert "owner-runtime-source-revision-drift" in review["reason_codes"]


def test_schema_or_owner_file_drift_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = json.loads(
        (REPO_ROOT / "generated" / "summary_surface_catalog.min.json").read_text(
            encoding="utf-8"
        )
    )
    payload["unknown_owner_claim"] = True
    review = _review(tmp_path / "schema", payload, NOW + timedelta(seconds=1))
    assert review["grounding_state"] == "rejected"
    assert "owner-payload-schema-invalid" in review["reason_codes"]

    payload.pop("unknown_owner_claim")
    other = tmp_path / "other-catalog.json"
    other.write_text(json.dumps({**payload, "surfaces": []}), encoding="utf-8")
    monkeypatch.setattr(
        "scripts.review_stats_mcp_result.COMMITTED_CATALOG",
        other,
    )
    review = _review(tmp_path / "content", payload, NOW + timedelta(seconds=1))
    assert review["grounding_state"] == "rejected"
    assert "owner-catalog-content-mismatch" in review["reason_codes"]


def test_public_or_tampered_capture_fails_closed(tmp_path: Path) -> None:
    payload = json.loads(
        (REPO_ROOT / "generated" / "summary_surface_catalog.min.json").read_text(
            encoding="utf-8"
        )
    )
    receipt, result = _capture(tmp_path, payload)
    os.chmod(result, 0o644)
    sdk_schema = tmp_path / "sdk-review.schema.json"
    sdk_schema.write_text(json.dumps(_sdk_schema()), encoding="utf-8")
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    with pytest.raises(StatsOwnerReviewError, match="group/world"):
        review_stats_capture(
            capture_root=tmp_path,
            receipt_path=receipt,
            artifact_path=result,
            sdk_review_schema_path=sdk_schema,
            source_revision=revision,
            reviewed_at=NOW + timedelta(seconds=1),
        )
    os.chmod(result, 0o600)
    artifact = json.loads(result.read_text(encoding="utf-8"))
    artifact["owner_payload"]["surfaces"] = []
    _write_private_json(result, artifact)
    with pytest.raises(StatsOwnerReviewError, match="content address"):
        review_stats_capture(
            capture_root=tmp_path,
            receipt_path=receipt,
            artifact_path=result,
            sdk_review_schema_path=sdk_schema,
            source_revision=revision,
            reviewed_at=NOW + timedelta(seconds=1),
        )
