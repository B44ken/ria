# docs (slop)

# validation scope

`python main.py` runs the audit after export. A failed check makes the entry point exit nonzero; results are written to `build/validation.json`. `--no-validate` is an explicit opt-out, not an implicit success. Mesh export integrity checks still run on that path.

The audit checks valid positive-volume CAD, reopened STEP assemblies, reopened GLB meshes and metre/Y-up conversion, and every exported STL. A print must be one connected watertight, consistently wound mesh with positive volume and a bed-contacting minimum Z. Its bytes are hashed after reopening.

The actual sampled involute extrusion polygons are tested through a complete carrier revolution at 721 poses, with all three planets. Both sun/planet and planet/ring engagement are checked, as are adjacent planets. A small signed backlash probe distinguishes a meshing gear from a gear merely floating without contact. The absolute planet spin is -2.5 times carrier angle; the sun spins 10/3 times, and the motor 10 times.

A conservative carrier silhouette is checked against the neck at 241 poses through -120 to +120 degrees. The carrier rear axial clearance and the resized sun-hub clearance are checked separately. The full servo projection is checked against a conservative inward tooth-tip envelope of the taut belt, not just the visible smooth backing.

Neutral collision checks use OpenCascade intersections of the actual B-reps after an axis-aligned broadphase. Gear-to-gear and gear-to-ring pairs use their extruded-profile/axial-stack proof instead of expensive redundant solid Booleans. Named dowel press fits and tap-pilot overlaps are reported separately. Any overlap at an unchanged reference-to-reference hip/head interface is also reported separately; it is not silently labelled an intended new fit. The numerical positive-volume reporting threshold is 0.012 mm3.

The installed model is checked between sides and against the head at neutral. The per-leg result is reused for the two identical rigid installations. This is not a combined hip articulation sweep, collision dynamics, interference-force calculation, finite-element analysis, tolerance stack, or bearing life calculation. The nominally stationary motor/reference assembly and simplified shaft envelopes are retained from the archive.

## regression

Run `python main.py --compare-source /path/to/ria.zip` to compare the port with the supplied built geometry. The old source is never executed. New functions build an explicit archived 28/14/56 fixture, which is checked against all 56 original local components. Tests compare tessellated vertex sets in both directions, CAD volumes and bounds; a differing triangulation falls back to two B-rep cuts and their symmetric-difference volume.

The default new design then checks its 35 unchanged local parts, 72 unchanged installed parts including the two head objects, and three preserved mating regions. Allowed changes include the belt, motor pulley, knee gears, their carrier/frame/hub, moved planet bearings/pins, and the new three-part frame and its fasteners. The motor grub screw is absent. The hip-side frame at Y >= 44, distal carrier mount at Y <= -26 (beyond the old carrier disk) and pulley body at Z >= 23.6 retain their geometry.

Reports are geometric evidence, not certification that any chosen printer, belt, screw or motor will assemble and carry load. The thin planet wall, screwless shaft connection and stock-belt length mismatch are explicit limitations in the report and print notes.


# provenance

The input is the user's supplied `ria.zip`, containing the previous 28/14/56 build, Python source, reference STEP models and timing-pulley profile references.

`src/head.py` and `src/hip.py` now construct the custom head, lid, bearing housings, hip mount, pinion and spacers from dimensions. Default geometry is regressed against the original build. Only the four purchased actuator shapes remain as CAD assets: 5010 rotor/stator and SG90 body/spline. They are vendored under `assets/motors/`, with source paths, hashes and coordinate transforms in its manifest. Normal builds do not read the old archive or `assets/reference` cache.

`src/gears.py` rewrites the original Python's involute construction and sampling; it does not import or execute the archived SCAD. The timing groove polygon in `src/belt.py` retains the archived `tooth_profile_GT2_3mm` coordinates, width allowance and depth offset without re-fitting. The archive attributes the timing-profile source to droftarts and rbuckland; its `pulley_profiles.scad` also credits Per Ivar Nerseth's modifications. This inherited groove is not asserted to be a manufacturer-certified GT3 profile.

Original third-party notices and ownership are not replaced by a new licence grant here. The supplied `involute_gears.scad` identifies GregFrost and a Creative Commons / GNU LGPL 2.1 licence, but that SCAD implementation is not required or distributed as runtime source by this rewrite. The original archive remains the provenance record for the supplied references. No licence for purchased/reference CAD is inferred from its presence in that archive.


# printing and assembly

All exported STL coordinates are in millimetres and touch Z=0. Caps face the bed on the head shell and both pulleys; the planet bearing socket faces up. The assembly STEP/GLB poses are unchanged by these print orientations.

There are eleven distinct robot prints: hip link (2), knee backplate (2), knee ring (2), carrier (2), 12T planet (6), sun/48T pulley (2), motor pulley (2), hip pinion (2), SG90 ear spacer (4), head shell (1), head lid (1). The nine additional files are fit coupons, not assembly components. Quantity and orientation are also recorded in `build/print_manifest.json`.

## fit first

Try the 8.0/8.1/8.2 mm bearing coupons, the 2.9/3.0/3.1 mm pin pilots and the 16T pulley/4.9 mm bore coupon with the actual hardware. The nominal model uses an 8.1 mm bearing seat and a 2.9 mm pin pilot. These are CAD dimensions, not guaranteed printed fits.

The 12T planet root diameter is 9.5 mm. Its 8.1 mm bearing seat leaves only **0.70 mm of radial material**. Do not assume it can withstand a forced bearing insertion or rated motor torque. Inspect the sliced wall and tooth paths, print a planet, and check it before assembling the robot. No material or infill prescription here is a strength certification.

The frame is now three flat-printing parts. Both knee pieces have no unsupported growth in the 0.2 mm layer audit; the unchanged hip has two small counterbore bridges. Inspect the head and other retained parts in the slicer. Cap-down pulley orientation reduces the large underside overhang; the small sun-to-hub transition still needs a slicer check. The project does not contain printer-specific G-code or a validated support strategy.

The exploded/cutaway appearance in a preview is never a printable part. Bearings, wires, purchased motors, metal pins, inner-race spacers and screws are context/hardware geometry, not included as fake plastic substitutes.

## retained hardware per leg

Six 693ZZ bearing envelopes are retained: three planet bearings, one carrier bearing and two input bearings, each nominally 3 x 8 x 4 mm. Three smooth 3 x 8 mm steel dowels locate the planets. The fixed centre uses the original M3 x 20 pan-head axle with modelled 6 mm diameter, 2.4 mm high head.

The metal spacers are 4.1 mm outside diameter / 3.1 mm bore, with lengths 0.7, 0.7, 2.7 and 0.5 mm. The SG90 retains its ear spacers and two M2 x 10 low-head screws (3.8 mm head diameter, 1.55 mm head height). The hip hardware is rebuilt parametrically to the supplied dimensions; check purchased head and shaft dimensions against the CAD.

There is **no motor-pulley grub screw** in the new bill of materials, and no radial hole to tap. The 4.9 mm through bore clears the supplied 4.8 mm shaft. The requested removal leaves positive torque transfer and axial retention unresolved; do not power this interface on the assumption that the CAD fit secures it.

## assembly order

Start with the carrier, central bearing and rear inner spacer, without the planet dowels. Place it on the separate knee backplate before attaching the ring; see the flat-print frame sequence below. Install the planet dowels with the carrier supported; the rear access windows track their 15 mm orbit. Do not use insertion force to compensate for an incorrect print fit.

Fit a bearing into each planet and lower each onto its pin, phased as shown in the neutral CAD pose. The bearing protrudes 0.3 mm behind the gear. Its inner race rests on the carrier pad; the outer race clears the annular recess.

Fit the two bearings and inner spacer into the one-piece sun/pulley, place the carrier-to-input spacer, and lower the input into mesh. The reduced 7.5 mm radius hub clears the planets; the larger pulley flange remains above them. Add the top inner washer and fixed axle. Check that tightening the metal inner-race stack does not bind the rotating races or strip the printed pilot.

Install the rotated SG90 and route its leads as in the supplied geometry. The wires are flexible envelopes, not a prescribed physical bend radius. The motor and input pulley tooth bands remain coplanar. The pulleys may need to be fitted with the belt already around them because of the flanges.

The drawn taut pitch path is **298.339 mm at 100 mm centres**. A nominal 300 mm pitch-length belt has 1.661 mm extra length. The render contains no bow, but does not make that stock belt taut. No tensioner, centre adjustment or retention solution is specified by this port.

Check assembly access, retention, free movement, backlash, axial play and belt tracking by hand before any powered test. The correct input-to-output ratio is 10:1, with the ring fixed. Actual load capacity, service life, friction and belt skipping remain to be established.

## flat-print leg frame

The old monolithic leg is replaced by `hip_link`, `knee_backplate` and `knee_ring`. Print two of each using the exported orientations: all three broad front faces go down. Heights are 9.7, 8.2 and 10.4 mm. The old `upper_leg.stl` is removed on rebuild. The hip/knee centres, ring teeth and drivetrain stack are unchanged.

Per leg: three M3x25 socket-head screws, three M3 nuts (5.5 mm flats, 2.4 mm thick), three M3 washers (7 mm OD, 0.5 mm thick), two 3x25 mm smooth steel dowels. Nuts seat in the rear pockets. Bolts clamp; dowels locate the ring. The hip link uses 2.95 mm press pilots; the upper pieces use 3.05 mm slip bores. Test the two supplied frame-dowel coupons first. Do not force an undersized printed bore.

Seat the nuts. Fit the carrier bearing and rear spacer and place the carrier on the backplate before fitting the ring. Stack the three frame pieces, start the screws loosely, then install the locating dowels flush with the ring face while supporting the hip link. Snug screws progressively; do not crush the nut-pocket floor. Finish the existing planet/input assembly above. Screw tips extend 1.4 mm and dowels 1.9 mm behind the hip plate, included in the collision check.

`frame_print_parts.png` shows actual print orientations; `frame_exploded.png` is assembly only. Each frame STL is checked at 0.2 mm layers for floating islands and growth beyond 45 degrees. Both knee parts pass without unsupported growth. The retained hip has two short counterbore bridges (unsupported components under 7 mm), explicitly reported in `frame_printability.json`. Check their bridge paths in your slicer. This is not G-code or a physical print test. An 8 mm driver envelope clears each clamp screw in the neutral assembly. Printed fits, bolt preload, stiffness and fatigue strength still require testing.
