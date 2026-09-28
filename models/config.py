class Head:
    width = 80.0
    depth = 84.0
    height = 60.0
    corner_r = 12.0
    pivot_height = 16.0
    pivot_d = 3.0
    pivot_boss_d = 10.0
    pivot_length = 8.0

class Gears:
    thickness = 4.0
    teeth_head = 28
    teeth_pinion = 36
    module = 1.0
    pressure_angle = 20.0
    backlash = 0.0

class Belt: 
    teeth_motor = 16
    teeth_pulley = 48
    teeth = 100
    bore_motor = 4.0
    belt_height = 6.0
    pitch = 3.0
    z = 24.8
    band = belt_height + 0.8
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
    backlash = 0.2
    clearance = 0.3
    thickness = 5.0
    z = 10.4
    wall = 3
    back = 2.0
    square = 8.0
    carrier_thickness = 4.8
    bearing_od = 8.0
    bearing_w = 4.0
    pin_d = 3.0
    screw = 20.0

class Leg: # todo: move motor/servo stuff to its own class
    length = 100.0
    width = 20.0
    knee_limit = 2.6
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
    nub_h = 1.2
    angle = 45.0
    top_r = 12.4
    top_h = 1.25

class Encoder:
    magnet_dia = 6.0
    magnet_h = 2.5
    gap = 1.5
    height = 3.25
    pcb = 1.6
    holes = [(x, y) for x in (-8.5, 8.5) for y in (-8.5, 8.5)]
    boss_d = 8.0

class Electronics:
    standoff_dia = 6.0
    tap_depth = 8.0
    plate_t = 2.4
    tray_clearance = 0.3
    hole_d = 1.4
    hole_pitch = 2.54
    spacer_h = 38.0
    spacer_d = 8.0
    spacer_pilot_d = 2.5
    spacer_pilot_depth = 8.0
    side_screw_z = 24.0
    side_boss_d = 7.0
    screw_d = 3.2
    posts = [(x, y) for x in (-31.5, 31.5) for y in (-33.5, 33.5)]
    driver_x = 26.5
    driver_y = 2.0
    battery_clamp_travel = 0.8
    battery_back_h = 26.0
    battery_shoe_t = 2.8
    battery_screw_loc = (26.7, -26.5, 9.0)
    tca_loc = (24.5, -3.0)
    mp_loc = (-24.5, 20.0)
    xt60_loc = (-21.0, -2.775)
    pico_loc = (10.5, 13.0)
    imu_loc = (0.0, 24.0)
    usb_opening = (12.0, 7.0)
    wiring_bays = [((-31.05, 0.25), (8.5, 19.5)), ((24.0, 21.0), (22.0, 12.0)),
                   ((-19.0, -26.0), (14.0, 22.0))]
    wiring_bay_r = 2.0

class Mass:
    grams = {
        '5010_body': 50.0,
        '5010_rotor': 50.0,
        'gbm2804': 42.0,
        'sg90_body': 9.0,
        'as5600': 2.0,
        'simplefocmini_dual': 6.0,
        'tca9548a': 3.0,
        'mp1584': 3.0,
        'xt60h_m': 4.0,
        'pipico': 5.0,
        'mpu6050': 2.0,
        'tattu_lipo': 150.0,
        'belt': 8.0,
        'magnet_knee': 1.0,
        'magnet_ankle': 1.0,
    }
    pla_density = 0.7 # vv rough, accounting for infill

class Config:
    wall = 2.4
    press_fit = 0.1
    m2_dia = 2.0
    m3_dia = 3.0
    m3_pilot_dia = 2.5
    m3_csink_dia = 5.0
    head = Head()
    gears = Gears()
    belt = Belt()
    planetary = Planetary()
    servo = Servo()
    motor_upper = MotorUpper()
    motor_lower = MotorLower()
    encoder = Encoder()
    wheels = Wheels()
    leg = Leg()
    electronics = Electronics()
    mass = Mass()

config = Config()
