"""Prove the port against the supplied built model, not screenshots alone."""
from pathlib import Path
import json
import tempfile

import cadquery as cq
import numpy as np
import trimesh
from scipy.spatial import cKDTree

from .assets import AssetLibrary, HEAD_OBJECTS, SourceArchive
from .config import RobotConfig
from .export import mesh_of
from .geometry import bounds, box
from .knee import build_knee
from .model import Model
from .robot import installed

# These are the only local parts allowed to differ from the 28/14/56 build.
CHANGED = {"upper_leg", "carrier", "sun_pulley", "motor_pulley", "belt"}
CHANGED |= {f"planet_{i}" for i in range(3)}
CHANGED |= {f"planet_pin_{i}" for i in range(3)}
CHANGED |= {f"planet_bearing_{i}_{race}" for i in range(3) for race in ("inner", "outer", "shields")}


def reference_solid(name: str, source: SourceArchive) -> cq.Shape:
    """Read the actual reference solid in the same local or installed frame.

    The archive stores per-part STEPs only for the local knee. Installed
    meshes were produced by rigidly transforming those same solids; there
    are no `right_*.step` or `left_*.step` files in its build directory.
    """
    with tempfile.TemporaryDirectory(prefix="ria-regression-") as temp:
        path = Path(temp) / "reference.step"
        if name in HEAD_OBJECTS.values():
            path.write_bytes(source.read("references/head_neck_reference.step"))
            item = cq.Assembly.importStep(str(path)).objects[name]
            return item.obj.moved(item.loc)
        if name.startswith(("right_", "left_")):
            side, local_name = name.split("_", 1)
            path.write_bytes(source.read("build/" + local_name + ".step"))
            shape = cq.importers.importStep(str(path)).val()
            return installed(shape, RobotConfig.archived(), left=side == "left")
        path.write_bytes(source.read("build/" + name + ".step"))
        return cq.importers.importStep(str(path)).val()


def compare_part(part, reference: dict, source: SourceArchive) -> dict:
    mesh = mesh_of(part.shape)
    vertices = np.asarray(reference["vertices"])
    distance = max(cKDTree(mesh.vertices).query(vertices)[0].max(),
                   cKDTree(vertices).query(mesh.vertices)[0].max())
    if "volume" in reference and "bounds" in reference:
        volume = abs(part.shape.Volume() - reference["volume"])
        extent = float(np.abs(np.asarray(bounds(part.shape)) - reference["bounds"]).max())
    else:
        # The archived installed-model JSON stores meshes without CAD metrics.
        reference_mesh = trimesh.Trimesh(vertices, reference["faces"], process=False)
        volume = abs(mesh.volume - reference_mesh.volume)
        extent = float(np.abs(mesh.bounds - reference_mesh.bounds).max())
    row = {"name": part.name, "reference": reference["name"],
           "max_vertex_distance_mm": float(distance), "volume_delta_mm3": volume,
           "bounds_delta_mm": extent, "pass": bool(distance < 1e-5 and volume < 1e-4 and extent < 1e-5)}
    if not row["pass"]:
        # Matching solids can be triangulated differently, particularly on a
        # long belt span. Resolve that ambiguity with two exact solid cuts.
        print("  exact-solid fallback: " + part.name, flush=True)
        shape = reference_solid(reference["name"], source)
        delta = part.shape.cut(shape).Volume() + shape.cut(part.shape).Volume()
        row["symmetric_difference_mm3"] = delta
        row["pass"] = delta < 1e-4
    return row


def compare_source(knee: Model, robot: Model | None, assets: AssetLibrary,
                   source_path: Path, output: Path) -> dict:
    source = SourceArchive(source_path)
    try:
        original = json.loads(source.read("build/geometry.json"))
        original = {part["name"]: part for part in original["parts"]}
        archived = build_knee(assets, RobotConfig.archived())
        previous = archived.by_name()
        rows = []
        for part in archived.parts:
            print("  regression fixture: " + part.name, flush=True)
            rows.append(compare_part(part, original[part.archived_name], source))
        unchanged = []
        for part in knee.parts:
            if part.name not in CHANGED:
                print("  unchanged: " + part.name, flush=True)
                unchanged.append(compare_part(part, original[previous[part.name].archived_name], source))
        # Check the hip-side frame, lower-leg mounting lug, and unchanged
        # pulley body above the resized sun hub as B-rep regions, not just bounds.
        # The distal lug check starts beyond the OLD 25.5 mm-radius disk;
        # including that disk's edge would misclassify its intentional resize.
        regions = (("upper_leg", box(200, 200, 200, (0, 144, 0))),
                   ("carrier", box(200, 200, 200, (0, -126, 0))),
                   ("sun_pulley", box(200, 200, 200, (0, 0, 123.6))))
        interfaces = []
        for name, clip in regions:
            first = previous[name].shape.intersect(clip)
            second = knee.by_name()[name].shape.intersect(clip)
            delta = first.cut(second).Volume() + second.cut(first).Volume()
            interfaces.append({"part": name, "symmetric_difference_mm3": delta, "pass": delta < 1e-4})
        head = []
        if robot:
            original_robot = json.loads(source.read("build/robot_geometry.json"))
            old_robot = {part["name"]: part for part in original_robot["parts"]}
            # Both unchanged head objects and all 70 unchanged installed parts.
            for part in robot.parts:
                local = part.name.split("_", 1)[1]
                if part.name.startswith("head_") or local not in CHANGED:
                    reference = old_robot.get(part.archived_name)
                    if reference is None and part.name.startswith("head_"):
                        reference = old_robot.get(part.name)
                    if reference is None:
                        raise ValueError("Missing installed reference part: " + part.archived_name)
                    print("  unchanged installed: " + part.name, flush=True)
                    head.append(compare_part(part, reference, source))
        report = {"archived_fixture": rows, "unchanged_local_parts": unchanged,
                  "unchanged_installed_parts": head, "preserved_interfaces": interfaces,
                  "intentional_changed_local_parts": sorted(CHANGED),
                  "removed": ["motor_set_screw"],
                  "pass": all(row["pass"] for row in rows + unchanged + interfaces + head)}
        (output / "regression.json").write_text(json.dumps(report, indent=2) + "\n")
        return report
    finally:
        source.close()
