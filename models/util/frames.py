import numpy as np
from config import config

def frame(origin, x, z):
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = x, np.cross(z, x), z, origin
    return M

outside = config.head.width/2 + config.gears.thickness
pivot_z = config.head.pivot_height - config.head.height/2 + config.wall/2
right = frame((outside + config.press_fit, 0, pivot_z), (0, 1, 0), (1, 0, 0))
left = frame((-(outside + config.press_fit), 0, pivot_z), (0, -1, 0), (-1, 0, 0))

# joint origins in the cad leg assembly, in millimetres
knee_origin = np.array((0, -config.leg.length, 0))
wheel_origin = np.array((0, -2 * config.leg.length,
                        config.leg.thickness + 0.3 + config.planetary.carrier_thickness
                        + config.motor_lower.height - config.wheels.width / 2 + 1))
