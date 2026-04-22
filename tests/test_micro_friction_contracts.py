from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


def _load(relative_path: str) -> object:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def test_micro_friction_contracts_validate() -> None:
    cases = [
        ("schemas/micro_friction_receipt.schema.json", "examples/micro_friction_receipt.example.json"),
        (
            "schemas/micro_friction_recurrence.schema.json",
            "examples/micro_friction_recurrence.example.json",
        ),
        ("schemas/micro_friction_inbox.schema.json", "examples/micro_friction_inbox.example.json"),
    ]

    for schema_path, example_path in cases:
        schema = _load(schema_path)
        example = _load(example_path)
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(example)


def test_micro_friction_docs_route_mentions_contracts() -> None:
    docs = (ROOT / "docs" / "MICRO_FRICTION_RECEIPTS.md").read_text(encoding="utf-8")
    assert "micro_friction_receipt.schema.json" in docs
    assert "micro_friction_recurrence.schema.json" in docs
    assert "micro_friction_inbox.schema.json" in docs
