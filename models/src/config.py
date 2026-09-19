"""Design inputs and derived dimensions. All lengths are millimetres.

The supplied model defines the unchanged hip interfaces and axial stack.
The default frame is now three flat-printing parts. The planetary tooth
counts, ring margin, belt display and motor pulley also differ from the
archived 28/14/56 prototype, which remains an explicit regression fixture.
"""

from dataclasses import dataclass, field
from math import asin, cos, pi, sin


@dataclass(frozen=True)
class GearTrain:
    sun_teeth: int = 18
    planet_teeth: int = 12
    ring_teeth: int = 42
    planet_count: int = 3
    module: float = 1.0
    pressure_angle: float = 25.0
    backlash: float = 0.12
    ring_root_wall: float = 2.75

    def __post_init__(self) -> None:
        teeth = (self.sun_teeth, self.planet_teeth, self.ring_teeth)
        if any(type(n) is not int or n < 4 for n in teeth):
            raise ValueError("Tooth counts must be integers of at least four.")
        if self.ring_teeth != self.sun_teeth + 2 * self.planet_teeth:
            raise ValueError("Concentric gears require ring = sun + 2 * planet.")
        if self.planet_count < 2 or (self.sun_teeth + self.ring_teeth) % self.planet_count:
            raise ValueError("The chosen equally spaced planets cannot be phased.")
        if min(self.module, self.ring_root_wall) <= 0 or self.backlash < 0:
            raise ValueError("Module and wall must be positive; backlash nonnegative.")
        if not 0 < self.pressure_angle < 45:
            raise ValueError("Pressure angle must lie between 0 and 45 degrees.")
        if 2 * self.orbit_radius * sin(pi / self.planet_count) <= 2 * self.planet_tip_radius:
            raise ValueError("Adjacent planets would overlap.")

    @property
    def orbit_radius(self) -> float:
        return self.module * (self.sun_teeth + self.planet_teeth) / 2

    @property
    def sun_hub_radius(self) -> float:
        """Stay within the sun root, clear of the adjacent planet front faces."""
        return self.module * (self.sun_teeth / 2 - 1.25) - 0.25

    @property
    def planet_tip_radius(self) -> float:
        return self.module * (self.planet_teeth / 2 + 1)

    @property
    def planet_root_radius(self) -> float:
        return self.module * (self.planet_teeth / 2 - 1.25)

    @property
    def ring_root_radius(self) -> float:
        return self.module * (self.ring_teeth / 2 + 1.25)

    @property
    def case_radius(self) -> float:
        return self.ring_root_radius + self.ring_root_wall

    @property
    def sun_per_carrier(self) -> float:
        """Fixed ring: sun angle / carrier angle."""
        return 1 + self.ring_teeth / self.sun_teeth

    @property
    def planet_per_carrier(self) -> float:
        """Absolute planet spin, not its spin relative to the carrier."""
        return 1 - self.ring_teeth / self.planet_teeth

    @property
    def ring_phase(self) -> float:
        return 180 / self.ring_teeth

    def planet_centre(self, index: int) -> tuple[float, float]:
        angle = 2 * pi * index / self.planet_count
        return self.orbit_radius * cos(angle), self.orbit_radius * sin(angle)

    def planet_phase(self, index: int) -> float:
        centre_angle = 360 * index / self.planet_count
        phase = 180 / self.planet_teeth
        phase += (self.sun_teeth + self.planet_teeth) / self.planet_teeth * centre_angle
        return phase % (360 / self.planet_teeth)


@dataclass(frozen=True)
class BeltDrive:
    motor_teeth: int = 16
    knee_teeth: int = 48
    pitch: float = 3.0
    width: float = 6.0
    centre_distance: float = 100.0
    stock_pitch_length: float = 300.0
    model_slack: bool = False

    @property
    def ratio(self) -> float:
        return self.knee_teeth / self.motor_teeth

    @property
    def knee_pitch_radius(self) -> float:
        return self.knee_teeth * self.pitch / (2 * pi)

    @property
    def motor_pitch_radius(self) -> float:
        return self.motor_teeth * self.pitch / (2 * pi)

    @property
    def tangent_angle(self) -> float:
        difference = self.knee_pitch_radius - self.motor_pitch_radius
        if not 0 <= difference < self.centre_distance:
            raise ValueError("The pulleys have no external common tangents.")
        return asin(difference / self.centre_distance)

    @property
    def straight_span(self) -> float:
        return self.centre_distance * cos(self.tangent_angle)

    @property
    def taut_pitch_length(self) -> float:
        angle = self.tangent_angle
        return (2 * self.straight_span
                + self.knee_pitch_radius * (pi + 2 * angle)
                + self.motor_pitch_radius * (pi - 2 * angle))


@dataclass(frozen=True)
class AxialStack:
    """Z increases outboard. Preserve the supplied thin stack exactly."""

    backplate_bottom: float = 9.7
    backplate_top: float = 12.7
    carrier_bottom: float = 13.0
    carrier_top: float = 17.8
    gear_bottom: float = 18.1
    gear_top: float = 23.1
    pulley_bottom_flange: float = 23.6
    teeth_bottom: float = 24.3
    teeth_top: float = 30.9
    cap_top: float = 31.7


@dataclass(frozen=True)
class HeadConfig:
    """Outside envelope and removable bottom lid. Z=0 is the lid's bed face."""
    width: float = 72.0
    depth: float = 72.0
    height: float = 60.0
    corner_radius: float = 12.0
    wall: float = 2.4
    lid_thickness: float = 2.4
    lid_gap: float = 0.2
    pivot_height: float = 12.0
    bearing_seat_clearance: float = 0.2  # diametral, around the 11 mm 685ZZ
    boss_radial_clearance: float = 0.25

    def __post_init__(self) -> None:
        if min(self.width, self.depth, self.height, self.wall, self.lid_thickness) <= 0:
            raise ValueError("Head dimensions and wall thickness must be positive.")
        if not self.wall < self.corner_radius < min(self.width, self.depth) / 2:
            raise ValueError("Head corner radius must exceed the wall and fit the footprint.")
        if self.width < 40 or self.depth < 50:
            raise ValueError("The retained twin hip housings require at least a 40 x 50 mm head.")
        if self.height - self.wall <= self.pivot_height + 7.5:
            raise ValueError("Head roof must be above the hip housings.")
        if self.pivot_height < self.lid_thickness + self.lid_gap + 7.5:
            raise ValueError("The hip bearing housing would intersect the lid.")
        if min(self.lid_gap, self.bearing_seat_clearance, self.boss_radial_clearance) < 0:
            raise ValueError("Head fit clearances cannot be negative.")

    @property
    def side(self) -> float:
        return self.depth / 2

    @property
    def shell_bottom(self) -> float:
        return self.lid_thickness + self.lid_gap


@dataclass(frozen=True)
class HipConfig:
    """The printed motor mount and the fixed purchased-hardware interface.

    The 16 x 19 mm motor hole pattern and Z stack are hardware datums, not
    global scaling factors. Mount radius and print-fit clearances are inputs.
    """
    mount_radius: float = 13.1
    mounting_hole_diameter: float = 3.2
    mounting_countersink_diameter: float = 6.2
    sleeve_seat_diameter: float = 5.2
    axle_pilot_diameter: float = 2.5
    outer_boss_radius: float = 6.8
    spigot_radius: float = 3.5
    # Axial dimensions retain the supplied motor, bearing and pulley stack.
    plate_thickness: float = field(default=4.5, init=False)
    boss_bottom: float = field(default=-1.8, init=False)
    spigot_bottom: float = field(default=-5.2, init=False)
    bearing_bottom: float = field(default=-10.2, init=False)
    sleeve_top: float = field(default=-2.2, init=False)
    servo_shoulder: float = field(default=-1.3, init=False)
    bearing_od: float = field(default=11.0, init=False)
    bearing_id: float = field(default=5.0, init=False)
    bearing_width: float = field(default=5.0, init=False)

    def __post_init__(self) -> None:
        if self.mount_radius <= 9.5 + self.mounting_countersink_diameter / 2:
            raise ValueError("Hip mount must contain the motor countersinks.")
        if not 3.0 <= self.mounting_hole_diameter < self.mounting_countersink_diameter:
            raise ValueError("Hip mount requires clearance for its M3 screws.")
        if not 5.0 <= self.sleeve_seat_diameter < 2 * self.spigot_radius:
            raise ValueError("Sleeve seat must clear the 5 mm sleeve and leave a spigot wall.")
        if not 0 < self.axle_pilot_diameter <= 3:
            raise ValueError("Hip axle pilot must fit the nominal M3 thread.")
        if not self.spigot_radius < self.outer_boss_radius < self.mount_radius:
            raise ValueError("Hip boss radii must nest inside the mount.")

    def motor_holes(self, centre_y: float) -> tuple[tuple[float, float], ...]:
        return ((-8, centre_y), (8, centre_y), (0, centre_y + 9.5), (0, centre_y - 9.5))


@dataclass(frozen=True)
class HipGears:
    """The original 28/36 spur pair, distinct from the 25-degree knee gears."""
    fixed_teeth: int = 28
    pinion_teeth: int = 36
    module: float = 1.0
    pressure_angle: float = 20.0
    backlash: float = 0.22
    thickness: float = 4.0
    wall_standoff: float = 0.5
    leg_gap: float = 0.2

    def __post_init__(self) -> None:
        if (self.fixed_teeth, self.pinion_teeth, self.module, self.thickness) != (28, 36, 1.0, 4.0):
            raise ValueError("Changing the hip gear pair requires redesigning the servo and bearing stack.")
        if not 0 < self.pressure_angle < 45 or self.backlash < 0:
            raise ValueError("Invalid hip tooth profile.")
        if self.wall_standoff < 0 or self.leg_gap < 0:
            raise ValueError("Hip axial clearances cannot be negative.")

    @property
    def centre_distance(self) -> float:
        return (self.fixed_teeth + self.pinion_teeth) * self.module / 2


@dataclass(frozen=True)
class RobotConfig:
    gears: GearTrain = field(default_factory=GearTrain)
    belt: BeltDrive = field(default_factory=BeltDrive)
    stack: AxialStack = field(default_factory=AxialStack)
    head: HeadConfig = field(default_factory=HeadConfig)
    hip: HipConfig = field(default_factory=HipConfig)
    hip_gears: HipGears = field(default_factory=HipGears)
    bearing_seat_diameter: float = 8.1
    motor_shaft_diameter: float = 4.8
    motor_bore_diameter: float = 4.9
    motor_set_screw: bool = False
    servo_rotation: float = -90.0
    knee_travel: float = 120.0
    split_frame: bool = True

    @property
    def servo_output_y(self) -> float:
        return self.belt.centre_distance - self.hip_gears.centre_distance

    @property
    def hip_world_offset(self) -> float:
        return (self.head.side + self.hip_gears.wall_standoff
                + self.hip_gears.thickness + self.hip_gears.leg_gap)

    @property
    def knee_world_height(self) -> float:
        return self.head.pivot_height - self.belt.centre_distance

    @property
    def total_ratio(self) -> float:
        return self.belt.ratio * self.gears.sun_per_carrier

    @property
    def planet_seat_wall(self) -> float:
        return self.gears.planet_root_radius - self.bearing_seat_diameter / 2

    @classmethod
    def archived(cls) -> "RobotConfig":
        """Regression fixture only; not the default design."""
        return cls(
            gears=GearTrain(sun_teeth=28, planet_teeth=14, ring_teeth=56,
                            ring_root_wall=1.75),
            belt=BeltDrive(model_slack=True),
            motor_set_screw=True,
            split_frame=False,
        )
