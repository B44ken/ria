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
