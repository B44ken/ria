"""Geometry audits with explicit scope and separately reported intended fits.

No mesh Boolean plug-in is needed: gear motion uses the actual extrusion
polygons; the neutral assembly uses OpenCascade solid intersections. These
are geometry checks, not a strength analysis or a certification of purchased
part dimensions, friction, belt preload, or motor-shaft retention.
"""
from hashlib import sha256
from itertools import combinations
from math import cos, radians, sin
from pathlib import Path
import json

import cadquery as cq
import numpy as np
from shapely.affinity import rotate, translate
from shapely.geometry import MultiPoint, Point, Polygon
import trimesh

from .belt import belt_path, pulley_outline
from .config import RobotConfig
from .export import CAD_TO_GLTF
from .gears import external_profile, internal_void_profile
from .geometry import bounds
from .model import Model


def check_gears(config: RobotConfig, samples: int = 721) -> dict:
    g = config.gears
    sun = Polygon(external_profile(g.sun_teeth, g))
    planet = Polygon(external_profile(g.planet_teeth, g))
    void = rotate(Polygon(internal_void_profile(g)), g.ring_phase, origin=(0, 0))
    worst, largest_gap, least_contact = 0.0, 0.0, float("inf")
    for angle in np.linspace(0, 360, samples):
        moving_sun = rotate(sun, float(angle) * g.sun_per_carrier, origin=(0, 0))
        planets = []
        for index in range(g.planet_count):
            a = radians(float(angle) + 360 * index / g.planet_count)
            centre = (g.orbit_radius * cos(a), g.orbit_radius * sin(a))
            moving = translate(rotate(planet, float(angle) * g.planet_per_carrier + g.planet_phase(index),
                                      origin=(0, 0)), *centre)
            planets.append(moving)
            worst = max(worst, moving.intersection(moving_sun).area, moving.difference(void).area)
            largest_gap = max(largest_gap, moving_sun.distance(moving), void.boundary.distance(moving))
            # Confirm that the clearance isn't just a disconnected, non-meshing gear train.
            for sign in (-1, 1):
                probe = rotate(moving, sign * 2, origin=centre)
                contact = max(probe.intersection(moving_sun).area, probe.difference(void).area)
                least_contact = min(least_contact, contact)
        for first, second in combinations(planets, 2):
            worst = max(worst, first.intersection(second).area)
    hub_gap = g.orbit_radius - g.planet_tip_radius - g.sun_hub_radius
    return {"samples": samples, "carrier_range_deg": [0, 360], "planets_per_sample": g.planet_count,
            "worst_overlap_mm2": worst, "largest_tooth_gap_mm": largest_gap,
            "minimum_2deg_backlash_probe_contact_mm2": least_contact,
            "sun_hub_to_planet_tip_conservative_gap_mm": hub_gap,
            "pass": worst < 1e-6 and largest_gap < 0.13 and least_contact > 0 and hub_gap >= 0.3}


def check_carrier_sweep(config: RobotConfig, samples: int = 241) -> dict:
    """Conservative XY silhouettes, at the only shared carrier/neck Z layer."""
    g = config.gears
    radius = g.orbit_radius + 4.5
    root = -(radius - 5.5)
    lug = [(-8, -20), (-7, -40), (7, -40), (8, -20)]
    if root > -20:
        lug = [(-8, root), *lug, (8, root)]
    carrier = Point(0, 0).buffer(radius, quad_segs=256).union(Polygon(lug))
    neck = Polygon([(-10, g.case_radius - 5), (10, g.case_radius - 5),
                    (10, g.case_radius + 5), (-10, g.case_radius + 5)])
    neck = neck.difference(Point(0, 0).buffer(g.case_radius - 1.4, quad_segs=256))
    peak, minimum = 0.0, float("inf")
    for angle in np.linspace(-config.knee_travel, config.knee_travel, samples):
        moving = rotate(carrier, float(angle), origin=(0, 0))
        peak = max(peak, moving.intersection(neck).area)
        minimum = min(minimum, moving.distance(neck))
    return {"samples": samples, "range_deg": [-config.knee_travel, config.knee_travel],
            "worst_carrier_neck_overlap_mm2": peak, "minimum_carrier_neck_gap_mm": minimum,
            "rear_plate_axial_gap_mm": config.stack.carrier_bottom - config.stack.backplate_top,
            "scope": "Conservative carrier silhouette against neck; web and backplate lie below the carrier. No combined hip sweep.",
            "pass": peak < 1e-6 and minimum > 0 and config.stack.carrier_bottom > config.stack.backplate_top}


def check_belt(config: RobotConfig, meshes: dict) -> dict:
    path, bow = belt_path(config.belt)
    interior = Polygon(path).buffer(-1.55)
    servo = MultiPoint(meshes["hip_sg90_body_supplied_step"].vertices[:, :2]).convex_hull
    clearance = interior.boundary.distance(servo)
    # Pitch-to-outer-radius offset is 0.381; backing starts 0.371 inside pitch.
    # Chord discretisation is checked on the actual polygon, not just on radii.
    backing_inner = Polygon(path).buffer(-0.371)
    small = translate(Polygon(pulley_outline(config.belt.motor_teeth)), yoff=config.belt.centre_distance)
    large = Polygon(pulley_outline(config.belt.knee_teeth))
    backing_clear = backing_inner.covers(small) and backing_inner.covers(large)
    return {"span_bow_mm": bow, "pitch_path_length_mm": config.belt.taut_pitch_length,
            "stock_pitch_length_mm": config.belt.stock_pitch_length,
            "stock_minus_taut_mm": config.belt.stock_pitch_length - config.belt.taut_pitch_length,
            "servo_inside_conservative_tooth_envelope": bool(interior.contains(servo)),
            "servo_tooth_envelope_clearance_mm": clearance,
            "both_pulleys_clear_of_backing": bool(backing_clear),
            "pass": bow == 0 and interior.contains(servo) and backing_clear}


def broadphase(first: cq.Shape, second: cq.Shape) -> bool:
    a, b = np.array(bounds(first)), np.array(bounds(second))
    return bool(np.all(np.minimum(a[1], b[1]) - np.maximum(a[0], b[0]) > 1e-5))


def check_static(knee: Model, robot: Model | None) -> dict:
    intended = {frozenset(row["parts"]): row["reason"] for row in knee.intentional_fits}
    fits, inherited, collisions, checked = [], [], [], []
    gear_names = {p.name for p in knee.parts if p.name.startswith("planet_") and p.motion == "planet"
                  and "bearing" not in p.name}
    gear_names.add("sun_pulley")
    candidates = [(a, b, False) for a, b in combinations(knee.parts, 2)]
    if robot:
        # Same-side checks above are identical under the two rigid transforms.
        candidates += [(a, b, True) for a, b in combinations(robot.parts, 2)
                       if a.name.split("_")[0] != b.name.split("_")[0]
                       or (a.name.startswith("head_") and b.name.startswith("head_"))]
    for first, second, installed in candidates:
        a, b = first.name, second.name
        if not broadphase(first.shape, second.shape):
            continue
        pair = frozenset((a, b))
        if not installed and ((a in gear_names and b in gear_names)
                              or ("upper_leg" in pair and bool(pair & gear_names))):
            checked.append({"parts": [a, b], "method": "extruded-profile gear audit and disjoint axial stack"})
            continue
        # Intersect the actual B-reps, including purchased/reference interfaces.
        print(f"  collision: {a} / {b}", flush=True)
        intersection = first.shape.intersect(second.shape)
        volume = max(0.0, intersection.Volume())
        row = {"parts": [a, b], "overlap_mm3": volume, "method": "OpenCascade B-rep intersection"}
        checked.append(row)
        if volume <= 0.012:
            continue
        if pair in intended:
            fits.append({**row, "reason": intended[pair]})
        elif (a.startswith("hip_") and b.startswith("hip_")) or (
            installed and ((a.startswith("head_") and "_hip_" in b)
                           or (b.startswith("head_") and "_hip_" in a))):
            inherited.append({**row, "reason": "Unchanged reference-to-reference interface; reported, not silently excused as a new design fit."})
        else:
            collisions.append(row)
    return {"pose": "neutral", "positive_volume_tolerance_mm3": 0.012,
            "checks": checked, "intentional_press_or_tap_fits": fits,
            "inherited_reference_overlaps": inherited, "unexpected_overlaps": collisions,
            "pass": not collisions,
            "scope": "All neutral local pairs and installed cross-group pairs broadphase checked. Gear extrusion pairs use the all-phase profile test. No load/deflection or combined hip motion analysis."}


def check_exports(build: Path, knee: Model, robot: Model | None) -> dict:
    records = []
    for name, model in (("knee", knee), ("robot", robot)):
        if model is None:
            continue
        path = build / (name + ".glb")
        scene = trimesh.load(path, force="scene", process=True)
        total_vertices, valid = 0, True
        actual_bounds = []
        for node in scene.graph.nodes_geometry:
            transform, key = scene.graph[node]
            mesh = scene.geometry[key].copy().apply_transform(np.linalg.inv(CAD_TO_GLTF) @ transform)
            mesh.merge_vertices(digits_vertex=5)
            valid &= bool(mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0)
            total_vertices += len(mesh.vertices)
            actual_bounds.append(mesh.bounds)
        expected = np.array([bounds(p.shape) for p in model.parts])
        actual = np.array(actual_bounds)
        error = float(np.abs(np.array([expected[:, 0].min(0), expected[:, 1].max(0)])
                            - np.array([actual[:, 0].min(0), actual[:, 1].max(0)])).max())
        # STEP importer checks the actual assembly bytes and named object count.
        assembly = cq.Assembly.importStep(str(build / (name + ".step")))
        solids = [item for item in assembly.objects.values() if isinstance(item.obj, cq.Shape)]
        step_valid = all(item.obj.isValid() and item.obj.Volume() > 0 for item in solids)
        ok = valid and error < 0.04 and len(scene.geometry) == len(model.parts) and len(solids) == len(model.parts) and step_valid
        records.append({"assembly": name, "parts": len(model.parts), "vertices": total_vertices,
                        "glb_watertight_positive_consistent": valid, "glb_bounds_error_mm": error,
                        "step_valid_parts": len(solids), "pass": bool(ok)})
    prints = json.loads((build / "print_manifest.json").read_text())
    for record in prints:
        raw = (build / record["file"]).read_bytes()
        if sha256(raw).hexdigest() != record["sha256"]:
            raise ValueError("Print export checksum changed: " + record["name"])
    return {"assemblies": records, "validated_print_files": len(prints),
            "pass": all(row["pass"] for row in records)}


def validate_build(knee: Model, robot: Model | None, config: RobotConfig, exported: dict, build: Path) -> dict:
    checks = {}
    for name, call in (
        ("gear_motion", lambda: check_gears(config)),
        ("carrier_motion", lambda: check_carrier_sweep(config)),
        ("belt", lambda: check_belt(config, exported["knee_meshes"])),
        ("exports", lambda: check_exports(build, knee, robot)),
        ("static_assembly", lambda: check_static(knee, robot)),
    ):
        print("checking " + name, flush=True)
        checks[name] = call()
        (build / "validation.json").write_text(json.dumps(checks, indent=2) + "\n")
    checks["pass"] = all(item["pass"] for item in checks.values())
    checks["limitations"] = [
        "12T planet: 0.70 mm radial wall at the 8.1 mm bearing seat. Print and test coupons; strength/life not established.",
        "No motor grub screw or radial hole. A 4.9 mm clearance bore on a 4.8 mm shaft does not establish torque or axial retention.",
        "The 100 mm-centre taut pitch path is 298.339 mm, not a fitted stock 300 mm belt; no tensioner or mounting adjustment was invented.",
        "Bearing, screw and belt teeth are simplified envelopes; the GT profile is inherited, not manufacturer-certified.",
        "Geometry audits do not simulate loads, contact friction, wear, belt preload or combined hip articulation.",
    ]
    (build / "validation.json").write_text(json.dumps(checks, indent=2) + "\n")
    return checks
