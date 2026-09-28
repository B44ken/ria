import cadquery as cq
import trimesh
import numpy as np
from util.frames import right, left
import head, upperleg

def meshes(asm, bought):
    for name, part in asm.traverse():
        if part.obj is not None:
            cq.exporters.export(part.obj.val().moved(part.loc), f'../build/{name}.stl', tolerance=0.1, angularTolerance=0.3)
            m = trimesh.load(f'../build/{name}.stl')
            m.visual.face_colors = part.color.toTuple()
            yield name, m
    for name, T in bought:
        yield name, trimesh.load(f'assets/{name}.glb').to_mesh().apply_scale(1000).apply_transform(T)

scene = trimesh.Scene()
scene.graph.update(frame_from='world', frame_to='ria', matrix=np.diag([0.001, 0.001, 0.001, 1]))
scene.graph.update(frame_from='ria', frame_to='head')
scene.graph.update(frame_from='ria', frame_to='right_leg', matrix=right)
scene.graph.update(frame_from='ria', frame_to='left_leg', matrix=left)
for i, (name, m) in enumerate(meshes(head.head(), head.meshes)):
    scene.add_geometry(m, geom_name=name, node_name=f'{name}_{i}', parent_node_name='head')
for i, (name, m) in enumerate(meshes(upperleg.leg(), upperleg.meshes)):
    node = scene.add_geometry(m, geom_name=name, node_name=f'right_leg/{name}_{i}', parent_node_name='right_leg')
    scene.graph.update(frame_from='left_leg', frame_to=f'left_leg/{name}_{i}', geometry=scene.graph[node][1])
scene.export('../build/ria.glb')
