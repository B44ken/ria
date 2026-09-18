"""Named CAD parts, without filesystem or rendering side effects."""

from dataclasses import dataclass, field
from typing import Literal

import cadquery as cq

from .geometry import Point2, clean_solid

Motion = Literal["fixed", "carrier", "sun", "planet", "motor", "context"]

# Display colours follow the supplied model, not material specifications.
COLOURS = {
    "purple": (0.36, 0.20, 0.64), "cyan": (0.18, 0.62, 0.75),
    "orange": (0.98, 0.44, 0.08), "yellow": (0.98, 0.72, 0.12),
    "blue": (0.04, 0.15, 0.45), "steel": (0.50, 0.56, 0.62),
    "dark": (0.065, 0.075, 0.095), "belt": (0.07, 0.075, 0.09),
    "copper": (0.60, 0.27, 0.11), "head": (0.76, 0.80, 0.84),
}


@dataclass
class Part:
    name: str
    shape: cq.Shape
    material: str = "purple"
    motion: Motion = "fixed"
    centre: Point2 = (0, 0)
    print_quantity: int = 0
    note: str = ""
    archived_name: str = ""


@dataclass
class Model:
    parts: list[Part] = field(default_factory=list)
    intentional_fits: list[dict] = field(default_factory=list)

    def add(self, name: str, shape: cq.Shape, **metadata) -> Part:
        if any(part.name == name for part in self.parts):
            raise ValueError(f"Duplicate part name: {name}")
        shape = clean_solid(shape, name, single=bool(metadata.get("print_quantity")))
        part = Part(name, shape, **metadata)
        self.parts.append(part)
        return part

    def by_name(self) -> dict[str, Part]:
        return {part.name: part for part in self.parts}

    def fit(self, first: str, second: str, reason: str) -> None:
        self.intentional_fits.append({"parts": [first, second], "reason": reason})

    def assembly(self, name: str) -> cq.Assembly:
        assembly = cq.Assembly(name=name)
        for part in self.parts:
            assembly.add(part.shape, name=part.name, color=cq.Color(*COLOURS[part.material]))
        return assembly
