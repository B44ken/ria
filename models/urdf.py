import xml.etree.ElementTree as ET
from pathlib import Path
import cadquery as cq
import numpy as np
import trimesh
from trimesh.transformations import euler_from_matrix, translation_matrix
from config import config
from util.frames import right, left
import head, upperleg

out = Path('../build')
(out / 'urdf').mkdir(exist_ok=True)
density = config.mass.pla_density * 1000
L = config.leg.length
fmt = lambda v: ' '.join(f'{x:.6g}' for x in np.ravel(v))

def box(mass, lo, hi):
    a = hi - lo
    return mass, (lo + hi)/2, mass/12 * np.diag([a[1]**2 + a[2]**2, a[0]**2 + a[2]**2, a[0]**2 + a[1]**2]), lo, hi

def printed(name, part, shift, file):
    solid = part.obj.val().moved(part.loc).translate(cq.Vector(*shift))
    bb = solid.BoundingBox()
    cq.exporters.export(solid, str(out / 'urdf' / file), tolerance=0.1, angularTolerance=0.3)
    lo, hi = np.array([bb.xmin, bb.ymin, bb.zmin])/1000, np.array([bb.xmax, bb.ymax, bb.zmax])/1000
    if name in config.mass.grams:
        return box(config.mass.grams[name]/1000, lo, hi)
    return solid.Volume()*density*1e-9, np.array(solid.Center().toTuple())/1000, np.array(cq.Shape.matrixOfInertia(solid))*density*1e-15, lo, hi

def bought(name, T, shift, file):
    m = trimesh.load(f'assets/{name}.glb').to_mesh().apply_scale(1000).apply_transform(T).apply_translation(shift)
    m.export(out / 'urdf' / file)
    lo, hi = m.bounds/1000
    return box(config.mass.grams[name]/1000, lo, hi)

def combine(bodies):
    M = sum(m for m, *_ in bodies)
    C = sum(m*c for m, c, *_ in bodies)/M
    I = sum(I + m*(d @ d*np.eye(3) - np.outer(d, d)) for m, c, I, *_ in bodies for d in [c - C])
    lo, hi = np.min([b[3] for b in bodies], axis=0), np.max([b[4] for b in bodies], axis=0)
    return M, C, I, lo, hi

def link(kind, parts, meshes, shift, collision):
    files = [f'{kind}_{n}.stl' for n, _ in parts] + [f'{kind}_{n}_{i}.stl' for i, (n, _) in enumerate(meshes)]
    bodies = [printed(n, p, shift, f) for (n, p), f in zip(parts, files)] + [bought(n, T, shift, f) for (n, T), f in zip(meshes, files[len(parts):])]
    M, C, I, lo, hi = combine(bodies)
    return files, M, C, I, collision(lo, hi)

def leg_box(lo, hi):
    return (0, -L/2000, (lo[2] + hi[2])/2), ET.Element('box', size=fmt((config.leg.width/1000, L/1000, hi[2] - lo[2])))

def head_box(lo, hi):
    return (0, 0, 0), ET.Element('box', size=fmt(np.array((config.head.width, config.head.depth, config.head.height))/1000))

def wheel_cylinder(lo, hi):
    return (lo + hi)/2, ET.Element('cylinder', radius=f'{config.wheels.dia/2000:.6g}', length=f'{hi[2] - lo[2]:.6g}')

robot = ET.Element('robot', name='ria')
ET.SubElement(ET.SubElement(robot, 'mujoco'), 'compiler', discardvisual='false', fusestatic='false')

def emit_link(name, files, M, C, I, collision):
    l = ET.SubElement(robot, 'link', name=name)
    for f in files:
        ET.SubElement(ET.SubElement(ET.SubElement(l, 'visual'), 'geometry'), 'mesh', filename=f'urdf/{f}', scale='0.001 0.001 0.001')
    inertial = ET.SubElement(l, 'inertial')
    ET.SubElement(inertial, 'origin', xyz=fmt(C))
    ET.SubElement(inertial, 'mass', value=f'{M:.6g}')
    ET.SubElement(inertial, 'inertia', **{k: f'{v:.6g}' for k, v in zip(['ixx', 'ixy', 'ixz', 'iyy', 'iyz', 'izz'], I[np.triu_indices(3)])})
    origin, geom = collision
    c = ET.SubElement(l, 'collision')
    ET.SubElement(c, 'origin', xyz=fmt(origin))
    ET.SubElement(c, 'geometry').append(geom)

def emit_joint(name, type, parent, child, T, **limit):
    j = ET.SubElement(robot, 'joint', name=name, type=type)
    ET.SubElement(j, 'origin', xyz=fmt(T[:3, 3]/1000), rpy=fmt(euler_from_matrix(T)))
    ET.SubElement(j, 'parent', link=parent)
    ET.SubElement(j, 'child', link=child)
    ET.SubElement(j, 'axis', xyz='0 0 1')
    ET.SubElement(j, 'limit', **{k: f'{v:.6g}' for k, v in limit.items()})

parts = {n: p for n, p in upperleg.leg().traverse() if p.obj is not None}
pick = lambda *names: [(n, parts[n]) for n in names]
encoders = [m for m in upperleg.meshes if m[0] == 'as5600']
wheel_z = parts['wheel'].obj.val().BoundingBox().center.z

head_link = link('head', [(n, p) for n, p in head.head().traverse() if p.obj is not None], head.meshes, (0, 0, 0), head_box)
upper = link('upper_leg', pick('upper_leg', 'pinion', 'sprocket_upper', 'belt', 'ring', 'sun', 'pulley', 'magnet_knee'),
             [m for m in upperleg.meshes if m[0] in ('5010_body', '5010_rotor', 'sg90_body')] + encoders[:1], (0, 0, 0), leg_box)
lower = link('lower_leg', pick('lower_leg', 'planet_0', 'planet_1', 'planet_2', 'magnet_ankle'),
             [m for m in upperleg.meshes if m[0] == 'gbm2804'] + encoders[1:], (0, L, 0), leg_box)
wheel = link('wheel', pick('wheel'), [], (0, 2*L, -wheel_z), wheel_cylinder)

emit_link('head', *head_link)
for side, hip in (('r', right), ('l', left)):
    emit_link(f'upper_leg_{side}', *upper)
    emit_link(f'lower_leg_{side}', *lower)
    emit_link(f'wheel_{side}', *wheel)
    emit_joint(f'hip_{side}', 'revolute', 'head', f'upper_leg_{side}', hip, lower=-1.9, upper=1.9, effort=0.25, velocity=8)
    emit_joint(f'knee_{side}', 'revolute', f'upper_leg_{side}', f'lower_leg_{side}', translation_matrix((0, -L, 0)), lower=-config.leg.knee_limit, upper=config.leg.knee_limit, effort=3, velocity=30)
    emit_joint(f'wheel_{side}', 'continuous', f'lower_leg_{side}', f'wheel_{side}', translation_matrix((0, -L, wheel_z)), effort=0.3, velocity=100)

tree = ET.ElementTree(robot)
ET.indent(tree)
tree.write(out / 'ria.urdf', xml_declaration=True, encoding='utf-8')
