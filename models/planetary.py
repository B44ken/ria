from math import cos, pi, sin
import cadquery as cq
from config import config
from util.gear import spur_gear, ring_gear
from transmission import sprocket_lower
from hardware import planet_screw_z

def sun():
    p, e = config.planetary, config.encoder
    shoulder_z = config.leg.thickness + .3 + p.carrier_thickness + p.axial_clearance
    shoulder = cq.Workplane('XY', origin=(0, 0, shoulder_z - p.z)).circle(p.shaft_d/2 + 1).extrude(p.shoulder_t)
    return spur_gear(p.sun, p) \
        .faces('>Z').workplane().rect(p.square, p.square).extrude(p.clearance + p.back + 2.0) \
        .faces('>Z').workplane().hole(config.m3_pilot_dia, p.screw - p.screw_floor + 1.0) \
        .faces('<Z').workplane().circle(p.shaft_d/2).extrude(p.z - e.gap) \
        .faces('<Z').workplane().hole(e.magnet_dia + 2*config.press_fit, e.magnet_h) \
        .union(shoulder) \
        .translate((0, -config.leg.length, p.z))

def pulley():
    p, b = config.planetary, config.belt
    hub_z = p.z + p.thickness + p.clearance
    screw_seat = hub_z + p.back + 2.0 + p.screw_floor
    recess = b.z + b.band + b.flange - screw_seat
    return cq.Workplane('XY').circle(p.drive_d/2).extrude(b.z - b.flange - hub_z).translate((0, 0, hub_z)) \
        .union(sprocket_lower()) \
        .faces('<Z').workplane().rect(p.square + 0.2, p.square + 0.2).cutBlind(-(p.back + 2.0)) \
        .faces('>Z').workplane().cboreHole(config.m3_dia + 0.2, 6.5, recess) \
        .translate((0, -config.leg.length, 0))

def planets():
    p, l = config.planetary, config.leg
    lift = p.z - (l.thickness + 0.3 + p.carrier_thickness + p.axial_clearance)
    gear = spur_gear(p.planet, p) \
        .faces('<Z').workplane().circle(p.planet_hub_d/2).extrude(lift) \
        .faces('<Z').workplane().hole(p.bearing_od + 0.1, p.bearing_w - p.axial_clearance) \
        .faces('>Z').workplane().hole(4.6) \
        .rotate((0, 0, p.thickness/2), (1, 0, p.thickness/2), 180) \
        .rotate((0, 0, 0), (0, 0, 1), 180 / p.planet) \
        .translate((0, 0, p.z))

    orbit = p.module * (p.sun + p.planet) / 2
    return [gear.translate((orbit * cos(2*pi*i/p.count), -l.length + orbit * sin(2*pi*i/p.count), 0)) for i in range(p.count)]

def ring():
    p, l = config.planetary, config.leg
    case = p.module * (p.ring/2 + 1.25) + p.wall
    reach = p.module * (p.sun + p.planet) / 2 + p.module * (p.planet/2 + 1) + p.clearance
    gear_top = p.z + p.thickness
    roof_z = planet_screw_z() + p.planet_head_clearance
    top = roof_z + p.back
    neck = cq.Workplane('XY').polyline([(-1.5, reach), (-5, 30), (-5, 45), (5, 45), (5, 30), (1.5, reach)]).close() \
        .extrude(top - l.thickness).translate((0, 0, l.thickness)) \
        .cut(cq.Workplane('XY').circle(reach).extrude(top)) \
        .cut(cq.Workplane('XY').circle(case).extrude(top - p.z).translate((0, 0, p.z)))
    bore = p.drive_d/2 + config.press_fit
    back = cq.Workplane('XY').circle(case).circle(reach).extrude(top - gear_top).translate((0, 0, gear_top)) \
        .union(cq.Workplane('XY').circle(case).circle(bore).extrude(p.back).translate((0, 0, roof_z))) \
        .union(cq.Workplane('XY').circle(p.shaft_d/2 + 1).circle(bore) \
               .extrude(roof_z - gear_top - p.clearance).translate((0, 0, gear_top + p.clearance)))
    return ring_gear(p.ring, p, case).rotate((0, 0, 0), (0, 0, 1), 180 / p.ring).translate((0, 0, p.z)) \
        .union(neck).union(back) \
        .faces('<Z').workplane().pushPoints([(x, -y) for x, y in p.mounts]).hole(config.m3_pilot_dia, p.mount_screw + 1.0 - l.thickness) \
        .translate((0, -l.length, 0))
