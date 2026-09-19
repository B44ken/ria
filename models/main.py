import cadquery as cq
import trimesh
import numpy as np
from config import config
import head, upperleg

def frame(origin, x, z):
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = x, np.cross(z, x), z, origin
    return M

def meshes(asm, bought):
    for name, part in asm.traverse():
        if part.obj is not None:
            cq.exporters.export(part.obj.val().moved(part.loc), f'../build/{name}.stl', tolerance=0.1, angularTolerance=0.3)
            m = trimesh.load(f'../build/{name}.stl')
            m.visual.face_colors = part.color.toTuple()
            yield name, m
    for name, T in bought:
        yield name, trimesh.load(f'assets/{name}.glb').to_mesh().apply_scale(1000).apply_transform(T)

outside = config.head.width/2 + config.gears.thickness
pivot_z = config.head.pivot_height - config.head.height/2 + config.wall/2
right = frame((outside + config.press_fit, 0, pivot_z), (0, 1, 0), (1, 0, 0))
left = frame((-(outside + config.press_fit), 0, pivot_z), (0, -1, 0), (-1, 0, 0))

scene = trimesh.Scene()
scene.graph.update(frame_from='world', frame_to='ria', matrix=np.diag([0.001, 0.001, 0.001, 1]))
scene.graph.update(frame_from='ria', frame_to='head')
scene.graph.update(frame_from='ria', frame_to='right_leg', matrix=right)
scene.graph.update(frame_from='ria', frame_to='left_leg', matrix=left)
for name, m in meshes(head.head(), head.meshes):
    scene.add_geometry(m, geom_name=name, node_name=name, parent_node_name='head')
for name, m in meshes(upperleg.leg(), upperleg.meshes):
    scene.add_geometry(m, geom_name=name, node_name=f'right_leg/{name}', parent_node_name='right_leg')
    scene.graph.update(frame_from='left_leg', frame_to=f'left_leg/{name}', geometry=name)
scene.export('../build/ria.glb')
