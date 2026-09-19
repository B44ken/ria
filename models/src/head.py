"""Rounded head, integral hip sectors and removable bearing-retainer lid.

Everything here is constructed from dimensions; no reference CAD is loaded.
World axes: X left/right on a side face, Y across the two hips, Z upward.
The default feature dimensions reproduce the supplied head and lid solids.
"""
import cadquery as cq

from .config import RobotConfig
from .gears import external_profile
from .geometry import box_between, rounded_rectangle, xz_prism, y_cylinder

HEAD_OBJECTS = {
    "head_shell": "head_shell_with_integral_sectors_and_housings",
    "head_lid": "head_lid",
}


def opposite_side(shape: cq.Shape) -> cq.Shape:
    return shape.rotate((0, 0, 0), (0, 0, 1), 180)


def bearing_housing(config: RobotConfig) -> cq.Shape:
    """One integral seat, open cheeks and the outward-facing 28T sector."""
    head, hip, gears = config.head, config.hip, config.hip_gears
    side, axis, bottom = head.side, head.pivot_height, head.shell_bottom
    top = axis + 7.5
    back = side - 10
    gear_back = side + gears.wall_standoff
    gear_front = gear_back + gears.thickness

    cheeks = box_between((-13.5, back, bottom), (13.5, side, top))
    # The open middle is closed at the top by a 3.5 mm bridge.
    cheeks = cheeks.cut(box_between((-8.5, back - 1, bottom - 1),
                                     (8.5, side + 1, axis + 4)))
    cheeks = cheeks.fuse(y_cylinder(7.5, side - 5.5, gear_back, 0, axis))
    # Pocket for the lid's retainer tongue; the cheek tops remain connected.
    cheeks = cheeks.cut(box_between((-11.8, side - 8.65, bottom - 1),
                                     (11.8, side - 5.35, axis + 7.1)))
    cheeks = cheeks.cut(box_between((-8.5, back - 1, bottom - 1),
                                     (8.5, side - 5.5, top + 1)))

    outline = external_profile(gears.fixed_teeth, gears,
                               flank_intervals=14, tip_intervals=4)
    sector = xz_prism([(x, z + axis) for x, z in outline], gear_back, gear_front)
    sector = sector.intersect(box_between((-30, gear_back - 1, axis - 30),
                                         (30, gear_front + 1, top)))
    housing = cheeks.fuse(sector)

    seat_radius = (hip.bearing_od + head.bearing_seat_clearance) / 2
    # Seat shoulder coincides with the outer race's outboard face.
    seat_end = config.hip_world_offset + hip.spigot_bottom
    seat_mouth = side - 5.35
    housing = housing.cut(y_cylinder(seat_radius, seat_mouth - 0.25, seat_end, 0, axis))
    housing = housing.cut(cq.Solid.makeCone(seat_radius + 0.2, seat_radius, 0.2,
                                           cq.Vector(0, seat_mouth, axis), cq.Vector(0, 1, 0)))
    housing = housing.cut(y_cylinder(4.35, seat_mouth - 0.25, gear_front + 0.1, 0, axis))
    counterbore_radius = hip.outer_boss_radius + head.boss_radial_clearance
    counterbore_back = config.hip_world_offset + hip.boss_bottom - 0.1
    housing = housing.cut(y_cylinder(counterbore_radius, counterbore_back,
                                     gear_front + 0.1, 0, axis))
    # Small connecting relief avoids a zero-thickness ridge between tangent holes.
    relief_top = axis - counterbore_radius + 0.06
    housing = housing.cut(box_between((-0.1, counterbore_back - 0.05, relief_top - 1),
                                       (0.1, gear_front + 0.25, relief_top)))
    return housing


def detent_slot(config: RobotConfig) -> cq.Shape:
    side, axis = config.head.side, config.head.pivot_height
    # Open all the way through the curved shell, rather than a trapped recess.
    return box_between((11.65, side - 8.75, axis + 4.15),
                       (config.head.width / 2 + 10, side - 5.35, axis + 6.8))


def head_shell(config: RobotConfig) -> cq.Shape:
    head = config.head
    bottom, roof = head.shell_bottom, head.height - head.wall
    shell = rounded_rectangle(head.width, head.depth, head.corner_radius, bottom, head.height)
    cavity = rounded_rectangle(head.width - 2 * head.wall, head.depth - 2 * head.wall,
                                head.corner_radius - head.wall, bottom - 0.1, roof)
    shell = shell.cut(cavity)
    side, axis = head.side, head.pivot_height
    # Clear the shell first, then add the concentric bearing seats back into it.
    clearance = y_cylinder(8, side - 16, side + 9, 0, axis)
    shell = shell.cut(clearance).cut(opposite_side(clearance))
    housing = bearing_housing(config)
    shell = shell.fuse(housing).fuse(opposite_side(housing))
    # Driver reaches the lower motor screw; it follows the pivot, not the lid.
    access = y_cylinder(2.35, side - 5.5, side + 9, 0, axis - 9.4)
    slot = detent_slot(config)
    for cutter in (access, slot):
        shell = shell.cut(cutter).cut(opposite_side(cutter))
    return shell.clean()


def lid_retainer(config: RobotConfig) -> cq.Shape:
    """U-shaped bearing retainer with a slotted, ramped snap finger."""
    head = config.head
    back, front = head.side - 8.55, head.side - 5.65
    axis, top = head.pivot_height, head.pivot_height + 6.9
    tongue = box_between((-11.5, back, head.lid_thickness), (11.5, front, top))
    detent = xz_prism([(11.5, axis + 4.4), (12, axis + 4.4),
                      (12, axis + 5.4), (11.5, axis + 6.4)], back, front)
    tongue = tongue.fuse(detent)
    tongue = tongue.cut(y_cylinder(4.35, back - 0.1, front + 0.1, 0, axis))
    tongue = tongue.cut(box_between((-4.35, back - 0.1, axis), (4.35, front + 0.1, top + 1)))
    # Rounded flexure-slot end, not a sharp stress-raising inside corner.
    slot_bottom = axis - 5.2
    tongue = tongue.cut(y_cylinder(0.4, back - 0.1, front + 0.1, 10.1, slot_bottom))
    tongue = tongue.cut(box_between((9.7, back - 0.1, slot_bottom), (10.5, front + 0.1, top + 1)))
    return tongue


def head_lid(config: RobotConfig) -> cq.Shape:
    head = config.head
    lid = rounded_rectangle(head.width, head.depth, head.corner_radius, 0, head.lid_thickness)
    tongue = lid_retainer(config)
    return lid.fuse(tongue).fuse(opposite_side(tongue)).clean()
