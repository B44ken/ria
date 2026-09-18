# printing and assembly

All exported STL coordinates are in millimetres and touch Z=0. Caps face the bed on the head shell and both pulleys; the planet bearing socket faces up. The assembly STEP/GLB poses are unchanged by these print orientations.

There are eight distinct robot prints: upper leg/ring (2), carrier (2), 12T planet (6), sun/48T pulley (2), motor pulley (2), hip pinion (2), head shell (1), head lid (1). The seven additional files are fit coupons, not assembly components. Quantity and orientation are also recorded in `build/print_manifest.json`.

## fit first

Try the 8.0/8.1/8.2 mm bearing coupons, the 2.9/3.0/3.1 mm pin pilots and the 16T pulley/4.9 mm bore coupon with the actual hardware. The nominal model uses an 8.1 mm bearing seat and a 2.9 mm pin pilot. These are CAD dimensions, not guaranteed printed fits.

The 12T planet root diameter is 9.5 mm. Its 8.1 mm bearing seat leaves only **0.70 mm of radial material**. Do not assume it can withstand a forced bearing insertion or rated motor torque. Inspect the sliced wall and tooth paths, print a planet, and check it before assembling the robot. No material or infill prescription here is a strength certification.

The frame's raised backplate/bridge still needs underside support. Inspect support contact around the ring teeth, bearing bores, hip interface and head features in the slicer. Cap-down pulley orientation reduces the large underside overhang; the small sun-to-hub transition still needs a slicer check. The project does not contain printer-specific G-code or a validated support strategy.

The exploded/cutaway appearance in a preview is never a printable part. Bearings, wires, purchased motors, metal pins, inner-race spacers and screws are context/hardware geometry, not included as fake plastic substitutes.

## retained hardware per leg

Six 693ZZ bearing envelopes are retained: three planet bearings, one carrier bearing and two input bearings, each nominally 3 x 8 x 4 mm. Three smooth 3 x 8 mm steel dowels locate the planets. The fixed centre uses the original M3 x 20 pan-head axle with modelled 6 mm diameter, 2.4 mm high head.

The metal spacers are 4.1 mm outside diameter / 3.1 mm bore, with lengths 0.7, 0.7, 2.7 and 0.5 mm. The SG90 retains its ear spacers and two M2 x 10 low-head screws (3.8 mm head diameter, 1.55 mm head height). Other hip/motor hardware is unchanged from the supplied references; check purchased head and shaft dimensions against the CAD.

There is **no motor-pulley grub screw** in the new bill of materials, and no radial hole to tap. The 4.9 mm through bore clears the supplied 4.8 mm shaft. The requested removal leaves positive torque transfer and axial retention unresolved; do not power this interface on the assumption that the CAD fit secures it.

## assembly order

Start with the carrier, central bearing and rear inner spacer, without the three dowels. Slide that assembly into the side opening below the ring, then seat it. Install the dowels with the carrier supported; the rear access windows track their new 15 mm orbit. Do not use insertion force to compensate for an incorrect print fit.

Fit a bearing into each planet and lower each onto its pin, phased as shown in the neutral CAD pose. The bearing protrudes 0.3 mm behind the gear. Its inner race rests on the carrier pad; the outer race clears the annular recess.

Fit the two bearings and inner spacer into the one-piece sun/pulley, place the carrier-to-input spacer, and lower the input into mesh. The reduced 7.5 mm radius hub clears the planets; the larger pulley flange remains above them. Add the top inner washer and fixed axle. Check that tightening the metal inner-race stack does not bind the rotating races or strip the printed pilot.

Install the rotated SG90 and route its leads as in the supplied geometry. The wires are flexible envelopes, not a prescribed physical bend radius. The motor and input pulley tooth bands remain coplanar. The pulleys may need to be fitted with the belt already around them because of the flanges.

The drawn taut pitch path is **298.339 mm at 100 mm centres**. A nominal 300 mm pitch-length belt has 1.661 mm extra length. The render contains no bow, but does not make that stock belt taut. No tensioner, centre adjustment or retention solution is specified by this port.

Check assembly access, retention, free movement, backlash, axial play and belt tracking by hand before any powered test. The correct input-to-output ratio is 10:1, with the ring fixed. Actual load capacity, service life, friction and belt skipping remain to be established.
