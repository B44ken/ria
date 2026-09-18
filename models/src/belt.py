"""Timing-pulley profiles and an exact two-pulley tangent path.

The belt is a smooth backing envelope, as in the supplied build; its teeth
are not modelled. GT 3 mm groove coordinates come from the archived
rbuckland / droftarts profile. This is not a manufacturer-certified GT3 fit.
"""

from functools import lru_cache
from math import acos, atan2, cos, dist, pi, sin, sqrt

import cadquery as cq
from shapely.affinity import rotate, scale, translate
from shapely.geometry import Point, Polygon

from .config import BeltDrive
from .geometry import Point2, prism

# The archived tooth_profile_GT2_3mm polygon, retained without re-fitting.
GROOVE = (
    (-1.155171, -0.5), (-1.155171, 0), (-1.065317, 0.016448),
    (-0.989057, 0.062001), (-0.932970, 0.130969), (-0.903640, 0.217664),
    (-0.863705, 0.408181), (-0.800056, 0.591388), (-0.713587, 0.765004),
    (-0.605190, 0.926747), (-0.469751, 1.032548), (-0.320719, 1.108119),
    (-0.162625, 1.153462), (0, 1.168577), (0.162625, 1.153462),
    (0.320719, 1.108119), (0.469751, 1.032548), (0.605190, 0.926747),
    (0.713587, 0.765004), (0.800056, 0.591388), (0.863705, 0.408181),
    (0.903640, 0.217664), (0.932921, 0.130969), (0.988924, 0.062001),
    (1.065168, 0.016448), (1.155171, 0), (1.155171, -0.5),
)


@lru_cache(maxsize=8)
def pulley_outline(teeth: int, pitch: float = 3.0) -> tuple[Point2, ...]:
    if pitch != 3.0:
        raise ValueError("The archived groove is for 3 mm pitch only.")
    radius = teeth * pitch / (2 * pi) - 0.381
    tooth_width = 2.31 + 0.10
    groove = scale(Polygon(GROOVE), xfact=tooth_width / 2.31, yfact=1, origin=(0, 0))
    groove = translate(groove, yoff=-sqrt(radius ** 2 - (tooth_width / 2) ** 2) + 0.04)
    outline = Point(0, 0).buffer(radius, quad_segs=teeth * 8)
    for tooth in range(teeth):
        outline = outline.difference(rotate(groove, tooth * 360 / teeth, origin=(0, 0)))
    if not outline.is_valid or outline.geom_type != "Polygon":
        raise ValueError("Timing-pulley outline is not a single valid polygon.")
    return tuple(outline.exterior.coords[:-1])


def timing_pulley(teeth: int, bottom: float, top: float) -> cq.Shape:
    return prism(pulley_outline(teeth), bottom, top)


def belt_path(drive: BeltDrive, samples: int = 180) -> tuple[list[Point2], float]:
    """Return the pitch path and display bow. Default free spans are straight.

    The optional bowed path exists only to reproduce the archived regression
    fixture; it is never used by the current design.
    """
    centres = ((0.0, 0.0), (0.0, drive.centre_distance))
    radii = (drive.knee_pitch_radius, drive.motor_pitch_radius)
    exits: list[Point2] = []
    entries: list[Point2 | None] = [None, None]
    for index in range(2):
        other = 1 - index
        delta = (centres[other][0] - centres[index][0], centres[other][1] - centres[index][1])
        angle = atan2(delta[1], delta[0]) - acos((radii[index] - radii[other]) / drive.centre_distance)
        normal = cos(angle), sin(angle)
        exits.append(tuple(centres[index][axis] + radii[index] * normal[axis] for axis in range(2)))
        entries[other] = tuple(centres[other][axis] + radii[other] * normal[axis] for axis in range(2))

    bow = 0.0
    if drive.model_slack:
        # Legacy-only integration. No length-fitting or optimizer in the new path.
        from scipy.integrate import quad
        from scipy.optimize import brentq
        chord = drive.straight_span
        arc_length = drive.taut_pitch_length - 2 * chord
        def bowed_length(height: float) -> float:
            span = quad(lambda t: sqrt(chord ** 2 + (height * pi * sin(2 * pi * t)) ** 2), 0, 1)[0]
            return arc_length + 2 * span
        bow = brentq(lambda height: bowed_length(height) - drive.stock_pitch_length, 0, 12)

    points: list[Point2] = []
    for index in range(2):
        entry, exit = entries[index], exits[index]
        start = atan2(entry[1] - centres[index][1], entry[0] - centres[index][0])
        end = atan2(exit[1] - centres[index][1], exit[0] - centres[index][0])
        sweep = (end - start) % (2 * pi)
        for sample in range(samples):
            angle = start + sweep * sample / (samples - 1)
            points.append((centres[index][0] + radii[index] * cos(angle),
                           centres[index][1] + radii[index] * sin(angle)))
        next_entry = entries[1 - index]
        dx, dy = next_entry[0] - exit[0], next_entry[1] - exit[1]
        chord = dist(exit, next_entry)
        for sample in range(1, samples):
            fraction = sample / samples
            offset = bow * sin(pi * fraction) ** 2
            points.append((exit[0] + fraction * dx + offset * dy / chord,
                           exit[1] + fraction * dy - offset * dx / chord))
    return points, bow


def belt_envelope(drive: BeltDrive) -> cq.Shape:
    path, _ = belt_path(drive)
    region = Polygon(path)
    outside = region.buffer(0.909, quad_segs=16)
    inside = region.buffer(-0.371, quad_segs=16)
    midplane = 27.6
    bottom, top = midplane - drive.width / 2, midplane + drive.width / 2
    return prism(outside.exterior.coords[:-1], bottom, top).cut(
        prism(inside.exterior.coords[:-1], bottom - 0.1, top + 0.1))
