"""Design inputs and derived dimensions. All lengths are millimetres.

The supplied model defines the unchanged hip interfaces and axial stack.
Only the planetary tooth counts, ring margin, belt display and motor pulley
retaining screw differ from the archived 28/14/56 prototype.
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
class RobotConfig:
    gears: GearTrain = field(default_factory=GearTrain)
    belt: BeltDrive = field(default_factory=BeltDrive)
    stack: AxialStack = field(default_factory=AxialStack)
    bearing_seat_diameter: float = 8.1
    motor_shaft_diameter: float = 4.8
    motor_bore_diameter: float = 4.9
    motor_set_screw: bool = False
    servo_output_y: float = 68.0
    servo_rotation: float = -90.0
    hip_world_offset: float = 40.7
    knee_world_height: float = -88.0
    knee_travel: float = 120.0

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
        )
