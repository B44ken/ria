from pathlib import Path

import mujoco
import numpy as np
import pytest


@pytest.mark.parametrize('knee_angle', [0, 1.2])
def test_mesh_ground_contact(knee_angle):
    spec = mujoco.MjSpec.from_file(str(Path(__file__).resolve().parents[1] / 'ria.xml'))
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
