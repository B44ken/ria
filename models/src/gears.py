"""Involute outlines with the archive's sampling and backlash convention.

External teeth lose `backlash` at the pitch circle; the internal void gains it.
Keeping the original 20 flank intervals and 5 tip intervals also permits a
geometry-level regression against the supplied build, not just a visual match.
"""

from math import acos, cos, dist, pi, radians, sin, sqrt

from .config import GearTrain, HipGears
from .geometry import Point2

FLANK_INTERVALS = 20
TIP_INTERVALS = 5


def involute_angle(radius: float, base_radius: float) -> float:
    return sqrt(max(0.0, (radius / base_radius) ** 2 - 1)) - acos(min(1.0, base_radius / radius))


def polar(radius: float, angle: float) -> Point2:
    return radius * cos(angle), radius * sin(angle)


def without_duplicate_vertices(points: list[Point2]) -> list[Point2]:
    return [point for i, point in enumerate(points) if dist(point, points[i - 1]) > 1e-8]


def external_profile(teeth: int, train: GearTrain | HipGears, *,
                     flank_intervals: int = FLANK_INTERVALS,
                     tip_intervals: int = TIP_INTERVALS) -> list[Point2]:
    pitch = teeth * train.module / 2
    base = pitch * cos(radians(train.pressure_angle))
    root = pitch - 1.25 * train.module
    tip = pitch + train.module
    flank_start = max(base, root)
    half_tooth = pi / (2 * teeth) - train.backlash / (2 * pitch)
    pitch_involute = involute_angle(pitch, base)
    root_angle = half_tooth + pitch_involute - involute_angle(flank_start, base)
    tip_angle = half_tooth + pitch_involute - involute_angle(tip, base)
    points: list[Point2] = []

    for tooth in range(teeth):
        centre = tooth * 2 * pi / teeth
        points.extend((polar(root, centre - pi / teeth), polar(root, centre - root_angle)))
        for sample in range(flank_intervals + 1):
            radius = flank_start + (tip - flank_start) * sample / flank_intervals
            angle = centre - half_tooth - pitch_involute + involute_angle(radius, base)
            points.append(polar(radius, angle))
        for sample in range(1, tip_intervals + 1):
            angle = centre - tip_angle + 2 * tip_angle * sample / tip_intervals
            points.append(polar(tip, angle))
        for sample in range(1, flank_intervals + 1):
            radius = tip - (tip - flank_start) * sample / flank_intervals
            angle = centre + half_tooth + pitch_involute - involute_angle(radius, base)
            points.append(polar(radius, angle))
        points.append(polar(root, centre + root_angle))
    return without_duplicate_vertices(points)


def internal_void_profile(train: GearTrain) -> list[Point2]:
    """Region removed from the fixed ring, including its tooth spaces."""
    teeth = train.ring_teeth
    pitch = teeth * train.module / 2
    base = pitch * cos(radians(train.pressure_angle))
    tip = pitch - train.module
    root = pitch + 1.25 * train.module
    half_space = pi / (2 * teeth) + train.backlash / (2 * pitch)
    pitch_involute = involute_angle(pitch, base)
    tip_angle = half_space + pitch_involute - involute_angle(tip, base)
    root_angle = half_space + pitch_involute - involute_angle(root, base)
    points: list[Point2] = []

    for tooth in range(teeth):
        centre = tooth * 2 * pi / teeth
        points.extend((polar(tip, centre - pi / teeth), polar(tip, centre - tip_angle)))
        for sample in range(FLANK_INTERVALS + 1):
            radius = tip + (root - tip) * sample / FLANK_INTERVALS
            angle = centre - half_space - pitch_involute + involute_angle(radius, base)
            points.append(polar(radius, angle))
        for sample in range(1, TIP_INTERVALS + 1):
            angle = centre - root_angle + 2 * root_angle * sample / TIP_INTERVALS
            points.append(polar(root, angle))
        for sample in range(1, FLANK_INTERVALS + 1):
            radius = root - (root - tip) * sample / FLANK_INTERVALS
            angle = centre + half_space + pitch_involute - involute_angle(radius, base)
            points.append(polar(radius, angle))
    return without_duplicate_vertices(points)
