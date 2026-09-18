"""Small, explicit CAD primitives in a common XY / Z coordinate system."""

from math import cos, pi, sin, sqrt
from typing import Iterable

import cadquery as cq

Point2 = tuple[float, float]
Point3 = tuple[float, float, float]


def box(width: float, depth: float, height: float,
        centre: Point3 = (0, 0, 0)) -> cq.Shape:
    return cq.Workplane("XY").box(width, depth, height).translate(centre).val()


def cylinder(radius: float, bottom: float, top: float,
             centre: Point2 = (0, 0)) -> cq.Shape:
    if top <= bottom or radius <= 0:
        raise ValueError("A cylinder requires positive radius and height.")
    return cq.Solid.makeCylinder(radius, top - bottom,
                                 cq.Vector(*centre, bottom), cq.Vector(0, 0, 1))


def annulus(outer: float, inner: float, bottom: float, top: float,
            centre: Point2 = (0, 0)) -> cq.Shape:
    return cylinder(outer, bottom, top, centre).cut(
        cylinder(inner, bottom - 0.1, top + 0.1, centre))


def prism(points: Iterable[Point2], bottom: float, top: float) -> cq.Shape:
    return (cq.Workplane("XY").polyline(list(points)).close()
            .extrude(top - bottom).translate((0, 0, bottom)).val())


def hex_socket(across_flats: float, bottom: float, top: float,
               centre: Point2 = (0, 0)) -> cq.Shape:
    radius = across_flats / sqrt(3)
    points = [(centre[0] + radius * cos(2 * pi * i / 6),
               centre[1] + radius * sin(2 * pi * i / 6)) for i in range(6)]
    return prism(points, bottom, top)


def along_axis(radius: float, start: Point3, length: float,
               direction: Point3) -> cq.Shape:
    return cq.Solid.makeCylinder(radius, length, cq.Vector(*start), cq.Vector(*direction))


def bounds(shape: cq.Shape) -> list[list[float]]:
    value = shape.BoundingBox()
    return [[value.xmin, value.ymin, value.zmin],
            [value.xmax, value.ymax, value.zmax]]


def clean_solid(shape: cq.Shape, name: str, single: bool = False) -> cq.Shape:
    shape = shape.clean()
    if not shape.isValid() or shape.Volume() <= 0:
        raise ValueError(f"Invalid CAD shape: {name}")
    if single and len(shape.Solids()) != 1:
        raise ValueError(f"Printable {name} must be one connected solid.")
    return shape
