"""Preview or explicitly launch a bounded RIA continuation run."""

import argparse
import json
import math


def reset(bot, env, rng):
    starts = [float(rng.uniform(0.15, 0.4))]
    while starts[-1] < 19:
        starts.append(starts[-1] + float(rng.uniform(2.5, 3.5)))
    bot.tags = {
        'jumps': [(st, float(rng.uniform(0.4, 0.7))) for st in starts],
        'cmds': [(t, float(rng.uniform(-0.04, 0.012)), float(rng.uniform(-0.004, 0.004)))
                 for t in range(0, 24, 2)]
    }
    # The first observation should contain the episode's first command.
    _, speed, turn = bot.tags['cmds'][0]
    bot.input(speed, turn, False)


def reward(bot, env):
    t = env.time()
    held = any(start <= t < start + hold for start, hold in bot.tags['jumps'])
    launch = any(start + hold <= t < start + hold + 0.45 for start, hold in bot.tags['jumps'])
    _, speed, heading = next(c for c in reversed(bot.tags['cmds']) if c[0] <= t)
    bot.input(speed, heading, held)
    
    s = bot.state()
    target = 0.08 if held else 0.20 if launch else 0.16
    posture = 1 + s['upright'] - 400 * (s['height'] - target) ** 2
    env.reward(motion=-(s['speed'] - speed) ** 2 + math.cos(s['turn'] - heading),
               jump=[max(0, s['rise']) + 20 * max(0, s['lowest'] - 0.03) if launch else 0, 12],
               posture=posture, fall=[s['fall'], -40], done=s['fall'])

def parser():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument('--resume', required=True, help='Validated source policy: project/name')
    args.add_argument('--save', required=True, help='New, unused destination: project/name')
    args.add_argument('--lr', required=True, type=float, help='Explicit positive learning rate')
    args.add_argument('--steps', required=True, type=int, help='Additional transitions requested')
    args.add_argument('--n', type=int, default=36)
    args.add_argument('--shards', type=int, default=1)
    args.add_argument('--n-steps', type=int, default=20_000)
    args.add_argument('--n-epochs', type=int, default=1)
    args.add_argument('--save-steps', type=int, default=200_000)
    args.add_argument('--seed', type=int, default=0)
    args.add_argument('--launch', action='store_true', help='Launch after preview review')
    args.add_argument('--confirmed-idle', action='store_true',
                      help='Operator has confirmed no conflicting training run is active')
    args.add_argument('--confirmed-new-save', action='store_true',
                      help='Operator has checked that the destination asset does not exist')
    return args


def policy_path(value):
    value = value.removesuffix('.zip')
    if len(value.split('/')) != 2 or any(
        not part or part in ('.', '..') or any(char.isspace() for char in part)
        or '\\' in part for part in value.split('/')
    ):
        raise ValueError('policy paths must be project/name, optionally ending in .zip')
    return value


def training_options(args):
    resume, save = policy_path(args.resume), policy_path(args.save)
    if resume == save:
        raise ValueError('save must differ from resume to preserve the source checkpoint')
    if not math.isfinite(args.lr) or args.lr <= 0:
        raise ValueError('lr must be finite and positive; zero disables learning')
    for name in ('steps', 'n', 'shards', 'n_steps', 'n_epochs', 'save_steps'):
        if getattr(args, name) <= 0:
            raise ValueError(f'{name} must be positive')
    if args.n % args.shards:
        raise ValueError('n must be divisible by shards')
    if args.seed < 0:
        raise ValueError('seed must be nonnegative')
    return dict(resume=resume, save=save, lr=args.lr, steps=args.steps,
                n=args.n, shards=args.shards, n_steps=args.n_steps,
                n_epochs=args.n_epochs, save_steps=args.save_steps, seed=args.seed)


def main(argv=None):
    arg_parser = parser()
    args = arg_parser.parse_args(argv)
    try:
        options = training_options(args)
    except ValueError as error:
        arg_parser.error(str(error))
    rollout = options['n'] * options['n_steps']
    plan = {'environment': {'dt': 0.01, 'seconds': 24}, 'training': options,
            'rollout_transitions': rollout,
            'expected_additional_transitions': math.ceil(options['steps'] / rollout) * rollout,
            'launch': args.launch}
    print(json.dumps(plan, indent=2))
    if not args.launch:
        return plan
    if not args.confirmed_idle or not args.confirmed_new_save:
        arg_parser.error('launch requires --confirmed-idle and --confirmed-new-save')

    # Importing this module or previewing options must never start a job.
    from botblocks import GymEnv, Plane
    from ria import Ria

    return GymEnv([Plane(), Ria()], dt=0.01, seconds=24, reward=reward, reset=reset).train(**options)


if __name__ == '__main__':
    main()
