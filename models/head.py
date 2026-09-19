import cadquery as cq
import numpy as np
from trimesh.transformations import rotation_matrix, translation_matrix, concatenate_matrices
from config import config
from util.gear import spur_gear

floor_z = -config.head.height/2 + config.wall/2
X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)

def place(x, y, z, *rots):
    return concatenate_matrices(translation_matrix((x, y, z + floor_z)), *[rotation_matrix(np.radians(a), ax) for a, ax in rots])

_e = config.electronics
_smini = place(0, _e.fin_y - _e.fin_t/2 - _e.standoff, _e.smini_z, (180, Z), (-90, X))
meshes = [
    ('simplefocmini_dual', _smini),
    ('simplefocmini_dual', concatenate_matrices(rotation_matrix(np.pi, Z), _smini)),
    ('tca9548a', place(*_e.tca_loc, _e.standoff, (90, Z))),
    ('mp1584', place(*_e.mp_loc, 0)),
    ('tattu_lipo', place(0, 0, _e.lipo_z, (90, Z))),
    ('pipico', place(*_e.pico_loc, (120, (1, 1, 1)))),
]

def head_top():
    pivot_z = config.head.pivot_height - config.head.height/2

    main = cq.Workplane('XY') \
        .box(config.head.width, config.head.depth, config.head.height) \
        .edges("|Z").fillet(config.head.corner_r) \
        .faces('<Z').shell(-config.wall)

    gear = spur_gear(config.gears.teeth_head).rotate((0, 0, 0), (0, 1, 0), 90) \
        .translate((config.head.width/2, 0, pivot_z))

    outside = config.head.width/2 + config.gears.thickness

    bearing_r = cq.Workplane('YZ') \
        .cylinder(config.head.bearing_depth, config.head.bearing_od/2 + config.press_fit) \
        .translate((outside - config.head.bearing_depth/2, 0, pivot_z))

    bearing_l = cq.Workplane('YZ') \
        .cylinder(config.head.bearing_depth, config.head.bearing_od/2 + config.press_fit) \
        .translate((-outside + config.head.bearing_depth/2, 0, pivot_z))

    bore = cq.Workplane('YZ') \
        .cylinder(2*outside + 2, config.head.bearing_id/2 + config.press_fit) \
        .translate((0, 0, pivot_z))
    
    return main.union(gear).union(gear.mirror('YZ')) \
        .cut(bearing_r).cut(bearing_l).cut(bore)

def head_bottom():
    e, h = config.electronics, config.head
    floor = cq.Workplane('XY', origin=(0, 0, config.wall/2))
    plate = cq.Workplane('XY').box(h.width, h.depth, config.wall).edges('|Z').fillet(h.corner_r)
    fin_a = floor.center(0, e.fin_y).rect(e.fin_len, e.fin_t).extrude(e.fin_h)
    fin_b = floor.rect(e.fin_b_len, e.fin_b_t).extrude(e.fin_h)
    smini_pts = [(sx*e.smini_holes[0], e.smini_z + sz*e.smini_holes[1]) for sx in (-1, 1) for sz in (-1, 1)]
    smini_face = e.fin_y - e.fin_t/2
    smini_standoffs = cq.Workplane('XZ', origin=(0, smini_face, config.wall/2)).pushPoints(smini_pts).circle(e.standoff_dia/2).extrude(e.standoff)
    side_holes = cq.Workplane('XZ', origin=(0, smini_face - e.standoff, config.wall/2)).pushPoints(smini_pts).circle(config.m3_dia/2).extrude(-e.tap_depth)
    tca_pts = [(e.tca_loc[0] + s*e.tca_holes, e.tca_loc[1]) for s in (-1, 1)]
    tca_standoffs = floor.pushPoints(tca_pts).circle(e.standoff_dia/2).extrude(e.standoff)
    tca_holes = cq.Workplane('XY', origin=(0, 0, config.wall/2 + e.standoff)).pushPoints(tca_pts).circle(config.m3_dia/2).extrude(-e.tap_depth)
    pico_pts = [(e.pico_loc[0] + z, e.pico_loc[1] + x) for x, z in e.pico_holes]
    pico_strip = floor.center(0, e.pico_loc[1] + e.pico_w/2).rect(h.width, e.pico_w - 2*e.pico_header).extrude(e.pico_standoff)
    pico_standoffs = floor.pushPoints(pico_pts).circle(e.pico_standoff_dia/2).extrude(e.pico_standoff).intersect(pico_strip)
    pico_holes = cq.Workplane('XY', origin=(0, 0, config.wall/2 + e.pico_standoff)).pushPoints(pico_pts).circle(config.m2_dia/2).extrude(-e.tap_depth)
    axle = cq.Workplane('YZ', origin=(0, 0, config.wall/2 + h.pivot_height)).circle(h.bearing_id/2 + config.press_fit).extrude(h.width, both=True)
    slab = floor.rect(h.width, h.depth).extrude(e.fin_h)
    side = fin_a.union(smini_standoffs).intersect(slab)
    return plate.union(side).union(side.rotate((0, 0, 0), (0, 0, 1), 180)) \
        .union(fin_b).union(tca_standoffs).union(pico_standoffs) \
        .cut(side_holes).cut(side_holes.rotate((0, 0, 0), (0, 0, 1), 180)) \
        .cut(tca_holes).cut(pico_holes).cut(axle)

def head():
    asm = cq.Assembly(name='head')
    asm.add(head_top(), name='head_top', color=cq.Color('white'), loc=cq.Location(cq.Vector(0, 0, config.wall/2)))
    asm.add(head_bottom(), name='head_bottom', color=cq.Color('lightgray'), loc=cq.Location(cq.Vector(0, 0, -config.head.height/2)))
    return asm