from math import cos, pi, sin
import cadquery as cq
from config import config

ankle_z = config.leg.thickness + 0.3 + config.planetary.carrier_thickness

def lower_leg():
    p, l, m = config.planetary, config.leg, config.motor_lower
    orbit = p.module * (p.sun + p.planet) / 2
    pins = [(orbit * cos(2*pi*i/p.count), orbit * sin(2*pi*i/p.count)) for i in range(p.count)]
    return cq.Workplane('XY').circle(orbit + 4.5).extrude(p.carrier_thickness) \
        .union(cq.Workplane('XY').center(0, -l.length/2).slot2D(l.length + l.width, l.width, 90).extrude(p.carrier_thickness)) \
        .union(cq.Workplane('XY').center(0, -l.length).circle(m.dia/2).extrude(p.carrier_thickness)) \
        .faces('>Z').workplane().cboreHole(4.6, p.bearing_od + 0.1, 4.5) \
        .faces('>Z').workplane().pushPoints(pins).hole(p.pin_d - 0.1) \
        .faces('>Z').workplane().pushPoints(pins).circle(4.2).circle(2.05).cutBlind(-0.4) \
        .faces('>Z').workplane().center(0, -l.length).hole(8) \
        .faces('<Z').workplane(origin=(0, -l.length, 0)).pushPoints([(x, -y) for x, y in m.base_holes]).cskHole(config.m3_dia, config.m3_csink_dia, 90) \
        .translate((0, -l.length, l.thickness + 0.3))

def wheel():
    w, m = config.wheels, config.motor_lower
    return cq.Workplane('XY').circle(w.dia/2).extrude(w.width + 2) \
        .faces('<Z').workplane().hole(m.dia + 1, w.width) \
        .faces('>Z').workplane().hole(8) \
        .faces('>Z').workplane().pushPoints(m.top_holes).hole(config.m3_dia) \
        .translate((0, -2*config.leg.length, ankle_z + m.height - w.width))
