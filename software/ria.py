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
