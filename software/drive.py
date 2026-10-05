import sys, os, math, random
sys.path.append(os.getcwd())

from botblocks import GymEnv, Plane, Policy, Keyboard, MujocoEnv
from ria import Ria

robot = Ria()
keys = Keyboard()

@robot.loop
def _(bot, env):
    speed = (('w' in keys) - ('s' in keys)) / 8
    turn =  (('a' in keys) - ('d' in keys)) / 8
    jump = ' ' in keys
    bot.input(speed, turn, jump)

MujocoEnv([Plane(), robot, keys]).run(Policy('ria/pi4', robot=robot))