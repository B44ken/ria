"""Fast design tests; the entry point additionally audits exported CAD/meshes."""
import importlib.util
import json
from math import pi
from pathlib import Path

import cadquery as cq
import numpy as np
import pytest
from shapely.affinity import rotate
from shapely.geometry import Polygon

from src.assets import MotorLibrary
from src.belt import belt_path, pulley_outline
from src.config import BeltDrive, GearTrain, RobotConfig
from src.gears import external_profile, internal_void_profile
from src.knee import motor_pulley, output_carrier, sun_and_pulley
from src.model import Part
from src.robot import head_transform, installed, motion_transform
from src.validate import check_carrier_sweep, check_gears


def test_default_ratios_and_envelopes():
    c = RobotConfig()
    assert (c.gears.sun_teeth, c.gears.planet_teeth, c.gears.ring_teeth) == (18, 12, 42)
    assert c.gears.sun_per_carrier == pytest.approx(10 / 3)
    assert c.total_ratio == 10
    assert c.gears.planet_per_carrier == -2.5
    assert 2 * c.gears.case_radius == 50
    assert c.planet_seat_wall == pytest.approx(0.7)
    assert c.gears.sun_hub_radius == 7.5
    assert c.gears.orbit_radius - c.gears.planet_tip_radius - c.gears.sun_hub_radius == 0.5


def test_willis_and_both_mesh_constraints():
    g = GearTrain()
    carrier, ring = 1, 0
    sun, planet = g.sun_per_carrier, g.planet_per_carrier
    assert g.sun_teeth * (sun - carrier) + g.ring_teeth * (ring - carrier) == pytest.approx(0)
    assert g.sun_teeth * (sun - carrier) + g.planet_teeth * (planet - carrier) == pytest.approx(0)
    assert g.ring_teeth * (ring - carrier) - g.planet_teeth * (planet - carrier) == pytest.approx(0)


@pytest.mark.parametrize("kwargs", [dict(ring_teeth=43), dict(planet_count=7),
                                    dict(module=-1), dict(backlash=-1), dict(pressure_angle=0),
                                    dict(sun_teeth=18.5)])
def test_reject_bad_gear_inputs(kwargs):
    with pytest.raises(ValueError):
        GearTrain(**kwargs)


@pytest.mark.parametrize("teeth", [12, 18, 28])
def test_external_profiles_are_valid_and_periodic(teeth):
    g = GearTrain()
    shape = Polygon(external_profile(teeth, g))
    assert shape.is_valid and shape.area > 0
    assert shape.symmetric_difference(rotate(shape, 360 / teeth, origin=(0, 0))).area < 1e-8


def test_ring_periodicity():
    shape = Polygon(internal_void_profile(GearTrain()))
    assert shape.is_valid
    assert shape.symmetric_difference(rotate(shape, 360 / 42, origin=(0, 0))).area < 1e-8


@pytest.mark.parametrize("teeth", [16, 48])
def test_gt_profile_periodicity(teeth):
    shape = Polygon(pulley_outline(teeth))
    assert shape.is_valid
    assert shape.symmetric_difference(rotate(shape, 360 / teeth, origin=(0, 0))).area < 1e-8


def test_belt_has_straight_spans_not_a_300mm_fit():
    b = BeltDrive()
    path, bow = belt_path(b)
    assert bow == 0
    assert b.taut_pitch_length == pytest.approx(298.33901355335774)
    assert b.stock_pitch_length - b.taut_pitch_length > 1.6
    # Samples 180..358 are the first free span, after its exit at index 179.
    points = np.asarray(path[179:359])
    offsets = points - points[0]
    tangent = offsets[-1]
    cross = offsets[:, 0] * tangent[1] - offsets[:, 1] * tangent[0]
    assert abs(cross).max() < 1e-9


def test_archived_fixture_is_explicitly_separate():
    c = RobotConfig.archived()
    assert c.total_ratio == 9 and c.motor_set_screw and c.belt.model_slack
    assert c.gears.sun_hub_radius == 12.5
    assert belt_path(c.belt)[1] > 5
    assert not RobotConfig().belt.model_slack


@pytest.mark.parametrize("angle", [-120, -37, 0, 29, 120])
def test_orbit_and_signed_spin(angle):
    c = RobotConfig()
    centre = c.gears.planet_centre(1)
    part = Part("planet", None, motion="planet", centre=centre)
    matrix = motion_transform(part, angle, c)
    point = matrix @ np.array([*centre, 0, 1])
    expected = rotate(Polygon([(centre[0], centre[1]), (0, 0), (1, 0)]), angle, origin=(0, 0)).exterior.coords[0]
    assert point[:2] == pytest.approx(expected)
    assert np.linalg.det(matrix[:3, :3]) == pytest.approx(1)
    phase = angle * c.gears.planet_per_carrier * pi / 180
    assert matrix[:2, 0] == pytest.approx([np.cos(phase), np.sin(phase)])


@pytest.mark.parametrize("left", [False, True])
def test_installed_shape_and_mesh_transforms_agree(left):
    c = RobotConfig()
    original = cq.Solid.makeBox(2, 3, 4).translate((6, 7, 8))
    shape = installed(original, c, left)
    centre = head_transform(c, left) @ np.array([7, 8.5, 10, 1])
    assert shape.Center().toTuple() == pytest.approx(centre[:3])


def test_default_motor_has_no_radial_hole():
    new = motor_pulley(RobotConfig()).Solids()[0]
    old = motor_pulley(RobotConfig.archived()).Solids()[0]
    point = cq.Vector(4.5, 100, 27.4)
    assert new.isInside(point, 1e-6)
    assert not old.isInside(point, 1e-6)
    assert not new.isInside(cq.Vector(0, 100, 27.4), 1e-6)


def test_carrier_lug_and_sun_are_single_connected_solids():
    for shape in (output_carrier(RobotConfig()), sun_and_pulley(RobotConfig())):
        assert shape.isValid() and len(shape.Solids()) == 1
        assert shape.Volume() > 0


def test_full_gear_sweep():
    assert check_gears(RobotConfig())["pass"]


def test_carrier_sweep():
    assert check_carrier_sweep(RobotConfig())["pass"]


def test_importing_entrypoint_does_not_build(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = Path(__file__).resolve().parents[1] / "main.py"
    spec = importlib.util.spec_from_file_location("entrypoint_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert list(tmp_path.iterdir()) == []


def test_missing_assets_has_actionable_error(tmp_path):
    with pytest.raises(FileNotFoundError, match="Vendored motor assets"):
        MotorLibrary(tmp_path)


def test_manifest_cannot_escape_assets_directory(tmp_path):
    (tmp_path / "manifest.json").write_text(json.dumps({"parts": {"bad": {"file": "../escape.brep.xz"}}}))
    with pytest.raises(ValueError, match="outside"):
        MotorLibrary(tmp_path).load("bad")


def test_asset_checksum_is_enforced(tmp_path):
    (tmp_path / "bad.brep.xz").write_bytes(b"corrupt")
    (tmp_path / "manifest.json").write_text(json.dumps({"parts": {"bad": {"file": "bad.brep.xz", "sha256": "wrong"}}}))
    with pytest.raises(ValueError, match="checksum"):
        MotorLibrary(tmp_path).load("bad")
