from pathlib import Path

import cadquery as cq
import trimesh
from shapely.geometry import Point, box
import numpy as np
from trimesh.transformations import rotation_matrix, translation_matrix, concatenate_matrices
from config import config
from util.gear import spur_gear

floor_z = -config.head.height/2 + config.wall/2
X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)

def place(x, y, z, *rots):
    return concatenate_matrices(translation_matrix((x, y, z + floor_z)), *[rotation_matrix(np.radians(a), ax) for a, ax in rots])

_e = config.electronics
tray_z = _e.spacer_h + _e.plate_t
# correct the reference assets to the measured 44 x 21 x 10 and 75 x 35 x 30 mm.
_driver_scale = np.diag([1, 21/24, 10/10.55, 1])
_battery_scale = np.diag([75/73, 1, 30/28.5, 1])
meshes = [
    ('simplefocmini_dual', place(-_e.driver_x, _e.driver_y, 0, (90, Z)) @ _driver_scale),
    ('simplefocmini_dual', place(_e.driver_x, _e.driver_y, 0, (-90, Z)) @ _driver_scale),
    ('tca9548a', place(*_e.tca_loc, tray_z)),
    ('mp1584', place(*_e.mp_loc, tray_z)),
    ('xt60h_m', place(*_e.xt60_loc, tray_z)),
    ('tattu_lipo', place(-15.4, 0, 17.5, (120, (1, 1, 1))) @ _battery_scale),
    # the asset's usb opening is at (10.5, 1.75, -52.3); rear is -y.
    ('pipico', place(*_e.pico_loc, tray_z + 9.5, (180, Z), (90, X))),
    ('mpu6050', place(*_e.imu_loc, tray_z)),
]

def head_cavity(height):
    h = config.head
    return cq.Workplane('XY').box(h.width - 2*config.wall, h.depth - 2*config.wall, height,
                                  centered=(True, True, False)).edges('|Z').fillet(h.corner_r - config.wall)


def head_top():
    pivot_z = config.head.pivot_height - config.head.height/2

    main = cq.Workplane('XY') \
        .box(config.head.width, config.head.depth, config.head.height) \
        .edges("|Z").fillet(config.head.corner_r) \
        .faces('<Z').shell(-config.wall)

    gear = spur_gear(config.gears.teeth_head).rotate((0, 0, 0), (0, 1, 0), 90) \
        .translate((config.head.width/2, 0, pivot_z))

    outside = config.head.width/2 + config.gears.thickness

    # total support length includes the gear and shell wall.
    boss = cq.Workplane('YZ', origin=(outside - config.head.pivot_length, 0, pivot_z)) \
        .circle(config.head.pivot_boss_d/2).extrude(config.head.pivot_length)

    bore = cq.Workplane('YZ') \
        .cylinder(2*outside + 2, config.head.pivot_d/2) \
        .translate((0, 0, pivot_z))

    usb = cq.Workplane('XY').box(_e.usb_opening[0], 2*config.wall + 4, _e.usb_opening[1]) \
        .translate((0, -config.head.depth/2, floor_z + tray_z + 11.25 - config.wall/2))

    sx, sy, sz = _e.battery_screw_loc
    clamp_access = cq.Workplane('YZ', origin=(config.head.width/2, sy, floor_z + sz - config.wall/2)) \
        .circle(2).extrude(-config.wall)

    inside = head_cavity(config.head.height).translate((0, 0, -config.head.height/2))
    side_z = floor_z + _e.side_screw_z - config.wall/2
    for x, y in _e.posts:
        side = np.sign(x)
        seat = cq.Workplane('YZ', origin=(side*(config.head.width/2 + 0.5), y, side_z))
        pad = seat.circle(_e.side_boss_d/2).extrude(-side*8).cut(inside)
        clearance = seat.circle(_e.screw_d/2).extrude(-side*8)
        main = main.union(pad).cut(clearance)
    
    return main.union(gear).union(gear.mirror('YZ')) \
        .union(boss).union(boss.mirror('YZ')).cut(bore).cut(usb).cut(clamp_access)

def tray_outline():
    h, e = config.head, config.electronics
    inset = config.wall + e.tray_clearance
    return h.width - 2*inset, h.depth - 2*inset, h.corner_r - inset


def board_hole_points(upper=False):
    e = config.electronics
    names = ('pipico', 'mpu6050', 'tca9548a', 'mp1584') if upper else ('simplefocmini_dual',)
    footprints = []
    for name, transform in meshes:
        if name in names:
            mesh = trimesh.load(Path(__file__).parent / 'assets' / f'{name}.glb').to_mesh()
            lo, hi = mesh.apply_scale(1000).apply_transform(transform).bounds
            footprints.append(box(*lo[:2], *hi[:2]).buffer(-e.hole_d/2))
    w, d, r = tray_outline()
    interior = box(-w/2+r, -d/2+r, w/2-r, d/2-r).buffer(r).buffer(-2-e.hole_d/2)
    exclusions = [Point(x, y).buffer(5+e.hole_d/2) for x, y in e.posts]
    if upper:
        exclusions += [box(x-sw/2, y-sd/2, x+sw/2, y+sd/2).buffer(.8+e.hole_d/2)
                       for (x, y), (sw, sd) in e.wiring_bays]
    return [(x*e.hole_pitch, y*e.hole_pitch)
            for x in range(-int(w/2/e.hole_pitch), int(w/2/e.hole_pitch)+1)
            for y in range(-int(d/2/e.hole_pitch), int(d/2/e.hole_pitch)+1)
            if interior.covers(point := Point(x*e.hole_pitch, y*e.hole_pitch))
            and any(footprint.covers(point) for footprint in footprints)
            and not any(exclusion.covers(point) for exclusion in exclusions)]


def electronics_plate(width, depth, radius, cutaway=False):
    e = config.electronics
    outline = cq.Workplane('XY').rect(width, depth).val()
    outline = outline.fillet2D(radius, outline.Vertices())
    holes = cq.Workplane('XY').pushPoints(board_hole_points(upper=cutaway)).circle(e.hole_d/2).vals()
    holes += cq.Workplane('XY').pushPoints(e.posts).circle(e.screw_d/2).vals()
    if cutaway:
        for loc, size in e.wiring_bays:
            opening = cq.Workplane('XY').center(*loc).rect(*size).val()
            holes.append(opening.fillet2D(e.wiring_bay_r, opening.Vertices()))
    return cq.Workplane(obj=cq.Solid.extrudeLinear(outline, holes, (0, 0, e.plate_t)))


def battery_guides():
    # a continuous rear wall joins the corner fences; heights start at the floor.
    guides = cq.Workplane('XY').box(34, 1.6, _e.battery_back_h, centered=(True, True, False)) \
        .translate((0, -38.5, 0))
    for side in (-1, 1):
        for end in (-1, 1):
            if end > 0:
                guides = guides.union(cq.Workplane('XY').box(7, 1.4, 10, centered=(True, True, False))
                                      .translate((side*13.5, 38.6, 0)))
            y0, y1 = (25, 37.9) if end > 0 else (-37.9, -25)
            if side > 0 and end < 0:
                y1 = -36
            guides = guides.union(cq.Workplane('XY').box(1.6, y1-y0, 12, centered=(True, True, False))
                                  .translate((side*16.2, (y0+y1)/2, 0)))
    # the shoe rests on the floor between two guide rails. its ears meet the stops.
    for y in (-35.4, -21.6):
        guides = guides.union(cq.Workplane('XY').box(4, 1.2, 4, centered=(True, True, False))
                              .translate((18.4, y, 0)))
    for y in (-34, -23):
        guides = guides.union(cq.Workplane('XY').box(1, 1, 2, centered=(True, True, False))
                              .translate((16.9, y, 0)))
    x, y, z = _e.battery_screw_loc
    boss = cq.Workplane('XY').box(6, 8, 14, centered=(True, True, False)) \
        .translate((x-3, y, 0))
    pilot = cq.Workplane('YZ', origin=(x, y, z)).circle(_e.spacer_pilot_d/2).extrude(-6)
    return guides.union(boss.cut(pilot))


def battery_shoe(opening=0):
    # the rounded printed face contacts the pack; keep the screw seat and stops fixed.
    face = cq.Workplane('XY').box(_e.battery_shoe_t, 10, 14, centered=(True, True, False)) \
        .faces('<X').edges().fillet(.4).translate((17.4-_e.battery_shoe_t/2, -28.5, 0))
    foot = cq.Workplane('XY').box(2.2, 12, 2, centered=(True, True, False)).translate((18.5, -28.5, 0))
    _, y, z = _e.battery_screw_loc
    socket = cq.Workplane('YZ', origin=(17.4, y, z)).circle(1.7).extrude(-.7)
    return face.union(foot).cut(socket).translate((opening, 0, 0))


def head_bottom():
    h = config.head
    plate = electronics_plate(h.width, h.depth, h.corner_r)
    return plate.union(battery_guides().translate((0, 0, _e.plate_t)))


def head_tray():
    return electronics_plate(*tray_outline(), cutaway=True)


def tray_spacer(x_sign=1, y_sign=1):
    e = config.electronics
    x, y = e.posts[-1]
    # a 45-degree underside supports the projecting boss when printed upright.
    reach = config.head.width/2 - x
    boss = cq.Workplane('XZ').polyline([(0, e.side_screw_z - reach - e.side_boss_d/2),
                                       (reach, e.side_screw_z - e.side_boss_d/2),
                                       (reach, e.side_screw_z + e.side_boss_d/2),
                                       (0, e.side_screw_z + e.side_boss_d/2)]).close() \
        .extrude(e.side_boss_d/2, both=True)
    boss = boss.intersect(head_cavity(e.spacer_h).translate((-x, -y, 0)))
    side_pilot = cq.Workplane('YZ', origin=(reach - config.wall, 0, e.side_screw_z)) \
        .circle(e.spacer_pilot_d/2).extrude(-e.spacer_pilot_depth)
    spacer = cq.Workplane('XY').circle(e.spacer_d/2).extrude(e.spacer_h) \
        .union(boss).cut(side_pilot) \
        .faces('>Z').workplane().hole(e.spacer_pilot_d, e.spacer_pilot_depth) \
        .faces('<Z').workplane().hole(e.spacer_pilot_d, e.spacer_pilot_depth)
    if x_sign < 0:
        spacer = spacer.mirror('YZ')
    if y_sign < 0:
        spacer = spacer.mirror('XZ')
    return spacer


def head():
    e = config.electronics
    asm = cq.Assembly(name='head')
    asm.add(head_top(), name='head_top', color=cq.Color('white'), loc=cq.Location(cq.Vector(0, 0, config.wall/2)))
    asm.add(head_bottom(), name='head_bottom', color=cq.Color('lightgray'), loc=cq.Location(cq.Vector(0, 0, floor_z - e.plate_t)))
    asm.add(head_tray(), name='head_tray', color=cq.Color('lightgray'), loc=cq.Location(cq.Vector(0, 0, floor_z + e.spacer_h)))
    asm.add(battery_shoe(), name='battery_shoe', color=cq.Color('orange'),
            loc=cq.Location(cq.Vector(0, 0, floor_z)))
    for i, (x, y) in enumerate(e.posts):
        asm.add(tray_spacer(np.sign(x), np.sign(y)), name=f'tray_spacer_{i}', color=cq.Color('gray'),
                loc=cq.Location(cq.Vector(x, y, floor_z)))
    return asm
