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


KP_EXP=1.;KD_EXP=2.;DT=.01
def scenarios():
    out=[]
    for speed in [-.5,0.,.5,1.,1.5]:
        out.append(dict(name='speed_'+str(speed),seconds=6.,commands=[(0.,0.,0.,False),(1.,speed,0.,False),(4.,0.,0.,False)]))
    for speed in [0.,.6]:
        for turn in [-1.5,-.75,.75,1.5]:
            out.append(dict(name='turn_'+str(speed)+'_'+str(turn),seconds=6.,commands=[(0.,speed,0.,False),(1.,speed,turn,False),(3.,speed,-turn,False),(5.,0.,0.,False)]))
    out.append(dict(name='taps_reverse_diagonal',seconds=12.,commands=[(0.,0.,0.,False),(.5,1.5,0.,False),(.7,0.,0.,False),(1.5,-.5,0.,False),(1.8,0.,0.,False),(3.,1.,1.5,False),(6.,-.5,-1.5,False),(9.,0.,0.,False)]))
    for speed in [0.,.4,.8,1.2]:
        for hold in [.7,1.1,1.5]:
            out.append(dict(name='jump_'+str(speed)+'_'+str(hold),seconds=7.,press=2.,release=2.+hold,commands=[(0.,speed,0.,False),(2.,speed,0.,True),(2.+hold,speed,0.,False)]))
    for angle in [-1.25,-.95,.95,1.25]:
        out.append(dict(name='recover_'+str(angle),seconds=8.,tilt=angle,commands=[(0.,0.,0.,False)]))
    return out



from botblocks import Policy
rng=np.random.default_rng(90301)
torch.set_num_threads(2)
cases=[]
for i in range(24):
 v=float(rng.uniform(0.,1.2));press=round(float(rng.uniform(1.5,3.)),2);hold=round(float(rng.uniform(.7,1.5)),2)
 cases.append(dict(name='random_jump_'+str(i),seconds=press+hold+4.,press=press,release=press+hold,tilt=float(rng.uniform(-.03,.03)),commands=[(0.,v,0.,False),(press,v,0.,True),(press+hold,v,0.,False)]))
b=ResidualRia();actor=Policy(SAVE,robot=b)
for case in cases:
 b.pos=[0.,0.,0.];b.rot=[case.get("tilt",0.),0.,0.]
 e=GymEnv([Plane(),b],subsys=[b[n] for n in CUSTOM],dt=DT,seconds=case['seconds'],timestep=.005,reset=reset_feedback,reward=no_reward);e.reset(seed=90206)
 actor.reset();ground=float(b.state()['lowest']);initial_pose=dict(root_pos=list(b.pos),root_rot=list(b.rot),wheel_z=ground,head_z=float(b['imu_head'].pos()[2]),upright=float(b.state()['upright']),velocity=list(map(float,b['imu_head'].vel_world())),gyro=list(map(float,b['imu_head'].ang_vel())));falls=0.;knees=0.;first_fall=None;peak=0.;press_air=0.;hold_fall=0.;landing=0;landed=False;takeoff=None;at_release=None;prepress=None;takeoff_speed=None;squat_start=None;squat_min=None
 speed_errors=[];turn_errors=[];scored=set();last_v=last_w=None;vstart=wstart=0.;was_held=False
 for k in range(round(case['seconds']/DT)):
  t=round(k*DT,8);_,v,w,held=next(c for c in reversed(case['commands']) if c[0]<=t+1e-8)
  if v!=last_v:vstart=t;last_v=v
  if w!=last_w:wstart=t;last_w=w
  if held and not was_held:prepress=float(b.state()['speed']);squat_start=float(b.state()['height'])
  if was_held and not held:at_release=bool(b.state()['ground'])
  was_held=held;b.input(v,w,held);e.step(actor.act());st=b.state();now=round((k+1)*DT,8);clear=max(0.,float(st['lowest'])-ground)
  for name,delay,start,error in [('speed',2.,vstart,float(st['speed']-v)),('turn',1.,wstart,float(st['turn']-w))]:
   key=(name,start)
   if now>=start+delay-1e-8 and key not in scored:
    (speed_errors if name=='speed' else turn_errors).append(dict(command=v if name=='speed' else w,error=error,t=now));scored.add(key)
  falls+=DT*bool(st['fall']);knees+=DT*bool(st['knee'])
  if st['fall'] and first_fall is None:first_fall=now
  if held:
   press_air+=DT*(clear>.01);hold_fall+=DT*bool(st['fall']);squat_min=float(st['height']) if squat_min is None else min(squat_min,float(st['height']))
  if 'release' in case and now>=case['release']:
   if now<=case['release']+1.4 and first_fall is None:
    peak=max(peak,clear)
    if takeoff is None and clear>.01:takeoff=now-case['release'];takeoff_speed=float(st['speed'])
   if takeoff is not None and st['ground'] and not st['fall'] and st['upright']>.85:landing+=1
   else:landing=0
   if landing>=50:landed=True
 valid=None if 'release' not in case else bool(at_release and press_air==0 and hold_fall==0 and takeoff is not None and landed and falls==0)
 print('KEYBOARD_VALID_CASE '+json.dumps(dict(name=case['name'],seconds=case['seconds'],initial_tilt=case.get('tilt'),initial_pose=initial_pose,speed_errors=speed_errors,turn_errors=turn_errors,fall_seconds=falls,knee_seconds=knees,first_fall=first_fall,valid_jump=valid,peak_before_fall=peak,press_airborne=press_air,hold_fall=hold_fall,grounded_at_release=at_release,stable_landing=landed,takeoff_latency=takeoff,prepress_speed=prepress,takeoff_speed=takeoff_speed,squat_drop=None if squat_min is None else squat_start-squat_min)),flush=True)
 e.close()
print('KEYBOARD_GENERALIZATION_COMPLETE',flush=True)
r=Ria();original=Policy('ria/resume-jump-20261005-2015',robot=r)
for tilt in [-1.25,-.95,.95,1.25]:
 r.pos=[0.,0.,0.];r.rot=[tilt,0.,0.]
 e=GymEnv([Plane(),r],dt=.01,seconds=8.,timestep=.005,reward=no_reward);e.reset(seed=90206)
 original.reset();initial_pose=dict(root_pos=list(r.pos),root_rot=list(r.rot),wheel_z=float(r.state()['lowest']),head_z=float(r['imu_head'].pos()[2]),upright=float(r.state()['upright']),velocity=list(map(float,r['imu_head'].vel_world())),gyro=list(map(float,r['imu_head'].ang_vel())));falls=0.;stable=0.;recovered=None
 for k in range(800):
  r.input(0.,0.,False);e.step(original.act());st=r.state();falls+=.01*bool(st['fall'])
  stable=stable+.01 if not st['fall'] and st['upright']>.85 and st['height']>.1 else 0.
  if stable>=1. and recovered is None:recovered=(k+1)*.01-1.
 print('CORRECTED_RECOVERY_CASE '+json.dumps(dict(tilt=tilt,initial_pose=initial_pose,fall_seconds=falls,recovery_time=recovered,final_upright=float(st['upright']),final_height=float(st['height']))),flush=True);e.close()
print('COMPILER_POSE_VALIDATION_COMPLETE',flush=True)
