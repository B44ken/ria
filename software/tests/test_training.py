"""Offline regressions; these tests never contact Botblocks or run physics."""

import importlib.util
import math
from pathlib import Path
import random
import subprocess
import sys
from types import SimpleNamespace

import pytest


SOFTWARE = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(f'ria_test_{name}', SOFTWARE / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


train = load('train')
drive = load('drive')
ARGS = ['--resume', 'ria/jump', '--save', 'ria/test-new', '--lr', '0.0001', '--steps', '1000']


class Bot:
    def input(self, *command):
        self.command = command

    def state(self):
        return self.values


@pytest.mark.parametrize('name', ['train', 'drive'])
def test_import_never_loads_runtime_or_launches(name):
    # A separate interpreter detects top-level imports even if another test has
    # temporarily installed a mock runtime in sys.modules.
    result = subprocess.run([sys.executable, '-c', f'''
import runpy, sys
sys.modules['botblocks'] = None
runpy.run_path({str(SOFTWARE / (name + '.py'))!r}, run_name='inspection')
'''], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_preview_does_not_import_runtime(monkeypatch):
    monkeypatch.setitem(sys.modules, 'botblocks', None)
    plan = train.main(ARGS)
    assert plan['launch'] is False
    assert plan['training']['resume'] == 'ria/jump'
    assert plan['rollout_transitions'] == 720_000
    assert plan['expected_additional_transitions'] == 720_000


@pytest.mark.parametrize('value', ['0', '-0.001', 'nan', 'inf'])
def test_rejects_nonlearning_or_invalid_rate(value):
    with pytest.raises(SystemExit):
        train.main(ARGS + ['--lr', value])


@pytest.mark.parametrize('extra', [
    ['--save', 'ria/jump.zip'], ['--steps', '0'], ['--n', '0'],
    ['--shards', '5'], ['--n-steps', '-1'], ['--seed', '-1'],
    ['--save', '/tmp/model'], ['--save', 'ria/../jump'],
])
def test_rejects_overwrite_or_invalid_plan(extra):
    with pytest.raises(SystemExit):
        train.main(ARGS + extra)


@pytest.mark.parametrize('flags', [[], ['--confirmed-idle'], ['--confirmed-new-save']])
def test_launch_requires_both_operator_checks(monkeypatch, flags):
    monkeypatch.setitem(sys.modules, 'botblocks', None)
    with pytest.raises(SystemExit):
        train.main(ARGS + ['--launch'] + flags)


def test_explicit_launch_forwards_the_reviewed_options(monkeypatch):
    calls = []

    class Gym:
        def __init__(self, things, **kwargs):
            calls.append(('env', kwargs))

        def train(self, **kwargs):
            calls.append(('train', kwargs))
            return 'test-model'

    monkeypatch.setitem(sys.modules, 'botblocks', SimpleNamespace(GymEnv=Gym, Plane=object))
    monkeypatch.setitem(sys.modules, 'ria', SimpleNamespace(Ria=object))
    assert train.main(ARGS + ['--launch', '--confirmed-idle', '--confirmed-new-save']) == 'test-model'
    assert calls[0][1]['reward'] is train.reward
    assert calls[0][1]['reset'] is train.reset
    assert calls[1][1] == train.training_options(train.parser().parse_args(ARGS))


def test_resets_use_supplied_rng_and_expose_first_command():
    first, second, third = Bot(), Bot(), Bot()
    train.reset(first, None, random.Random(11))
    random.seed(500)  # Global random changes must not change this episode.
    train.reset(second, None, random.Random(11))
    train.reset(third, None, random.Random(12))
    assert first.tags == second.tags
    assert first.tags != third.tags
    _, speed, turn = first.tags['cmds'][0]
    assert first.command == (speed, turn, False)
    assert all(-0.04 <= speed <= 0.012 and -0.004 <= turn <= 0.004
               for _, speed, turn in first.tags['cmds'])
    assert all(0.4 <= hold <= 0.7 for _, hold in first.tags['jumps'])


@pytest.mark.parametrize('time, held, launch, height', [
    (0.199, False, False, 0.16), (0.2, True, False, 0.08),
    (0.699, True, False, 0.08), (0.7, False, True, 0.20),
    (1.149, False, True, 0.20), (1.15, False, False, 0.16),
])
def test_reward_phase_boundaries(time, held, launch, height):
    bot = Bot()
    bot.tags = {'jumps': [(0.2, 0.5)], 'cmds': [(0, 0.01, 0.002)]}
    bot.values = dict(upright=1, height=height, speed=0.01, turn=0.002,
                      rise=0.2, lowest=0.08, fall=False)
    terms = {}
    env = SimpleNamespace(time=lambda: time, reward=lambda **kwargs: terms.update(kwargs))
    train.reward(bot, env)
    assert bot.command == (0.01, 0.002, held)
    assert terms['posture'] == pytest.approx(2)
    assert terms['motion'] == pytest.approx(1)
    assert terms['jump'] == pytest.approx([1.2 if launch else 0, 12])
    assert terms['done'] is False


def test_reward_switches_commands_and_terminates_falls():
    bot = Bot()
    bot.tags = {'jumps': [], 'cmds': [(0, 0.01, 0.002), (2, -0.02, -0.003)]}
    bot.values = dict(upright=0.5, height=0.16, speed=0, turn=0,
                      rise=-0.1, lowest=0.02, fall=True)
    terms = {}
    train.reward(bot, SimpleNamespace(time=lambda: 2, reward=lambda **kwargs: terms.update(kwargs)))
    assert bot.command == (-0.02, -0.003, False)
    assert terms['motion'] == pytest.approx(-0.02 ** 2 + math.cos(0.003))
    assert terms['fall'] == [True, -40]
    assert terms['done'] is True


def test_drive_uses_selected_checkpoint_and_keyboard(monkeypatch):
    calls = []
    keys = {'w', 'a', ' '}

    class Robot(Bot):
        def loop(self, fn):
            self.callback = fn
            return fn

    robot = Robot()

    class Env:
        def __init__(self, things):
            assert things[1:] == [robot, keys]

        def run(self, policy):
            robot.callback(robot, self)
            return policy

    def policy(path, **kwargs):
        calls.append((path, kwargs))
        return 'test-policy'

    monkeypatch.setitem(sys.modules, 'botblocks', SimpleNamespace(
        Plane=object, Policy=policy, Keyboard=lambda: keys, MujocoEnv=Env))
    monkeypatch.setitem(sys.modules, 'ria', SimpleNamespace(Ria=lambda: robot))
    assert drive.main(['--policy', 'ria/jump']) == 'test-policy'
    assert calls == [('ria/jump', {'robot': robot})]
    assert robot.command == (0.125, 0.125, True)
