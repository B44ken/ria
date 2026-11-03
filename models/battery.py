"""two 70 mm battery leads, routed with >=8 mm bends and a straight 13 mm tail."""
import cadquery as cq
import numpy as np
from scipy.interpolate import BSpline
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCP.Geom import Geom_BSplineCurve
from OCP.gp import gp_Pnt
from OCP.TColgp import TColgp_Array1OfPnt
from OCP.TColStd import TColStd_Array1OfReal, TColStd_Array1OfInteger

# cubic control points in mm from the bottom's inside face; the pack is rolled 90 degrees and yawed 80 degrees.
poles = np.array([
    [
        [-34.325568, 15.283923, 36.3],
        [-38.848063, 19.078747, 36.3],
        [-38.737498, 28.823103, 42.481599],
        [-35.298838, 34.241612, 52.708654],
        [-25.836513, 34.928448, 54.984729],
        [-18.547292, 31.751862, 49.285582],
        [-20.2, 27.975, 42.228276],
        [-20.2, 27.975, 36.6],
    ],
    [
        [-34.325568, 15.283923, 41.1],
        [-38.258666, 18.584184, 41.1],
        [-39.431273, 26.385427, 47.727772],
        [-34.492018, 29.867504, 54.6359],
        [-24.816159, 29.95067, 55.354014],
        [-16.649927, 28.561406, 54.54536],
        [-13, 27.975, 47.03992],
        [-13, 27.975, 36.6],
    ],
])
knots = [0, .2, .4, .6, .8, 1]
mults = [4, 1, 1, 1, 1, 4]
curves = [BSpline(np.repeat(knots, mults), points, 3) for points in poles]


def path(index):
    points = TColgp_Array1OfPnt(1, 8)
    values = TColStd_Array1OfReal(1, 6)
    counts = TColStd_Array1OfInteger(1, 6)
    for i, point in enumerate(poles[index], 1):
        points.SetValue(i, gp_Pnt(*point))
    for i, (knot, count) in enumerate(zip(knots, mults), 1):
        values.SetValue(i, knot)
        counts.SetValue(i, count)
    curve = Geom_BSplineCurve(points, values, counts, 3)
    bend = cq.Edge(BRepBuilderAPI_MakeEdge(curve).Edge())
    tail = cq.Edge.makeLine(bend.endPoint(), bend.endPoint() + cq.Vector(0, 0, -13))
    return cq.Wire.assembleEdges([bend, tail])


def lead(index, radius=2.25):
    plane = cq.Plane(origin=tuple(poles[index, 0]), normal=tuple(curves[index](0, nu=1)))
    return cq.Workplane(plane).circle(radius).sweep(path(index), isFrenet=False)


def cable_clip():
    # a roof saddle at x=-30 captures both leads beside the battery.
    centers = [curves[i](u)[[1, 2]] for i, u in enumerate((0.511485065023, 0.490668950859))]
    plane = cq.Plane(origin=(-30, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0))
    outer = cq.Workplane(plane).center(*centers[0]).circle(3.9).extrude(2, both=True)
    outer = outer.union(cq.Workplane(plane).center(*centers[1]).circle(3.9).extrude(2, both=True))
    bores = lead(0, 2.8).union(lead(1, 2.8))
    y, z = centers[0]
    mouth = cq.Workplane(plane).center(y, z-5).rect(4, 10).extrude(3, both=True)
    return outer.cut(bores).cut(mouth)
