"""The leg and thin knee transmission, built as separate named components.

Local knee centre: (0, 0). Hip / motor centre: (0, 100).
Axial order: rear carrier -> sun and planets -> integral input pulley.
"""

from math import cos, radians, sin

import cadquery as cq

from .assets import MotorLibrary
from .belt import belt_envelope, timing_pulley
from .config import RobotConfig
from .gears import external_profile, internal_void_profile
from .frame import add_frame
from .geometry import along_axis, annulus, box, cylinder, prism
from .hardware import add_knee_hardware
from .hip import add_hip, hip_nose
from .model import Model


def upper_leg(config: RobotConfig) -> cq.Shape:
    """Regression only: the old suspended monolith, never a default print."""
    gears, stack = config.gears, config.stack
    frame = hip_nose(config).fuse(box(20, 55, 4.5, (0, 66.5, 2.25)))
    frame = frame.cut(box(12.5, 23.5, 6, (0, 62.5, 2.25)))
    for y in (48.5, 76.5):
        frame = frame.cut(cylinder(0.8, -0.1, 4.6, (0, y)))
    for centre in ((-8, 100), (8, 100), (0, 90.5), (0, 109.5)):
        frame = frame.cut(cylinder(1.6, -0.1, 4.6, centre))
        frame = frame.cut(cylinder(3.1, -0.1, 0.2, centre))
        countersink = cq.Solid.makeCone(3.1, 1.6, 1.5, cq.Vector(*centre, 0.2), cq.Vector(0, 0, 1))
        frame = frame.cut(countersink)

    # The web follows the reduced case radius; its hip-side interface stays put.
    profiles = []
    for y, bottom, top in ((gears.case_radius - 2, 9.7, 12.7), (44, 0, 4.5)):
        points = [cq.Vector(x, y, z) for x, z in
                  ((-9, bottom), (9, bottom), (9, top), (-9, top), (-9, bottom))]
        profiles.append(cq.Wire.makePolygon(points))
    frame = frame.fuse(cq.Solid.makeLoft(profiles))
    frame = frame.fuse(cylinder(gears.case_radius, stack.backplate_bottom, stack.backplate_top))
    frame = frame.fuse(cylinder(6, 8.7, 12.7)).cut(cylinder(1.25, 9.0, 12.8))

    bridge = box(20, 10, 13.4, (0, gears.case_radius, 16.4))
    bridge = bridge.cut(cylinder(gears.case_radius - 1.4, 9.6, stack.gear_bottom))
    cavity = prism(internal_void_profile(gears), stack.gear_bottom, stack.gear_top)
    cavity = cavity.rotate((0, 0, 0), (0, 0, 1), gears.ring_phase)
    ring = cylinder(gears.case_radius, stack.gear_bottom, stack.gear_top).cut(cavity)
    frame = frame.fuse(bridge).fuse(ring).cut(cavity)
    for index in range(gears.planet_count):
        frame = frame.cut(cylinder(3.3, 9.6, 12.8, gears.planet_centre(index)))
    return frame


def output_carrier(config: RobotConfig) -> cq.Shape:
    radius = config.gears.orbit_radius + 4.5
    carrier = cylinder(radius, 13, 17.8)
    # Preserve the original lower-leg mounting holes and distal end. Extend
    # the lug into the smaller carrier rather than leaving it disconnected.
    lug_root = -(radius - 5.5)
    lug_outline = [(-8, -20), (-7, -40), (7, -40), (8, -20)]
    if lug_root > -20:
        lug_outline = [(-8, lug_root), *lug_outline, (8, lug_root)]
    lug = prism(lug_outline, 13, 17.8)
    carrier = carrier.fuse(lug)
    carrier = carrier.cut(cylinder(config.bearing_seat_diameter / 2, 13.4, 17.9))
    carrier = carrier.cut(cylinder(2.3, 12.9, 13.5))
    for y in (-31, -37):
        carrier = carrier.cut(cylinder(1.25, 12.9, 17.9, (0, y)))
    for index in range(config.gears.planet_count):
        centre = config.gears.planet_centre(index)
        carrier = carrier.cut(annulus(4.2, 2.05, 17.5, 17.9, centre))
        carrier = carrier.cut(cylinder(1.45, 13.8, 17.9, centre))
    for angle in (60, 180, 300):
        centre = 12 * cos(radians(angle)), 12 * sin(radians(angle))
        carrier = carrier.cut(cylinder(4, 12.9, 17.9, centre))
    return carrier


def planet(config: RobotConfig) -> cq.Shape:
    stack, gears = config.stack, config.gears
    shape = prism(external_profile(gears.planet_teeth, gears), stack.gear_bottom, stack.gear_top)
    shape = shape.cut(cylinder(config.bearing_seat_diameter / 2, 18, 21.8))
    return shape.cut(cylinder(2.3, 21.7, 23.2))


def sun_and_pulley(config: RobotConfig) -> cq.Shape:
    """One connected print, with both bearing seats and no joining shaft."""
    stack, gears = config.stack, config.gears
    shape = prism(external_profile(gears.sun_teeth, gears), stack.gear_bottom, stack.gear_top)
    shape = shape.fuse(cylinder(gears.sun_hub_radius, stack.gear_top, stack.pulley_bottom_flange))
    shape = shape.fuse(cylinder(23.6, stack.pulley_bottom_flange, stack.teeth_bottom))
    shape = shape.fuse(timing_pulley(config.belt.knee_teeth, stack.teeth_bottom, stack.teeth_top))
    shape = shape.fuse(cylinder(23.6, stack.teeth_top, stack.cap_top))
    seat_radius = config.bearing_seat_diameter / 2
    shape = shape.cut(cylinder(seat_radius, 18, 22.1))
    shape = shape.cut(cylinder(seat_radius, 24.8, 31.8))
    shape = shape.cut(cylinder(2.3, 22, 24.9))
    for angle in (0, 120, 240):
        centre = 15 * cos(radians(angle)), 15 * sin(radians(angle))
        shape = shape.cut(cylinder(4.5, 23.5, 31.8, centre))
    return shape


def motor_pulley(config: RobotConfig) -> cq.Shape:
    """Tooth band + 0.8 mm cap + through bore; no default radial screw hole."""
    stack = config.stack
    shape = timing_pulley(config.belt.motor_teeth, stack.teeth_bottom, stack.teeth_top)
    shape = shape.fuse(cylinder(9, stack.teeth_top, stack.cap_top))
    shape = shape.cut(cylinder(config.motor_bore_diameter / 2, 24.2, 31.8))
    if config.motor_set_screw:  # Archived fixture only.
        shape = shape.cut(along_axis(1.25, (2.3, 0, 27.4), 5.3, (1, 0, 0)))
    return shape.translate((0, config.belt.centre_distance, 0))


def build_knee(motors: MotorLibrary, config: RobotConfig) -> Model:
    model = Model()
    gears = config.gears
    if config.split_frame:
        add_frame(model, config)
    else:  # Original one-piece frame exists only for geometry regression.
        model.add("upper_leg", upper_leg(config),
                  archived_name="upper_leg_100mm_integral_ring",
                  note="Archived monolithic frame; not an exported print design.")
    model.add("carrier", output_carrier(config), material="cyan", motion="carrier", print_quantity=2,
              archived_name="knee_output_carrier", note="Rear carrier; original lower-leg mounting interface.")
    planet_shape = planet(config)
    for index in range(gears.planet_count):
        centre = gears.planet_centre(index)
        shape = planet_shape.rotate((0, 0, 0), (0, 0, 1), gears.planet_phase(index))
        shape = shape.translate((*centre, 0))
        model.add(f"planet_{index}", shape, material="orange", motion="planet", centre=centre,
                  print_quantity=2 * gears.planet_count if index == 0 else 0,
                  archived_name=f"planet_{gears.planet_teeth}T_{index}",
                  note=f"{gears.planet_teeth}T module-1 planet; 693ZZ seat; {config.planet_seat_wall:.2f} mm root wall.")
    model.add("sun_pulley", sun_and_pulley(config), material="yellow", motion="sun", print_quantity=2,
              archived_name=f"sun_{gears.sun_teeth}T_and_pulley_48T",
              note=f"One solid: {gears.sun_teeth}T sun and 48T timing pulley.")
    model.add("motor_pulley", motor_pulley(config), material="yellow", motion="motor", centre=(0, 100),
              print_quantity=2, archived_name="motor_pulley_16T_3M",
              note="16T timing pulley, 7.4 mm high, 4.9 mm bore. No grub screw or radial hole.")
    if config.motor_set_screw:
        screw = along_axis(1.5, (2.4, 100, 27.4), 3, (1, 0, 0))
        screw = screw.cut(along_axis(0.75, (4.8, 100, 27.4), 0.7, (1, 0, 0)))
        model.add("motor_set_screw", screw, material="steel", motion="motor", centre=(0, 100),
                  archived_name="motor_pulley_M3x3_set_screw")
        model.fit("motor_set_screw", "motor_pulley", "Archived M3 grub screw / tap pilot")
    model.add("belt", belt_envelope(config.belt), material="belt",
              archived_name="300_3MGT_6_belt_slack_envelope",
              note="Smooth backing envelope; straight external-tangent spans; teeth omitted.")
    add_knee_hardware(model, config)
    add_hip(model, motors, config)
    return model
