"""Three flat-printing parts replace the suspended, one-piece leg frame.

Assembled Z datums are unchanged: hip plate 0..4.5, carrier backplate
9.7..12.7, fixed ring 18.1..23.1 mm. Each part prints with its largest
+Z face DOWN. All raised features then grow within that first-layer outline.

Three M3 through bolts clamp the stack. Two 3 x 25 mm steel dowels register
all three parts; clearance screws alone must not locate the ring gear.
"""
from dataclasses import dataclass

import cadquery as cq

from .assets import AssetLibrary
from .config import RobotConfig
from .gears import internal_void_profile
from .geometry import annulus, box, cylinder, hex_socket, prism
from .model import Model


@dataclass(frozen=True)
class FrameJoint:
    """One shared hole pattern, in the carrier's unused upper sector."""
    bolts: tuple = ((-7.5, 28.5), (7.5, 28.5), (0.0, 39.5))
    dowels: tuple = ((-6.0, 35.0), (6.0, 35.0))
    bolt_clearance: float = 3.4
    dowel_bore: float = 3.05
    dowel_press_pilot: float = 2.95
    nut_pocket_flats: float = 5.8
    nut_seat_z: float = 3.0
    neck_inner_radius: float = 23.6
    outline: tuple = ((-10, 22), (10, 22), (13, 25), (13, 40),
                      (10, 44), (-10, 44), (-13, 40), (-13, 25))


JOINT = FrameJoint()
FRAME_PARTS = ("hip_link", "knee_backplate", "knee_ring")


def joint_holes(shape: cq.Shape, joint: FrameJoint = JOINT, *, press_fit: bool = False) -> cq.Shape:
    for centre in joint.bolts:
        shape = shape.cut(cylinder(joint.bolt_clearance / 2, -1, 25, centre))
    for centre in joint.dowels:
        diameter = joint.dowel_press_pilot if press_fit else joint.dowel_bore
        shape = shape.cut(cylinder(diameter / 2, -1, 25, centre))
    return shape


def hip_link(assets: AssetLibrary, joint: FrameJoint = JOINT) -> cq.Shape:
    """Flat hip/servo spine. Original rear-facing hip boss is retained."""
    shape = assets.load("hip_nose").fuse(box(20, 41, 4.5, (0, 64.5, 2.25)))
    shape = shape.fuse(prism(joint.outline, 0, 4.5))
    shape = shape.cut(box(12.5, 23.5, 6, (0, 62.5, 2.25)))
    for y in (48.5, 76.5):
        shape = shape.cut(cylinder(0.8, -0.1, 4.6, (0, y)))
    for centre in ((-8, 100), (8, 100), (0, 90.5), (0, 109.5)):
        shape = shape.cut(cylinder(1.6, -0.1, 4.6, centre))
        shape = shape.cut(cylinder(3.1, -0.1, 0.2, centre))
        countersink = cq.Solid.makeCone(3.1, 1.6, 1.5,
                                       cq.Vector(*centre, 0.2), cq.Vector(0, 0, 1))
        shape = shape.cut(countersink)
    shape = joint_holes(shape, joint, press_fit=True)
    # These pockets face UP in the exported print: no trapped-nut ceiling.
    for centre in joint.bolts:
        shape = shape.cut(hex_socket(joint.nut_pocket_flats, -0.1,
                                     joint.nut_seat_z, centre))
    return shape.clean()


def knee_backplate(config: RobotConfig, joint: FrameJoint = JOINT) -> cq.Shape:
    """Flat carrier support with a downward offset pad, not a suspended disk."""
    stack = config.stack
    shape = cylinder(config.gears.case_radius, stack.backplate_bottom, stack.backplate_top)
    shape = shape.fuse(prism(joint.outline, 4.5, stack.backplate_top))
    shape = shape.fuse(cylinder(6, 8.7, stack.backplate_top))
    # Same engaged axle length, but a through pilot eliminates a blind-hole roof.
    shape = shape.cut(cylinder(1.25, 8.6, 12.8))
    for index in range(config.gears.planet_count):
        shape = shape.cut(cylinder(3.3, 9.6, 12.8, config.gears.planet_centre(index)))
    return joint_holes(shape, joint).clean()


def knee_ring(config: RobotConfig, joint: FrameJoint = JOINT) -> cq.Shape:
    """Fixed 42T ring with its own downward neck spacer and clamping flange."""
    gears, stack = config.gears, config.stack
    if (gears.sun_teeth, gears.planet_teeth, gears.ring_teeth) != (18, 12, 42):
        raise ValueError("The split-frame joint is designed for the 18/12/42 knee.")
    cavity = prism(internal_void_profile(gears), stack.gear_bottom, stack.gear_top)
    cavity = cavity.rotate((0, 0, 0), (0, 0, 1), gears.ring_phase)
    shape = cylinder(gears.case_radius, stack.gear_bottom, stack.gear_top)
    shape = shape.fuse(prism(joint.outline, stack.gear_bottom, stack.gear_top)).cut(cavity)
    spacer = prism(joint.outline, stack.backplate_top, stack.gear_bottom)
    spacer = spacer.cut(cylinder(joint.neck_inner_radius, 12.6, 18.2))
    return joint_holes(shape.fuse(spacer), joint).clean()


def add_frame_hardware(model: Model, config: RobotConfig, joint: FrameJoint = JOINT) -> None:
    """Nominal metal envelopes: M3x25 socket screws, washers, nuts, dowels."""
    seat = config.stack.gear_top
    for index, centre in enumerate(joint.bolts):
        washer = annulus(3.5, 1.6, seat, seat + 0.5, centre)
        shank_top = seat + 0.5
        screw = cylinder(1.5, shank_top - 25, shank_top, centre)
        screw = screw.fuse(cylinder(2.75, shank_top, shank_top + 3, centre))
        screw = screw.cut(hex_socket(2.5, shank_top + 1.5, shank_top + 3.1, centre))
        nut = hex_socket(5.5, joint.nut_seat_z - 2.4, joint.nut_seat_z, centre)
        nut = nut.cut(cylinder(1.25, -0.1, 3.1, centre))
        screw_name, nut_name = f"frame_screw_{index}", f"frame_nut_{index}"
        model.add(screw_name, screw, material="steel", note="M3 x 25 socket-head screw; 2.5 mm hex drive.")
        model.add(f"frame_washer_{index}", washer, material="steel", note="M3 washer, 7 OD x 3.2 ID x 0.5 mm.")
        model.add(nut_name, nut, material="steel", note="M3 hex nut: 5.5 mm across flats x 2.4 mm thick.")
        model.fit(screw_name, nut_name, "Nominal M3 thread cylinders; helical threads are not modelled.")
    for index, centre in enumerate(joint.dowels):
        model.add(f"frame_dowel_{index}", cylinder(1.5, seat - 25, seat, centre),
                  material="steel", note="3 x 25 mm steel locating dowel; 2.95 mm press pilot in hip link, 3.05 mm slip bores above.")
        model.fit(f"frame_dowel_{index}", "hip_link", "3 mm locating dowel retained in 2.95 mm printed press pilot.")


def add_frame(model: Model, assets: AssetLibrary, config: RobotConfig) -> None:
    model.add("hip_link", hip_link(assets), print_quantity=2,
              note="Flat hip/servo spine. Print motor face down; captive nut pockets face up.")
    model.add("knee_backplate", knee_backplate(config), print_quantity=2,
              note="Carrier backplate and offset pad. Print carrier face down.")
    model.add("knee_ring", knee_ring(config), print_quantity=2,
              note="42T fixed ring and neck spacer. Print tooth face down; spacer grows upward.")
    add_frame_hardware(model, config)
