"""export current cad from a temporary source snapshot; never modify build/."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
import shutil
import sys
from tempfile import TemporaryDirectory

viewer = Path(__file__).resolve().parents[1]
repo = viewer.parent
output = viewer / "public/models"
output.mkdir(parents=True, exist_ok=True)

with TemporaryDirectory(prefix="ria-viewer-") as directory:
    snapshot = Path(directory)
    shutil.copytree(repo / "models", snapshot / "models",
                    ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))
    shutil.copytree(repo / "pcb", snapshot / "pcb",
                    ignore=shutil.ignore_patterns("*-backups", "*.kicad_prl"))
    (snapshot / "software").mkdir()
    shutil.copy2(repo / "software/bot.json", snapshot / "software/bot.json")
    files = sorted(path for path in snapshot.rglob("*") if path.is_file())
    digest = sha256()
    for path in files:
        digest.update(str(path.relative_to(snapshot)).encode())
        digest.update(path.read_bytes())

    os.chdir(snapshot / "models")
    sys.path.insert(0, str(snapshot / "models"))
    model = runpy.run_path("main.py")
    scene = model["scene"]
    import cadquery as cq
    import trimesh
    from trimesh.exchange.gltf import export_glb
    from config import config
    from util.frames import knee_origin, wheel_origin

    p = config.planetary
    meshes = []

    def identify(tree):
        for node in tree["nodes"]:
            name = node["name"]
            parts = name.split("/")
            side = "right" if parts[0] == "right_leg" else "left" if parts[0] == "left_leg" else "head"
            link = "wheel" if "wheel" in parts[:-1] else "lower_leg" if "lower_leg" in parts[:-1] else "upper_leg" if "upper_leg" in parts[:-1] else "head"
            node["extras"] = {"cadName": name, "part": parts[-1], "side": side, "link": link}
            if "mesh" in node:
                meshes.append(node["extras"])

    (output / "ria.glb").write_bytes(export_glb(scene, tree_postprocessor=identify))

    details = trimesh.Scene()
    for name, part in model["leg"].traverse():
        if name not in ("ring", "lower_leg"):
            continue
        shape = part.obj.val().moved(part.loc).translate(tuple(-knee_origin))
        bounds = shape.BoundingBox()
        low = [bounds.xmin - 1, bounds.ymin - 1, bounds.zmin - 1]
        high = [bounds.xmax + 1, bounds.ymax + 1, bounds.zmax + 1]
        if name == "ring":
            high[1], high[2] = 26, p.z + p.thickness - 0.05
            detail = "ring_open"
        else:
            low[1] = -24
            detail = "carrier_detail"
        keep = cq.Solid.makeBox(*(end - start for start, end in zip(low, high)), cq.Vector(*low))
        path = snapshot / f"{detail}.stl"
        shape.intersect(keep).exportStl(str(path), 0.1, 0.3)
        mesh = trimesh.load_mesh(path)
        details.add_geometry(mesh, geom_name=detail, node_name=detail)

    def identify_details(tree):
        for node in tree["nodes"]:
            if "mesh" in node:
                node["extras"] = {"part": node["name"], "sourcePart": "ring" if node["name"] == "ring_open" else "lower_leg"}

    (output / "drive-details.glb").write_bytes(export_glb(details, tree_postprocessor=identify_details))
    manifest = {
        "sourceHash": digest.hexdigest(),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "units": "mm",
        "modelScale": 0.001,
        "knee": knee_origin.tolist(),
        "wheel": wheel_origin.tolist(),
        "planetary": {
            "sun": p.sun, "planet": p.planet, "ring": p.ring, "count": p.count,
            "module": p.module, "orbitRadius": p.module * (p.sun + p.planet) / 2,
            "gearZ": p.z, "gearThickness": p.thickness,
            "carrierZ": config.leg.thickness + 0.3, "carrierThickness": p.carrier_thickness,
        },
        "belt": {"motor": config.belt.teeth_motor, "pulley": config.belt.teeth_pulley},
        "sourceFiles": [str(path.relative_to(snapshot)) for path in files],
        "meshes": meshes,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

print(f"exported {len(meshes)} meshes to {output}")
