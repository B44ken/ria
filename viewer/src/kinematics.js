// fixed ring; angles are radians, measured in the stationary frame.
export function planetaryMotion(sunAngle, gears = { sun: 18, planet: 12, ring: 42 }) {
  const carrier = sunAngle * gears.sun / (gears.sun + gears.ring);
  const planetRelative = -(sunAngle - carrier) * gears.sun / gears.planet;
  return { sun: sunAngle, carrier, planet: carrier + planetRelative, planetRelative };
}
