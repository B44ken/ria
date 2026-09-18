# ria

Readable CadQuery source for the supplied head, two upper legs, and knee transmissions. This is the same upper-body assembly, not a newly invented lower-leg/wheel robot.

## run

Python 3.13 was used for the checked build.

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The repository contains the modelling code, not the large supplied STEP references or generated builds. **Import the original `ria.zip` once:**

```sh
python main.py --import-source /path/to/ria.zip
```

The importer selects and checks 19 unchanged reference shapes; it does **not** execute the old Python. Subsequent builds are simply:

```sh
python main.py
```

The accompanying complete project ZIP already contains `assets/reference/`, so it needs no import step. Keep that directory for reproducible, offline rebuilds. The cached assets are small compressed B-reps; the original 132 MB archive is not a runtime dependency after import.

The default command builds both assemblies, exports CAD/meshes/print parts, checks geometry, and renders stills plus a motion GIF. `python main.py --help` lists the switches. Useful variants:

```sh
python main.py --knee-only
python main.py --no-render
python main.py --compare-source /path/to/ria.zip
python -m pip install -r requirements-dev.txt
python -m pytest
```

On a system without a usable off-screen OpenGL context, use `--no-render`. Rendering uses VTK; Blender and the old `deps/` folder are not required. Build/validation failures exit nonzero. No geometry is built by importing the entry point.

## what changed

The fixed-ring planetary is now **18T sun / three 12T planets / 42T ring**. With the unchanged 16T-to-48T belt stage:

```
planetary = 1 + 42/18 = 10/3
belt      = 48/16     = 3
overall   = (10/3)*3  = 10
```

The case is **50 mm outside diameter**, including **2.75 mm ring-root wall** (the previously requested extra 1 mm). The planet orbit, carrier, bearing/pin locations and frame transition follow the smaller gearset. The lower-leg mounting interface stays put. The sun hub shrinks to radius 7.5 mm to retain 0.5 mm conservative radial clearance from the planets; the pulley faces and axial stack stay put.

The belt has straight, external-tangent free spans: **zero modelled bow**. The motor pulley is only its toothed band, cap and through bore: **no radial grub screw or radial screw hole**. The fixed central knee bearing axle remains.

Everything else is carried over. Regression mode rebuilds the old 28/14/56 configuration with the new functions and compares it to the supplied build, then separately checks the unchanged parts and interfaces in the new model. It does not copy or run the original modelling script.

## where to edit

| file | responsibility |
|---|---|
| `main.py` | build, export, validate, render |
| `ria/config.py` | design inputs, tooth relationships, reductions and stack datums |
| `ria/knee.py` | frame, carrier, planets, integral sun/pulley and motor pulley |
| `ria/gears.py`, `ria/belt.py` | explicit involute profiles, inherited timing grooves, tangent belt path |
| `ria/hardware.py`, `ria/hip.py` | named bearings, pins, screws and retained hip hardware |
| `ria/robot.py` | installed transforms and signed motion |
| `ria/assets.py` | one-time reference import, provenance and hash checks |
| `ria/export.py`, `ria/render.py` | STEP, metre-scaled GLB, bed-oriented STLs and actual-geometry previews |
| `ria/validate.py`, `ria/regression.py` | geometry audits and comparison with the supplied build |

The original hip/head geometry is retained as B-reps because its construction history was not in the archive's Python. It is not disguised as newly parametric geometry. The 100 mm hip interface and purchased-part stack are fixed interfaces; arbitrary changes to those datums require editing their mating geometry, not just changing a number.

## outputs

`build/robot.step` and `build/robot.glb` contain the installed head and two legs. `build/knee.step` and `build/knee.glb` contain one local leg. `build/cad_parts/` keeps every local component separate. `build/printable/` contains eight distinct robot print designs and seven fit coupons; `print_manifest.json` gives quantities, orientations and hashes.

`build/previews/` contains full-assembly views, honest gear cutaways, a contact sheet of every STL, and the knee motion GIF. `model.json`, `validation.json`, and optional `regression.json` retain the numerical evidence.

CAD and STL units are millimetres. GLB is metres, Y-up. Local knee coordinates are `(0,0)`, hip `(0,100)`, positive Z outboard. The right-leg installation is `(-x, z+40.7, y-88)`; the left leg is the same geometry rotated 180 degrees about head vertical.

## before hardware

This is a geometry-checked prototype, not a load-rated design. Read [the print and assembly notes](docs/printing.md) and [validation scope](docs/validation.md).

Three unresolved physical constraints are deliberately not hidden: the 12T bearing-seat root wall is only **0.70 mm**; the screwless **4.9 mm bore on a 4.8 mm shaft does not establish torque/axial retention**; and a taut belt at the fixed centres has a **298.339 mm pitch path, not 300 mm**. No interference fit, tensioner, hidden adjustment or strength claim was invented to erase those differences.
