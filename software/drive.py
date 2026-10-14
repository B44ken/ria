"""Drive an explicitly selected RIA policy with the keyboard."""

import argparse


def main(argv=None):
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument('--policy', required=True, help='Policy to test: project/name')
    policy = args.parse_args(argv).policy

    from botblocks import Plane, Policy, Keyboard, MujocoEnv
    from ria import Ria

    robot = Ria()
    keys = Keyboard()

    @robot.loop
    def keyboard_input(bot, env):
        speed = (('w' in keys) - ('s' in keys)) / 8
        turn = (('a' in keys) - ('d' in keys)) / 8
        bot.input(speed, turn, ' ' in keys)

    return MujocoEnv([Plane(), robot, keys]).run(Policy(policy, robot=robot))


if __name__ == '__main__':
    main()
