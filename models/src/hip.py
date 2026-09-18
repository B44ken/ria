"""Original hip hardware in leg coordinates, with the archived SG90 placement."""

import cadquery as cq

from .assets import AssetLibrary, HIP_OBJECTS
from .config import RobotConfig
from .geometry import along_axis, cylinder, hex_socket
from .model import Model


def servo_wire(index: int) -> cq.Shape:
    """The same bent flexible-wire envelope as the supplied build."""
    x = (index - 3) * 1.2
    points = [(x, 72.5, 22.8), (x, 73.6, 22.8), (x, 73.9, 23.1),
              (x, 74.0, 25.3), (x, 77.5, 25.3)]
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


def add_hip(model: Model, assets: AssetLibrary, config: RobotConfig) -> None:
    pivot = (0, config.servo_output_y, 0)
    axis = (0, config.servo_output_y, 1)
    for key in HIP_OBJECTS:
        shape = assets.load(key)
        if key == "5010_stator_supplied_STEP":
            shape = shape.fuse(cylinder(config.motor_shaft_diameter / 2, 24, 32, (0, 100)))
        if any(token in key for token in ("sg90_body", "sg90_output_spline", "SG90_spacer")):
            shape = shape.rotate(pivot, axis, config.servo_rotation)
        if key == "servo_pinion_36T_m1":
            # Preserve the pinion teeth. Only its spline socket follows the rotated servo.
            shaft = assets.load("sg90_output_spline").rotate(pivot, axis, config.servo_rotation)
            shape = shape.fuse(cylinder(3, -4.2, -1.4, (0, 68)))
            shape = shape.cut(shaft.fuse(cylinder(0.6, -4.4, -1.2, (0, 68))))

        if "spacer" in key.lower():
            material = "purple"
        elif "sg90_body" in key:
            material = "blue"
        elif "stator" in key:
            material = "copper"
        elif "rotor" in key:
            material = "dark"
        elif "pinion" in key:
            material = "yellow"
        else:
            material = "steel"
        name = "hip_" + key.lower()
        model.add(name, shape, material=material,
                  motion="motor" if "5010_rotor" in key else "context", centre=(0, 100),
                  print_quantity=2 if "servo_pinion" in key else 0,
                  archived_name="hip_" + key,
                  note="Unchanged reference hip hardware / archived servo placement.")

    for index, y in enumerate((48.5, 76.5)):
        shape = cylinder(1, 0.1, 10.1, (0, y)).fuse(cylinder(1.9, 10.1, 11.65, (0, y)))
        shape = shape.cut(hex_socket(1.5, 11, 11.8, (0, y)))
        name = f"hip_servo_mount_screw_{index}"
        model.add(name, shape, material="steel", motion="context",
                  archived_name=f"hip_SG90_mount_M2x10_direct_screw_{index}")
        model.fit(name, "hip_link" if config.split_frame else "upper_leg", "M2 mounting screw in 1.6 mm tap pilot")

    for index in (2, 3, 4):
        model.add(f"hip_servo_wire_{index}", servo_wire(index), material="dark", motion="context",
                  archived_name=f"hip_sg90_wire_{index}")
    model.fit("hip_axle_m3x12_pan_screw", "hip_link" if config.split_frame else "upper_leg", "Original hip axle / tap pilot")
