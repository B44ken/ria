import math, random
from botblocks import GymEnv, Plane
from ria import Ria

def reset(bot, env, _):
    starts = [random.uniform(0.15, 0.4)]
    while starts[-1] < 19:
        starts += [starts[-1] + random.uniform(2.5, 3.5)]
    bot.tags = {
      'jumps': [(st, random.uniform(0.4, 0.7)) for st in starts],
      'cmds': [(t, random.uniform(-0.04, 0.012), random.uniform(-0.004, 0.004)) for t in range(0, 24, 2)]
    }
    bot.input(0, 0, False)

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

GymEnv([Plane(), Ria()], dt=0.01, seconds=24, reward=reward, reset=reset) \
  .train(resume='ria/pi', save='ria/pi', save_steps=200_000, n=36, shards=1, n_steps=20000, n_epochs=1, lr=0.000)