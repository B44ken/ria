"""Layer-by-layer checks of the exported frame STLs, not just solid validity.

This is a geometric cross-section audit, NOT a slicer or a physical print.
45-degree layer growth is allowed. Two small, inherited hip counterbore
roofs are reported explicitly as bridges; no other mid-air growth is allowed.
"""
from functools import reduce
import json
from math import ceil
from pathlib import Path

import numpy as np
from shapely.geometry import Point, Polygon
import trimesh

from .frame import FRAME_PARTS


def components(region):
    if region.geom_type == "Polygon":
        return [region]
    return [part for part in getattr(region, "geoms", ()) if part.geom_type == "Polygon"]


def slice_polygons(mesh: trimesh.Trimesh, layer_height: float):
    height = float(mesh.bounds[1, 2])
    starts = np.arange(ceil((height - 1e-5) / layer_height)) * layer_height
    centres = (starts + np.minimum(starts + layer_height, height)) / 2
    paths = mesh.section_multiplane([0, 0, 0], [0, 0, 1], centres)
    regions = []
    for path in paths:
        if path is None:
            regions.append(Polygon())
        elif not path.is_closed:
            raise ValueError("Open contour found in a frame print layer.")
        else:
            # XOR nested closed contours preserves holes without optional rtree.
            loops = path.polygons_closed
            region = reduce(lambda a, b: a.symmetric_difference(b), loops, Polygon())
            if not region.is_valid:
                raise ValueError("Invalid frame layer polygon.")
            regions.append(region)
    return centres, regions


def check_layers(mesh: trimesh.Trimesh, name: str, *, layer_height: float = 0.2,
                 hip_bore_centre: tuple | None = None) -> dict:
    if not mesh.is_watertight or mesh.body_count != 1 or abs(mesh.bounds[0, 2]) > 0.01:
        raise ValueError("Frame print must be one watertight body on Z=0.")
    centres, regions = slice_polygons(mesh, layer_height)
    problems, bridges, islands = [], [], []
    for index in range(1, len(regions)):
        previous, current = regions[index - 1], regions[index]
        z = float(centres[index])
        for part in components(current):
            if part.intersection(previous).area < 1e-5:
                islands.append({"z_mm": z, "area_mm2": part.area, "bounds_mm": list(part.bounds)})
        growth = float(centres[index] - centres[index - 1])
        unsupported = current.difference(previous.buffer(growth + 1e-5))
        if unsupported.area <= 0.01:
            continue
        sizes = [max(p.bounds[2] - p.bounds[0], p.bounds[3] - p.bounds[1])
                 for p in components(unsupported)]
        row = {"z_mm": z, "area_mm2": unsupported.area,
               "largest_component_span_mm": max(sizes), "bounds_mm": list(unsupported.bounds)}
        allowed = False
        if name == "hip_link" and hip_bore_centre is not None:
            zone = Point(hip_bore_centre).buffer(7.2, quad_segs=128)
            at_existing_roof = (2.0 < z < 2.5) or (4.4 < z < 4.95)
            allowed = (at_existing_roof and max(sizes) < 7.0
                       and unsupported.difference(zone).area < 0.01)
        if allowed:
            bridges.append({**row, "reason": "Unchanged hip counterbore roof; tune bridging in the slicer."})
        else:
            problems.append(row)
    return {"name": name, "layer_height_mm": layer_height, "layers": len(regions),
            "first_layer_area_mm2": regions[0].area,
            "bounds_mm": mesh.bounds.tolist(), "floating_islands": islands,
            "unsupported_growth": problems, "explicit_small_bridges": bridges,
            "pass": bool(not problems and not islands and regions[0].area > 100),
            "scope": "Actual STL cross-sections, 45-degree growth allowance. Not toolpaths, G-code, or a physical print test."}


def audit_frame_prints(build: Path) -> dict:
    manifest = {part["name"]: part for part in json.loads((build / "print_manifest.json").read_text())}
    records = []
    for name in FRAME_PARTS:
        record = manifest[name]
        mesh = trimesh.load_mesh(build / record["file"], process=True)
        translation = record["translation_mm"]
        hip_centre = (translation[0], -100 + translation[1]) if name == "hip_link" else None
        records.append(check_layers(mesh, name, hip_bore_centre=hip_centre))
    result = {"parts": records, "pass": all(row["pass"] for row in records),
              "hardware": "Three M3x25 screws, three M3 nuts, three M3 washers, two 3x25 steel locating dowels per leg.",
              "limitation": "Knee pieces have no unsupported layer growth. Original hip bore roofs still require short bridging; inspect your slicer's paths and test the fit coupons."}
    (build / "frame_printability.json").write_text(json.dumps(result, indent=2) + "\n")
    return result
