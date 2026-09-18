"""Purchased bearing envelopes and the original knee axle / spacers.

Bearings are race and shield envelopes, not ball/cage simulations. Nominal
thread cylinders intentionally intersect their tap pilots; the audit records
these fits by exact part pair instead of hiding arbitrary overlaps.
"""

from .config import RobotConfig
from .geometry import Point2, annulus, box, cylinder
from .model import Model, Motion


def bearing_693(model: Model, name: str, centre: Point2, bottom: float,
                outer_motion: Motion, inner_motion: Motion,
                archived_prefix: str) -> None:
    model.add(name + "_outer", annulus(4, 3.2, bottom, bottom + 4, centre),
              material="steel", motion=outer_motion, centre=centre,
              archived_name=archived_prefix + "_outer")
    model.add(name + "_inner", annulus(2.05, 1.5, bottom, bottom + 4, centre),
              material="steel", motion=inner_motion, centre=centre,
              archived_name=archived_prefix + "_inner")
    shields = annulus(3.18, 2.08, bottom + 0.15, bottom + 0.3, centre)
    shields = shields.fuse(annulus(3.18, 2.08, bottom + 3.7, bottom + 3.85, centre))
    model.add(name + "_shields", shields, material="dark", motion=outer_motion,
              centre=centre, archived_name=archived_prefix + "_shields")


def add_knee_hardware(model: Model, config: RobotConfig) -> None:
    bearing_693(model, "carrier_bearing", (0, 0), 13.4, "carrier", "fixed", "carrier_693zz")
    for index in range(config.gears.planet_count):
        centre = config.gears.planet_centre(index)
        bearing_693(model, f"planet_bearing_{index}", centre, 17.8,
                    "planet", "carrier", f"planet_693zz_{index}")
        name = f"planet_pin_{index}"
        model.add(name, cylinder(1.5, 13.8, 21.8, centre), material="steel", motion="carrier",
                  note="Smooth steel dowel, diameter 3 x length 8 mm.",
                  archived_name=f"planet_3x8_dowel_{index}")
        model.fit(name, "carrier", "3 mm dowel in 2.9 mm printed press-fit pilot")

    bearing_693(model, "sun_lower_bearing", (0, 0), 18.1, "sun", "fixed", "sun_693zz_lower")
    bearing_693(model, "sun_upper_bearing", (0, 0), 24.8, "sun", "fixed", "sun_693zz_upper")
    spacers = (
        ("carrier_rear_inner_spacer", 12.7, 13.4),
        ("carrier_to_sun_inner_spacer", 17.4, 18.1),
        ("sun_inner_spacer", 22.1, 24.8),
        ("axle_head_inner_washer", 28.8, 29.3),
    )
    for name, bottom, top in spacers:
        model.add(name, annulus(2.05, 1.55, bottom, top), material="steel",
                  note="Finished metal inner-race spacer on the fixed knee axle.", archived_name=name)

    axle = cylinder(1.5, 9.3, 29.3).fuse(cylinder(3, 29.3, 31.7))
    axle = axle.cut(box(3.6, 0.8, 1.2, (0, 0, 31.4))).cut(box(0.8, 3.6, 1.2, (0, 0, 31.4)))
    model.add("knee_axle", axle, material="steel", archived_name="common_axle_M3x20_pan",
              note="Fixed M3 x 20 knee bearing axle; not a lead screw or a motor-pulley grub screw.")
    model.fit("knee_axle", "upper_leg", "M3 axle in 2.5 mm tap pilot")
