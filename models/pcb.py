"""mechanical references read from the control board; rear is -y."""
from functools import cache
from pathlib import Path

import cadquery as cq
import numpy as np
import sexpdata
from shapely.geometry import LineString
from shapely.ops import polygonize

folder = Path(__file__).resolve().parents[1] / 'pcb'
board = sexpdata.loads((folder / 'ria.kicad_pcb').read_text())


def entries(node, key):
    return [v for v in node if isinstance(v, list) and v and str(v[0]) == key]


def value(node, key):
    return entries(node, key)[0][1:]


edges = [g for g in entries(board, 'gr_line') if value(g, 'layer') == ['Edge.Cuts']]
outline = next(iter(polygonize([LineString([value(g, 'start'), value(g, 'end')]) for g in edges])))
cy = (outline.bounds[1] + outline.bounds[3])/2
# center on the board bounding box, including its front notch.
cx = (outline.bounds[0] + outline.bounds[2])/2
thickness = value(entries(board, 'general')[0], 'thickness')[0]
footprints = {next(p[2] for p in entries(f, 'property') if p[1] == 'Reference'): f
              for f in entries(board, 'footprint')}


def xy(point):
    return point[0] - cx, cy - point[1]


def position(footprint, point=(0, 0)):
    transform = entries(footprint, 'transform')[0]
    x, y = value(transform, 'translate')
    a = np.radians(value(transform, 'rotate')[0])
    px, py = point
    return xy((x + px*np.cos(a) + py*np.sin(a), y - px*np.sin(a) + py*np.cos(a)))


contacts = [(ref, position(f, value(p, 'at')[:2]), value(p, 'drill')[0])
            for ref, f in footprints.items() if ref in {f'MOTOR-J{i}' for i in range(3, 9)}
            for p in entries(f, 'pad')]


def substrate():
    shape = cq.Workplane('XY').polyline([xy(p) for p in outline.exterior.coords[:-1]]).close().extrude(thickness)
    for f in footprints.values():
        for pad in entries(f, 'pad'):
            drills = entries(pad, 'drill')
            if drills and isinstance(drills[0][1], (int, float)):
                shape = shape.cut(cq.Workplane('XY').center(*position(f, value(pad, 'at')[:2]))
                                  .circle(drills[0][1]/2).extrude(thickness))
    return shape


@cache
def step(name):
    return cq.importers.importStep(str(folder / '3dmodels/ria.3dshapes' / name)).val()


def connectors():
    # the tall connectors determine the shelf clearance. usb has no supplied step model.
    result = {}
    for ref, f in footprints.items():
        if ref.startswith(('ENC-J', 'SERVO-J')) or ref in ('MOTOR-J1', 'MOTOR-J2', 'POWER-J1', 'ESP-U1'):
            model = entries(f, 'model')[0]
            shape = step(Path(model[1]).name)
            offset = value(entries(model, 'offset')[0], 'xyz')
            angle = value(entries(f, 'transform')[0], 'rotate')[0]
            result[ref] = shape.translate(tuple(offset)).rotate((0, 0, 0), (0, 0, 1), angle) \
                .translate((*position(f), thickness))
    f = footprints['USB-J1']
    result['USB-J1'] = cq.Workplane('XY').box(8.94, 7.3, 3.2, centered=(True, True, False)) \
        .translate((*position(f, (0, 1.319097)), thickness)).val()
    return result
