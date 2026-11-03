# pcb review / current sensing / 2026-11-03

four-motor current-sensing conversion of the reviewed board, saved with backplane kicad 10.99.0-bp.6. the board uses native format 20260901; stock kicad 10 needs a compatibility export.

## circuit and layout

- all four ss6343m drivers remain. each motor has two ina241a3iddfr amplifiers, two smr12m1fr010t 10 mΩ / 1% / 1 w shunts, and two 100 nf bypass capacitors.
- a and b phase currents are measured. c is reconstructed as `-(a + b)` for a three-wire motor without a separate neutral or leakage return. the two-channel arrangement cannot independently detect a nonzero three-phase current sum.
- shunt land patterns use separate kelvin fingers and net-tie groups at the two resistor terminals. sense nets contain only an amplifier input and its shunt sense pad. the motor-current tracks do not pass through the sensing branches.
- gain is 0.5 v/a; ref1 at 3.3 v and ref2 at ground give a nominal 1.65 v zero-current output. firmware must calibrate offsets and sample with pwm switching in mind.
- phase a/b adc gpios are 2/3, 4/5, 6/7 and 8/9 for motors 1–4, all on adc1. imu sda/scl move to gpio11/12. battery sensing stays on gpio1, imu interrupt on gpio10 and servo pwm on gpio40/41.
- four encoder headers and six unused pull-ups are removed. the two imu pull-ups remain and are relocated.
- motor-current trunks are 0.8 mm, retaining the original 0.18 mm fine-pitch driver escapes. local ground connections and stitching were repaired after routing.
- all parts remain on top. existing connector, driver, power-supply and module positions and the board outline are preserved. the six motor bullet holes remain 3.6 mm drills with 6.4 mm lands.
- the main schematic retains the reviewed a1 layout; an a3 child sheet contains the eight current-sensing channels. new package models are included locally.

## verification

- erc: zero errors or warnings.
- drc with zone refill and schematic parity: zero errors, warnings, unconnected items or parity issues. existing manufacturing constraints, check severities and exclusions are preserved; no new checks are ignored.
- exported schematic netlist matches the expected conversion pin for pin, including all unaffected connections, adc assignments, kelvin inputs, amplifier references and shunt polarity.
- all original footprint placements are preserved apart from the removed encoder parts and relocated imu pull-ups. connector drills, pads and outline are checked against the reviewed source.
- 107 physical footprints; 101 bom and placement rows agree exactly. all assembled parts have an lcsc number, manufacturer and mpn. the six bare motor-wire holes are excluded from both assembly files.
- exported plated-drill data contains exactly six 3.6 mm motor holes. board bounds remain 50 × 69.45 mm, four copper layers and 1.6 mm thickness; smallest plated drill is 0.3 mm.
- the eight existing mechanical integration tests pass. the board render, schematic and copper layers are inspected separately from the rule checks.

manufacturing files are in `build/gerber`. reports, export commands and source/archive hashes are in `build/pcb-review/verification.json`; electrical and layout reports are `erc.json` and `drc.json` beside it. the conversion/export integration check is `/tmp/ria-current-final/verify-export.py`; the pre-conversion pcb source is backed up in `/tmp/ria-current-final/backup/pcb`.

## hardware limits

- rule checks do not establish physical motor operation, current-measurement accuracy, sensorless startup, thermal performance or transient immunity. those need measurements on the assembled revision.
- the [ss6343m v1.2 datasheet](https://www.leadpoweric.com/uploads/admin/file/20230717/f2edd0e2706f078eaf6584854d43b7dc.pdf) specifies 18 v operation; the 4s battery reaches 16.8 v. motor-bus transients still require measurement.
- the [tokmas imu](https://pcbparts.dev/mcp/datasheet/C54308212) uses address 0x37 and its own register map, rather than the tdk part's map.
- the servo supply still needs its planned 2 a load, transient and thermal test.
- the existing header step model cannot be meshed by the renderer; usb connector/esd models remain unavailable. the render is a layout aid, not physical-fit certification.
