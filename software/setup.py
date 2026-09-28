import botblocks as bl
ria = bl.Robot('stuff/ria')

@ria.ready
def _(bot, env):
  pass

@ria.loop
def _loop(bot, env):
  pass

bl.MujocoEnv([bl.Plane(), bl.Box(size=0.08, pos=[1,0,0]), ria]).start()