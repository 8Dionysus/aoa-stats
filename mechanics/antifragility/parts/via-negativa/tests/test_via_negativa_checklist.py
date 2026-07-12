from __future__ import annotations

import json
from pathlib import Path


PART_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[5]
OPERATION_REF = Path(
    "stats/operation-contracts/active/antifragility.via-negativa.operation.json"
)


def test_via_negativa_checklist_is_reciprocally_routed_and_unbound() -> None:
    part_readme = (PART_ROOT / "README.md").read_text(encoding="utf-8")
    operation = json.loads((REPO_ROOT / OPERATION_REF).read_text(encoding="utf-8"))

    assert "docs/VIA_NEGATIVA_CHECKLIST.md" in part_readme
    assert OPERATION_REF.as_posix() in part_readme
    assert operation["mechanic_route"] == (
        "mechanics/antifragility/parts/via-negativa"
    )
    assert operation["input_posture"] == "documentation_checklist"
    assert operation["result_posture"] == "part_local_review_guidance"
    assert operation["owner_truth_inputs"] == [
        {
            "owner_repo": "Agents-of-Abyss",
            "truth_scope": (
                "Common antifragility exclusion, removal, and weak-signal "
                "restraint meaning"
            ),
            "binding": "symbolic_unbound",
        }
    ]
    assert "does not prove that a review occurred" in operation["observation_rule"]


def test_via_negativa_checklist_preserves_common_center_stop_lines() -> None:
    checklist = (PART_ROOT / "docs" / "VIA_NEGATIVA_CHECKLIST.md").read_text(
        encoding="utf-8"
    )

    assert (
        "keep, merge, move, suppress, quarantine, deprecate,\n"
        "delete"
    ) in checklist
    assert "name the owner and the provenance that\nsurvives" in checklist
    assert "source evidence that must be retained" in checklist
    assert "before its owner repository reviews" in checklist
    assert "Route proof failure first to `aoa-evals`" in checklist
    assert "never as\n  authority to mutate a surface" in checklist
    assert "Checklist presence does not prove that a review occurred" in checklist


def test_via_negativa_proof_does_not_invent_an_execution_surface() -> None:
    assert not any(
        (PART_ROOT / route).exists()
        for route in ("config", "examples", "generated", "scripts", "src")
    )
