"""Place two identical legs against the parametric head's shared hip datums."""

from dataclasses import replace
from math import cos, radians, sin

import cadquery as cq
import numpy as np

from .head import HEAD_OBJECTS, head_shell, head_lid
from .config import RobotConfig
from .model import Model, Part


def head_transform(config: RobotConfig, left: bool = False) -> np.ndarray:
    """Local (x, y, z) -> head (-x, z + 40.7, y - 88), then mirror by rotation."""
    transform = np.array([[-1, 0, 0, 0], [0, 0, 1, config.hip_world_offset],
                          [0, 1, 0, config.knee_world_height], [0, 0, 0, 1]], dtype=float)
    if left:
        transform = np.diag([-1, -1, 1, 1]) @ transform
    return transform


def installed(shape: cq.Shape, config: RobotConfig, left: bool = False) -> cq.Shape:
    shape = shape.rotate((0, 0, 0), (0, 0, 1), 180)
    shape = shape.rotate((0, 0, 0), (1, 0, 0), -90)
    shape = shape.translate((0, config.hip_world_offset, config.knee_world_height))
    return shape.rotate((0, 0, 0), (0, 0, 1), 180) if left else shape


def build_robot(knee: Model, config: RobotConfig) -> Model:
    robot = Model()
    for name, shape in (("head_shell", head_shell(config)), ("head_lid", head_lid(config))):
        robot.add(name, shape, material="head", print_quantity=1,
                  archived_name=HEAD_OBJECTS[name], note="Parametric head geometry; dimensions in config.head and config.hip.")
    for side in ("right", "left"):
        for part in knee.parts:
            robot.parts.append(replace(part, name=f"{side}_{part.name}",
                                       shape=installed(part.shape, config, left=side == "left"),
                                       print_quantity=0,
                                       archived_name=f"{side}_{part.archived_name}"))
    return robot


def motion_transform(part: Part, angle: float, config: RobotConfig) -> np.ndarray:
    """Rigid part motion for a carrier angle, with the correct orbital planets."""
    factors = {"carrier": 1.0, "sun": config.gears.sun_per_carrier,
               "planet": config.gears.planet_per_carrier, "motor": config.total_ratio}
    spin = radians(factors.get(part.motion, 0.0) * angle)
    rotation = np.array([[cos(spin), -sin(spin), 0],
                         [sin(spin), cos(spin), 0], [0, 0, 1]])
    centre = np.array([*part.centre, 0.0]) if part.motion in ("planet", "motor") else np.zeros(3)
    target = centre.copy()
    if part.motion == "planet":
        orbit = radians(angle)
        target[:2] = (centre[0] * cos(orbit) - centre[1] * sin(orbit),
                      centre[0] * sin(orbit) + centre[1] * cos(orbit))
    transform = np.eye(4)
    transform[:3, :3] = rotation
    transform[:3, 3] = target - rotation @ centre
    return transform
