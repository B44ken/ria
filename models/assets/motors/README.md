# actuator cad

These are the supplied 5010 rotor/stator and SG90 body/output spline, not new approximate motor models. All lengths are millimetres. `manifest.json` records the original archive-relative STEP paths, source and vendored SHA-256 hashes, bounds, volumes and coordinate transforms.

5010 coordinates use the mounting face at Z=0, shaft toward +Z. SG90 coordinates use its output shoulder at Z=0, spline toward -Z and body length along X. `src/hip.py` places them into the assembly.

The 5010 shapes are XZ-compressed STEP, re-exported without redundant p-curves and checked for zero solid-volume difference. SG90 files are XZ-compressed OpenCascade B-reps. `MotorLibrary` decompresses them locally and verifies hashes before import; it never downloads CAD. The old archive is needed only for an optional regression comparison.

No supplier licence accompanied the user-provided references; this project does not assert a new licence or manufacturer certification for them. The GBM2804 wheel motor is not represented by this upper-body model.
