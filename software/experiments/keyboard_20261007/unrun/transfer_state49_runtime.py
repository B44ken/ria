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
    def reset(self):self.phase_weight=0.;self.knee_target=0.;self.was_held=False;self.release_time=999.;self.filtered_speed=0.;self.speed_integral=0.;self.target_speed=0.
    def act(self):
        r=self.robot;u=r['imu_head'];g=u.gravity();om=u.ang_vel();s=r.state()
        pitch=math.atan2(-g[1],-g[2]);estimated_base_speed=float(s['speed']+s['height']*om[0])
        self.filtered_speed+=.1*(estimated_base_speed-self.filtered_speed)
        self.target_speed+=float(np.clip(r.fwd_goal-self.target_speed,-self.accel*.01,self.accel*.01))
        error=self.filtered_speed-self.target_speed
        self.speed_integral=float(np.clip(self.speed_integral+error*.01,-1.,1.))
        ref=float(np.clip(-.05+self.kv*error+self.ki*self.speed_integral,-.25,.15))
        ratio=float(np.clip(s['height']/.154,.4,1.)) if (r.jump_held or self.was_held or self.release_time<.6) else 1.
        d=float(np.clip(-self.pitch_kp*ratio*(pitch-ref)-self.pitch_kd*ratio**2*om[0],-self.dcap,self.dcap))
        c=float(np.clip(-.02*(r.turn_goal-om[2]),-.1,.1))
        if self.was_held and not r.jump_held:self.release_time=0.
        self.was_held=r.jump_held
        self.knee_target+=float(np.clip((-.9 if r.jump_held else (.2 if self.release_time<self.kick_time else 0.))-self.knee_target,-.02,.02))
        left=float(np.clip(.03-.5*(r['knee_l'].read()-self.knee_target)-.02*r['knee_l'].velocity(),-.2,.2))
        right=float(np.clip(-.03-.5*(r['knee_r'].read()+self.knee_target)-.02*r['knee_r'].velocity(),-.2,.2))
        if self.release_time<self.kick_time:
            self.knee_target=.2;left=self.kick;right=-self.kick
        self.release_time+=.01
        self.phase_weight=1. if r.jump_held else float(np.clip(3.-self.release_time,0.,1.))
        return np.asarray([-.5*r['knee_l'].read()*self.phase_weight,-.5*r['knee_r'].read()*self.phase_weight,left,right,d+c,-d+c],np.float32)
from botblocks import GymEnv,Plane
import json,numpy as np,math

from botblocks.subsys import Subsystem
from botblocks.rl.gymenv import SimVecEnv
import inspect,textwrap,copy
REAL=['neck_l','neck_r','knee_l','knee_r','wheel_l','wheel_r']
SCALE=np.array([.3,.3,.3,.3,.15,.15],np.float32)
class ResidualObserver(Subsystem):
 obs_dim=43
 def observe(self):
  b=self._robot;c=getattr(b,'feedback_controller',None)
  extra=np.zeros(6) if c is None else np.array([c.filtered_speed,c.speed_integral,c.target_speed,c.knee_target,float(c.was_held),min(c.release_time,3.)])
  task=np.array([getattr(b,'jump_peak',0.),float(getattr(b,'air_seen',False)),min(getattr(b,'land_ticks',0)/50.,1.),float(getattr(b,'qualified_landing',False))])
  return np.concatenate([b['imu_head'].observe(),*[b[n].observe() for n in REAL],b['command'].observe(),extra,task]).astype(np.float32)
class ResidualChannel(Subsystem):
 def __init__(self,index):super().__init__('residual_'+str(index));self.index=index
 def act_range(self):return (-1.,1.)
 def act(self,value):
  b=self._robot
  if self.index==0:b.base_control=b.feedback_controller.act()
  sub=b[REAL[self.index]];lo,hi=sub.act_range()
  sub.act(float(np.clip(b.base_control[self.index]+SCALE[self.index]*value*b.feedback_controller.phase_weight,lo,hi)))
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
                value=float(np.clip(base[i]+SCALE[i]*act[i]*b.feedback_controller.phase_weight,lo,hi))
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
from botblocks import Policy
import botblocks.rl.gymenv as gm
DT=.01;HORIZON=9.;GAMMA=.995
BASE='ria/keyboard-residual-20261007-jump04-moving'
INIT='ria/keyboard-residual-20261007-state49-init'
RESET_BASE=reset_feedback

def reset_feedback(b,e,rng):
 RESET_BASE(b,e,rng)
 b.tick=0;b.ground_z=float(b.state()['lowest']);b.jump_peak=0.;b.air_seen=False;b.land_ticks=0;b.qualified_landing=False;b.jump_failed=False;b.ever_fall=False;b.prev_held=False;b.last_grounded=bool(b.state()['ground']);b.release_eligible=False;b.reward_phi=0.

def update_jump_state(b):
 st=b.state();held=b.jump_held;clear=max(0.,float(st['lowest'])-b.ground_z)
 if held and not b.prev_held:
  b.jump_peak=0.;b.air_seen=False;b.land_ticks=0;b.qualified_landing=False;b.jump_failed=False;b.release_eligible=False
 if held and (clear>.01 or st['fall']):b.jump_failed=True
 if b.prev_held and not held:b.release_eligible=b.last_grounded and not b.jump_failed
 if st['fall']:b.ever_fall=True;b.jump_failed=True
 after=not held and b.feedback_controller.release_time<3.
 if after and b.release_eligible and not b.jump_failed:
  if b.feedback_controller.release_time<=1.4:b.jump_peak=max(b.jump_peak,min(clear,.2))
  if clear>.01:b.air_seen=True
 if after and b.air_seen and st['ground'] and not st['fall'] and st['upright']>.85:b.land_ticks+=1
 else:b.land_ticks=0
 if b.land_ticks>=50:b.qualified_landing=True
 b.prev_held=held;b.last_grounded=bool(st['ground']);return st

def no_reward(b,e):
 update_jump_state(b);b.tick+=1;e.reward(value=0.)

def reset_training(b,e,rng):
 install_residual_dispatch();reset_feedback(b,e,rng)
 b.goal=float(rng.uniform(0.,1.2));b.press_tick=int(rng.integers(150,301));b.release_tick=b.press_tick+int(rng.integers(70,151));b.input(b.goal,0.,False)

def reward_training(b,e):
 st=update_jump_state(b);fall=bool(st['fall']);timeout=b.tick+1>=round(HORIZON/DT);terminal=fall or timeout
 phi=0. if terminal else 500.*b.jump_peak
 shaping=GAMMA*phi-b.reward_phi;b.reward_phi=phi
 paid=(2.+500.*b.jump_peak) if timeout and not b.ever_fall and b.qualified_landing and b.release_eligible and not b.jump_failed else 0.
 ev=float(st['speed']-b.goal);ew=float(st['turn']);desired=.076 if b.jump_held else .154
 e.reward(upright=.02*max(0.,float(st['upright'])),tracking=.02*(math.exp(-(ev/.3)**2)+.5*math.exp(-(ew/.5)**2)),height=.015*math.exp(-((float(st['height'])-desired)/.04)**2),jump_shaping=shaping,qualified_jump=paid,fall=-100. if fall else 0.,premature=-1. if b.jump_held and b.jump_failed else 0.,done=fall)
 b.tick+=1;b.input(b.goal,0.,b.press_tick<=b.tick<b.release_tick)

original_save=gm.save_policy


def retry_save(model,path):
 for attempt in range(5):
  try:return original_save(model,path)
  except urllib.error.HTTPError as ex:
   if ex.code<500 or attempt==4:raise
   print('UPLOAD_RETRY',ex.code,attempt+1,flush=True);time.sleep(2**(attempt+1))
gm.save_policy=retry_save

def expanded_stats(old,new_values):return np.concatenate([old[:39],np.asarray(new_values,dtype=old.dtype),old[39:]])
class TransferInit(BaseCallback):
 def _on_training_start(self):
  old=source_policy.pi.policy.state_dict();new=self.model.policy.state_dict();changed=[]
  for name,value in old.items():
   if value.shape==new[name].shape:new[name].copy_(value)
   elif value.ndim==2 and value.shape[1]==45 and new[name].shape==(value.shape[0],49):
    new[name].zero_();new[name][:,:39]=value[:,:39];new[name][:,43:]=value[:,39:];changed.append(name)
   else:raise RuntimeError((name,value.shape,new[name].shape))
  assert len(changed)==2,changed;self.model.policy.load_state_dict(new)
  vn=self.model.get_env();vn.obs_rms.mean=expanded_stats(source_policy.vn.obs_rms.mean,[0,0,0,0]);vn.obs_rms.var=expanded_stats(source_policy.vn.obs_rms.var,[.01,1,1,1]);vn.obs_rms.count=source_policy.vn.obs_rms.count
  vn.training=False;vn.clip_reward=1e6;vn.ret_rms.mean=np.array(0.);vn.ret_rms.var=np.array(100.);vn.ret_rms.count=1.;vn.gamma=GAMMA
  self.model._last_obs=vn.normalize_obs(vn.get_original_obs())
  rng=np.random.default_rng(91401);old_obs=rng.normal(size=(100,45)).astype(np.float32);new_obs=np.concatenate([old_obs[:,:39],rng.normal(size=(100,4)).astype(np.float32),old_obs[:,39:]],axis=1)
  with torch.no_grad():
   a=source_policy.pi.policy.get_distribution(torch.as_tensor(old_obs)).distribution.mean
   b=self.model.policy.get_distribution(torch.as_tensor(new_obs)).distribution.mean
   delta=float(torch.max(torch.abs(a-b)))
  assert delta<1e-6,delta
  self.model.botblocks_spec.update(task='keyboard residual with explicit jump outcome state and smooth mode blend',observation_count=49,custom_runtime_required=True,parent_asset=BASE,parent_training_steps=int(source_policy.pi.num_timesteps),transfer_max_mean_delta=delta,validation_pending=True)
  print('STATE49_TRANSFER',json.dumps(dict(parent_steps=int(source_policy.pi.num_timesteps),max_mean_delta=delta,adapted_layers=changed,observations=49)),flush=True)
 def _on_step(self):return True

torch.set_num_threads(2)
source_policy=Policy(BASE)
b=ResidualRia();env=GymEnv([Plane(),b],subsys=[b[n] for n in CUSTOM],dt=DT,seconds=HORIZON,timestep=.005,reset=reset_training,reward=reward_training)
assert env.observation_space.shape==(49,) and env.action_space.shape==(6,)
env.train(save=INIT,n=16,shards=1,spacing=100,steps=0,net=[128,128],algorithm='ppo',learning_rate=.00005,n_steps=256,batch_size=512,n_epochs=4,gamma=GAMMA,gae_lambda=.97,ent_coef=.001,target_kl=.02,seed=91401,threads=2,callback=TransferInit())
print('STATE49_INIT_SAVED',INIT,flush=True)
actor=Policy(INIT,robot=b)
for speed in [0.,.4,.8,1.2]:
 for hold in [.7,1.1,1.5]:
  b.pos=[0.,0.,0.];b.rot=[0.,0.,0.]
  e=GymEnv([Plane(),b],subsys=[b[n] for n in CUSTOM],dt=DT,seconds=7.,timestep=.005,reset=reset_feedback,reward=no_reward);e.reset(seed=90206);actor.reset();first_fall=None;falls=0.;peak=0.;latency=None;release=2.+hold
  for k in range(700):
   t=k*DT;b.input(speed,0.,2.<=t<release);e.step(actor.act());st=b.state();now=(k+1)*DT
   if st['fall'] and first_fall is None:first_fall=now
   falls+=DT*bool(st['fall'])
   if now>=release and now<=release+1.4 and first_fall is None:
    clear=max(0.,float(st['lowest'])-b.ground_z);peak=max(peak,clear)
    if clear>.01 and latency is None:latency=now-release
  print('STATE49_INIT_CASE '+json.dumps(dict(speed=speed,hold=hold,valid=bool(b.qualified_landing and b.release_eligible and not b.jump_failed and not b.ever_fall),peak_before_fall=peak,first_fall=first_fall,fall_seconds=falls,latency=latency,qualified_landing=b.qualified_landing,jump_state_peak=b.jump_peak)),flush=True);e.close()
print('STATE49_INIT_COMPLETE',flush=True)
