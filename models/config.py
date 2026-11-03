class config:
    wall = 2.4
    press_fit = 0.1
    m2_dia = 2.0
    m3_dia = 3.0
    m3_pilot_dia = 2.5
    m3_csink_dia = 5.0

    class head:
        width = 85.0
        depth = 77.0
        height = 60.0
        corner_r = 12.0
        pivot_height = 16.0
        pivot_d = 3.2
        pivot_boss_d = 10.0
        pivot_length = 8.0
        pivot_screw = 16.0 # m3 iso 7046, including the head
        pivot_endplay = 0.2 # total axial travel, including press_fit
        race_inner = 17.8
        race_outer = 21.2
        race_clearance = 0.2
        race_depth = 1.2
        race_wall = 1.2

    class gears:
        thickness = 4.0
        teeth_head = 28
        teeth_pinion = 36
        module = 1.0
        pressure_angle = 20.0
        backlash = 0.0

    class belt:
        teeth_motor = 16
        teeth_pulley = 48
        bore_motor = 4.7
        belt_height = 6.0
        pitch = 3.0
        z = 24.8
        band = belt_height + 0.8
        flange = 0.8
        back = 0.909
        tooth = 0.371

    class planetary:
        sun = 18
        planet = 12
        ring = 42
        count = 3
        module = 1.0
        pressure_angle = 25.0
        backlash = 0.2
        clearance = 0.3
        thickness = 5.0
        z = 11.7
        wall = 3
        back = 2.0
        square = 4.7
        carrier_thickness = 4.8
        bearing_od = 8.0
        bearing_w = 4.0
        pin_d = 3.0
        screw = 16.0 # m3 flathead, including the head
        planet_screw = 10.0
        screw_type = 'iso10642'
        shaft_d = 18.0
        axial_clearance = 0.2
        shoulder_t = 1.2
        drive_bearing_id = 7.0
        drive_bearing_od = 14.0
        drive_bearing_w = 5.0
        drive_socket_depth = 4.0
        planet_hub_d = 9.6
        mounts = [(0, 30), (0, 40)]
        mount_screw = 25.0 # m3 din 7991, including the head

    class leg:
        length = 100.0
        width = 20.0
        thickness = 5.0
        mount_r = 13.1
        motor_holes = [(-8, 0), (8, 0), (0, 9.5), (0, -9.5)]
        motor_center_dia = 11.2

        motor_center_bore = 2.6
        hip_pad_y = 19.5
        hip_pad_d = 8.0
        hip_pad_screw = 10.0 # m3 din 965, including the head; tip runs in the hip race
        servo_slot = (12.5, 23.5)
        servo_slot_offset = 5.5
        servo_pilots = (8.5, -19.5)
        servo_spacer = 3.2
        servo_ear_r = 3.3
        servo_shoulder = 1.3
        servo_boss_r = 8.75
        servo_spline_d = 4.8

    class wheels:
        dia = 67.0
        width = 27.0
        bead_dia = 48.0
        lip_dia = 51.0
        barrel_dia = 54.0
        bead_outer = 1.8
        bead_inner = 4.0
        wall = 2.0
        clearance = 0.2

    class motor_lower:
        dia = 34.8
        height = 15.25
        base_holes = [(6.7, 6.7), (-6.7, -6.7), (-5.65, 5.65), (5.65, -5.65)]
        top_holes = [(8, 0), (0, 8), (-8, 0), (0, -8)]
        nub_h = 1.2
        angle = 45.0

    class encoder:
        magnet_dia = 6.0
        magnet_h = 2.5
        gap = 1.5
        height = 3.25
        pcb = 1.6
        holes = [(x, y) for x in (-8.5, 8.5) for y in (-8.5, 8.5)]

    class electronics:
        standoff_dia = 6.0
        tap_depth = 8.0
        plate_t = 2.4
        tray_clearance = 0.3
        screw_d = 3.2
        spacer_pilot_d = 2.5
        side_boss_d = 7.0
        side_screw_z = 11.0
        posts = [(x, y) for x in (-33.0, 33.0) for y in (-31.0, 31.0)]
        post_radius = 3.0
        pcb_clearance = 0.3
        pcb_z = 6.0 # from the inside of the bottom
        bullet_d = 3.6
        bullet_depth = 6.0
        shelf_z = 18.8 # underside, above the floor
        battery_size = (30.0, 75.0, 35.0) # pack on its side
        battery_x = 0.0
        battery_y = -6.0
        battery_angle = 80.0
        pcb_angle = 0.0
        battery_clearance = 0.4
        usb_opening = (12.0, 7.0)
        balance_opening = (16.0, 7.0) # xhp-5: 14.8 x 5.7 mm, plus clearance
        balance_x = 0.0
        balance_z = 35.0
