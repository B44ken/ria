# Capacitor necessity audit — 2026-10-05

The previous statement that every retained capacitor was required was too broad. A useful function is not proof of a minimum component count. There were 27 capacitors; this candidate has 24 and 69 total components.

## Removed: optional parallel bypassing

- ESP-C2, 100 nF, module supply: removed while retaining the nearby 10 µF supply reservoir and the module's internal circuitry. Espressif's layout guidance describes extra parallel 0.1/1 µF as optional; DOIT's module minimum-system section does not mandate a separate 100 nF carrier capacitor. This is a design choice pending RF/supply testing, not a proven equivalence claim.
- POWER-C2, 100 nF, buck input: removed while retaining 22 µF at the input. AP63300's application circuit uses one input capacitor, and its input-selection guidance does not independently require this extra 100 nF.
- USB-C1, 100 nF, VBUS: removed. USBLC6-2's USB application diagram does not require this discrete capacitor. The ESD protection IC and its supply/ground connections remain. No IEC ESD test or inrush-compliance test has been performed.

## Retained with specific justification

| References | Qty/value | Basis | Classification |
|---|---|---|---|
| MOTOR1–4-C2 | 4 × 1 µF | SS6343M external charge-pump capacitor between VCP and VIN | Functional requirement |
| MOTOR1–4-C6 | 4 × 4.7 µF | SS6343M's internal 3.3 V LDO/gate-drive output bypass, specified 4.7–10 µF | Datasheet-specified support |
| MOTOR1–4-C3 | 4 × 100 nF | Local high-frequency motor-supply bypass | Layout/noise support; not a mathematically established minimum |
| MOTOR1–4-C5 | 4 × 10 µF | Local pulsed motor-supply reservoirs | Current/transient dependent; value/count need physical power-integrity validation |
| POWER-C1 | 1 × 22 µF | Buck input ripple/current support; datasheet says >10 µF sufficient for most applications | Required function; chosen value not universal minimum |
| POWER-C3 | 1 × 100 nF | BST-to-SW high-side bootstrap | Functional requirement |
| POWER-C4/C5 | 2 × 22 µF | Buck output loop/transient support; matches reference configuration, within suggested 22–68 µF | Retain pending effective-capacitance/load calculation; not both categorically mandatory |
| ESP-C1 | 1 × 10 µF | Local module supply reservoir for RF/current steps; DOIT specifies >500 mA startup demand | Supply-integrity recommendation |
| ESP-C3 | 1 × 1 µF | EN reset RC with 10 kΩ, allowing supply settling | Startup-timing recommendation; not supply decoupling |
| IMU-C1/C2 | 2 × 100 nF | Actual Tokmas ICM-42688-P datasheet, section10.2 figure24, shows one on VDD and one on VDDIO | Exact-vendor reference circuit |

The IMU is the Tokmas-labelled C54308212, not an assumed TDK part. The TDK datasheet has different bypass recommendations and was not substituted for the actual vendor document. The downloaded Tokmas PDF identifies TOKMAS as author and figure24 was visually inspected.

## Sources

- Diodes AP63300/AP63301: sections12–14 and reference circuit: https://www.diodes.com/datasheet/download/AP63300_AP63301.pdf
- SS6343M manufacturer: https://www.leadpoweric.com/en/productshow9.html . the 2026-10-14 review retrieved the [manufacturer v1.2 pdf](https://www.leadpoweric.com/uploads/admin/file/20230717/f2edd0e2706f078eaf6584854d43b7dc.pdf) and checked the pinout, 1 µf charge-pump capacitor and 4.7 µf ldo capacitor against it.
- DOIT ESPS3-32 manual, sections5 and9: https://atta.szlcsc.com/upload/public/pdf/source/20250610/5E546491D868C5B4673AE97C7A2DC844.pdf
- Espressif power-layout guidance: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html
- Exact Tokmas part and linked vendor datasheet, section10.2 figure24 (PDF page53): https://jlcpcb.com/partdetail/Tokmas-ICM_42688_P_TOKMAS/C54308212
- ST USBLC6-2: USB application figure13: https://www.st.com/resource/en/datasheet/usblc6-2.pdf

## Verification limits

ERC, DRC and netlist comparison pass for this 69-component revision. Those checks cannot establish transient droop, RF behaviour, ESD immunity, capacitor DC-bias derating or a global minimum BOM. The remaining motor bulk and buck output capacitance must not be removed merely to meet a numerical part-count target. No such target was requested.
