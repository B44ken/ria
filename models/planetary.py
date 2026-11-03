from math import cos, pi, sin
import cadquery as cq
from config import config
from util.gear import spur_gear, ring_gear
from transmission import sprocket_lower

def sun():
    p, e = config.planetary, config.encoder
    shoulder_z = config.leg.thickness + .3 + p.carrier_thickness + p.axial_clearance
    shoulder = cq.Workplane('XY', origin=(0, 0, shoulder_z - p.z)).circle(p.shaft_d/2 + 1).extrude(p.shoulder_t)
    pilot_depth = p.screw - (pulley_screw_seat() - (p.z + p.thickness)) + 1.0
    pilot = cq.Workplane('XY', origin=(0, 0, p.thickness - pilot_depth)) \
        .circle(config.m3_pilot_dia/2).extrude(pilot_depth)
    return spur_gear(p.sun, p) \
        .faces('>Z').workplane().rect(p.square + 0.2, p.square + 0.2).cutBlind(-p.drive_socket_depth) \
        .faces('<Z').workplane().circle(p.shaft_d/2).extrude(p.z - e.gap) \
        .faces('<Z').workplane().hole(e.magnet_dia + 2*config.press_fit, e.magnet_h) \
        .union(shoulder).cut(pilot) \
        .translate((0, -config.leg.length, p.z))

def drive_bearing_z():
    p = config.planetary
    return p.z + p.thickness + p.clearance + 1.0

def pulley_screw_seat():
    return config.belt.z - config.belt.flange + 0.5

def pulley():
    p, b = config.planetary, config.belt
    gear_top = p.z + p.thickness
    shaft = cq.Workplane('XY', origin=(0, 0, gear_top)).circle(p.drive_bearing_id/2 + config.press_fit) \
        .extrude(b.z - b.flange - gear_top)
    drive = cq.Workplane('XY', origin=(0, 0, gear_top - p.drive_socket_depth)) \
        .rect(p.square, p.square).extrude(p.drive_socket_depth)
    recess = b.z + b.band + b.flange - pulley_screw_seat()
    return sprocket_lower().union(shaft).union(drive) \
        .faces('>Z').workplane().cboreHole(config.m3_dia + 0.2, 6.5, recess) \
        .translate((0, -config.leg.length, 0))

def planets():
    p, l = config.planetary, config.leg
    lift = p.z - (l.thickness + 0.3 + p.carrier_thickness + p.axial_clearance)
    gear = spur_gear(p.planet, p) \
        .faces('<Z').workplane().circle(p.planet_hub_d/2).extrude(lift) \
        .faces('<Z').workplane().hole(p.bearing_od + 0.1, p.bearing_w - p.axial_clearance) \
        .faces('>Z').workplane().hole(6.5) \
        .rotate((0, 0, 0), (0, 0, 1), 180 / p.planet) \
        .translate((0, 0, p.z))

    orbit = p.module * (p.sun + p.planet) / 2
    return [gear.translate((orbit * cos(2*pi*i/p.count), -l.length + orbit * sin(2*pi*i/p.count), 0)) for i in range(p.count)]

def ring():
    p, l = config.planetary, config.leg
    case = p.module * (p.ring/2 + 1.25) + p.wall
    reach = p.module * (p.sun + p.planet) / 2 + p.module * (p.planet/2 + 1) + p.clearance
    gear_top = p.z + p.thickness
    top = drive_bearing_z() + p.drive_bearing_w
    roof_z = top - p.back
    neck = cq.Workplane('XY').polyline([(-1.5, reach), (-5, 30), (-5, 45), (5, 45), (5, 30), (1.5, reach)]).close() \
        .extrude(top - l.thickness).translate((0, 0, l.thickness)) \
        .cut(cq.Workplane('XY').circle(reach).extrude(top)) \
        .cut(cq.Workplane('XY').circle(case).extrude(top - p.z).translate((0, 0, p.z)))
    bearing_top = drive_bearing_z() + p.drive_bearing_w
    housing_r = p.drive_bearing_od/2 + p.wall
    back = cq.Workplane('XY').circle(case).circle(reach).extrude(top - gear_top).translate((0, 0, gear_top)) \
        .union(cq.Workplane('XY').circle(case).circle(housing_r).extrude(p.back).translate((0, 0, roof_z))) \
        .union(cq.Workplane('XY', origin=(0, 0, gear_top + p.clearance)).circle(housing_r).circle(6.35) \
               .extrude(bearing_top - gear_top - p.clearance)) \
        .cut(cq.Workplane('XY', origin=(0, 0, drive_bearing_z())).circle(p.drive_bearing_od/2 + config.press_fit) \
             .extrude(p.drive_bearing_w))
    return ring_gear(p.ring, p, case).rotate((0, 0, 0), (0, 0, 1), 180 / p.ring).translate((0, 0, p.z)) \
        .union(neck).union(back) \
        .faces('<Z').workplane().pushPoints([(x, -y) for x, y in p.mounts]).hole(config.m3_pilot_dia) \
        .translate((0, -l.length, 0))
