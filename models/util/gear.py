from math import acos, cos, pi, sin, tan
import cadquery as cq
from config import config

def outline(teeth, g, r_root, r_tip):
    pa = g.pressure_angle * pi / 180
    r_pitch = g.module * teeth / 2
    r_base = r_pitch * cos(pa)

    def inv(r):
        a = acos(r_base / r)
        return tan(a) - a

    half = pi / (2 * teeth) + inv(r_pitch)
    start = max(r_base, r_root)
    flank = [start + (r_tip - start) * i / 10 for i in range(11)]
    pts = []
    for tooth in range(teeth):
        c = tooth * 2 * pi / teeth
        left = [(r, c - half + inv(r)) for r in flank]
        right = [(r, c + half - inv(r)) for r in reversed(flank)]
        for r, th in [(r_root, c - half), *left, *right, (r_root, c + half)] if r_root < r_base else [*left, *right]:
            pts.append((r * cos(th), r * sin(th)))
    return cq.Workplane('XY').polyline(pts).close()

def spur_gear(teeth: int, g=config.gears):
    return outline(teeth, g, g.module * (teeth/2 - 1.25), g.module * (teeth/2 + 1)).extrude(g.thickness)

def ring_gear(teeth: int, g, case_r: float):
    return cq.Workplane('XY').circle(case_r).extrude(g.thickness) \
        .cut(outline(teeth, g, g.module * (teeth/2 - 1), g.module * (teeth/2 + 1.25)).extrude(g.thickness))
