from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.issue_stats_mcp_source_identity import (
    StatsSourceIdentityError,
    _validate_receipt,
    issue_source_identity,
    write_outputs,
)


NOW = datetime(2026, 8, 1, 6, 0, tzinfo=timezone.utc)


def test_source_identity_binds_committed_catalog_without_authority_promotion(
    tmp_path: Path,
) -> None:
    receipt, overlay = issue_source_identity(
        require_clean=False,
        clock=lambda: NOW,
    )

    assert receipt["owner"] == "aoa-stats"
    assert receipt["canonical_source_ref"] == (
        "generated/summary_surface_catalog.min.json"
    )
    assert receipt["tree_digest"] == receipt["expected_sync_tree_digest"]
    assert receipt["source_ref"].startswith("owner-source://aoa-stats/")
    subject = overlay["subjects"][0]
    assert subject["organ_id"] == "aoa-stats"
    assert set(subject) == {"organ_id", "policy_family", "source"}
    assert "proof" not in subject
    assert "acceptance" not in subject

    receipt_path, overlay_path = write_outputs(receipt, overlay, tmp_path)
    assert os.stat(receipt_path).st_mode & 0o777 == 0o600
    assert os.stat(overlay_path).st_mode & 0o777 == 0o600
    assert json.loads(receipt_path.read_text(encoding="utf-8")) == receipt


def test_source_identity_rejects_dirty_source_and_tampered_digest(
    tmp_path: Path,
) -> None:
    (tmp_path / ".git").mkdir()
    with pytest.raises(StatsSourceIdentityError):
        issue_source_identity(repo_root=tmp_path)

    receipt, _ = issue_source_identity(require_clean=False, clock=lambda: NOW)
    receipt["tree_digest"] = "sha256:" + ("0" * 64)
    with pytest.raises(StatsSourceIdentityError, match="digest mismatch"):
        _validate_receipt(receipt)


def test_public_example_is_schema_and_content_address_valid() -> None:
    example = json.loads(
        (
            Path(__file__).parents[1]
            / "examples"
            / "stats_mcp_source_identity_receipt.example.json"
        ).read_text(encoding="utf-8")
    )

    _validate_receipt(example)
