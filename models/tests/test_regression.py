"""Regression must distinguish a changed solid from a changed triangulation."""
from pathlib import Path

import cadquery as cq
import pytest

from src.assets import SourceArchive
from src.head import HEAD_OBJECTS
from src.config import RobotConfig
from src.export import mesh_of
from src.model import Part
from src.regression import compare_part, reference_solid
from src.robot import installed


@pytest.fixture
def reference_archive(tmp_path: Path) -> SourceArchive:
    (tmp_path / "build").mkdir()
    (tmp_path / "references").mkdir()
    shape = cq.Solid.makeBox(2, 3, 4).translate((6, 7, 8))
    cq.exporters.export(shape, str(tmp_path / "build/component.step"))
    head = cq.Assembly()
    head.add(shape, name=HEAD_OBJECTS["head_shell"])
    head.export(str(tmp_path / "references/head_neck_reference.step"))
    return SourceArchive(tmp_path)


@pytest.mark.parametrize("side", ["right", "left"])
def test_installed_fallback_uses_local_step(reference_archive, side):
    local = reference_solid("component", reference_archive)
    expected = installed(local, RobotConfig.archived(), left=side == "left")
    actual = reference_solid(side + "_component", reference_archive)
    assert actual.Center().toTuple() == pytest.approx(expected.Center().toTuple())
    assert actual.cut(expected).Volume() + expected.cut(actual).Volume() < 1e-8


def test_head_fallback_reads_named_reference_object(reference_archive):
    actual = reference_solid(HEAD_OBJECTS["head_shell"], reference_archive)
    assert actual.Center().toTuple() == pytest.approx((7, 8.5, 10))
    assert actual.Volume() == pytest.approx(24)


@pytest.mark.parametrize("changed", [False, True])
def test_exact_fallback_cannot_hide_a_changed_solid(reference_archive, changed):
    expected = reference_solid("right_component", reference_archive)
    mesh = mesh_of(expected)
    # Extra subdivision changes vertices, not the solid surface.
    subdivided = mesh.subdivide()
    reference = {"name": "right_component", "vertices": subdivided.vertices.tolist(),
                 "faces": subdivided.faces.tolist()}
    actual = expected.translate((0.1, 0, 0)) if changed else expected
    result = compare_part(Part("right_component", actual), reference, reference_archive)
    assert result["pass"] is (not changed)
    assert "symmetric_difference_mm3" in result


def test_distal_carrier_mount_stays_put_beyond_the_resized_disk():
    from src.geometry import box
    from src.knee import output_carrier

    # The old disk reaches Y=-25.5; the new disk reaches only Y=-19.5.
    # The unchanged mounting region contains both holes, at -31 and -37.
    clip = box(200, 200, 200, (0, -126, 0))
    old = output_carrier(RobotConfig.archived()).intersect(clip)
    new = output_carrier(RobotConfig()).intersect(clip)
    assert old.Volume() > 0 and new.Volume() > 0
    assert old.cut(new).Volume() + new.cut(old).Volume() < 1e-8
