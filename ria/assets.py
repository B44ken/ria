"""Import the unchanged reference geometry; never execute the old source code.

Only the head, original hip nose and purchased / pre-existing hip components
are retained as B-reps. The leg, gears, pulleys, belt and knee hardware are
built by readable Python functions elsewhere in this package.
"""

from functools import lru_cache
from hashlib import sha256
from io import BytesIO
import json
import lzma
from pathlib import Path
import tempfile
import zipfile

import cadquery as cq

from .geometry import bounds, box, clean_solid

HEAD_OBJECTS = {
    "head_shell": "head_shell_with_integral_sectors_and_housings",
    "head_lid": "head_lid",
}
HIP_OBJECTS = (
    "5010_mount_M3x8_countersunk_0", "5010_mount_M3x8_countersunk_1",
    "5010_mount_M3x8_countersunk_2", "5010_mount_M3x8_countersunk_3",
    "5010_rotor_supplied_STEP", "5010_stator_supplied_STEP",
    "5mm_OD_3p2mm_ID_sleeve", "685zz_bearing_0_inner_race",
    "685zz_bearing_0_outer_race", "685zz_bearing_0_shields",
    "SG90_spacer_0", "SG90_spacer_1", "axle_M3x12_pan_screw",
    "servo_pinion_36T_m1", "sg90_body_supplied_STEP", "sg90_output_spline",
)


class SourceArchive:
    """Read fixed, known STEP paths from either ria.zip or its extracted folder."""

    def __init__(self, path: Path):
        self.path = path.resolve()
        self.archive = zipfile.ZipFile(path) if path.is_file() else None
        self.prefix = ""
        if self.archive:
            matches = [name for name in self.archive.namelist()
                       if name.endswith("references/head_neck_reference.step")]
            if len(matches) != 1:
                raise ValueError("Expected exactly one references/head_neck_reference.step in the archive.")
            self.prefix = matches[0][:-len("references/head_neck_reference.step")]
        elif not (path / "references/head_neck_reference.step").is_file():
            raise FileNotFoundError(f"No reference model found in {path}.")

    def read(self, relative: str) -> bytes:
        if self.archive:
            return self.archive.read(self.prefix + relative)
        return (self.path / relative).read_bytes()

    def close(self) -> None:
        if self.archive:
            self.archive.close()


def import_assets(source: Path, destination: Path) -> dict:
    """Convert selected original STEP shapes to small, hash-checked B-reps."""
    source_files = SourceArchive(source)
    destination.mkdir(parents=True, exist_ok=True)
    manifest: dict = {"format": 1, "units": "mm", "parts": {}}

    def retain(name: str, shape: cq.Shape, source_path: str, source_bytes: bytes) -> None:
        shape = clean_solid(shape, name)
        stream = BytesIO()
        shape.exportBrep(stream)
        data = lzma.compress(stream.getvalue(), preset=9)
        filename = name + ".brep.xz"
        (destination / filename).write_bytes(data)
        manifest["parts"][name] = {
            "file": filename, "sha256": sha256(data).hexdigest(),
            "source": source_path, "source_sha256": sha256(source_bytes).hexdigest(),
            "volume_mm3": shape.Volume(), "bounds_mm": bounds(shape),
            "solids": len(shape.Solids()),
        }
        print(f"  reference: {name}", flush=True)

    try:
        with tempfile.TemporaryDirectory(prefix="ria-import-") as temp:
            step_path = Path(temp) / "input.step"
            relative = "references/head_neck_reference.step"
            raw = source_files.read(relative)
            step_path.write_bytes(raw)
            head = cq.Assembly.importStep(str(step_path))
            for key, original_name in HEAD_OBJECTS.items():
                obj = head.objects[original_name]
                retain(key, obj.obj.moved(obj.loc), relative + "#" + original_name, raw)

            relative = "references/leg_local_reference.step"
            raw = source_files.read(relative)
            step_path.write_bytes(raw)
            nose = cq.importers.importStep(str(step_path)).val()
            nose = nose.rotate((0, 0, 0), (1, 0, 0), 90)
            nose = nose.rotate((0, 0, 0), (0, 0, 1), 180).translate((0, 100, -40.7))
            nose = nose.intersect(box(100, 50, 60, (0, 110, 10)))
            retain("hip_nose", nose, relative + "#y>=85_local_clip", raw)

            for key in HIP_OBJECTS:
                relative = f"references/hip_breps/right_{key}.step"
                raw = source_files.read(relative)
                step_path.write_bytes(raw)
                retain(key, cq.importers.importStep(str(step_path)).val(), relative, raw)
    finally:
        source_files.close()
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


class AssetLibrary:
    def __init__(self, directory: Path):
        self.directory = directory.resolve()
        manifest_path = self.directory / "manifest.json"
        if not manifest_path.is_file():
            raise FileNotFoundError(
                "Reference assets are missing. Import your archive once with:\n"
                "  python main.py --import-source /path/to/ria.zip\n"
                "Then subsequent builds only need: python main.py"
            )
        self.manifest = json.loads(manifest_path.read_text())

    @lru_cache(maxsize=None)
    def load(self, name: str) -> cq.Shape:
        record = self.manifest["parts"][name]
        path = (self.directory / record["file"]).resolve()
        if not path.is_relative_to(self.directory):
            raise ValueError("Reference manifest points outside its assets directory.")
        data = path.read_bytes()
        if sha256(data).hexdigest() != record["sha256"]:
            raise ValueError(f"Reference checksum failed: {name}")
        shape = cq.Shape.importBrep(BytesIO(lzma.decompress(data)))
        return clean_solid(shape, name)
