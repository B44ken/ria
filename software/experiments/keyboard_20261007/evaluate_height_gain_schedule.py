"""Bounded retries for transient read failures only; never retry auth failures."""
import urllib.request
import urllib.error
import time

_original_urlopen = urllib.request.urlopen

def retry_read_urlopen(request, *args, **kwargs):
    method = request.get_method() if isinstance(request, urllib.request.Request) else 'GET'
    for attempt in range(5):
        try:
            return _original_urlopen(request, *args, **kwargs)
        except urllib.error.HTTPError as error:
            if method != 'GET' or error.code < 500 or attempt == 4:
                raise
            print('READ_RETRY', error.code, attempt + 1, flush=True)
            time.sleep(2 ** (attempt + 1))

urllib.request.urlopen = retry_read_urlopen
from botblocks import Robot, Command

class Ria(Robot):
    def __init__(self, mode='train'):
        super().__init__('ria/robot')
        self['command'] = Command(n = 3)
        self.fwd_goal, self.turn_goal, self.jump_held = 0.0, 0.0, False

    def spec(self):
        return {**super().spec(), 'cls': 'Robot'}

    def reset(self):
        super().reset()
        self.fwd_goal, self.turn_goal = 0.0, 0.0
        self.jump_held = False
        self.jump_peak, self.landing_ticks = 0.0, 0
        self['command'].set([0, 0, 0])

    def input(self, fwd: float, turn: float, jump: bool):
      self.fwd_goal, self.turn_goal = fwd, turn
      self.jump_held = jump
      self['command'].set([fwd, turn, int(jump)])
  
    def state(self, wheel_zone = 0.04, fall_angle = 0.7):
        U = self['imu_head']
        pos = U.pos()
        head = pos[2]
        upright = -U.gravity()[2]
        lowest = min(self['wheel_l'].pose.pos[2], self['wheel_r'].pose.pos[2])
        ground = max(self['wheel_l'].pose.pos[2], self['wheel_r'].pose.pos[2]) < wheel_zone
        legs = U.to_body([self[name].pose.pos - pos for name in ('wheel_l', 'wheel_r', 'neck_l', 'neck_r')])
        splay = max(abs(legs[0, 1] + legs[1, 1]), abs(legs[2, 1] + legs[3, 1]))
        knee = min(self['knee_l'].pose.pos[2], self['knee_r'].pose.pos[2]) < lowest
        fall = upright < fall_angle or head - lowest < wheel_zone
        rise = (U.vel_world()[2] + min(self['imu_wheel_l'].vel_world()[2], self['imu_wheel_r'].vel_world()[2])) / 2
      
        return {
            'height': head - lowest,
            'lowest': lowest,
            'speed': U.vel()[1],
            'turn': U.ang_vel()[2],
            'upright': -U.gravity()[2],
            'ground': ground,
            'knee': knee,
            'splay': splay,
            'rise': rise,
            'fall': fall
        }
import math,numpy as np
class RampedFeedbackController:
    spec={'subsys':['neck_l','neck_r','knee_l','knee_r','wheel_l','wheel_r']}
    def __init__(self,robot,kv=.2,ki=.02,accel=1.5,dcap=.8,pitch_kp=2.,pitch_kd=.2,kick=.08,kick_time=.1):
        self.kick=kick;self.kick_time=kick_time;self.robot=robot;self.kv=kv;self.ki=ki;self.accel=accel;self.dcap=dcap;self.pitch_kp=pitch_kp;self.pitch_kd=pitch_kd;self.reset()
    def reset(self):self.knee_target=0.;self.was_held=False;self.release_time=999.;self.filtered_speed=0.;self.speed_integral=0.;self.target_speed=0.
    def act(self):
        r=self.robot;u=r['imu_head'];g=u.gravity();om=u.ang_vel();s=r.state()
        pitch=math.atan2(-g[1],-g[2]);estimated_base_speed=float(s['speed']+s['height']*om[0])
        self.filtered_speed+=.1*(estimated_base_speed-self.filtered_speed)
        self.target_speed+=float(np.clip(r.fwd_goal-self.target_speed,-self.accel*.01,self.accel*.01))
        error=self.filtered_speed-self.target_speed
        self.speed_integral=float(np.clip(self.speed_integral+error*.01,-1.,1.))
        ref=float(np.clip(-.05+self.kv*error+self.ki*self.speed_integral,-.25,.15))
        ratio=float(np.clip(s['height']/.154,.4,1.)) if (r.jump_held or self.was_held or self.release_time<.6) else 1.
        d=float(np.clip(-self.pitch_kp*ratio**KP_EXP*(pitch-ref)-self.pitch_kd*ratio**KD_EXP*om[0],-self.dcap,self.dcap))
        c=float(np.clip(-.02*(r.turn_goal-om[2]),-.1,.1))
        if self.was_held and not r.jump_held:self.release_time=0.
        self.was_held=r.jump_held
        self.knee_target+=float(np.clip((-.9 if r.jump_held else (.2 if self.release_time<self.kick_time else 0.))-self.knee_target,-.02,.02))
        left=float(np.clip(.03-.5*(r['knee_l'].read()-self.knee_target)-.02*r['knee_l'].velocity(),-.2,.2))
        right=float(np.clip(-.03-.5*(r['knee_r'].read()+self.knee_target)-.02*r['knee_r'].velocity(),-.2,.2))
        if self.release_time<self.kick_time:
            self.knee_target=.2;left=self.kick;right=-self.kick
        self.release_time+=.01
        return np.asarray([-.5*r['knee_l'].read(),-.5*r['knee_r'].read(),left,right,d+c,-d+c],np.float32)
from botblocks import GymEnv,Plane
import json,numpy as np,math

from botblocks.subsys import Subsystem
from botblocks.rl.gymenv import SimVecEnv
import inspect,textwrap,copy
REAL=['neck_l','neck_r','knee_l','knee_r','wheel_l','wheel_r']
SCALE=np.array([.3,.3,.3,.3,.15,.15],np.float32)
class ResidualObserver(Subsystem):
 obs_dim=39
 def observe(self):
  b=self._robot;c=getattr(b,'feedback_controller',None)
  extra=np.zeros(6) if c is None else np.array([c.filtered_speed,c.speed_integral,c.target_speed,c.knee_target,float(c.was_held),min(c.release_time,3.)])
  return np.concatenate([b['imu_head'].observe(),*[b[n].observe() for n in REAL],b['command'].observe(),extra]).astype(np.float32)
class ResidualChannel(Subsystem):
 def __init__(self,index):super().__init__('residual_'+str(index));self.index=index
 def act_range(self):return (-1.,1.)
 def act(self,value):
  b=self._robot
  if self.index==0:b.base_control=b.feedback_controller.act()
  sub=b[REAL[self.index]];lo,hi=sub.act_range()
  sub.act(float(np.clip(b.base_control[self.index]+SCALE[self.index]*value*float(b.jump_held or b.feedback_controller.release_time<=2.5),lo,hi)))
class ResidualRia(Ria):
 def __init__(self):
  super().__init__();self['feedback_obs']=ResidualObserver('feedback_obs')
  for i in range(6):self['residual_'+str(i)]=ResidualChannel(i)
CUSTOM=['feedback_obs']+['residual_'+str(i) for i in range(6)]
def reset_feedback(b,e,rng):
 b.feedback_controller=RampedFeedbackController(b,kv=.6,accel=1.,dcap=.8,pitch_kp=4.,pitch_kd=.2,kick=.4,kick_time=.08)
 b.base_control=np.zeros(6);b.input(0.,0.,False)
def no_reward(b,e):e.reward(value=0.)
source=textwrap.dedent(inspect.getsource(SimVecEnv.step_wait))
old="""    ctrl = []
    for subs, act in zip(self.act_subs, self._actions):    # every robot's targets in one message
        for s, a in zip(subs, act):
            p = s.provider; ctrl.append([f'{p.on}/{p.name}', float(a)])
"""
new="""    ctrl = []
    for subs, act in zip(self.act_subs, self._actions):
        if subs[0].name == 'residual_0':
            b=subs[0]._robot
            assert all(s._robot is b for s in subs)
            base=b.feedback_controller.act()
            b.base_control=base.copy()
            for i,name in enumerate(REAL):
                s=b[name];lo,hi=s.act_range();p=s.provider
                value=float(np.clip(base[i]+SCALE[i]*act[i]*float(b.jump_held or b.feedback_controller.release_time<=2.5),lo,hi))
                ctrl.append([f'{p.on}/{p.name}',value])
        else:
            for s,a in zip(subs,act):
                p=s.provider;ctrl.append([f'{p.on}/{p.name}',float(a)])
"""
assert source.count(old)==1,source
namespace=dict(SimVecEnv.step_wait.__globals__);namespace.update(globals());exec(source.replace(old,new),namespace)
SimVecEnv.step_wait=namespace['step_wait']
SimVecEnv.step_wait._residual_ready=True
def install_residual_dispatch():
 from botblocks.rl.gymenv import SimVecEnv as WorkerVec
 if getattr(WorkerVec.step_wait,'_residual_ready',False):return
 worker_source=textwrap.dedent(inspect.getsource(WorkerVec.step_wait))
 assert worker_source.count(old)==1,worker_source
 worker_namespace=dict(WorkerVec.step_wait.__globals__);worker_namespace.update(globals())
 exec(worker_source.replace(old,new),worker_namespace)
 WorkerVec.step_wait=worker_namespace['step_wait'];WorkerVec.step_wait._residual_ready=True
 print('RESIDUAL_WORKER_DISPATCH_READY',flush=True)
print('RESIDUAL_INTERFACE_READY',flush=True)

import torch,time,urllib.error
from stable_baselines3.common.callbacks import BaseCallback
import botblocks.rl.gymenv as gm
BASE='ria/keyboard-residual-20261007-jump03-stationary'
SAVE='ria/keyboard-residual-20261007-jump04-moving'
BASE_RESET=reset_feedback

def reset_training(b,e,rng):
 install_residual_dispatch()
 BASE_RESET(b,e,rng)
 b.tick=0;b.goal=float(rng.choice([0.,.4,.8,1.2]));b.press_tick=200;b.release_tick=200+int(rng.integers(70,151))
 b.ground_z=float(b.state()['lowest']);b.peak=0.;b.air_seen=False;b.land_ticks=0;b.landing_paid=False
 b.input(b.goal,0.,False)

def reward_training(b,e):
 s=b.state();t=(b.tick+1)*.01;held=b.jump_held
 release=b.release_tick*.01;after=t>=release
 ev=float(s['speed']-b.goal);ew=float(s['turn']);fall=bool(s['fall'])
 clear=max(0.,float(s['lowest'])-b.ground_z)
 peak_delta=0.
 if after and t<=release+1.4:
  capped=min(clear,.2);peak_delta=max(0.,capped-b.peak);b.peak=max(b.peak,capped)
 if after and clear>.01:b.air_seen=True
 if after and b.air_seen and s['ground'] and not fall and s['upright']>.85:b.land_ticks+=1
 else:b.land_ticks=0
 landing=0.
 if b.land_ticks>=50 and not b.landing_paid:landing=10.;b.landing_paid=True
 desired=.076 if held else .154
 height=math.exp(-((float(s['height'])-desired)/.04)**2)
 track=math.exp(-(ev/.3)**2)+.5*math.exp(-(ew/.5)**2)
 premature=held and clear>.01
 e.reward(upright=.02*max(0.,float(s['upright'])),tracking=.02*track,height=.015*height,
          jump=300.*peak_delta,landing=landing,fall=-20. if fall else 0.,premature=-1. if premature else 0.,
          done=fall)
 b.tick+=1;b.input(b.goal,0.,b.press_tick<=b.tick<b.release_tick)

original_save=gm.save_policy


def retry_save(model,path):
 for attempt in range(5):
  try:return original_save(model,path)
  except urllib.error.HTTPError as ex:
   if ex.code<500 or attempt==4:raise
   print('UPLOAD_RETRY',ex.code,attempt+1,flush=True);time.sleep(2**(attempt+1))
gm.save_policy=retry_save
class Progress(BaseCallback):
 def _on_training_start(self):
  vn=self.model.get_env()
  vn.obs_rms.mean=OBS_MEAN.copy();vn.obs_rms.var=OBS_VAR.copy();vn.obs_rms.count=OBS_COUNT
  vn.training=False
  self.model._last_obs=vn.normalize_obs(vn.get_original_obs())
  self.model.ep_info_buffer.clear();self.model.ep_success_buffer.clear()
  self.last=self.num_timesteps
  self.model.botblocks_spec.update(task='physical feedback plus learned residual keyboard jump',custom_runtime_required=True,observation_count=45,action_semantics='six residuals; physical = clipped baseline + scale * residual',residual_scale=SCALE.tolist(),validation_pending=True)
  print('RESIDUAL_TRAIN_INITIALIZED',json.dumps({'obs':self.model.observation_space.shape,'act':self.model.action_space.shape}),flush=True)
 def _on_step(self):
  if self.num_timesteps-self.last>=65536:
   retry_save(self.model,SAVE+'-checkpoint');self.last=self.num_timesteps
   print('RESIDUAL_CHECKPOINT',self.num_timesteps,flush=True)
  return True

from botblocks import Policy
b=ResidualRia();actor=Policy(SAVE,robot=b)
for KP_EXP,KD_EXP in [(1.,1.),(1.,2.),(2.,1.),(2.,2.)]:
 for speed in [0.,.4,.8,1.2]:
  for hold in [.7,1.1,1.5]:
   e=GymEnv([Plane(),b],subsys=[b[n] for n in CUSTOM],dt=.01,seconds=7.,timestep=.005,reset=reset_feedback,reward=no_reward);e.reset(seed=90206);actor.reset()
   ground=float(b.state()['lowest']);peak=0.;press_air=0.;hold_fall=0.;falls=0.;land=0;landed=False;takeoff=None;at_release=None;prepress=None;takeoff_speed=None
   release=2.+hold
   for k in range(700):
    t=k*.01;held=2.<=t<release
    if k==200:prepress=float(b.state()['speed'])
    if k==round(release*100):at_release=bool(b.state()['ground'])
    b.input(speed,0.,held);e.step(actor.act());s=b.state();now=(k+1)*.01;clear=max(0.,float(s['lowest'])-ground)
    falls+=.01*bool(s['fall'])
    if held:press_air+=.01*(clear>.01);hold_fall+=.01*bool(s['fall'])
    if now>=release:
     if now<=release+1.4 and falls==0:
      peak=max(peak,clear)
      if takeoff is None and clear>.01:takeoff=now-release;takeoff_speed=float(s['speed'])
     if takeoff is not None and s['ground'] and not s['fall'] and s['upright']>.85:land+=1
     else:land=0
     if land>=50:landed=True
   valid=bool(at_release and press_air==0 and hold_fall==0 and takeoff is not None and landed and falls==0)
   print('RESIDUAL_JUMP_CASE '+json.dumps(dict(kp_exponent=KP_EXP,kd_exponent=KD_EXP,speed=speed,hold=hold,valid=valid,peak=peak,fall_seconds=falls,press_airborne=press_air,hold_fall=hold_fall,grounded_at_release=at_release,stable_landing=landed,takeoff_latency=takeoff,prepress_speed=prepress,takeoff_speed=takeoff_speed)),flush=True)
   e.close()
print('GAIN_SCHEDULE_EVAL_COMPLETE',flush=True)
