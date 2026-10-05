from functools import cache
from math import cos, pi, sin

import cadquery as cq
from cq_warehouse.fastener import CounterSunkScrew
from config import config


@cache
def flathead(length):
    return CounterSunkScrew(size='M3-0.5', length=length,
                           fastener_type=config.planetary.screw_type, simple=False)


def planet_bearing_z():
    p, l = config.planetary, config.leg
    carrier_top = l.thickness + .3 + p.carrier_thickness
    hub_height = p.z - carrier_top - p.axial_clearance
    pocket_depth = p.bearing_w - p.axial_clearance
    return p.z + p.thickness + hub_height - pocket_depth


def planet_screw_z():
    p = config.planetary
    return planet_bearing_z() + p.bearing_w + (flathead(p.planet_screw).screw_data['dk'] - p.pin_d)/2


def knee_bearings():
    p, l = config.planetary, config.leg
    bearing = cq.Workplane('XY', origin=(0, 0, planet_bearing_z())) \
        .circle(p.bearing_od/2).circle(p.pin_d/2).extrude(p.bearing_w)
    orbit = p.module * (p.sun + p.planet)/2
    return [bearing.translate((orbit*cos(i*2*pi/p.count), orbit*sin(i*2*pi/p.count)-l.length, 0))
            for i in range(p.count)]


def knee_screws():
    p, l = config.planetary, config.leg
    asm = cq.Assembly(name='knee_screws')
    metal = cq.Color(.72, .75, .8)
    mount = flathead(p.mount_screw)
    mount_shape = cq.Solid(mount.wrapped)
    mount_z = (6.3 - mount.screw_data['dk']) / 2
    for i, (x, y) in enumerate(p.mounts):
        screw = mount_shape.rotate((0, 0, 0), (1, 0, 0), 180).translate((x, y-l.length, mount_z))
        asm.add(cq.Workplane(obj=screw), name=f'ring_screw_{i}', color=metal,
                metadata={'link': 'upper_leg', 'length': p.mount_screw})

    planet = flathead(p.planet_screw)
    planet_shape = cq.Solid(planet.wrapped)
    planet_z = planet_screw_z()
    orbit = p.module * (p.sun + p.planet) / 2
    for i in range(p.count):
        point = (orbit*cos(i*2*pi/p.count), orbit*sin(i*2*pi/p.count)-l.length, planet_z)
        asm.add(cq.Workplane(obj=planet_shape.translate(point)), name=f'planet_screw_{i}', color=metal,
                metadata={'link': 'lower_leg', 'length': p.planet_screw})

    pulley = flathead(p.screw)
    seat_z = p.z + p.thickness + p.clearance + p.back + 2 + p.screw_floor
    pulley_z = seat_z + (pulley.screw_data['dk'] - 3.2) / 2
    asm.add(cq.Workplane(obj=cq.Solid(pulley.wrapped).translate((0, -l.length, pulley_z))), name='pulley_screw', color=metal,
            metadata={'link': 'upper_leg', 'length': p.screw})
    return asm
