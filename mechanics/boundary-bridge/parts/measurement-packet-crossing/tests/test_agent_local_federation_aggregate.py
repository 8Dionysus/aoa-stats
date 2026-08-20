from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

import sys


PART_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = Path(__file__).resolve().parents[5] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aoa_stats_builder.utility import (  # noqa: E402
    validate_agent_local_federation_aggregate,
)
SCHEMA = (
    PART_ROOT
    / "schemas"
    / "active_organ_agent_local_federation_aggregate_v0.schema.json"
)


def payload() -> dict:
    return {
        "schema_version": "active_organ_agent_local_federation_aggregate_v0",
        "aggregate_id": "agent-local-aggregate:phase12-reference",
        "run_ref": "eval-run:phase12/reference",
        "namespace_count": 4,
        "agent_count": 4,
        "tenant_count": 2,
        "local_case_count": 24,
        "duplicate_case_count": 4,
        "promotion": {
            "nominated": 8,
            "memo_candidates": 3,
            "duplicate_no_write": 2,
            "conflict_quarantine": 1,
            "rejected": 1,
            "deferred": 1,
            "silent_shared_truth_count": 0,
        },
        "isolation": {
            "max_fault_blast_radius_namespaces": 1,
            "cross_agent_contamination_count": 0,
            "cross_tenant_leak_count": 0,
            "private_to_shared_leak_count": 0,
            "degraded_isolation_passed": True,
            "shared_organ_failures_from_local_disable": 0,
        },
        "portability": {
            "model_pins_tested": 3,
            "portable_result_count": 3,
            "nonportable_result_count": 0,
        },
        "consumer_zero": {
            "namespaces_removed": 1,
            "residual_readers": 0,
            "residual_writers": 0,
            "residual_promoters": 0,
            "residual_material": 0,
        },
        "operator": {
            "review_minutes": 9,
            "review_budget_minutes": 12,
            "saved_re_grounding_minutes": 18,
            "net_minutes_saved": 9,
            "promotion_benefit_exceeds_burden": True,
        },
        "source_refs": [
            "aoa-agents:namespace-contract",
            "aoa-memo:promotion-receipts",
            "aoa-evals:phase12-run",
        ],
        "measurement_authority": "aoa-stats",
        "promotion_authority": "forbidden",
        "proof_authority": "forbidden",
    }


def test_agent_local_aggregate_is_descriptive_and_reconciled() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    value = payload()
    assert list(validator.iter_errors(value)) == []
    assert validate_agent_local_federation_aggregate(value) == []


def test_hidden_promotion_and_bad_burden_math_are_detected() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    widened = deepcopy(payload())
    widened["promotion_authority"] = "allowed"
    assert list(validator.iter_errors(widened))

    unreconciled = deepcopy(payload())
    unreconciled["promotion"]["memo_candidates"] += 1
    assert any(
        "promotion result counts must reconcile" in issue
        for issue in validate_agent_local_federation_aggregate(unreconciled)
    )

    burden = deepcopy(payload())
    burden["operator"]["review_minutes"] = 20
    assert any(
        "operator net minutes must reconcile" in issue
        for issue in validate_agent_local_federation_aggregate(burden)
    )

    portability = deepcopy(payload())
    portability["portability"]["portable_result_count"] = 2
    assert any(
        "portability result counts must reconcile" in issue
        for issue in validate_agent_local_federation_aggregate(portability)
    )
