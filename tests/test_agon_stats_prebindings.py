from __future__ import annotations
import pathlib
import json
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def run(cmd):
    return subprocess.run([sys.executable, *cmd], cwd=ROOT, text=True, capture_output=True)


def test_wave7_generated_surface_is_current():
    result = run(['scripts/build_agon_stats_prebinding_registry.py', '--check'])
    assert result.returncode == 0, result.stderr


def test_wave7_generated_surface_uses_declared_record_key():
    generated = json.loads((ROOT / 'generated/agon_stats_prebinding_registry.min.json').read_text(encoding='utf-8'))
    assert generated['record_key'] == 'prebindings'
    assert 'prebindings' in generated
    assert 'records' not in generated


def test_wave7_validator_passes():
    result = run(['scripts/validate_agon_stats_prebindings.py'])
    assert result.returncode == 0, result.stderr
