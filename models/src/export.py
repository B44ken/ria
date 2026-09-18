"""Export CAD, correctly scaled glTF, individually bed-oriented prints and metadata."""

from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial

from .belt import timing_pulley
from .config import RobotConfig
from .geometry import annulus, bounds, cylinder
from .frame import FRAME_PARTS, JOINT
from .model import COLOURS, Model, Part
from .robot import head_transform

CAD_TO_GLTF = np.array([[1, 0, 0, 0], [0, 0, 1, 0],
                        [0, -1, 0, 0], [0, 0, 0, 1000]], dtype=float) / 1000


def mesh_of(shape: cq.Shape, linear: float = 0.025, angular: float = 0.06) -> trimesh.Trimesh:
    vertices, faces = shape.tessellate(linear, angular)
    mesh = trimesh.Trimesh([vertex.toTuple() for vertex in vertices], faces, process=True)
    mesh.merge_vertices(digits_vertex=7)
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.update_faces(mesh.unique_faces())
    mesh.remove_unreferenced_vertices()
    mesh.fix_normals(multibody=True)
    if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
        raise ValueError("CAD tessellation produced a non-solid mesh.")
    return mesh


def make_meshes(model: Model) -> dict[str, trimesh.Trimesh]:
    result = {}
    for part in model.parts:
        result[part.name] = mesh_of(part.shape)
        print(f"  mesh: {part.name}", flush=True)
    return result


def robot_meshes(knee_meshes: dict[str, trimesh.Trimesh], robot: Model,
                 config: RobotConfig) -> dict[str, trimesh.Trimesh]:
    result = {}
    for part in robot.parts:
        if part.name.startswith("head_"):
            result[part.name] = mesh_of(part.shape)
    for side in ("right", "left"):
        transform = head_transform(config, left=side == "left")
        for name, mesh in knee_meshes.items():
            result[f"{side}_{name}"] = mesh.copy().apply_transform(transform)
    return result


def export_glb(model: Model, meshes: dict[str, trimesh.Trimesh], path: Path) -> None:
    scene = trimesh.Scene()
    for part in model.parts:
        mesh = meshes[part.name].copy().apply_transform(CAD_TO_GLTF)
        colour = [round(channel * 255) for channel in COLOURS[part.material]] + [255]
        material = PBRMaterial(name=part.material, baseColorFactor=colour,
                               metallicFactor=0.65 if part.material in ("steel", "copper") else 0,
                               roughnessFactor=0.38)
        mesh.visual = trimesh.visual.TextureVisuals(material=material)
        mesh.metadata = {"description": part.note, "motion": part.motion}
        scene.add_geometry(mesh, node_name=part.name, geom_name=part.name)
    path.write_bytes(scene.export(file_type="glb"))


def fit_coupons() -> list[Part]:
    parts = []
    for diameter in (8.0, 8.1, 8.2):
        name = f"fit_693_{diameter:.1f}".replace(".", "p")
        parts.append(Part(name, annulus(6, diameter / 2, 0, 4), print_quantity=1,
                          note=f"693ZZ bearing fit coupon; {diameter:.1f} mm seat."))
    for diameter in (2.9, 3.0, 3.1):
        name = f"fit_pin_{diameter:.1f}".replace(".", "p")
        parts.append(Part(name, annulus(4, diameter / 2, 0, 4), print_quantity=1,
                          note=f"3 mm steel dowel fit coupon; {diameter:.1f} mm pilot."))
    for diameter in (2.95, 3.05):
        name = f"fit_frame_dowel_{diameter:.2f}".replace(".", "p")
        parts.append(Part(name, annulus(4, diameter / 2, 0, 4.5), print_quantity=1,
                          note=f"Frame locating dowel coupon; {diameter:.2f} mm CAD bore."))
    pulley = timing_pulley(16, 0, 3).cut(cylinder(2.45, -0.1, 3.1))
    parts.append(Part("fit_pulley_16t_4p9", pulley, material="yellow", print_quantity=1,
                      note="Check the actual belt tooth profile and 4.8 mm shaft in this 4.9 mm bore."))
    return parts


def printable_parts(knee: Model, robot: Model | None) -> list[Part]:
    parts = [part for part in knee.parts if part.print_quantity]
    if robot:
        parts += [part for part in robot.parts if part.name.startswith("head_")]
    return parts + fit_coupons()


def export_printables(parts: list[Part], directory: Path) -> tuple[list[dict], dict[str, trimesh.Trimesh]]:
    directory.mkdir(parents=True, exist_ok=True)
    records, meshes = [], {}
    for part in parts:
        # Put closed caps on the bed; leave bearing sockets facing upward.
        flip = part.name in {"head_shell", "sun_pulley", "motor_pulley", "planet_0", *FRAME_PARTS}
        oriented = part.shape.rotate((0, 0, 0), (1, 0, 0), 180) if flip else part.shape
        extent = bounds(oriented)
        transform = (-(extent[0][0] + extent[1][0]) / 2,
                     -(extent[0][1] + extent[1][1]) / 2, -extent[0][2])
        bed_shape = oriented.translate(transform)
        if len(bed_shape.Solids()) != 1 or not bed_shape.isValid():
            raise ValueError(f"Printable {part.name} is not one valid CAD solid.")
        path = directory / (part.name + ".stl")
        cq.exporters.export(bed_shape, str(path), tolerance=0.008, angularTolerance=0.03)
        # Re-open the bytes actually written; do not certify just the in-memory mesh.
        mesh = trimesh.load_mesh(path, process=True)
        mesh.merge_vertices(digits_vertex=6)
        good = (mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
                and mesh.body_count == 1 and abs(mesh.bounds[0, 2]) < 0.01)
        if not good:
            raise ValueError(f"STL round-trip failed: {path.name}")
        meshes[part.name] = mesh
        records.append({"name": part.name, "file": f"printable/{path.name}",
                        "quantity_for_robot": part.print_quantity, "note": part.note,
                        "rotation_deg_xyz": [180 if flip else 0, 0, 0],
                        "translation_mm": list(transform),
                        "bounds_mm": mesh.bounds.tolist(), "volume_mm3": float(mesh.volume),
                        "watertight": True, "single_solid": True,
                        "sha256": sha256(path.read_bytes()).hexdigest()})
    return records, meshes


def part_record(part: Part) -> dict:
    return {"name": part.name, "archived_name": part.archived_name,
            "material": part.material, "motion": part.motion, "centre_mm": list(part.centre),
            "volume_mm3": part.shape.Volume(), "bounds_mm": bounds(part.shape),
            "solids": len(part.shape.Solids()), "note": part.note}


def export_models(knee: Model, robot: Model | None, config: RobotConfig,
                  destination: Path) -> dict:
    destination.mkdir(parents=True, exist_ok=True)
    # Remove only obsolete generated frame artifacts when upgrading an existing build.
    if config.split_frame:
        for relative in ("printable/upper_leg.stl", "cad_parts/upper_leg.step",
                         "previews/parts/upper_leg.png"):
            (destination / relative).unlink(missing_ok=True)
    part_dir = destination / "cad_parts"
    part_dir.mkdir(exist_ok=True)
    knee_mesh = make_meshes(knee)
    for part in knee.parts:
        cq.exporters.export(part.shape, str(part_dir / f"{part.name}.step"))
    print("  exporting knee STEP / glTF", flush=True)
    knee.assembly("ria_knee").export(str(destination / "knee.step"))
    export_glb(knee, knee_mesh, destination / "knee.glb")
    if config.split_frame:
        frame = Model(parts=[p for p in knee.parts if p.name in FRAME_PARTS or p.name.startswith("frame_")])
        frame.assembly("ria_printable_frame").export(str(destination / "frame.step"))
        export_glb(frame, knee_mesh, destination / "frame.glb")
    full_mesh = None
    if robot:
        print("  exporting robot STEP / glTF", flush=True)
        full_mesh = robot_meshes(knee_mesh, robot, config)
        robot.assembly("ria_robot").export(str(destination / "robot.step"))
        export_glb(robot, full_mesh, destination / "robot.glb")

    prints = printable_parts(knee, robot)
    manifest, print_mesh = export_printables(prints, destination / "printable")
    (destination / "print_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    metadata = {"units": {"cad": "mm", "stl": "mm", "glb": "m, Y-up"},
                "config": asdict(config),
                "frame_joint": asdict(JOINT) if config.split_frame else None, "derived": {
                    "planetary_ratio": config.gears.sun_per_carrier,
                    "planet_absolute_spin_per_carrier": config.gears.planet_per_carrier,
                    "belt_ratio": config.belt.ratio, "total_ratio": config.total_ratio,
                    "case_diameter_mm": 2 * config.gears.case_radius,
                    "sun_hub_radius_mm": config.gears.sun_hub_radius,
                    "ring_root_wall_mm": config.gears.ring_root_wall,
                    "planet_bearing_root_wall_mm": config.planet_seat_wall,
                    "taut_belt_pitch_length_mm": config.belt.taut_pitch_length,
                    "stock_belt_pitch_length_mm": config.belt.stock_pitch_length,
                    "modelled_belt_slack": config.belt.model_slack},
                "knee_parts": [part_record(part) for part in knee.parts],
                "robot_parts": [part_record(part) for part in robot.parts] if robot else [],
                "intentional_fits": knee.intentional_fits}
    (destination / "model.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return {"knee_meshes": knee_mesh, "robot_meshes": full_mesh,
            "print_parts": prints, "print_meshes": print_mesh, "metadata": metadata}
