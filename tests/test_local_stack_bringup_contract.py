from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / ".agents" / "skills" / "aoa-local-stack-bringup" / "scripts" / "bringup_contract.py"


def load_bringup_contract_module():
    spec = importlib.util.spec_from_file_location("bringup_contract", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_rendered_services_must_be_array() -> None:
    module = load_bringup_contract_module()

    report = module.build_report(
        {
            "runtime_name": "compose",
            "selector": "dev",
            "rendered_services": "api",
            "readiness_items": [],
            "launch_command": "docker compose up -d",
        }
    )

    assert report["rendered_services"] == []
    assert "rendered_services must be an array." in report["errors"]
    assert "rendered_services is empty." in report["errors"]
    assert report["verdict"] == "hold"
