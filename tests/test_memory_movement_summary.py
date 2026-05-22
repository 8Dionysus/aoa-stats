from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "build_views.py"


def load_build_views_module():
    spec = importlib.util.spec_from_file_location("build_views", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_json(relative_path: str) -> object:
    return json.loads((REPO_ROOT / relative_path).read_text(encoding="utf-8"))


def test_memory_movement_summary_schema_and_authority_boundary() -> None:
    schema = load_json("schemas/memory-movement-summary.schema.json")
    payload = load_json("generated/memory_movement_summary.min.json")

    assert isinstance(schema, dict)
    assert isinstance(payload, dict)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)

    assert payload["authority"]["summary_owner"] == "aoa-stats"
    assert payload["authority"]["memory_owner"] == "aoa-memo"
    assert "Derived movement summary only" in payload["authority"]["authority_ceiling"]
    assert payload["reviewed_corpus"]["object_count"] == payload["source_kind_counts"]["reviewed_corpus"]
    assert payload["reviewed_corpus"]["object_count"] >= 7
    assert payload["reviewed_intake"]["landing_result_counts"].get("landed", 0) >= 1
    assert "repo:aoa-stats" in payload["consumer_handoff"]["consumer_refs"]
    assert (
        payload["consumer_handoff"]["handoff_memory_ref"]
        == "memo.decision.2026-05-22.reviewed-memory-consumer-handoff-spine"
    )


def test_memory_movement_builder_rejects_catalog_object_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_views_module()
    memo_root = tmp_path / "aoa-memo"
    catalog_dir = memo_root / "generated" / "memory-objects"
    objects_dir = memo_root / "memo" / "objects"
    reviewed_dir = memo_root / "memo" / "intake" / "reviewed"
    receipts_dir = memo_root / "memo" / "intake" / "receipts"
    for path in (catalog_dir, objects_dir, reviewed_dir, receipts_dir):
        path.mkdir(parents=True, exist_ok=True)
    (catalog_dir / "memory_object_catalog.min.json").write_text(
        json.dumps(
            {
                "source_of_truth": "aoa-memo-object-read-models-v2",
                "memory_objects": [
                    {
                        "id": "memo.decision.2099-01-01.missing-object",
                        "source_kind": "reviewed_corpus",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("AOA_MEMO_ROOT", str(memo_root))
    with pytest.raises(module.ReceiptValidationError, match="object/catalog mismatch"):
        module.build_memory_movement_summary()


def test_memory_movement_summary_deduplicates_landed_refs_and_tracks_packet_time(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_build_views_module()
    memo_root = tmp_path / "aoa-memo"
    catalog_dir = memo_root / "generated" / "memory-objects"
    object_dir = memo_root / "memo" / "objects" / "decisions" / "2099" / "demo"
    reviewed_dir = memo_root / "memo" / "intake" / "reviewed"
    receipts_dir = memo_root / "memo" / "intake" / "receipts"
    for path in (catalog_dir, object_dir, reviewed_dir, receipts_dir):
        path.mkdir(parents=True, exist_ok=True)

    object_id = "memo.decision.2099-01-01.demo"
    (catalog_dir / "memory_object_catalog.min.json").write_text(
        json.dumps(
            {
                "source_of_truth": "aoa-memo-object-read-models-v2",
                "memory_objects": [
                    {
                        "id": object_id,
                        "source_kind": "reviewed_corpus",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (object_dir / "object.json").write_text(
        json.dumps(
            {
                "id": object_id,
                "kind": "decision",
                "time": {"observed_at": "2099-01-01T00:00:00Z"},
                "lifecycle": {
                    "review_state": "confirmed",
                    "current_recall": {"status": "preferred"},
                },
                "trust": {"temperature": "cool"},
                "bridges": {"kag_lift_status": "candidate"},
            }
        ),
        encoding="utf-8",
    )
    (reviewed_dir / "demo.reviewed-intake.json").write_text(
        json.dumps({"id": "export:demo", "created_at": "2099-01-02T00:00:00Z"}),
        encoding="utf-8",
    )
    for index in range(2):
        (receipts_dir / f"demo-{index}.landing-receipt.json").write_text(
            json.dumps(
                {
                    "id": f"landing-receipt:demo:{index}",
                    "object_ref": object_id,
                    "result": "landed",
                    "landed_at": "2099-01-01T01:00:00Z",
                }
            ),
            encoding="utf-8",
        )

    monkeypatch.setenv("AOA_MEMO_ROOT", str(memo_root))
    payload = module.build_memory_movement_summary()

    assert payload["generated_from"]["latest_observed_at"] == "2099-01-02T00:00:00Z"
    assert payload["reviewed_intake"]["landed_object_refs"] == [object_id]
    assert payload["reviewed_intake"]["landing_receipt_count"] == 2
