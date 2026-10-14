# RIA Backplane — simplified design

current authoritative status: [candidate-status.json](candidate-status.json) and [value-engineering checkpoint](../../value-engineering-2026-10-14.md). [FABRICATION.md](FABRICATION.md) records the original candidate.

- Four layers, 50 × 69.45 mm; 69 components, all top-mounted
- SS6343M motor drivers and DOIT ESPS3-32-N4 module
- 198 routing vias, minimum 0.3 mm drill / 0.6 mm land
- Zero via-in-pad holes; 24 motor and 12 module cooling holes removed
- Ground solder lands, decoupling, USB protection and required power/control circuitry retained
- Fresh DRC: zero violations, opens or schematic parity mismatches
- Contract verification: 69 components and 59 connected nets match the updated schematic
- Motor thermal/current qualification and USB signal-integrity checks remain unproven

Open ria.kicad_pro in KiCad 10.0.6 or newer. Footprint and symbol libraries accompany the project. The removed module holes are also removed from its local footprint library.

See CAPACITOR-AUDIT.md for the three optional bypass removals and the distinction between requirements and recommendations.
