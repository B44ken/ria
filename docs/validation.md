# validation scope

`python main.py` runs the audit after export. A failed check makes the entry point exit nonzero; results are written to `build/validation.json`. `--no-validate` is an explicit opt-out, not an implicit success. Mesh export integrity checks still run on that path.

The audit checks valid positive-volume CAD, reopened STEP assemblies, reopened GLB meshes and metre/Y-up conversion, and every exported STL. A print must be one connected watertight, consistently wound mesh with positive volume and a bed-contacting minimum Z. Its bytes are hashed after reopening.

The actual sampled involute extrusion polygons are tested through a complete carrier revolution at 721 poses, with all three planets. Both sun/planet and planet/ring engagement are checked, as are adjacent planets. A small signed backlash probe distinguishes a meshing gear from a gear merely floating without contact. The absolute planet spin is -2.5 times carrier angle; the sun spins 10/3 times, and the motor 10 times.

A conservative carrier silhouette is checked against the neck at 241 poses through -120 to +120 degrees. The carrier rear axial clearance and the resized sun-hub clearance are checked separately. The full servo projection is checked against a conservative inward tooth-tip envelope of the taut belt, not just the visible smooth backing.

Neutral collision checks use OpenCascade intersections of the actual B-reps after an axis-aligned broadphase. Gear-to-gear and gear-to-ring pairs use their extruded-profile/axial-stack proof instead of expensive redundant solid Booleans. Named dowel press fits and tap-pilot overlaps are reported separately. Any overlap at an unchanged reference-to-reference hip/head interface is also reported separately; it is not silently labelled an intended new fit. The numerical positive-volume reporting threshold is 0.012 mm3.

The installed model is checked between sides and against the head at neutral. The per-leg result is reused for the two identical rigid installations. This is not a combined hip articulation sweep, collision dynamics, interference-force calculation, finite-element analysis, tolerance stack, or bearing life calculation. The nominally stationary motor/reference assembly and simplified shaft envelopes are retained from the archive.

## regression

Run `python main.py --compare-source /path/to/ria.zip` to compare the port with the supplied built geometry. The old source is never executed. New functions build an explicit archived 28/14/56 fixture, which is checked against all 56 original local components. Tests compare tessellated vertex sets in both directions, CAD volumes and bounds; a differing triangulation falls back to two B-rep cuts and their symmetric-difference volume.

The default new design then checks its 35 unchanged local parts, 72 unchanged installed parts including the two head objects, and three preserved mating regions. Changes are confined to the belt, motor pulley, knee gears, their carrier/frame/hub, and the bearings/pins moved to the new planet orbit. The motor grub screw is absent. The hip-side frame at Y >= 44, distal carrier mount at Y <= -20 and pulley body at Z >= 23.6 retain their geometry.

Reports are geometric evidence, not certification that any chosen printer, belt, screw or motor will assemble and carry load. The thin planet wall, screwless shaft connection and stock-belt length mismatch are explicit limitations in the report and print notes.
