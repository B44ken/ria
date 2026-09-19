"""Hash-checked, vendored purchased-part CAD. No downloads or import cache."""
from functools import lru_cache
from hashlib import sha256
from io import BytesIO
import json
import lzma
from pathlib import Path
import zipfile
import tempfile

import cadquery as cq

from .geometry import clean_solid

VENDOR = Path(__file__).resolve().parents[1] / "assets/motors"
MOTOR_NAMES = ("5010_rotor", "5010_stator", "sg90_body", "sg90_output_spline")


class MotorLibrary:
    def __init__(self, directory: Path = VENDOR):
        self.directory = directory.resolve()
        path = self.directory / "manifest.json"
        if not path.is_file():
            raise FileNotFoundError(f"Vendored motor assets are missing: {path}. Restore models/assets/motors from the repository.")
        self.manifest = json.loads(path.read_text())

    @lru_cache(maxsize=None)
    def load(self, name: str) -> cq.Shape:
        record = self.manifest["parts"][name]
        path = (self.directory / record["file"]).resolve()
        if not path.is_relative_to(self.directory):
            raise ValueError("Motor manifest points outside its assets directory.")
        data = path.read_bytes()
        if sha256(data).hexdigest() != record["sha256"]:
            raise ValueError(f"Motor asset checksum failed: {name}")
        try:
            raw = lzma.decompress(data)
            if path.name.endswith(".step.xz"):
                with tempfile.TemporaryDirectory(prefix="ria-motor-") as directory:
                    step = Path(directory) / "motor.step"
                    step.write_bytes(raw)
                    shape = cq.importers.importStep(str(step)).val()
            else:
                shape = cq.Shape.importBrep(BytesIO(raw))
        except (lzma.LZMAError, ValueError, RuntimeError) as error:
            raise ValueError(f"Unreadable vendored motor CAD: {name}") from error
        return clean_solid(shape, name)


class SourceArchive:
    """Optional regression input only. The model never builds from this reader."""
    def __init__(self, path: Path):
        self.path = path.resolve()
        self.archive = zipfile.ZipFile(path) if path.is_file() else None
        self.prefix = ""
        if self.archive:
            matches = [name for name in self.archive.namelist()
                       if name.endswith("references/head_neck_reference.step")]
            if len(matches) != 1:
                self.archive.close()
                raise ValueError("Expected one references/head_neck_reference.step in the archive.")
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
