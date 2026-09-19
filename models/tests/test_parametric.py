"""The head and hip build from dimensions, not cached custom CAD."""
from dataclasses import replace
from hashlib import sha256
from pathlib import Path

import cadquery as cq
import numpy as np
import pytest

from src.assets import MOTOR_NAMES, MotorLibrary
from src.config import HeadConfig, HipConfig, RobotConfig
from src.export import mesh_of
from src.geometry import bounds
from src.head import head_lid, head_shell
from src.hip import hip_nose, servo_pinion, servo_rotation
from src.robot import head_transform


@pytest.fixture(scope="module")
def default_head():
    config = RobotConfig()
    return head_shell(config), head_lid(config)


def assert_solid(shape):
    assert shape.isValid() and len(shape.Solids()) == 1 and shape.Volume() > 0


def test_default_head_matches_archived_dimensions_and_volume(default_head):
    shell, lid = default_head
    for shape in default_head:
        assert_solid(shape)
    assert shell.Volume() == pytest.approx(51382.28987496787, abs=1e-5)
    assert lid.Volume() == pytest.approx(13772.21303982558, abs=1e-5)
    assert np.asarray(bounds(shell)) == pytest.approx(np.array([[-36, -40.5, -3], [36, 40.5, 60]]), abs=1e-6)
    assert np.asarray(bounds(lid)) == pytest.approx(np.array([[-36, -36, 0], [36, 36, 18.9]]), abs=1e-6)
    assert abs(shell.intersect(lid).Volume()) < 1e-6


def test_default_hip_mount_matches_archived_volume():
    nose = hip_nose(RobotConfig())
    assert_solid(nose)
    assert nose.Volume() == pytest.approx(2913.810391700595, abs=1e-5)


@pytest.mark.parametrize("head", [
    HeadConfig(width=84, depth=80, height=70),
    HeadConfig(width=78, depth=76, corner_radius=10, wall=3),
    HeadConfig(pivot_height=14, lid_thickness=3),
])
def test_head_dimensions_drive_shell_lid_and_installations(head):
    config = replace(RobotConfig(), head=head)
    shell, lid = head_shell(config), head_lid(config)
    for shape in (shell, lid):
        assert_solid(shape)
    lid_bounds = np.asarray(bounds(lid))
    assert lid_bounds[1, :2] - lid_bounds[0, :2] == pytest.approx([head.width, head.depth])
    assert bounds(shell)[1][2] == pytest.approx(head.height)
    assert abs(shell.intersect(lid).Volume()) < 1e-6
    for left in (False, True):
        installed_pivot = head_transform(config, left) @ np.array([0, 100, 0, 1])
        assert abs(installed_pivot[1]) == pytest.approx(head.depth / 2 + 4.7)
        assert installed_pivot[2] == pytest.approx(head.pivot_height)


def test_thicker_wall_changes_the_cavity_not_the_outside(default_head):
    config = replace(RobotConfig(), head=HeadConfig(wall=3))
    thick = head_shell(config)
    old = default_head[0]
    assert_solid(thick)
    assert thick.Volume() > old.Volume()
    assert np.asarray(bounds(thick)) == pytest.approx(np.asarray(bounds(old)))
    assert old.cut(thick).Volume() < 1e-5


def test_mount_radius_changes_plate_without_moving_motor_holes():
    default = RobotConfig()
    changed = replace(default, hip=HipConfig(mount_radius=14.5))
    old, new = hip_nose(default), hip_nose(changed)
    assert_solid(new)
    assert new.Volume() > old.Volume()
    assert bounds(new)[1][1] == pytest.approx(114.5)
    assert changed.hip.motor_holes(100) == default.hip.motor_holes(100)
    for centre in default.hip.motor_holes(100):
        assert not new.Solids()[0].isInside(cq.Vector(*centre, 3), 1e-7)


@pytest.mark.parametrize("kwargs", [
    {"wall": 0}, {"corner_radius": 40}, {"width": 39},
    {"depth": 49}, {"height": 20}, {"pivot_height": 8}, {"lid_gap": -1},
])
def test_invalid_head_dimensions_fail_before_modelling(kwargs):
    with pytest.raises(ValueError):
        HeadConfig(**kwargs)


@pytest.mark.parametrize("kwargs", [
    {"mount_radius": 12}, {"mounting_hole_diameter": 2.8},
    {"sleeve_seat_diameter": 4.8}, {"outer_boss_radius": 2},
])
def test_invalid_hip_dimensions_fail_before_modelling(kwargs):
    with pytest.raises(ValueError):
        HipConfig(**kwargs)


@pytest.mark.parametrize("name", MOTOR_NAMES)
def test_vendored_motor_reopens_in_mounting_coordinates(name):
    library = MotorLibrary()
    record = library.manifest["parts"][name]
    raw = (library.directory / record["file"]).read_bytes()
    assert sha256(raw).hexdigest() == record["sha256"]
    shape = library.load(name)
    assert_solid(shape)
    assert shape.Volume() == pytest.approx(record["volume_mm3"], abs=1e-6)
    assert np.asarray(bounds(shape)) == pytest.approx(np.asarray(record["bounds_mm"]), abs=1e-6)
    mesh = mesh_of(shape)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0


def test_custom_geometry_never_imports_motor_or_reference_cad(monkeypatch):
    def reject(*args, **kwargs):
        raise AssertionError("Custom head/hip construction tried to load opaque CAD")
    monkeypatch.setattr(cq.Shape, "importBrep", reject)
    monkeypatch.setattr(cq.importers, "importStep", reject)
    for build in (head_shell, head_lid, hip_nose):
        assert_solid(build(RobotConfig()))


def test_pinion_is_constructed_not_loaded_as_an_asset():
    library = MotorLibrary()
    assert set(library.manifest["parts"]) == set(MOTOR_NAMES)
    config = RobotConfig()
    spline = library.load("sg90_output_spline").translate((0, config.servo_output_y, config.hip.servo_shoulder))
    assert_solid(servo_pinion(servo_rotation(spline, config), config))
