from math import pi, sqrt
import cadquery as cq
from shapely import Point, Polygon
from shapely.affinity import rotate, scale, translate
from config import config

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

def sprocket(teeth: int):
    b = config.belt
    r, w = teeth * b.pitch / (2 * pi) - 0.381, 2.31 + 0.10
    groove = scale(Polygon(GROOVE), xfact=w / 2.31, yfact=1, origin=(0, 0))
    groove = translate(groove, yoff=0.04 - sqrt(r**2 - (w / 2)**2))
    outline = Point(0, 0).buffer(r, quad_segs=teeth * 8)
    for tooth in range(teeth):
        outline = outline.difference(rotate(groove, tooth * 360 / teeth, origin=(0, 0)))
    return cq.Workplane('XY').polyline(outline.exterior.coords[:-1]).close().extrude(b.band)

def belt(dist: float, r_top: float, r_bottom: float):
    b = config.belt
    path = Point(0, 0).buffer(r_top, quad_segs=64).union(Point(0, -dist).buffer(r_bottom, quad_segs=64)).convex_hull
    return cq.Workplane('XY').polyline(path.buffer(b.back).exterior.coords[:-1]).close().extrude(b.belt_height) \
        .cut(cq.Workplane('XY').polyline(path.buffer(-b.tooth).exterior.coords[:-1]).close().extrude(b.belt_height))
