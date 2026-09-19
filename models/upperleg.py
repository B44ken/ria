import cadquery as cq
from config import config
from util.gear import spur_gear
from transmission import sprocket_upper, belt
from planetary import sun, pulley, planets, ring
from lowerleg import lower_leg, wheel, ankle_z
from trimesh.transformations import rotation_matrix, translation_matrix, concatenate_matrices
from math import radians

centre = config.gears.module * (config.gears.teeth_head + config.gears.teeth_pinion) / 2

def upper_leg():
    l = config.leg
    pilots = [(0, -centre + p) for p in l.servo_pilots]
    return cq.Workplane('XY').circle(l.mount_r).extrude(l.thickness) \
        .union(cq.Workplane('XY').center(0, -l.length/2).slot2D(l.length + l.width, l.width, 90).extrude(l.thickness)) \
        .faces('<Z').workplane().pushPoints(l.motor_holes + [(0, l.length - 30), (0, l.length - 40)]).cskHole(config.m3_dia, config.m3_csink_dia, 90) \
        .faces('>Z').workplane().circle(l.motor_center_dia/2).cutBlind(-l.motor_center_bore) \
        .faces('>Z').workplane().pushPoints(pilots).circle(l.servo_ear_r).extrude(l.servo_spacer) \
        .faces('>Z').workplane(centerOption='ProjectedOrigin').pushPoints(pilots).hole(config.m2_dia) \
        .faces('>Z').workplane(centerOption='ProjectedOrigin').pushPoints([(0, 0), (0, -l.length)]).hole(config.m3_dia) \
        .faces('>Z').workplane(centerOption='ProjectedOrigin').center(0, -centre - l.servo_slot_offset).rect(*l.servo_slot).cutThruAll()

def pinion():
    g, l = config.gears, config.leg
    return spur_gear(g.teeth_pinion) \
        .faces('>Z').workplane().cboreHole(l.servo_spline_d, 2*l.servo_boss_r, l.servo_shoulder + 0.1 - config.press_fit) \
        .rotate((0, 0, 0), (0, 0, 1), 180/g.teeth_pinion) \
        .translate((0, -centre, -config.press_fit - g.thickness))

_m = config.motor_lower
meshes = [
    ('5010_body', translation_matrix((0, 0, config.leg.thickness))),
    ('5010_rotor', translation_matrix((0, 0, config.leg.thickness))),
    ('sg90_body', concatenate_matrices(translation_matrix((0, -centre, -config.leg.servo_shoulder)), rotation_matrix(radians(-90), (0, 0, 1)))),
    ('gbm2804', concatenate_matrices(translation_matrix((-_m.dia/2, _m.dia/2 - 2*config.leg.length, ankle_z - 1.2)), rotation_matrix(radians(90), (1, 0, 0)))),
]

def leg():
    l = config.leg
    asm = cq.Assembly(name='leg')
    asm.add(upper_leg(), name='upper_leg', color=cq.Color('orange'))
    asm.add(pinion(), name='pinion', color=cq.Color('yellow'))
    asm.add(sprocket_upper(), name='sprocket_upper', color=cq.Color('yellow'))
    asm.add(belt(), name='bought_belt', color=cq.Color('black'))
    asm.add(ring(), name='ring', color=cq.Color('orange'))
    asm.add(sun(), name='sun', color=cq.Color('yellow'))
    asm.add(pulley(), name='pulley', color=cq.Color('yellow'))
    for i, p in enumerate(planets()):
        asm.add(p, name=f'planet_{i}', color=cq.Color('orange'))
    asm.add(lower_leg(), name='lower_leg', color=cq.Color('cyan'))
    asm.add(wheel(), name='wheel', color=cq.Color('gray30'))
    return asm
