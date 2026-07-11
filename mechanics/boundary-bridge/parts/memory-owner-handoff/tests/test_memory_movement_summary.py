from __future__ import annotations

import importlib.util
import json
import os
import sys
from copy import deepcopy
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator


PART_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[5]
SRC_ROOT = REPO_ROOT / "src"
ROOT_BUILD_MODULE = REPO_ROOT / "scripts" / "build_views.py"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder import memory_movement  # noqa: E402
from aoa_stats_builder.memory_movement_sources import (  # noqa: E402
    MemoryMovementInputBundle,
    load_memory_movement_bundle,
    memory_movement_source_paths,
)


def resolve_owner_root() -> Path:
    candidates = (
        os.environ.get("AOA_MEMO_ROOT"),
        str(REPO_ROOT / ".deps" / "aoa-memo"),
        str(REPO_ROOT.parent / "aoa-memo"),
        "/srv/AbyssOS/aoa-memo",
    )
    for candidate in candidates:
        if candidate and (
            Path(candidate)
            / "generated/memory-objects/memory_object_catalog.min.json"
        ).is_file():
            return Path(candidate).expanduser().resolve()
    raise RuntimeError("could not resolve the aoa-memo owner root")


def stable_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


def load_root_build_module():
    spec = importlib.util.spec_from_file_location("build_views", ROOT_BUILD_MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_from_bundle(bundle: MemoryMovementInputBundle) -> dict[str, Any]:
    return memory_movement.build_memory_movement_summary(
        bundle.source,
        bundle.catalog,
        bundle.memory_objects,
        bundle.reviewed_intakes,
        bundle.landing_receipts,
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def prepare_owner_root(
    tmp_path: Path,
    *,
    catalog_objects: list[dict[str, Any]],
    memory_objects: list[tuple[str, dict[str, Any]]],
    reviewed_intakes: list[tuple[str, dict[str, Any]]] | None = None,
    landing_receipts: list[tuple[str, dict[str, Any]]] | None = None,
) -> Path:
    owner_root = tmp_path / "aoa-memo"
    catalog_path, objects_root, reviewed_root, receipts_root = (
        memory_movement_source_paths(owner_root)
    )
    write_json(
        catalog_path,
        {
            "source_of_truth": "aoa-memo-object-read-models-v2",
            "memory_objects": catalog_objects,
        },
    )
    objects_root.mkdir(parents=True, exist_ok=True)
    reviewed_root.mkdir(parents=True, exist_ok=True)
    receipts_root.mkdir(parents=True, exist_ok=True)
    for relative_path, payload in memory_objects:
        write_json(objects_root / relative_path, payload)
    for filename, payload in reviewed_intakes or []:
        write_json(reviewed_root / filename, payload)
    for filename, payload in landing_receipts or []:
        write_json(receipts_root / filename, payload)
    return owner_root


def test_owner_bundle_preserves_public_output_bytes_schema_and_authority() -> None:
    bundle = load_memory_movement_bundle(resolve_owner_root())
    payload = build_from_bundle(bundle)
    generated_path = REPO_ROOT / "generated/memory_movement_summary.min.json"
    schema_path = REPO_ROOT / "schemas/memory-movement-summary.schema.json"

    assert stable_json(payload) == generated_path.read_text(encoding="utf-8")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)

    assert payload["authority"]["summary_owner"] == "aoa-stats"
    assert payload["authority"]["memory_owner"] == "aoa-memo"
    assert "Derived movement summary only" in payload["authority"][
        "authority_ceiling"
    ]
    assert payload["reviewed_corpus"]["object_count"] == payload[
        "source_kind_counts"
    ]["reviewed_corpus"]
    bridge_row = next(
        item
        for item in payload["reviewed_corpus"]["objects"]
        if item["id"] == "memo.bridge.2026-03-23.tos-lineage-kag-candidate"
    )
    assert bridge_row["object_ref"] == (
        "aoa-memo/memo/objects/bridges/2026/"
        "tos-lineage-kag-candidate/object.json"
    )


def test_root_generated_from_facade_preserves_legacy_mutable_tuple_shape(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    owner_root = resolve_owner_root()
    monkeypatch.setenv("AOA_MEMO_ROOT", str(owner_root))
    module = load_root_build_module()

    source, catalog_objects, memory_objects, reviewed_intakes, landing_receipts = (
        module.memory_movement_generated_from()
    )

    assert isinstance(source, dict)
    assert isinstance(catalog_objects, list)
    assert all(isinstance(path, Path) for path, _ in memory_objects)
    assert all(isinstance(path, Path) for path, _ in reviewed_intakes)
    assert all(isinstance(path, Path) for path, _ in landing_receipts)
    assert all(path.is_relative_to(owner_root) for path, _ in memory_objects)
    assert [path for path, _ in memory_objects] == sorted(
        path for path, _ in memory_objects
    )


def test_adapter_uses_exact_four_roots_and_sorted_discovery() -> None:
    owner_root = resolve_owner_root()
    paths = memory_movement_source_paths(owner_root)
    bundle = load_memory_movement_bundle(owner_root)

    assert tuple(path.relative_to(owner_root).as_posix() for path in paths) == (
        "generated/memory-objects/memory_object_catalog.min.json",
        "memo/objects",
        "memo/intake/reviewed",
        "memo/intake/receipts",
    )
    assert tuple(bundle.source["receipt_input_paths"]) == (
        "aoa-memo/generated/memory-objects/memory_object_catalog.min.json",
        "aoa-memo/memo/objects",
        "aoa-memo/memo/intake/reviewed",
        "aoa-memo/memo/intake/receipts",
    )
    for referenced_payloads in (
        bundle.memory_objects,
        bundle.reviewed_intakes,
        bundle.landing_receipts,
    ):
        refs = tuple(ref for ref, _ in referenced_payloads)
        assert refs == tuple(sorted(refs))


def test_input_bundle_is_deeply_immutable_and_mutable_parts_are_detached() -> None:
    object_id = "memo.decision.2099-01-01.demo"
    source = {
        "receipt_input_paths": list(memory_movement.MEMORY_MOVEMENT_INPUT_REFS),
        "total_receipts": 3,
        "latest_observed_at": "2099-01-02T00:00:00Z",
    }
    catalog = {
        "source_of_truth": "aoa-memo-object-read-models-v2",
        "memory_objects": [
            {"id": object_id, "source_kind": "reviewed_corpus"}
        ],
    }
    memory_objects = [
        (
            "aoa-memo/memo/objects/decisions/2099/demo/object.json",
            {
                "id": object_id,
                "kind": "decision",
                "time": {"observed_at": "2099-01-01T00:00:00Z"},
            },
        )
    ]
    reviewed_intakes = [
        (
            "aoa-memo/memo/intake/reviewed/demo.json",
            {"id": "intake:demo", "created_at": "2099-01-02T00:00:00Z"},
        )
    ]
    landing_receipts = [
        (
            "aoa-memo/memo/intake/receipts/demo.json",
            {"id": "receipt:demo", "landed_at": "2099-01-01T01:00:00Z"},
        )
    ]
    bundle = MemoryMovementInputBundle(
        source,
        catalog,
        memory_objects,
        reviewed_intakes,
        landing_receipts,
    )

    source["receipt_input_paths"].append("later")
    catalog["memory_objects"][0]["id"] = "mutated"
    memory_objects[0][1]["kind"] = "mutated"
    detached = bundle.mutable_parts()
    detached[2][0][1]["kind"] = "detached-mutation"

    assert tuple(bundle.source["receipt_input_paths"]) == (
        *memory_movement.MEMORY_MOVEMENT_INPUT_REFS,
    )
    assert bundle.catalog["memory_objects"][0]["id"] == object_id
    assert bundle.memory_objects[0][1]["kind"] == "decision"
    with pytest.raises(TypeError):
        bundle.source["total_receipts"] = 4  # type: ignore[index]
    with pytest.raises(TypeError):
        bundle.catalog["memory_objects"][0]["id"] = "mutated"  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        bundle.source = {}  # type: ignore[misc]


def test_projection_core_is_filesystem_free_and_does_not_mutate_inputs() -> None:
    core_source = Path(memory_movement.__file__).read_text(encoding="utf-8")
    for forbidden in ("pathlib", "os.environ", "read_text(", "open("):
        assert forbidden not in core_source

    inputs = load_memory_movement_bundle(resolve_owner_root()).mutable_parts()
    original = deepcopy(inputs)
    memory_movement.build_memory_movement_summary(*inputs)
    assert inputs == original


def test_adapter_rejects_catalog_object_mismatch(tmp_path: Path) -> None:
    owner_root = prepare_owner_root(
        tmp_path,
        catalog_objects=[
            {
                "id": "memo.decision.2099-01-01.missing-object",
                "source_kind": "reviewed_corpus",
            }
        ],
        memory_objects=[],
    )

    with pytest.raises(
        memory_movement.ReceiptValidationError, match="object/catalog mismatch"
    ):
        load_memory_movement_bundle(owner_root)


def test_adapter_rejects_inputs_without_observable_timestamp(tmp_path: Path) -> None:
    object_id = "memo.decision.2099-01-01.timeless"
    owner_root = prepare_owner_root(
        tmp_path,
        catalog_objects=[{"id": object_id, "source_kind": "reviewed_corpus"}],
        memory_objects=[
            (
                "decisions/2099/timeless/object.json",
                {"id": object_id, "kind": "decision"},
            )
        ],
    )

    with pytest.raises(
        memory_movement.ReceiptValidationError,
        match="no observable timestamp",
    ):
        load_memory_movement_bundle(owner_root)


def test_core_deduplicates_landed_refs_and_tracks_packet_time(
    tmp_path: Path,
) -> None:
    object_id = "memo.decision.2099-01-01.demo"
    owner_root = prepare_owner_root(
        tmp_path,
        catalog_objects=[{"id": object_id, "source_kind": "reviewed_corpus"}],
        memory_objects=[
            (
                "decisions/2099/demo/object.json",
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
                },
            )
        ],
        reviewed_intakes=[
            (
                "z.reviewed-intake.json",
                {"id": "export:z", "created_at": "2099-01-02T00:00:00Z"},
            ),
            (
                "a.reviewed-intake.json",
                {"id": "export:a", "created_at": "2099-01-02T00:00:00Z"},
            ),
        ],
        landing_receipts=[
            (
                "z.landing-receipt.json",
                {
                    "id": "landing-receipt:z",
                    "object_ref": object_id,
                    "result": "landed",
                    "landed_at": "2099-01-01T01:00:00Z",
                },
            ),
            (
                "a.landing-receipt.json",
                {
                    "id": "landing-receipt:a",
                    "object_ref": object_id,
                    "result": "landed",
                    "landed_at": "2099-01-01T01:00:00Z",
                },
            ),
        ],
    )
    bundle = load_memory_movement_bundle(owner_root)
    payload = build_from_bundle(bundle)

    assert tuple(ref for ref, _ in bundle.reviewed_intakes) == tuple(
        sorted(ref for ref, _ in bundle.reviewed_intakes)
    )
    assert tuple(ref for ref, _ in bundle.landing_receipts) == tuple(
        sorted(ref for ref, _ in bundle.landing_receipts)
    )
    assert payload["generated_from"]["latest_observed_at"] == (
        "2099-01-02T00:00:00Z"
    )
    assert payload["reviewed_intake"]["landed_object_refs"] == [object_id]
    assert payload["reviewed_intake"]["landing_receipt_count"] == 2


def test_memory_movement_docs_name_consumer_route_boundary() -> None:
    doc = (PART_ROOT / "docs/MEMORY_MOVEMENT_SUMMARY.md").read_text(
        encoding="utf-8"
    )
    compact_doc = " ".join(doc.split())

    assert "route-only/read-only memory consumer" in compact_doc
    assert "does not create local memo candidates" in compact_doc
    assert "Session evidence remains `.aoa` evidence" in compact_doc
    assert "`aoa_memo` MCP brief/search/status/validation/landing-plan dry-runs" in (
        compact_doc
    )
    assert "reviewed source patch in `aoa-memo`" in compact_doc
