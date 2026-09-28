import cadquery as cq
import trimesh
import numpy as np
from pathlib import Path
import xml.etree.ElementTree as ET
from util.frames import right, left, knee_origin, wheel_origin
import head, upperleg

Path('../build/stl').mkdir(parents=True, exist_ok=True)

origins = {'head': np.zeros(3), 'upper_leg': np.zeros(3), 'lower_leg': knee_origin, 'wheel': wheel_origin}
mesh_origins = {
    geom.attrib['mesh']: origins[body.attrib['name'].removesuffix('_r').removesuffix('_l')]
    for body in ET.parse('../ria.xml').iter('body') for geom in body.findall('geom')
}

def export_local(name, mesh):
    mesh.copy().apply_translation(-mesh_origins[name]).export(f'../build/stl/{name}.stl')

def meshes(asm, bought):
    for name, part in asm.traverse():
        if part.obj is not None:
            cq.exporters.export(part.obj.val().moved(part.loc), f'../build/stl/{name}.stl', tolerance=0.1, angularTolerance=0.3)
            m = trimesh.load(f'../build/stl/{name}.stl')
            m.visual.face_colors = part.color.toTuple()
            if mesh_origins[name].any():
                export_local(name, m)
            yield name, m
    for i, (name, T) in enumerate(bought):
        m = trimesh.load(f'assets/{name}.glb').to_mesh().apply_scale(1000).apply_transform(T)
        export_local(f'{name}_{i}', m)
        yield name, m

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
