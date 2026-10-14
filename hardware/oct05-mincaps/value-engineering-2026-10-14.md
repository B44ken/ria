# value engineering, 2026-10-14

current checkpoint; live pricing and independent physical review are pending.

- five 1 µf capacitors now share basic c28323, 50 v x7r, with proper 0805 footprints. the four charge-pump capacitors retain the driver's specified dielectric and capacitance.
- four motor bulk capacitors now use basic c12891, 22 µf, 25 v x5r, in 1206 footprints. each local 100 nf bypass remains. the driver datasheet gives no fixed battery-bulk minimum; matching the previous capacitor's effective capacitance is not a requirement.
- ap63301wu-7/c2158003 replaces the unavailable ap63300. pinout, 3 a rating, input range and support circuit are unchanged. it uses continuous pwm and lacks spread spectrum; its manufacturer's 12 v/50 ma example indicates roughly 0.1 w more idle input power.
- motor plugs, other fixed components, connector drilling, outline and four-layer stackup are retained. nearby passives, five routing vias and local escapes moved to fit the larger charge-pump capacitors.

fresh saved/refilled drc reports zero violations, opens or schematic mismatches. erc and the strengthened source verifier pass: 69 components, 59 connected nets, correct part metadata/pinout and no via holes in smd copper or paste. these checks establish the current design checkpoint, not a completed manufacturing quote or bench qualification.

battery-lead inductance, pwm timing, braking spikes and capacitor temperature need qualification on the actual robot. the x5r bulk capacitors have an 85°c body-temperature limit. do not infer their adequacy from nominal capacitance alone. manufacturer curves show approximately 3.66 µf per part at 16.8 v and 25°c; that is a typical value.

pcb sha256: `1fff6f7f8d22bde5b384aa7697b88160119e8d21cdfc774fb0df4bbdcb69d6da`.

sources: [ss6343m v1.2](https://www.leadpoweric.com/uploads/admin/file/20230717/f2edd0e2706f078eaf6584854d43b7dc.pdf), [samsung c28323](https://product.samsungsem.com/mlcc/CL21B105KBFNNN.do), [samsung c12891](https://product.samsungsem.com/mlcc/CL31A226KAHNNN.do), [ap63300/ap63301](https://www.diodes.com/datasheet/download/AP63300_AP63301.pdf).
