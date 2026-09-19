from math import cos, pi, sin
import cadquery as cq
from config import config
from util.gear import spur_gear, ring_gear
from transmission import sprocket_lower

def sun():
    p = config.planetary
    return spur_gear(p.sun, p) \
        .faces('>Z').workplane().rect(p.square, p.square).extrude(0.3 + p.back + 2.0) \
        .faces('>Z').workplane().hole(4.6) \
        .faces('<Z').workplane().hole(p.bearing_od + 0.1, 4.1) \
        .translate((0, -config.leg.length, p.z))

def pulley():
    p, b = config.planetary, config.belt
    hub_z = p.z + p.thickness + 0.3
    return cq.Workplane('XY').circle(p.module * (p.sun/2 - 1.25) - 0.25).extrude(b.z - b.flange - hub_z).translate((0, 0, hub_z)) \
        .union(sprocket_lower()) \
        .faces('>Z').workplane().cboreHole(4.6, p.bearing_od + 0.1, 7) \
        .faces('<Z').workplane().rect(p.square + 0.2, p.square + 0.2).cutBlind(-(p.back + 2.0 + 0.2)) \
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
    top = p.z + p.thickness + 0.3 + p.back
    neck = cq.Workplane('XY').center(0, (20.5 + 45)/2).rect(l.width, 45 - 20.5).extrude(top - l.thickness).translate((0, 0, l.thickness)) \
        .cut(cq.Workplane('XY').circle(20.5).extrude(top)) \
        .cut(cq.Workplane('XY').circle(case).extrude(top - p.z).translate((0, 0, p.z)))
    back = cq.Workplane('XY').circle(case).extrude(0.3 + p.back).translate((0, 0, p.z + p.thickness)) \
        .cut(cq.Workplane('XY').circle(p.module * (p.ring/2 + 1.25)).extrude(0.3).translate((0, 0, p.z + p.thickness))) \
        .faces('>Z').workplane().hole(2 * (p.module * (p.sun/2 - 1.25) - 0.25 + config.press_fit))
    return ring_gear(p.ring, p, case).rotate((0, 0, 0), (0, 0, 1), 180 / p.ring).translate((0, 0, p.z)) \
        .union(neck).union(back) \
        .faces('>Z').workplane().pushPoints([(0, 30), (0, 40)]).hole(config.m3_dia) \
        .translate((0, -l.length, 0))
