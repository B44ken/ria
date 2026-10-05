from math import cos, pi, radians, sin
import cadquery as cq
from config import config
from util.frames import wheel_origin
from hardware import planet_bearing_z

ankle_z = config.leg.thickness + 0.3 + config.planetary.carrier_thickness
ankle_board_z = ankle_z - config.motor_lower.nub_h - config.encoder.magnet_h - config.encoder.gap - config.encoder.height

def lower_leg():
    p, l, m, e, s = config.planetary, config.leg, config.motor_lower, config.encoder, config.electronics
    orbit = p.module * (p.sun + p.planet) / 2
    pins = [(orbit * cos(2*pi*i/p.count), orbit * sin(2*pi*i/p.count)) for i in range(p.count)]
    a = radians(m.angle)
    base = [(x*cos(a) - y*sin(a), x*sin(a) + y*cos(a)) for x, y in m.base_holes]
    standoff = l.thickness + 0.3 - ankle_board_z - e.pcb
    standoffs = cq.Workplane('XY', origin=(0, -l.length, 0)).pushPoints(e.holes).circle(s.standoff_dia/2).extrude(-standoff)
    taps = cq.Workplane('XY', origin=(0, -l.length, -standoff)).pushPoints(e.holes).circle(config.m3_dia/2).extrude(s.tap_depth)
    seat_height = planet_bearing_z() - (l.thickness + .3 + p.carrier_thickness)
    seats = cq.Workplane('XY', origin=(0, 0, p.carrier_thickness)).pushPoints(pins).circle(2.05).extrude(seat_height)
    axles = cq.Workplane('XY').pushPoints(pins).circle((p.pin_d - .1)/2).extrude(p.carrier_thickness + seat_height)
    return cq.Workplane('XY').circle(orbit + 4.5).extrude(p.carrier_thickness) \
        .union(cq.Workplane('XY').center(0, -l.length/2).slot2D(l.length + l.width, l.width, 90).extrude(p.carrier_thickness)) \
        .union(cq.Workplane('XY').center(0, -l.length).circle(m.dia/2).extrude(p.carrier_thickness)) \
        .faces('>Z').workplane().hole(p.shaft_d + 0.2) \
        .faces('>Z').workplane().center(0, -l.length).hole(8) \
        .faces('<Z').workplane(origin=(0, -l.length, 0)).pushPoints([(x, -y) for x, y in base]).cskHole(config.m3_dia, config.m3_csink_dia, 90) \
        .union(seats).cut(axles).union(standoffs).cut(taps) \
        .translate((0, -l.length, l.thickness + 0.3))

def wheel():
    w, m = config.wheels, config.motor_lower
    return cq.Workplane('XY').circle(w.dia/2).extrude(w.width + 2) \
        .faces('<Z').workplane().hole(m.dia + 1, w.width) \
        .faces('>Z').workplane().hole(8) \
        .faces('>Z').workplane().pushPoints(m.top_holes).hole(config.m3_dia) \
        .translate(tuple(wheel_origin - (0, 0, (w.width + 2) / 2)))
