class Head:
    width = 70.0
    depth = 80.0
    height = 60.0
    corner_r = 12.0
    pivot_height = 16.0
    bearing_od = 8.0
    bearing_id = 3.0
    bearing_depth = 4.0

class Gears:
    thickness = 4.0
    teeth_head = 28
    teeth_pinion = 36
    module = 1.0
    pressure_angle = 20.0

class Belt: 
    teeth_motor = 12
    teeth_pulley = 36
    bore_motor = 4.0
    belt_height = 3.4
    pitch = 3.0
    z = 24.8
    band = 4.2
    flange = 0.8
    back = 0.909
    tooth = 0.371

class Planetary:
    sun = 18
    planet = 12
    ring = 42
    count = 3
    module = 1.0
    pressure_angle = 25.0
    thickness = 5.0
    z = 10.4
    wall = 3
    back = 2.0
    square = 8.0
    carrier_thickness = 4.8
    bearing_od = 8.0
    bearing_w = 4.0
    pin_d = 3.0

class Leg: # todo: move motor/servo stuff to its own class
    length = 100.0
    width = 20.0
    thickness = 5.0
    mount_r = 13.1
    motor_holes = [(-8, 0), (8, 0), (0, 9.5), (0, -9.5)]
    motor_center_dia = 11.2
    motor_center_bore = 2.6
    servo_slot = (12.5, 23.5)
    servo_slot_offset = 5.5
    servo_pilots = (8.5, -19.5)
    servo_spacer = 3.2
    servo_ear_r = 3.3
    servo_shoulder = 1.3
    servo_boss_r = 8.75
    servo_spline_d = 4.8
    
class Wheels:
    dia = 60.0
    width = 8.0

class Servo:
    pass

class MotorUpper:
    holes = [(-8, 0), (8, 0), (0, 9.5), (0, -9.5)]
    center_dia = 11.0
    center_bore = 2.4

class MotorLower:
    dia = 34.8
    height = 15.25
    base_holes = [(6.7, 6.7), (-6.7, -6.7), (-5.65, 5.65), (5.65, -5.65)]
    top_holes = [(8, 0), (0, 8), (-8, 0), (0, -8)]
    nub_r = 3.5
    top_r = 12.4
    top_h = 1.25

class Electronics:
    fin_h = 26.0
    fin_t = 3.0
    fin_len = 48.0
    fin_y = 35.1
    fin_b_t = 8.0
    fin_b_len = 60.0
    standoff = 3.0
    standoff_dia = 6.0
    tap_depth = 8.0
    smini_holes = (20.3, 10.4)
    smini_z = 13.0
    tca_holes = 12.93
    tca_loc = (-15.0, -16.0)
    mp_loc = (14.0, -13.5)
    pico_loc = (25.0, 5.0, 10.5)
    pico_holes = [(4.8, -2.0), (16.2, -2.0), (4.8, -49.0), (16.2, -49.0)]
    pico_standoff = 10.0
    pico_standoff_dia = 5.0
    pico_w = 21.0
    pico_header = 3.1
    lipo_z = 26.0

class Config:
    wall = 2.4
    press_fit = 0.1
    m2_dia = 2.0
    m3_dia = 3.0
    m3_csink_dia = 5.0
    head = Head()
    gears = Gears()
    belt = Belt()
    planetary = Planetary()
    servo = Servo()
    motor_upper = MotorUpper()
    motor_lower = MotorLower()
    wheels = Wheels()
    leg = Leg()
    electronics = Electronics()

config = Config()
