from pathlib import Path
import json

import mujoco
import numpy as np
import pytest
import trimesh
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]


def json_parts(part, parent=np.eye(4)):
    origin = part.get('joint', {}).get('origin', {})
    local = np.eye(4)
    local[:3, :3] = Rotation.from_euler('xyz', origin.get('rot', [0, 0, 0])).as_matrix()
    local[:3, 3] = origin.get('pos', [0, 0, 0])
    world = parent @ local
    yield part, world
    for child in part.get('children', []):
        yield from json_parts(child, world)


def assert_same_surface(a, b):
    assert cKDTree(a).query(b)[0].max() < 5e-7
    assert cKDTree(b).query(a)[0].max() < 5e-7


def test_json_and_mujoco_match_cad_assembly():
    robot = json.loads((ROOT / 'bot.json').read_text())
    software = json.loads((ROOT / 'software/bot.json').read_text())
    assert software['parts'] == robot['parts']
    assert software['subsystems'] == robot['subsystems']
    model = mujoco.MjModel.from_xml_path(str(ROOT / 'ria.xml'))
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    points = []
    for part, world in json_parts(robot['parts']):
        body = model.body(part['name']).id
        np.testing.assert_allclose(world[:3, 3], data.xpos[body], atol=1e-12)
        np.testing.assert_allclose(world[:3, :3], data.xmat[body].reshape(3, 3), atol=1e-12)
        expected_mass = .4 if part['name'] == 'head' else .08 if part['name'].startswith('wheel') else .04
        assert part['mass'] == expected_mass
        for name in part['meshes']:
            mesh = trimesh.load(ROOT / robot['mesh_config']['includes'] / f'{name}.stl')
            points.append(trimesh.transform_points(mesh.vertices * robot['mesh_config']['scale'], world))
    assembly = trimesh.load(ROOT / 'build/ria.glb')
    selected = []
    for name in assembly.graph.nodes_geometry:
        if 'leg/' in name or name.startswith(('head_top_', 'head_bottom_', 'head_tray_')):
            transform, geometry = assembly.graph[name]
            selected.append(trimesh.transform_points(assembly.geometry[geometry].vertices, transform))
    assert len(points) == len(selected) == 43
    assert_same_surface(np.vstack(points), np.vstack(selected))

    compiled = []
    for geom in range(model.ngeom):
        mesh = model.geom_dataid[geom]
        start, count = model.mesh_vertadr[mesh], model.mesh_vertnum[mesh]
        vertices = model.mesh_vert[start:start + count]
        compiled.append(vertices @ data.geom_xmat[geom].reshape(3, 3).T + data.geom_xpos[geom])
    assert model.ngeom == 56
    assert_same_surface(np.vstack(compiled), assembly.to_mesh().vertices)


@pytest.mark.parametrize('knee_angle', [0, 1.2])
def test_mesh_ground_contact(knee_angle):
    spec = mujoco.MjSpec.from_file(str(ROOT / 'ria.xml'))
    spec.body('head').add_freejoint()
    spec.worldbody.add_geom(name='ground', type=mujoco.mjtGeom.mjGEOM_PLANE,
                            size=[1, 1, .1], pos=[0, 0, -.3])
    model = spec.compile()
    data = mujoco.MjData(model)
    data.joint('knee_r').qpos[0] = knee_angle
    data.joint('knee_l').qpos[0] = -knee_angle
    assert np.all(model.body_mass[1:] > 0)
    assert np.all(model.body_inertia[1:] > 0)
    assert .65 < model.body_mass.sum() < .75

    ground = model.geom('ground').id
    contacts = set()
    for _ in range(1000):
        mujoco.mj_step(model, data)
        for contact in data.contact:
            if ground in (contact.geom1, contact.geom2):
                other = contact.geom2 if contact.geom1 == ground else contact.geom1
                assert model.geom_type[other] == mujoco.mjtGeom.mjGEOM_MESH
                contacts.add(model.body(model.geom_bodyid[other]).name)

    assert {'wheel_l', 'wheel_r'} <= contacts
    assert np.isfinite(data.qpos).all() and np.isfinite(data.qvel).all()
    assert not data.warning.number.any()
