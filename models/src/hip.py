"""Parametric hip mount, pinion and small hardware; only the actuators are CAD assets."""
import cadquery as cq

from .assets import MotorLibrary
from .config import RobotConfig
from .gears import external_profile
from .geometry import (along_axis, annulus, box, box_between, cylinder,
                       hex_socket, prism)
from .model import Model


def motor_mount_holes(shape: cq.Shape, config: RobotConfig) -> cq.Shape:
    hip = config.hip
    bore = hip.mounting_hole_diameter / 2
    sink = hip.mounting_countersink_diameter / 2
    for x, y in hip.motor_holes(config.belt.centre_distance):
        shape = shape.cut(cylinder(bore, -0.1, hip.plate_thickness + 0.1, (x, y)))
        shape = shape.cut(cylinder(sink, -0.1, 0.2, (x, y)))
        shape = shape.cut(cq.Solid.makeCone(sink, bore, sink - bore,
                                           cq.Vector(x, y, 0.2)))
    return shape


def hip_nose(config: RobotConfig) -> cq.Shape:
    """Rounded 5010 mount, clipped sketch tail, stepped sleeve seat and axle pilot."""
    hip, centre = config.hip, config.belt.centre_distance
    shape = cylinder(hip.mount_radius, 0, hip.plate_thickness, (0, centre))
    # Two straight-sided sketch regions retain the original spine junction.
    shoulder = [(-13, -14), (13, -14), (12, -5), (-12, -5)]
    tail = [(-17, -32), (35, -32), (13, -14), (-13, -14)]
    for outline in (shoulder, tail):
        shape = shape.fuse(prism([(x, y + centre) for x, y in outline], 0, hip.plate_thickness))
    shape = shape.intersect(box_between((-50, centre - 15, -20), (50, centre + 50, 20)))
    shape = shape.fuse(cylinder(hip.outer_boss_radius, hip.boss_bottom, 0, (0, centre)))
    shape = shape.fuse(cylinder(hip.spigot_radius, hip.spigot_bottom, hip.boss_bottom, (0, centre)))
    shape = motor_mount_holes(shape, config)
    shape = shape.cut(cylinder(hip.axle_pilot_diameter / 2, hip.spigot_bottom - 0.1, 2.3, (0, centre)))
    seat = hip.sleeve_seat_diameter / 2
    shape = shape.cut(cylinder(seat, hip.spigot_bottom, hip.sleeve_top, (0, centre)))
    shape = shape.cut(cq.Solid.makeCone(seat + 0.25, seat, 0.25, cq.Vector(0, centre, hip.spigot_bottom)))
    shape = shape.cut(cylinder(3.6, 2.3, hip.plate_thickness + 0.1, (0, centre)))
    return shape.clean()


def motor_mount_screw(centre: tuple[float, float]) -> cq.Shape:
    """M3x8 countersunk screw, with a real 2 mm hex-key opening."""
    x, y = centre
    shape = cylinder(1.5, 1.7, 8, centre).fuse(cylinder(3, 0, 0.2, centre))
    shape = shape.fuse(cq.Solid.makeCone(3, 1.5, 1.5, cq.Vector(x, y, 0.2)))
    socket = hex_socket(2, -0.1, 1.1, centre)
    socket = socket.rotate((x, y, 0), (x, y, 1), 30)
    return shape.cut(socket)


def hip_sleeve(config: RobotConfig) -> cq.Shape:
    hip, centre = config.hip, (0, config.belt.centre_distance)
    shape = annulus(2.5, 1.6, hip.bearing_bottom, hip.sleeve_top, centre)
    mouth = cq.Solid.makeCone(1.85, 1.6, 0.25, cq.Vector(*centre, hip.bearing_bottom))
    return shape.cut(mouth)


def hip_axle(config: RobotConfig) -> cq.Shape:
    centre, bottom = (0, config.belt.centre_distance), config.hip.bearing_bottom
    shape = cylinder(1.5, bottom, bottom + 12, centre)
    shape = shape.fuse(cylinder(3, bottom - 2.4, bottom, centre))
    slot_z = bottom - 2.4 + 0.5
    for width, depth in ((3.6, 0.85), (0.85, 3.6)):
        shape = shape.cut(box(width, depth, 1.2, (*centre, slot_z)))
    return shape


def servo_rotation(shape: cq.Shape, config: RobotConfig) -> cq.Shape:
    axis = (0, config.servo_output_y, 0)
    return shape.rotate(axis, (0, config.servo_output_y, 1), config.servo_rotation)


def servo_spacer(index: int, config: RobotConfig) -> cq.Shape:
    offset = 19.5 if index == 0 else -8.5
    centre = offset, config.servo_output_y
    shape = annulus(3.3, 1.15, config.hip.plate_thickness, 7.7, centre)
    # D-shaped cut follows the adjacent servo body; both ears use the same print.
    if index == 0:
        halfspace = box_between((offset - 2.15, centre[1] - 10, 4), (offset + 10, centre[1] + 10, 8))
    else:
        halfspace = box_between((offset - 10, centre[1] - 10, 4), (offset + 2.15, centre[1] + 10, 8))
    return servo_rotation(shape.intersect(halfspace), config)


def servo_pinion(spline: cq.Shape, config: RobotConfig) -> cq.Shape:
    """Printed 36T pinion, with the supplied spline envelope subtracted at its real pose."""
    gears, centre = config.hip_gears, config.servo_output_y
    outline = external_profile(gears.pinion_teeth, gears, flank_intervals=14, tip_intervals=4)
    front = -gears.leg_gap
    shape = prism(outline, front - gears.thickness, front)
    shape = shape.rotate((0, 0, 0), (0, 0, 1), 180 / gears.pinion_teeth).translate((0, centre, 0))
    # The wide recess clears the servo output boss; no decorative joining hub.
    pocket_bottom = config.hip.servo_shoulder - 0.1
    shape = shape.cut(cylinder(8.75, pocket_bottom, front + 0.1, (0, centre)))
    screw_clearance = cylinder(0.6, front - gears.thickness - 0.2,
                               config.hip.servo_shoulder + 0.1, (0, centre))
    return shape.cut(spline.fuse(screw_clearance))


def servo_wire(index: int, config: RobotConfig) -> cq.Shape:
    x, y = (index - 3) * 1.2, config.servo_output_y
    points = [(x, y + 4.5, 22.8), (x, y + 5.6, 22.8), (x, y + 5.9, 23.1),
              (x, y + 6, 25.3), (x, y + 9.5, 25.3)]
    segments = []
    for start, end in zip(points, points[1:]):
        direction = cq.Vector(*end) - cq.Vector(*start)
        segments.append(along_axis(0.6, start, direction.Length, direction.normalized().toTuple()))
    shape = segments[0]
    for segment in segments[1:]:
        shape = shape.fuse(segment)
    for point in points[1:]:
        shape = shape.fuse(cq.Solid.makeSphere(0.6, cq.Vector(*point)))
    return shape


def add_hip(model: Model, motors: MotorLibrary, config: RobotConfig) -> None:
    hip, centre = config.hip, config.belt.centre_distance

    def add(key: str, shape: cq.Shape, material: str = "steel", **metadata):
        model.add("hip_" + key.lower(), shape, material=material,
                  motion="context", archived_name="hip_" + key, **metadata)

    for index, hole in enumerate(hip.motor_holes(centre)):
        add(f"5010_mount_M3x8_countersunk_{index}", motor_mount_screw(hole))
    rotor = motors.load("5010_rotor").translate((0, centre, hip.plate_thickness))
    model.add("hip_5010_rotor_supplied_step", rotor, material="dark", motion="motor", centre=(0, centre),
              archived_name="hip_5010_rotor_supplied_STEP", note="Vendored supplied 5010 rotor; no external asset lookup.")
    stator = motors.load("5010_stator").translate((0, centre, hip.plate_thickness))
    # Preserve the measured 4.8 mm shaft extension from the previous model.
    stator = stator.fuse(cylinder(config.motor_shaft_diameter / 2, 24, 32, (0, centre)))
    add("5010_stator_supplied_STEP", stator, "copper", note="Vendored 5010 stator and retained shaft extension.")
    add("5mm_OD_3p2mm_ID_sleeve", hip_sleeve(config))
    bearing_bottom, bearing_top = hip.bearing_bottom, hip.bearing_bottom + hip.bearing_width
    add("685zz_bearing_0_inner_race", annulus(3.5, 2.5, bearing_bottom, bearing_top, (0, centre)))
    add("685zz_bearing_0_outer_race", annulus(5.5, 4.3, bearing_bottom, bearing_top, (0, centre)))
    shields = annulus(4.25, 3.55, bearing_bottom + 0.05, bearing_bottom + 0.20, (0, centre))
    shields = shields.fuse(annulus(4.25, 3.55, bearing_top - 0.20, bearing_top - 0.05, (0, centre)))
    add("685zz_bearing_0_shields", shields)
    for index in range(2):
        add(f"SG90_spacer_{index}", servo_spacer(index, config), "purple",
            print_quantity=4 if index == 0 else 0, note="3.2 mm D-shaped ear spacer; four identical prints per robot.")
    add("axle_M3x12_pan_screw", hip_axle(config))
    pose = (0, config.servo_output_y, hip.servo_shoulder)
    body = servo_rotation(motors.load("sg90_body").translate(pose), config)
    spline = servo_rotation(motors.load("sg90_output_spline").translate(pose), config)
    add("servo_pinion_36T_m1", servo_pinion(spline, config), "yellow", print_quantity=2,
        note="Parametric 36T pinion; original 20-degree involute, phase and output-spline fit.")
    add("sg90_body_supplied_STEP", body, "blue", note="Vendored supplied SG90 body.")
    add("sg90_output_spline", spline, note="Vendored supplied SG90 output; check against the actual servo variant.")

    frame_name = "hip_link" if config.split_frame else "upper_leg"
    for index, y in enumerate((config.servo_output_y - 19.5, config.servo_output_y + 8.5)):
        shape = cylinder(1, 0.1, 10.1, (0, y)).fuse(cylinder(1.9, 10.1, 11.65, (0, y)))
        shape = shape.cut(hex_socket(1.5, 11, 11.8, (0, y)))
        name = f"hip_servo_mount_screw_{index}"
        model.add(name, shape, material="steel", motion="context",
                  archived_name=f"hip_SG90_mount_M2x10_direct_screw_{index}")
        model.fit(name, frame_name, "M2 mounting screw in 1.6 mm tap pilot")
    for index in (2, 3, 4):
        model.add(f"hip_servo_wire_{index}", servo_wire(index, config), material="dark", motion="context",
                  archived_name=f"hip_sg90_wire_{index}")
    model.fit("hip_axle_m3x12_pan_screw", frame_name, "Hip axle / tap pilot")
