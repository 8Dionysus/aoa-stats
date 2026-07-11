from __future__ import annotations

import importlib.util
import json
from pathlib import Path


PART_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[5]
MODULE_PATH = REPO_ROOT / "scripts" / "install_live_refresh_units.py"


def load_install_module():
    spec = importlib.util.spec_from_file_location("install_live_refresh_units", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_registry(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "sources": [
                    {
                        "name": "skills",
                        "repo": "aoa-skills",
                        "relative_path": ".aoa/live_receipts/session-harvest-family.jsonl",
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_public_installer_uses_part_local_templates_and_registry() -> None:
    module = load_install_module()

    assert module.CANONICAL_IMPLEMENTATION == (
        PART_ROOT / "scripts" / "install_live_refresh_units.py"
    )
    assert module.DEFAULT_REGISTRY == PART_ROOT / "config" / "live_receipt_sources.json"
    assert module.TEMPLATE_DIR == PART_ROOT / "systemd"


def test_rendered_units_use_installer_paths(tmp_path: Path) -> None:
    module = load_install_module()
    root_with_spaces = tmp_path / "aoa stats"
    registry_path = root_with_spaces / "config" / "live_receipt_sources.json"
    registry_path.parent.mkdir(parents=True)
    write_registry(registry_path)
    federation_root = root_with_spaces / "federation"
    feed_output = root_with_spaces / "state" / "live_receipts.min.json"
    summary_output_dir = root_with_spaces / "state" / "generated"

    units = module.render_units(
        registry_path=registry_path,
        federation_root=federation_root,
        feed_output=feed_output,
        summary_output_dir=summary_output_dir,
    )

    service = units["aoa-stats-live-refresh.service"]
    assert f'WorkingDirectory="{module.REPO_ROOT}"' in service
    assert (
        f'ExecStart=/usr/bin/env python3 "{module.REPO_ROOT}/scripts/refresh_live_stats.py"'
        in service
    )
    assert f'--registry "{registry_path}"' in service
    assert f'--federation-root "{federation_root}"' in service
    assert f'--feed-output "{feed_output}"' in service
    assert f'--summary-output-dir "{summary_output_dir}"' in service

    path_unit = units["aoa-stats-live-refresh.path"]
    assert (
        f'PathModified="{federation_root}/aoa-skills/.aoa/live_receipts/session-harvest-family.jsonl"'
        in path_unit
    )


def test_systemd_arg_quotes_and_escapes_special_path_characters() -> None:
    module = load_install_module()

    rendered = module.systemd_arg(Path('/tmp/aoa stats/%root/$feed/"quoted"'))

    assert rendered == '"/tmp/aoa stats/%%root/$feed/\\"quoted\\""'


def test_systemd_exec_arg_escapes_dollars_for_exec_arguments() -> None:
    module = load_install_module()

    rendered = module.systemd_exec_arg(Path('/tmp/aoa stats/%root/$feed/"quoted"'))

    assert rendered == '"/tmp/aoa stats/%%root/$$feed/\\"quoted\\""'


def test_install_units_refuses_drift_without_overwrite(tmp_path: Path) -> None:
    module = load_install_module()
    registry_path = tmp_path / "config" / "live_receipt_sources.json"
    registry_path.parent.mkdir(parents=True)
    write_registry(registry_path)
    user_unit_dir = tmp_path / "units"
    user_unit_dir.mkdir()
    target = user_unit_dir / "aoa-stats-live-refresh.service"
    target.write_text("stale\n", encoding="utf-8")

    try:
        module.install_units(
            user_unit_dir=user_unit_dir,
            overwrite=False,
            registry_path=registry_path,
            federation_root=tmp_path / "federation",
            feed_output=tmp_path / "state" / "live_receipts.min.json",
            summary_output_dir=tmp_path / "state" / "generated",
        )
    except FileExistsError as exc:
        assert str(target) in str(exc)
    else:
        raise AssertionError("install_units should reject changed existing units without overwrite")
