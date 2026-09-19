from math import pi
import cadquery as cq
from config import config
from util import belt as gt3

def sprocket_upper():
    b = config.belt
    return gt3.sprocket(b.teeth_motor) \
        .faces('>Z').workplane().circle(b.teeth_motor * b.pitch / (2 * pi) + b.flange).extrude(b.flange) \
        .faces('>Z').workplane().hole(b.bore_motor) \
        .translate((0, 0, b.z))

def sprocket_lower():
    b = config.belt
    r = b.teeth_pulley * b.pitch / (2 * pi) + b.flange
    return gt3.sprocket(b.teeth_pulley) \
        .faces('>Z').workplane().circle(r).extrude(b.flange) \
        .faces('<Z').workplane().circle(r).extrude(b.flange) \
        .translate((0, 0, b.z))

def belt():
    b = config.belt
    return gt3.belt(config.leg.length, b.teeth_motor * b.pitch / (2 * pi), b.teeth_pulley * b.pitch / (2 * pi)) \
        .translate((0, 0, b.z + (b.band - b.belt_height) / 2))
