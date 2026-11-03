import { describe, expect, test } from 'bun:test';
import { planetaryMotion } from '../src/kinematics.js';

const gears = { sun: 18, planet: 12, ring: 42 };
const turn = 2 * Math.PI;

describe('fixed-ring planetary drive', () => {
  test('one input turn gives 108 degrees of output and -270 degrees of planet spin', () => {
    const motion = planetaryMotion(turn);
    expect(motion.sun).toBeCloseTo(turn, 12);
    expect(motion.carrier * 180 / Math.PI).toBeCloseTo(108, 10);
    expect(motion.planet * 180 / Math.PI).toBeCloseTo(-270, 10);
    expect(motion.planetRelative * 180 / Math.PI).toBeCloseTo(-378, 10);
  });

  test.each([-17, -1, 0, 0.15, 1, 12.75])('satisfies both gear contacts after %s turns', (turns) => {
    const { sun, carrier, planet, planetRelative } = planetaryMotion(turns * turn, gears);
    const ring = 0;
    expect(gears.sun * (sun - carrier) + gears.ring * (ring - carrier)).toBeCloseTo(0, 10);
    expect(gears.sun * (sun - carrier) + gears.planet * (planet - carrier)).toBeCloseTo(0, 10);
    expect(gears.ring * (ring - carrier) - gears.planet * (planet - carrier)).toBeCloseTo(0, 10);
    expect(planetRelative).toBeCloseTo(planet - carrier, 12);
  });

  test('reversing the input reverses every moving part', () => {
    const forward = planetaryMotion(2.7);
    const reverse = planetaryMotion(-2.7);
    for (const part of ['sun', 'carrier', 'planet', 'planetRelative']) {
      expect(reverse[part]).toBeCloseTo(-forward[part], 12);
    }
  });

  test('uses the supplied tooth counts', () => {
    const motion = planetaryMotion(turn, { sun: 24, planet: 12, ring: 48 });
    expect(motion.carrier).toBeCloseTo(turn / 3, 12);
    expect(motion.planet).toBeCloseTo(-turn, 12);
  });
});
