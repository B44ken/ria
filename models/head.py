import cadquery as cq
import numpy as np
from trimesh.transformations import rotation_matrix, translation_matrix, concatenate_matrices
from config import config
from util.gear import spur_gear
import pcb
import battery

floor_z = -config.head.height/2 + config.wall/2
X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)

def place(x, y, z, *rots):
    return concatenate_matrices(translation_matrix((x, y, z + floor_z)), *[rotation_matrix(np.radians(a), ax) for a, ax in rots])

_e = config.electronics
# measured battery envelope; the reference asset is 73 x 35 x 28.5 mm.
_battery_scale = np.diag([75/73, 30/35, 35/28.5, 1])
meshes = [('tattu_lipo', place(_e.battery_x, _e.battery_y,
                              _e.shelf_z + _e.plate_t + _e.battery_size[2]/2,
                              (_e.battery_angle, Z), (90, Y), (120, (1, 1, 1)))
           @ _battery_scale @ translation_matrix((0, 0, -14.25)))]


def battery_envelope(clearance=0):
    e = config.electronics
    w, d, h = e.battery_size
    return cq.Workplane('XY').box(w+2*clearance, d+2*clearance, h+2*clearance,
                                  centered=(True, True, False)) \
        .rotate((0, 0, 0), Z, e.battery_angle) \
        .translate((e.battery_x, e.battery_y, floor_z+e.shelf_z+e.plate_t-clearance))


def head_cavity(height):
    h = config.head
    return cq.Workplane('XY').box(h.width - 2*config.wall, h.depth - 2*config.wall, height,
                                  centered=(True, True, False)).edges('|Z').fillet(h.corner_r - config.wall)


def hip_race_blank(clearance=0):
    h = config.head
    return cq.Workplane('YZ', origin=(h.width/2 - config.wall - clearance, 0, h.pivot_height - h.height/2)) \
        .circle(h.race_outer + h.race_wall + clearance).circle(h.race_inner - h.race_wall - clearance) \
        .extrude(config.wall + 2*clearance)


def hip_race_groove():
    h = config.head
    return cq.Workplane('YZ', origin=(h.width/2, 0, h.pivot_height - h.height/2)) \
        .circle(h.race_outer).circle(h.race_inner).extrude(-h.race_depth)


def head_ports():
    h, e = config.head, config.electronics
    usb_x, _ = pcb_xy(pcb.position(pcb.footprints['USB-J1']))
    usb = cq.Workplane('XY').box(e.usb_opening[0], 2*config.wall+4, e.usb_opening[1]) \
        .edges('|Y').fillet(.8).translate((usb_x, -h.depth/2, floor_z+e.pcb_z+pcb.thickness+1.6))
    balance = cq.Workplane('XY').box(e.balance_opening[0], 2*config.wall+4, e.balance_opening[1]) \
        .edges('|Y').fillet(.8).translate((e.balance_x, h.depth/2, floor_z+e.balance_z))
    return usb.union(balance)


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

    inside = head_cavity(config.head.height).translate((0, 0, -config.head.height/2))
    side_z = floor_z + _e.side_screw_z - config.wall/2
    for x, y in _e.posts:
        side = np.sign(x)
        seat = cq.Workplane(cq.Plane(origin=(side*config.head.width/2, y, side_z),
                                    xDir=(0, 1, 0), normal=(side, 0, 0)))
        pad = seat.circle(_e.side_boss_d/2).extrude(-8).cut(inside)
        main = seat.newObject([main.union(pad).val()]).pushPoints([(0, 0)]) \
            .cskHole(_e.screw_d, 5.8, 90, 8)
    
    main = main.union(battery.cable_clip().translate((0, 0, -config.head.height/2)))
    # shallow internal reliefs preserve the original outside dimensions.
    for i in range(2):
        main = main.cut(battery.lead(i, 2.8).translate((0, 0, -config.head.height/2)))
    main = main.cut(battery_envelope(.4).translate((0, 0, -config.wall/2)))
    race = hip_race_blank()
    groove = hip_race_groove()
    return main.union(gear).union(gear.mirror('YZ')) \
        .union(boss).union(boss.mirror('YZ')).union(race).union(race.mirror('YZ')) \
        .cut(groove).cut(groove.mirror('YZ')) \
        .cut(bore).cut(head_ports().translate((0, 0, -config.wall/2)))

def pcb_xy(point):
    a = np.radians(_e.pcb_angle)
    return (point[0]*np.cos(a)-point[1]*np.sin(a), point[0]*np.sin(a)+point[1]*np.cos(a))


def bullet_points():
    # internal tangency, with the offset rotated along with the board.
    return [pcb_xy((x + np.sign(x)*(diameter-_e.bullet_d)/2, y))
            for _, (x, y), diameter in pcb.contacts]


def head_bottom():
    h, e = config.head, config.electronics
    plate = cq.Workplane('XY').box(h.width, h.depth, e.plate_t, centered=(True, True, False)) \
        .edges('|Z').fillet(h.corner_r)
    # build guides in pcb coordinates, then turn them with the board.
    w = (pcb.outline.bounds[2] - pcb.outline.bounds[0])/2
    d = (pcb.outline.bounds[3] - pcb.outline.bounds[1])/2
    for side in (-1, 1):
        rail = cq.Workplane('XY').box(3.2, 2*d + 1.6 - 15, e.pcb_z + pcb.thickness + 2,
                                     centered=(True, True, False)).translate((side*(w + 1), -7.5, e.plate_t))
        slot = cq.Workplane('XY').box(2*w + 2*e.pcb_clearance, 2*d + 4,
                                     pcb.thickness + .4, centered=(True, True, False)) \
            .translate((0, 0, e.plate_t + e.pcb_z))
        plate = plate.union(rail.cut(slot).rotate((0, 0, 0), Z, e.pcb_angle))
        stop = cq.Workplane('XY').box(3.2, .6, e.pcb_z + pcb.thickness,
                                     centered=(True, True, False)).translate((side*(w-1), -d-.6, e.plate_t))
        plate = plate.union(stop.rotate((0, 0, 0), Z, e.pcb_angle))
    # each blind pocket starts exactly at the pcb underside, leaving the floor intact.
    for x, y in bullet_points():
        boss = cq.Workplane('XY').center(x, y).circle(e.bullet_d/2 + 1.6).extrude(e.pcb_z)
        hole = cq.Workplane('XY', origin=(x, y, e.pcb_z)).circle(e.bullet_d/2).extrude(-e.bullet_depth)
        plate = plate.union(boss.cut(hole).translate((0, 0, e.plate_t)))
    for x, y in e.posts:
        post = cq.Workplane('XY').center(x, y).circle(e.post_radius).extrude(e.shelf_z)
        pilot = cq.Workplane('XY', origin=(x, y, e.shelf_z)).circle(e.spacer_pilot_d/2).extrude(-8)
        side = np.sign(x)
        reach = side*h.width/2 - x
        lug = cq.Workplane('XY').box(abs(reach), 7, 7, centered=(True, True, True)) \
            .translate((reach/2 + x, y, e.side_screw_z))
        side_hole = cq.Workplane('YZ', origin=(side*(h.width/2-config.wall), y, e.side_screw_z)) \
            .circle(e.spacer_pilot_d/2).extrude(-side*6)
        post = post.union(lug.intersect(head_cavity(e.shelf_z))).cut(pilot).cut(side_hole)
        plate = plate.union(post.translate((0, 0, e.plate_t)))
    # an m3 x 8 pan-head screw clamps the bare pcb edge after insertion.
    stop = cq.Workplane('XY').center(26.8, 20).circle(3).extrude(e.pcb_z)
    plate = plate.union(stop.translate((0, 0, e.plate_t)))
    pilot = cq.Workplane('XY', origin=(26.8, 20, e.plate_t + e.pcb_z)) \
        .circle(e.spacer_pilot_d/2).extrude(-7)
    relief = cq.Workplane('XY', origin=(26.8, 20, e.plate_t+e.pcb_z+pcb.thickness)) \
        .circle(3).extrude(4)
    plate = plate.cut(pilot).cut(relief)
    wires = cq.Workplane('XY').pushPoints([(-31, 0), (31, 0)]).rect(6, 18).extrude(e.plate_t) \
        .edges('|Z').fillet(1.5)
    plate = plate.cut(wires)
    race = hip_race_blank(h.race_clearance).translate((0, 0, config.wall/2 - floor_z + e.plate_t))
    return plate.cut(race).cut(race.mirror('YZ'))


def battery_tray():
    h, e = config.head, config.electronics
    inset = config.wall + e.tray_clearance
    tray = cq.Workplane('XY').box(h.width-2*inset, h.depth-2*inset, e.plate_t,
                                 centered=(True, True, False)).edges('|Z').fillet(h.corner_r-inset)
    # clear the xt60 column without removing a cradle mounting hole.
    opening = cq.Workplane('XY').box(18, 12, 10).translate((-16.6, 27.975, 0))
    tray = tray.cut(opening)
    guides = cq.Workplane('XY')
    for side in (-1, 1):
        guide = cq.Workplane('XY').box(1.6, 54, 5, centered=(True, True, False)) \
            .translate((side*(e.battery_size[0]/2+e.battery_clearance+.8), 0, e.plate_t))
        end = cq.Workplane('XY').box(3.6, 1.2, 5, centered=(True, True, False)) \
            .translate((side*9, side*(e.battery_size[1]/2+e.battery_clearance+.6), e.plate_t))
        guides = guides.union(guide).union(end)
    guides = guides.rotate((0, 0, 0), Z, e.battery_angle).translate((e.battery_x, e.battery_y, 0))
    tray = tray.union(guides)
    pivot_x = h.width/2+config.gears.thickness-h.pivot_length-.2+2.5
    pivots = cq.Workplane('XY').pushPoints([(-pivot_x, 0), (pivot_x, 0)]).rect(5, 12).extrude(e.plate_t)
    tray = tray.cut(pivots)
    holes = cq.Workplane('XY').pushPoints(e.posts).circle(e.screw_d/2).extrude(e.plate_t)
    return tray.cut(holes)


def head():
    e = config.electronics
    asm = cq.Assembly(name='head')
    asm.add(head_top(), name='head_top', color=cq.Color('white'), loc=cq.Location(cq.Vector(0, 0, config.wall/2)))
    asm.add(head_bottom(), name='head_bottom', color=cq.Color('lightgray'), loc=cq.Location(cq.Vector(0, 0, floor_z-e.plate_t)))
    asm.add(battery_tray(), name='head_tray', color=cq.Color('lightgray'), loc=cq.Location(cq.Vector(0, 0, floor_z+e.shelf_z)))
    asm.add(pcb.substrate().rotate((0, 0, 0), Z, e.pcb_angle), name='control_pcb', color=cq.Color('seagreen'), loc=cq.Location(cq.Vector(0, 0, floor_z+e.pcb_z)))
    for name, shape in pcb.connectors().items():
        asm.add(cq.Workplane(obj=shape).rotate((0, 0, 0), Z, e.pcb_angle), name=name.lower().replace('-', '_'), color=cq.Color('goldenrod'),
                loc=cq.Location(cq.Vector(0, 0, floor_z+e.pcb_z)))
    for i, color in enumerate(('gray20', 'firebrick')):
        asm.add(battery.lead(i), name=f'battery_lead_{i}', color=cq.Color(color),
                loc=cq.Location(cq.Vector(0, 0, floor_z)))
    return asm
