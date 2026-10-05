import head, upperleg
import trimesh
import numpy as np
from pathlib import Path
import json
from util.frames import right, left, knee_origin, wheel_origin

Path('../build/stl').mkdir(parents=True, exist_ok=True)

origins = {'head': np.zeros(3), 'upper_leg': np.zeros(3), 'lower_leg': knee_origin, 'wheel': wheel_origin}
robot = json.loads(Path('../software/bot.json').read_text())['parts']

def meshes(asm, bought):
    for name, part in asm.traverse():
        if part.obj is not None:
            path = f'../build/stl/{name}.stl'
            part.obj.val().moved(part.loc).exportStl(path, .1, .3)
            m = trimesh.load_mesh(path)
            m.visual.face_colors = part.color.toTuple()
            yield name, m, None
    for i, (name, T) in enumerate(bought):
        m = trimesh.load(f'assets/{name}.glb').to_mesh().apply_scale(1000).apply_transform(T)
        m.export(f'../build/stl/{name}_{i}.stl')
        yield f'{name}_{i}', m, name.partition('_')[0]

def add_links(part, parent, parent_origin):
    link = part['name'].removesuffix('_r').removesuffix('_l')
    node = f'{parent}/{link}'
    scene.graph.update(frame_from=parent, frame_to=node, translation=origins[link] - parent_origin)
    nodes = {name: (node, origins[link]) for name in part['meshes']}
    for child in part.get('children', []):
        nodes.update(add_links(child, node, origins[link]))
    return nodes

scene = trimesh.Scene()
scene.graph.update(frame_from='world', frame_to='ria', matrix=np.diag([0.001, 0.001, 0.001, 1]))
scene.graph.update(frame_from='ria', frame_to='head')
scene.graph.update(frame_from='ria', frame_to='right_leg', matrix=right)
scene.graph.update(frame_from='ria', frame_to='left_leg', matrix=left)
leg_nodes = {side: add_links(part, side, origins['upper_leg'])
             for side, part in zip(('right_leg', 'left_leg'), robot['children'])}
leg = upperleg.leg()
# these mechanical parts are omitted from the simplified simulation meshes.
cad_links = {**{f'planet_{i}': 'lower_leg' for i in range(3)},
             'as5600_4': 'upper_leg', 'as5600_5': 'lower_leg', 'magnet_ankle': 'wheel'}
cad_links.update({name: part.metadata['link'] for name, part in leg.traverse()
                  if 'link' in part.metadata})
for side, nodes in leg_nodes.items():
    parents = {'upper_leg': f'{side}/upper_leg',
               'lower_leg': f'{side}/upper_leg/lower_leg',
               'wheel': f'{side}/upper_leg/lower_leg/wheel'}
    nodes.update({name: (parents[link], origins[link]) for name, link in cad_links.items()})
for name, m, _ in meshes(head.head(), head.meshes):
    scene.add_geometry(m, geom_name=name, node_name=name, parent_node_name='head')
for name, m, group in meshes(leg, upperleg.meshes):
    m.apply_translation(-leg_nodes['right_leg'][name][1]).export(f'../build/stl/{name}.stl')
    for side in ('right_leg', 'left_leg'):
        parent, _ = leg_nodes[side][name]
        if group is not None:
            scene.graph.update(frame_from=parent, frame_to=f'{parent}/{group}')
            parent = f'{parent}/{group}'
        node = f'{parent}/{name}'
        if side == 'right_leg':
            scene.add_geometry(m, geom_name=name, node_name=node, parent_node_name=parent)
        else:
            scene.graph.update(frame_from=parent, frame_to=node, geometry=name)
scene.export('../build/ria.glb')
