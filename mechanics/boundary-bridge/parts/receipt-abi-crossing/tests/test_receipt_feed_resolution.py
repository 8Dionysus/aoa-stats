from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parents[5]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder import receipt_abi  # noqa: E402


def load_build_views_module():
    script_path = REPO_ROOT / "scripts" / "build_views.py"
    spec = importlib.util.spec_from_file_location(
        "build_views_receipt_abi",
        script_path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def make_receipt(
    event_id: str,
    observed_at: str,
    *,
    event_kind: str = "automation_candidate_receipt",
    supersedes: str | None = None,
    actor_ref: str = "aoa-skills:automation-opportunity-scan",
    object_repo: str = "aoa-skills",
    object_kind: str = "skill",
    object_id: str = "aoa-automation-opportunity-scan",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "event_kind": event_kind,
        "event_id": event_id,
        "observed_at": observed_at,
        "run_ref": f"run:{event_id}",
        "session_ref": "session:receipt-abi-crossing",
        "actor_ref": actor_ref,
        "object_ref": {
            "repo": object_repo,
            "kind": object_kind,
            "id": object_id,
            "version": "main",
        },
        "evidence_refs": [
            {"kind": "receipt", "ref": f"repo:{object_repo}/receipts/{event_id}"}
        ],
        "payload": payload or {},
    }
    if supersedes is not None:
        receipt["supersedes"] = supersedes
    return receipt


def test_root_build_facade_reexports_receipt_abi_core() -> None:
    facade = load_build_views_module()

    for name in (
        "ReceiptValidationError",
        "generated_from",
        "load_receipts",
        "resolve_active_receipts",
        "validate_receipt",
    ):
        assert getattr(facade, name) is getattr(receipt_abi, name)


@pytest.mark.parametrize(
    ("event_kind", "actor_ref", "object_kind", "object_id"),
    (
        (
            "memo_writeback_receipt",
            "aoa-memo:writeback",
            "memory_object",
            "memo.test.known-kind",
        ),
        (
            "memo_growth_writeback_receipt",
            "aoa-memo:growth-refinery-writeback",
            "support_memory",
            "memo:test-growth-known-kind",
        ),
    ),
)
def test_validate_receipt_accepts_admitted_unsummarized_event_kinds(
    event_kind: str,
    actor_ref: str,
    object_kind: str,
    object_id: str,
) -> None:
    receipt = make_receipt(
        f"evt-{event_kind}-0001",
        "2026-04-06T09:00:00Z",
        event_kind=event_kind,
        actor_ref=actor_ref,
        object_repo="aoa-memo",
        object_kind=object_kind,
        object_id=object_id,
        payload={"target_kind": "decision"},
    )

    receipt_abi.validate_receipt(receipt, location="memory")


def test_validate_receipt_rejects_unknown_kind_with_canonical_return_ref() -> None:
    receipt = make_receipt(
        "evt-memo-typo-0001",
        "2026-04-06T09:00:00Z",
        event_kind="memo_writeback_receipt_typo",
        actor_ref="aoa-memo:writeback",
        object_repo="aoa-memo",
        object_kind="memory_object",
        object_id="memo.test.unknown-kind",
        payload={"target_kind": "decision"},
    )

    with pytest.raises(
        receipt_abi.ReceiptValidationError,
        match="schemas/stats-event-envelope.schema.json",
    ):
        receipt_abi.validate_receipt(receipt, location="memory")


def test_jsonl_loading_keeps_latest_duplicate_event(tmp_path: Path) -> None:
    path = tmp_path / "live_receipts.jsonl"
    receipts = [
        make_receipt("evt-auto-test-0001", observed_at)
        for observed_at in (
            "2026-04-05T10:20:00Z",
            "2026-04-05T10:19:00Z",
            "2026-04-05T10:21:00Z",
            "2026-04-05T10:18:00Z",
        )
    ]
    path.write_text(
        "\n".join(json.dumps(receipt) for receipt in receipts) + "\n",
        encoding="utf-8",
    )

    loaded = receipt_abi.load_receipts([path])

    assert len(loaded) == 1
    assert loaded[0]["observed_at"] == "2026-04-05T10:21:00Z"


def test_supersedes_chain_resolves_to_latest_descendant_without_mutation() -> None:
    receipts = [
        make_receipt("evt-auto-0001", "2026-04-06T10:00:00Z"),
        make_receipt(
            "evt-auto-0002",
            "2026-04-06T10:01:00Z",
            supersedes="evt-auto-0001",
        ),
        make_receipt(
            "evt-auto-0003",
            "2026-04-06T10:02:00Z",
            supersedes="evt-auto-0002",
        ),
    ]
    original = deepcopy(receipts)

    active = receipt_abi.resolve_active_receipts(receipts)

    assert [receipt["event_id"] for receipt in active] == ["evt-auto-0003"]
    assert receipts == original
    assert receipt_abi.resolve_active_receipts(list(reversed(receipts))) == active


def test_sibling_corrections_keep_only_latest_observation() -> None:
    receipts = [
        make_receipt(
            "evt-harvest-0001",
            "2026-04-06T11:00:00Z",
            event_kind="harvest_packet_receipt",
        ),
        make_receipt(
            "evt-harvest-0002",
            "2026-04-06T11:01:00Z",
            event_kind="harvest_packet_receipt",
            supersedes="evt-harvest-0001",
        ),
        make_receipt(
            "evt-harvest-0003",
            "2026-04-06T11:02:00Z",
            event_kind="harvest_packet_receipt",
            supersedes="evt-harvest-0001",
        ),
    ]

    active = receipt_abi.resolve_active_receipts(receipts)

    assert [receipt["event_id"] for receipt in active] == ["evt-harvest-0003"]


def test_missing_supersedes_targets_and_cycles_remain_visible() -> None:
    receipts = [
        make_receipt(
            "evt-diagnose-0001",
            "2026-04-06T12:00:00Z",
            event_kind="diagnosis_packet_receipt",
            supersedes="evt-missing-9999",
        ),
        make_receipt(
            "evt-repair-0001",
            "2026-04-06T12:01:00Z",
            event_kind="repair_cycle_receipt",
            supersedes="evt-repair-0002",
        ),
        make_receipt(
            "evt-repair-0002",
            "2026-04-06T12:02:00Z",
            event_kind="repair_cycle_receipt",
            supersedes="evt-repair-0001",
        ),
    ]

    active = receipt_abi.resolve_active_receipts(receipts)

    assert [receipt["event_id"] for receipt in active] == [
        "evt-diagnose-0001",
        "evt-repair-0001",
        "evt-repair-0002",
    ]
