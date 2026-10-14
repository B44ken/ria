"""Offline checks of preserved source and evidence; never import experiments."""
import ast
import hashlib
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1] / 'experiments' / 'keyboard_20261007'


def read(name):
    return json.loads((ROOT / 'results' / name).read_text())


def test_preserved_manifest_and_source_syntax():
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    assert manifest['policy_training_steps'] == 1110016
    assert not manifest['policy_bytes_included']
    assert not manifest['implementation_changed_during_packaging']
    for entry in manifest['files']:
        path = ROOT / entry['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256']
        if path.suffix == '.py':
            ast.parse(path.read_text(), filename=str(path))
    unrun = [x for x in manifest['files'] if x['path'].startswith('unrun/')]
    assert len(unrun) == 1
    assert unrun[0]['status'] == 'unrun proposal'


def test_fixed_grid_best_height_schedule():
    all_cases = read('ria-height-gain-results.json')
    cases = [c for c in all_cases if (c['kp_exponent'], c['kd_exponent']) == (1, 2)]
    assert len(all_cases) == 48
    assert len(cases) == 12
    assert all(c['valid'] and c['fall_seconds'] == 0 for c in cases)
    assert all(c['press_airborne'] == 0 and c['hold_fall'] == 0 for c in cases)
    assert sum(c['peak'] for c in cases) / len(cases) == pytest.approx(0.0229028, abs=1e-7)


def test_randomized_results_match_summary_and_full_case_fall_veto():
    cases = read('ria-compiler-pose-results.json')
    summary = read('ria-compiler-pose-summary.json')
    valid = [c for c in cases if c['valid_jump']]
    assert len(cases) == summary['random_cases'] == 24
    assert len(valid) == summary['strict_valid'] == 23
    assert all(c['fall_seconds'] == 0 and c['first_fall'] is None for c in valid)
    assert sum(c['fall_seconds'] > 0 for c in cases) == summary['falls'] == 1
    assert sum(c['fall_seconds'] for c in cases) == pytest.approx(summary['fall_seconds'])
    assert sum(c['peak_before_fall'] for c in valid) / len(valid) == pytest.approx(summary['mean_qualified_peak'])
    assert not summary['promotion']


def test_recovery_results_are_separate_original_policy_evidence():
    cases = read('ria-compiler-pose-recovery.json')
    assert len(cases) == 4
    assert sum(c['recovery_time'] is not None for c in cases) == 2
    assert "original=Policy('ria/resume-jump-20261005-2015'" in (ROOT / 'validate_compiler_pose_keyboard.py').read_text()


def test_legacy_moving_labels_are_not_strict_success():
    summary = read('ria-residual-moving4-summary.json')
    assert summary['legacy_valid'] == 9
    assert summary['strict_valid'] == 8
    assert summary['fall_cases'] == 4
    assert not summary['promotion']


def test_feedback_driving_result_is_limited_and_unpromoted():
    summary = read('ria-feedback-valid4-summary.json')
    cases = read('ria-feedback-valid4-results.json')
    assert len(cases) == summary['all']['cases'] == 19
    assert summary['all']['seconds'] == 140
    assert summary['standard']['cases'] == 14
    assert summary['all']['fallEntries'] == 0
    assert summary['standard']['speedMae'] == pytest.approx(0.037073847999568456)
    assert summary['limitations']
