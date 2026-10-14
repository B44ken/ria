# pcb

open `ria.kicad_pro` in kicad or backplane. edit `ria.kicad_pcb` and `ria.kicad_sch` directly. the local symbols, footprints, library tables and `3dmodels/` travel with the project; `ts-pcb/` retains the original tscircuit source and generated outputs.

the sensorless revision uses a doit esps3-32-n4 module with 4mb flash, four drv8316ctrgfr motor drivers, an icm-42688-p imu, usb-c data and a vertical xt60 battery input. the four encoder headers and their pullups are removed. two measured phase currents per motor give eight adc channels; the third phase current is reconstructed from their sum. motor phase outputs never connect directly to the mcu.

the schematic has 104 components and 93 connected nets. on 2026-10-14, fresh kicad 10.0.6 checks with refilled zones reported zero erc violations, zero pcb errors, zero unrouted connections and zero schematic mismatches. the independent driver audit passed 288 pin/net assertions, and the saved-file verifier passed. fabrication design rules are unchanged. 39 pcb warnings remain: 20 routing-stub/via warnings and 19 silkscreen overlap, edge or mask-clipping warnings. this is a hardware revision; sensorless firmware, continuous motor-current temperature and bench operation are not verified.

the [layout preview](../build/review/current-sensing-65mm/board.png), native reports and verifier output are in `build/review/current-sensing-65mm/`.

run the native checks with kicad's python, which includes `pcbnew` and `wx`, and `kicad-cli` on the path. on this mac:

```sh
export PATH="/Applications/KiCad/KiCad.app/Contents/MacOS:$PATH"
"/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9" verify-kicad.py
"/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli" sch erc ria.kicad_sch --format json --exit-code-violations -o /tmp/ria-erc.json
"/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli" pcb drc ria.kicad_pcb --schematic-parity --format json --exit-code-violations -o /tmp/ria-drc.json
```

## current sensing and control

the [ti drv8316c datasheet](https://www.ti.com/lit/ds/symlink/drv8316c.pdf) defines the hardware interface and support parts. each drv8316ct uses three pwm inputs without spi. mode connects through 47kΩ to its own avdd, selecting three-pwm control with analog current outputs. the three low-side input pins connect to local avdd, drvoff and vsel_bk connect to ground, and nsleep uses gpio47 with an external pulldown. slew and ocp/sr connect to ground; gain floats for 0.3v/a. each fault output has its own 5.1kΩ pullup to local avdd and a separate mcu input.

soa and sob pass through 330Ω/22pf filters to adc1 inputs. vref connects to the driver's local avdd, giving a zero-current offset of avdd/2, nominally 1.65v. sample only during valid low-side conduction windows synchronized to pwm; these outputs do not continuously measure phase current through every switching state. the 16a hardware overcurrent threshold protects against faults. firmware must impose the intended 2.8a motor-current target rather than treating that threshold as an operating limit.

| motor | pwm a/b/c gpio | current a/b gpio | fault gpio |
| --- | --- | --- | --- |
| 1 | 13 / 14 / 15 | 4 / 5 | 44 |
| 2 | 16 / 17 / 18 | 1 / 2 | 48 |
| 3 | 21 / 35 / 36 | 6 / 7 | 42 |
| 4 | 37 / 38 / 39 | 8 / 9 | 11 |

imu sda/scl move to gpio40/41; its interrupt remains gpio12. battery sensing uses gpio10, a 100kΩ/20kΩ divider and 100nf bypass, giving 2.8v at a 16.8v battery input. gpio3 remains unused because it is a boot strap. use mcpwm for all twelve motor pwm outputs; ledc has eight channels.

each driver has a 47nf 50v charge-pump flying capacitor, 1µf charge-pump reservoir, two 100nf vm bypasses and 10µf 50v local bulk capacitance. local avdd uses a 1µf 50v x7r 0805 capacitor, c28323, selected for ti's effective 0.7–1.3µf requirement at 3.3v. vref shares that bypass; the optional extra capacitor is omitted. each hardware variant's buck converter uses 22Ω from sw_bk to fb_bk and a 22µf 25v 0805 output capacitor. its unloaded output and avdd remain private to that driver, separate from the board's 3.3v supply.

## layout and connectors

the board is 50×65mm, with four copper layers and nominal 1.6mm thickness. components mount on top. the inner layers provide ground and battery distribution; the antenna keepout covers all four copper layers, and the top notch removes pcb material from beneath the antenna. the nominal stackup uses jlc04161h-7628, with 35µm outer and 15.2µm inner copper.

the power connector is a vertical amass xt60pb-m.g.y, c19268037, with its mating face above the board. the [manufacturer drawing](https://www.china-amass.net/uploads/62.XT60PB-M-SPEC-2025V0.pdf) specifies a 15.5×8.1mm housing, 16mm height above the pcb, 7.2mm pin pitch and two 4.6mm pcb holes. the imported footprint was corrected to that drawing; pad 1 is ground and pad 2 is battery. its included 3d model is a simplified housing envelope, not the manufacturer's detailed model.

usb-c is at the bottom centre. the outward-facing motor headers sit at x=78.5/121.5mm, y=91mm, shifted down 2mm to clear the upright xt60. they use 5.08mm-pitch wj2edgr-5.08-03p-14-00a headers, c70914, with 1.7mm drills and 3mm lands. mating wire plugs are wj2edgk-5.08-03p-14-00a, c71371; these are not included in the pcb bom. their housings have no included 3d model, so fit uses the manufacturer's drawing and footprint fabrication outlines. the other two motors use mirrored a/b/c socket columns at 8mm pitch.

the mcu is doit esps3-32-n4, c49164655. its [manufacturer pin table and land drawing](https://atta.szlcsc.com/upload/public/pdf/source/20250610/5E546491D868C5B4673AE97C7A2DC844.pdf) define the module footprint. the ground stencil uses nine 0.9mm openings at 1.4mm pitch with twelve thermal holes between them. the existing wroom model represents its approximate 18×25.5mm envelope. the drv8316c model represents the manufacturer's 5×7mm rgf package.

the driver stencil uses twelve windows with thermal holes in the paste gaps. 58 routed via holes intersect top solder pads and their mask openings, including 24 driver thermal vias; the module also has twelve plated thermal holes. the bottom solder mask covers these holes. filling and capping is an optional assembly-process choice, not a blanket requirement; several terminal-pad vias need assembly review. this sensorless design is separate from the simplified ss6343m candidate in `hardware/oct05-mincaps/`, which has no via-in-pad holes and is the board reviewed and quoted on 2026-10-14.
