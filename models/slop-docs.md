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

The default new design then checks its 35 unchanged local parts, 72 unchanged installed parts including the two head objects, and three preserved mating regions. Changes are confined to the belt, motor pulley, knee gears, their carrier/frame/hub, and the bearings/pins moved to the new planet orbit. The motor grub screw is absent. The hip-side frame at Y >= 44, distal carrier mount at Y <= -26 (beyond the old carrier disk) and pulley body at Z >= 23.6 retain their geometry.

Reports are geometric evidence, not certification that any chosen printer, belt, screw or motor will assemble and carry load. The thin planet wall, screwless shaft connection and stock-belt length mismatch are explicit limitations in the report and print notes.


# provenance

The input is the user's supplied `ria.zip`, containing the previous 28/14/56 build, Python source, reference STEP models and timing-pulley profile references.

`ria/assets.py` selects the two original head objects, the hip nose clipped from the original local leg, and sixteen named existing/purchased hip components. Each retained compressed B-rep is accompanied by the source-relative path, SHA-256 of the source STEP bytes, SHA-256 of the cached B-rep, volume, bounds and solid count in `assets/reference/manifest.json`. No user-specific upload path is embedded in the application.

`ria/gears.py` rewrites the original Python's involute construction and sampling; it does not import or execute the archived SCAD. The timing groove polygon in `ria/belt.py` retains the archived `tooth_profile_GT2_3mm` coordinates, width allowance and depth offset without re-fitting. The archive attributes the timing-profile source to droftarts and rbuckland; its `pulley_profiles.scad` also credits Per Ivar Nerseth's modifications. This inherited groove is not asserted to be a manufacturer-certified GT3 profile.

Original third-party notices and ownership are not replaced by a new licence grant here. The supplied `involute_gears.scad` identifies GregFrost and a Creative Commons / GNU LGPL 2.1 licence, but that SCAD implementation is not required or distributed as runtime source by this rewrite. The original archive remains the provenance record for the supplied references. No licence for purchased/reference CAD is inferred from its presence in that archive.


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
