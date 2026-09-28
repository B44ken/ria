from math import cos, pi, sin
import cadquery as cq
from config import config
from util.gear import spur_gear, ring_gear
from transmission import sprocket_lower

def sun():
    p, e, b = config.planetary, config.encoder, config.belt
    square_top = p.z + p.thickness + p.clearance + p.back + 2.0
    pulley_top = b.z + b.band + b.flange
    return spur_gear(p.sun, p) \
        .faces('>Z').workplane().rect(p.square, p.square).extrude(square_top - p.z - p.thickness) \
        .faces('>Z').workplane().hole(config.m3_pilot_dia, p.screw - (pulley_top - square_top) + 1.0) \
        .faces('<Z').workplane().circle(e.boss_d/2).extrude(p.z - e.gap) \
        .faces('<Z').workplane().hole(e.magnet_dia + 2*config.press_fit, e.magnet_h) \
        .translate((0, -config.leg.length, p.z))

def pulley():
    p, b = config.planetary, config.belt
    hub_z = p.z + p.thickness + p.clearance
    return cq.Workplane('XY').circle(p.module * (p.sun/2 - 1.25) - 0.25).extrude(b.z - b.flange - hub_z).translate((0, 0, hub_z)) \
        .union(sprocket_lower()) \
        .faces('<Z').workplane().rect(p.square + 0.2, p.square + 0.2).cutBlind(-(p.back + 2.0)) \
        .faces('>Z').workplane().cskHole(config.m3_dia, config.m3_csink_dia, 90) \
        .translate((0, -config.leg.length, 0))

def planet():
    p = config.planetary
    return spur_gear(p.planet, p) \
        .faces('<Z').workplane().hole(p.bearing_od + 0.1, 3.8) \
        .faces('>Z').workplane().hole(4.6) \
        .rotate((0, 0, 0), (0, 0, 1), 180 / p.planet) \
        .translate((0, 0, p.z))

def planets():
    p = config.planetary
    orbit = p.module * (p.sun + p.planet) / 2
    return [planet().translate((orbit * cos(2*pi*i/p.count), -config.leg.length + orbit * sin(2*pi*i/p.count), 0)) for i in range(p.count)]

def ring():
    p, l = config.planetary, config.leg
    case = p.module * (p.ring/2 + 1.25) + p.wall
    reach = p.module * (p.sun + p.planet) / 2 + p.module * (p.planet/2 + 1) + p.clearance
    top = p.z + p.thickness + p.clearance + p.back
    neck = cq.Workplane('XY').center(0, (reach + 45)/2).rect(l.width, 45 - reach).extrude(top - l.thickness).translate((0, 0, l.thickness)) \
        .cut(cq.Workplane('XY').circle(reach).extrude(top)) \
        .cut(cq.Workplane('XY').circle(case).extrude(top - p.z).translate((0, 0, p.z)))
    back = cq.Workplane('XY').circle(case).extrude(p.clearance + p.back).translate((0, 0, p.z + p.thickness)) \
        .cut(cq.Workplane('XY').circle(reach).extrude(p.clearance).translate((0, 0, p.z + p.thickness))) \
        .faces('>Z').workplane().hole(2 * (p.module * (p.sun/2 - 1.25) - 0.25 + config.press_fit))
    return ring_gear(p.ring, p, case).rotate((0, 0, 0), (0, 0, 1), 180 / p.ring).translate((0, 0, p.z)) \
        .union(neck).union(back) \
        .faces('>Z').workplane().pushPoints([(0, 30), (0, 40)]).hole(config.m3_dia) \
        .translate((0, -l.length, 0))
