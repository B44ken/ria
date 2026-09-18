"""Print orientation and real joining geometry, not just watertightness."""
from dataclasses import replace
from pathlib import Path

import cadquery as cq
import numpy as np
import pytest
import trimesh

from src.assets import AssetLibrary
from src.config import RobotConfig
from src.export import export_printables
from src.frame import (FRAME_PARTS, JOINT, add_frame, hip_link, knee_backplate,
                       knee_ring)
from src.geometry import box, cylinder
from src.knee import upper_leg
from src.model import Model
from src.printability import audit_frame_prints, check_layers
from src.validate import check_carrier_sweep

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def assets():
    path = ROOT / "assets/reference"
    if not (path / "manifest.json").is_file():
        pytest.skip("Import ria.zip to run reference-geometry integration tests.")
    return AssetLibrary(path)


@pytest.fixture(scope="module")
def frame(assets):
    model = Model()
    add_frame(model, assets, RobotConfig())
    return model


def test_split_frame_is_default_only():
    assert RobotConfig().split_frame
    assert not RobotConfig.archived().split_frame


@pytest.mark.parametrize("builder", [knee_backplate, knee_ring])
def test_knee_prints_are_connected(builder):
    shape = builder(RobotConfig())
    assert shape.isValid() and len(shape.Solids()) == 1 and shape.Volume() > 0


def test_joint_requires_the_designed_gearset():
    with pytest.raises(ValueError, match="18/12/42"):
        knee_ring(RobotConfig.archived())


def test_no_extra_spurious_print_parts(frame):
    assert [p.name for p in frame.parts if p.print_quantity] == list(FRAME_PARTS)
    assert all(p.print_quantity == 2 for p in frame.parts if p.print_quantity)
    assert len(frame.parts) == 14  # 3 prints + 9 screw/nut/washer envelopes + 2 dowels.


def test_three_parts_touch_but_do_not_intersect(frame):
    parts = frame.by_name()
    for first, second in (("hip_link", "knee_backplate"), ("knee_backplate", "knee_ring")):
        a, b = parts[first].shape, parts[second].shape
        assert a.distance(b) < 1e-6
        assert abs(a.intersect(b).Volume()) < 1e-6


def test_original_hip_interface_is_unchanged(frame, assets):
    old = upper_leg(assets, replace(RobotConfig(), split_frame=False))
    clip = box(200, 200, 200, (0, 144, 0))
    a, b = old.intersect(clip), frame.by_name()["hip_link"].shape.intersect(clip)
    assert a.cut(b).Volume() + b.cut(a).Volume() < 1e-6


def test_original_42t_ring_tooth_region_is_unchanged(frame, assets):
    old = upper_leg(assets, replace(RobotConfig(), split_frame=False))
    clip = cylinder(25, 18.1, 23.1)
    a, b = old.intersect(clip), frame.by_name()["knee_ring"].shape.intersect(clip)
    assert a.cut(b).Volume() + b.cut(a).Volume() < 1e-6


def test_locating_dowels_are_retained_only_in_spine(frame):
    parts = frame.by_name()
    for index in range(2):
        pin = parts[f"frame_dowel_{index}"].shape
        assert pin.intersect(parts["hip_link"].shape).Volume() > 0.5
        for name in ("knee_backplate", "knee_ring"):
            assert abs(pin.intersect(parts[name].shape).Volume()) < 1e-6


def test_bolts_pass_through_every_print_and_engage_metal_nuts(frame):
    parts = frame.by_name()
    for index in range(3):
        bolt = parts[f"frame_screw_{index}"].shape
        for name in FRAME_PARTS:
            assert abs(bolt.intersect(parts[name].shape).Volume()) < 1e-6
        assert bolt.intersect(parts[f"frame_nut_{index}"].shape).Volume() > 1


def test_nuts_fit_real_pockets_and_are_accessible(frame):
    parts = frame.by_name()
    for index, centre in enumerate(JOINT.bolts):
        nut = parts[f"frame_nut_{index}"].shape
        assert abs(nut.intersect(parts["hip_link"].shape).Volume()) < 1e-6
        # Insertion from the underside, not through a closed nut-trap ceiling.
        for distance in (0.5, 2, 5):
            assert abs(nut.translate((0, 0, -distance)).intersect(parts["hip_link"].shape).Volume()) < 1e-6


def test_wider_spacer_keeps_full_carrier_travel():
    result = check_carrier_sweep(RobotConfig())
    assert result["pass"] and result["minimum_carrier_neck_gap_mm"] > 4.0


def test_frame_stls_are_flat_and_layer_audited(frame, tmp_path):
    import json
    parts = [p for p in frame.parts if p.print_quantity]
    manifest, _ = export_printables(parts, tmp_path / "printable")
    (tmp_path / "print_manifest.json").write_text(json.dumps(manifest))
    result = audit_frame_prints(tmp_path)
    assert result["pass"]
    records = {p["name"]: p for p in result["parts"]}
    assert all(p["first_layer_area_mm2"] > 1000 for p in records.values())
    assert not records["knee_ring"]["explicit_small_bridges"]
    assert not records["knee_backplate"]["explicit_small_bridges"]
    assert len(records["hip_link"]["explicit_small_bridges"]) == 2


def test_layer_audit_rejects_a_connected_but_unprintable_shelf():
    # This is watertight and connected, but a thin post cannot print a mid-air plate.
    post = cylinder(6, 0, 10)
    shelf = box(40, 40, 2, (0, 0, 11))
    vertices, faces = post.fuse(shelf).tessellate(0.05)
    mesh = trimesh.Trimesh([v.toTuple() for v in vertices], faces, process=True)
    mesh.merge_vertices()
    result = check_layers(mesh, "knee_backplate")
    assert not result["pass"]
    assert result["unsupported_growth"]
