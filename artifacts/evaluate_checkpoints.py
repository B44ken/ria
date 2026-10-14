"""Small local checkpoint comparison. Reads models; never trains or saves policies."""

import json
import math
from pathlib import Path
import signal
import time

import numpy as np
import torch
from botblocks import GymEnv, Plane, Policy
from ria import Ria
from train import reset, reward


def evaluate(path, seeds=(10001, 10002)):
    robot = Ria()
    policy = Policy(str(path), robot=robot)
    policy.vn.training = False
    env = GymEnv([Plane(), robot], subsys=[robot[name] for name in policy.spec['subsys']],
                 dt=policy.dt, timestep=policy.timestep, seconds=24, reset=reset, reward=reward)
    assert env.observation_space.shape == policy.pi.observation_space.shape
    assert env.action_space.shape == policy.pi.action_space.shape
    assert np.allclose(env.action_space.low, policy.pi.action_space.low)
    assert np.allclose(env.action_space.high, policy.pi.action_space.high)
    results = []
    try:
        for seed in seeds:
            observation, _ = env.reset(seed=seed)
            state, episode_start = None, True
            samples = []
            for step in range(env.horizon):
                normalized = policy.vn.normalize_obs(observation).astype(np.float32)
                action, state = policy.pi.predict(normalized, state=state,
                    episode_start=np.array([episode_start]), deterministic=True)
                episode_start = False
                observation, _, terminated, truncated, _ = env.step(action)
                values = robot.state()
                samples.append(dict(time=(step + 1) * policy.dt, **values,
                    speed_goal=robot.fwd_goal, turn_goal=robot.turn_goal))
                if terminated or truncated:
                    break
            events = []
            for start, hold in robot.tags['jumps']:
                release = start + hold
                window = [s for s in samples if release <= s['time'] < release + 1.2]
                if not window:
                    continue
                # Wheel radius is 0.03 m, derived from tracked wheel mesh extents.
                peak = max(s['lowest'] - 0.03 for s in window)
                landing_ticks = 0
                stable = False
                airborne = False
                for s in window:
                    airborne |= s['lowest'] - 0.03 > 0.05
                    contact = s['ground'] and not s['fall'] and s['upright'] >= 0.9
                    landing_ticks = landing_ticks + 1 if airborne and contact else 0
                    stable |= landing_ticks * policy.dt >= 0.2
                events.append({'release': release, 'peak_clearance_m': peak,
                               'above_5cm': peak > 0.05, 'stable_landing': stable})
            result = {'seed': seed, 'duration_s': len(samples) * policy.dt,
                'completed': len(samples) == env.horizon and not samples[-1]['fall'],
                'fell': bool(samples[-1]['fall']),
                'speed_rmse_m_s': math.sqrt(np.mean([(s['speed'] - s['speed_goal']) ** 2 for s in samples])),
                'turn_rmse_rad_s': math.sqrt(np.mean([(s['turn'] - s['turn_goal']) ** 2 for s in samples])),
                'jump_events': events}
            results.append(result)
            print(json.dumps({'policy': path.name, **result}), flush=True)
    finally:
        env.close()
    return results


if __name__ == '__main__':
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('evaluation time limit')))
    signal.alarm(180)
    torch.set_num_threads(2)
    started = time.monotonic()
    results = {}
    for name in ('jump', 'pi4'):
        results[name] = evaluate(Path(__file__).parent / f'{name}.zip')
    report = {'wall_time_s': time.monotonic() - started, 'seeds': [10001, 10002],
        'wheel_radius_m': 0.03, 'landing_definition': 'after >5cm clearance, 0.2s consecutive ground and upright >=0.9 without fall within 1.2s of release',
        'episodes': results}
    (Path(__file__).parent / 'evaluation-results.json').write_text(json.dumps(report, indent=2))
    print(json.dumps({'wall_time_s': report['wall_time_s']}), flush=True)
