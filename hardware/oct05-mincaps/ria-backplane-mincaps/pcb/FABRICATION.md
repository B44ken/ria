# Simplified Backplane — 2026-10-05

User requested removal of unnecessary board features. The separate lean candidate removes all 24 motor-driver thermal vias and the 12 extra plated thermal holes in the ESP module footprint. Solid exposed ground lands and the module's nine paste windows remain. All 39 ordinary pad-via intersections were previously rerouted off-pad.

There are now 198 routing vias, every one with a 0.3 mm drill and 0.6 mm land. Native shape audit reports zero routing-via holes intersecting SMD copper or paste, and no module thermal holes. No epoxy-filled/capped process is specified or required by a remaining via-in-pad geometry. Standard routing-via tenting and ordinary supplier DFM review remain appropriate; no vendor acceptance is claimed.

Fresh KiCad 10.0.6 saved-refill DRC: zero violations, opens and schematic parity mismatches. Contract verifier confirms 69 top-mounted components, 59 connected nets, driver pinouts, grounded exposed pads, outline and connector geometry. The three optional bypass capacitors are removed from PCB and schematic together; fresh ERC is clean. Component values and required power, decoupling, pullups and USB protection are preserved.

## Honest qualification limits

Removing the thermal holes changes heat flow. DRC proves electrical geometry/connectivity, not sustained motor-current capability. No current/ambient/duty thermal measurements are available. Do not advertise the datasheet's board-dependent maximum continuous current as proven on this simplified board. Bring-up must establish safe current limits under expected duty and ambient conditions. The prior thermal-via baseline remains preserved for comparison.

USB escape edits retain widths/layers/via counts, but the inherited pair changes reference layer and has not undergone impedance/eye-diagram validation. Existing configured DRC exclusions remain inherited. This is the requested simplified design checkpoint, not unconditional manufacturing or electrical qualification.

No order, paid fabrication process, vendor upload or supplier message was performed.

See CAPACITOR-AUDIT.md for the three optional bypass removals and the distinction between requirements and recommendations.
