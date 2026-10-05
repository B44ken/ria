import cadquery as cq
from config import config
from util.gear import spur_gear
from transmission import sprocket_upper, belt
from planetary import sun, pulley, planets, ring
from hardware import knee_screws, knee_bearings
from lowerleg import lower_leg, wheel, ankle_z, ankle_board_z
from trimesh.transformations import rotation_matrix, translation_matrix, concatenate_matrices
from math import radians

centre = config.gears.module * (config.gears.teeth_head + config.gears.teeth_pinion) / 2

def upper_leg():
    l, e, p = config.leg, config.encoder, config.planetary
    pilots = [(0, -centre + offset) for offset in l.servo_pilots]
    tab = cq.Workplane('XY').center(0, l.hip_pad_y/2).rect(l.hip_pad_d, l.hip_pad_y).extrude(l.thickness) \
        .union(cq.Workplane('XY').center(0, l.hip_pad_y).circle(l.hip_pad_d/2).extrude(l.thickness)) \
        .faces('>Z').workplane(origin=(0, 0, l.thickness)).pushPoints([(0, l.hip_pad_y)]).cskHole(3.2, 5.8, 90)
    return cq.Workplane('XY').circle(l.mount_r).extrude(l.thickness) \
        .union(cq.Workplane('XY').center(0, -l.length/2).slot2D(l.length + l.width, l.width, 90).extrude(l.thickness)) \
        .union(cq.Workplane('XY').center(0, -l.length).circle(16.5).extrude(l.thickness)) \
        .faces('<Z').workplane().pushPoints(l.motor_holes).cskHole(config.m3_dia, config.m3_csink_dia, 90) \
        .faces('<Z').workplane().pushPoints([(x, l.length - y) for x, y in p.mounts]).cskHole(config.m3_dia + 0.2, 6.3, 90) \
        .faces('>Z').workplane().circle(l.motor_center_dia/2).cutBlind(-l.motor_center_bore) \
        .faces('>Z').workplane().pushPoints(pilots).circle(l.servo_ear_r).extrude(l.servo_spacer) \
        .faces('>Z').workplane(centerOption='ProjectedOrigin').pushPoints(pilots).hole(config.m2_dia) \
        .faces('>Z').workplane(centerOption='ProjectedOrigin').pushPoints([(0, 0)]).hole(config.m3_dia) \
        .faces('>Z').workplane(centerOption='ProjectedOrigin').center(0, -centre - l.servo_slot_offset).rect(*l.servo_slot).cutThruAll() \
        .faces('<Z').workplane(origin=(0, -l.length, 0)).hole(p.shaft_d + 0.2) \
        .pushPoints(e.holes).hole(config.m3_dia, l.thickness) \
        .union(tab)

def hip_follower():
    h, l = config.head, config.leg
    depth = config.gears.thickness + config.press_fit + h.race_depth - h.race_clearance
    return cq.Workplane('XY', origin=(0, l.hip_pad_y, -depth)).circle(l.hip_pad_d/2).extrude(depth) \
        .faces('>Z').workplane().hole(config.m3_pilot_dia, 3.2)

def pinion():
    g, l = config.gears, config.leg
    return spur_gear(g.teeth_pinion) \
        .faces('>Z').workplane().cboreHole(l.servo_spline_d, 2*l.servo_boss_r, l.servo_shoulder + 0.1 - config.press_fit) \
        .rotate((0, 0, 0), (0, 0, 1), 180/g.teeth_pinion) \
        .translate((0, -centre, -config.press_fit - g.thickness))

_m, _e = config.motor_lower, config.encoder
meshes = [
    ('5010_body', translation_matrix((0, 0, config.leg.thickness))),
    ('5010_rotor', translation_matrix((0, 0, config.leg.thickness))),
    ('sg90_body', concatenate_matrices(translation_matrix((0, -centre, -config.leg.servo_shoulder)), rotation_matrix(radians(-90), (0, 0, 1)))),
    ('gbm2804', concatenate_matrices(translation_matrix((0, -2*config.leg.length, ankle_z - _m.nub_h)), rotation_matrix(radians(_m.angle), (0, 0, 1)), translation_matrix((-_m.dia/2, _m.dia/2, 0)), rotation_matrix(radians(90), (1, 0, 0)))),
    ('as5600', translation_matrix((0, -config.leg.length, -_e.height))),
    ('as5600', translation_matrix((0, -2*config.leg.length, ankle_board_z))),
]

def leg():
    l = config.leg
    magnet = cq.Workplane('XY').circle(_e.magnet_dia/2).extrude(_e.magnet_h)
    asm = cq.Assembly(name='leg')
    asm.add(upper_leg(), name='upper_leg', color=cq.Color('orange'))
    asm.add(hip_follower(), name='hip_follower', color=cq.Color('orange'))
    asm.add(pinion(), name='pinion', color=cq.Color('yellow'))
    asm.add(sprocket_upper(), name='sprocket_upper', color=cq.Color('yellow'))
    asm.add(belt(), name='belt', color=cq.Color('black'))
    asm.add(ring(), name='ring', color=cq.Color('orange'))
    asm.add(sun(), name='sun', color=cq.Color('yellow'))
    asm.add(pulley(), name='pulley', color=cq.Color('yellow'))
    asm.add(knee_screws())
    for i, bearing in enumerate(knee_bearings()):
        asm.add(bearing, name=f'planet_bearing_{i}', color=cq.Color(.65, .68, .72),
                metadata={'link': 'lower_leg'})
    for i, p in enumerate(planets()):
        asm.add(p, name=f'planet_{i}', color=cq.Color('orange'))
    asm.add(lower_leg(), name='lower_leg', color=cq.Color('cyan'))
    asm.add(wheel(), name='wheel', color=cq.Color('gray30'))
    asm.add(magnet.translate((0, -l.length, _e.gap)), name='magnet_knee', color=cq.Color('gray30'))
    asm.add(magnet.translate((0, -2*l.length, ankle_board_z + _e.height + _e.gap)), name='magnet_ankle', color=cq.Color('gray30'))
    return asm
