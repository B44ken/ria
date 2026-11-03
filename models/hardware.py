from functools import cache
from math import cos, pi, sin

import cadquery as cq
from cq_warehouse.fastener import CounterSunkScrew, HexNut
from config import config


@cache
def flathead(length):
    return CounterSunkScrew(size='M3-0.5', length=length,
                           fastener_type=config.planetary.screw_type, simple=False)


def hip_screw():
    l = config.leg
    screw = CounterSunkScrew(size='M3-0.5', length=l.hip_pad_screw,
                            fastener_type='iso7046', simple=False)
    seat_z = l.thickness + (screw.screw_data['dk'] - 5.8) / 2
    return cq.Workplane(obj=cq.Solid(screw.wrapped).translate((0, l.hip_pad_y, seat_z)))


@cache
def pivot_screw():
    return CounterSunkScrew(size='M3-0.5', length=config.head.pivot_screw,
                           fastener_type='iso7046', simple=False)


@cache
def pivot_nut():
    # din 985 m3: 5.5 af, 2.4 hex, 4.0 overall. collar/insert internals approximate.
    base = HexNut(size='M3-0.5', fastener_type='iso4032', simple=False)
    collar = cq.Workplane('XY', origin=(0, 0, 2.4)).circle(2.75).circle(2.2).extrude(1.6)
    lip = cq.Workplane('XY', origin=(0, 0, 3.4)).circle(2.75).circle(1.8).extrude(.6)
    metal = cq.Workplane(obj=cq.Solid(base.wrapped)).union(collar).union(lip) \
        .faces('>Z').edges().fillet(.2).val()
    # installed nylon bore; deformation and prevailing torque are not simulated.
    nylon = cq.Workplane('XY', origin=(0, 0, 2.4)).circle(2.2).circle(1.5).extrude(1.0).val()
    return metal, nylon


def pivot_hardware():
    h, l = config.head, config.leg
    asm = cq.Assembly(name='hip_pivot')
    seat_z = l.thickness - l.motor_center_bore
    nut_z = -h.pivot_length - h.pivot_endplay
    # align the ideal right-hand thread profiles at the selected axial position.
    phase = (180 + 360 * (nut_z - seat_z + h.pivot_screw) / pivot_screw().thread_pitch) % 360
    asm.add(cq.Workplane(obj=cq.Solid(pivot_screw().wrapped).translate((0, 0, seat_z))),
            name='pivot_screw', color=cq.Color(.72, .75, .8),
            metadata={'link': 'upper_leg', 'length': h.pivot_screw})
    for name, shape, color in zip(('pivot_nut', 'pivot_nut_insert'), pivot_nut(),
                                  (cq.Color(.72, .75, .8), cq.Color('blue'))):
        shape = shape.rotate((0, 0, 0), (1, 0, 0), 180) \
            .rotate((0, 0, 0), (0, 0, 1), phase).translate((0, 0, nut_z))
        asm.add(cq.Workplane(obj=shape), name=name, color=color,
                metadata={'link': 'upper_leg', 'standard': 'din985', 'endplay': h.pivot_endplay})
    return asm


def planet_bearing_z():
    p, l = config.planetary, config.leg
    return l.thickness + .3 + p.carrier_thickness


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

def drive_bearing():
    from planetary import drive_bearing_z
    p, l = config.planetary, config.leg
    return cq.Workplane('XY', origin=(0, -l.length, drive_bearing_z())) \
        .circle(p.drive_bearing_od/2).circle(p.drive_bearing_id/2).extrude(p.drive_bearing_w)


def knee_screws():
    from planetary import pulley_screw_seat
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
    seat_z = pulley_screw_seat()
    pulley_z = seat_z + (pulley.screw_data['dk'] - 3.2) / 2
    asm.add(cq.Workplane(obj=cq.Solid(pulley.wrapped).translate((0, -l.length, pulley_z))), name='pulley_screw', color=metal,
            metadata={'link': 'upper_leg', 'length': p.screw})
    return asm
