# ria

ria is a small wheeled biped built for jumping and fast ground motion.

## bom

- 2x 5010 260kv bldc
- 2x gbm2804 145kv bldc
- 2x sg90 servo
- 2x simplefocmini dual
- 4x as5600
- funfly 1300 4s lipo
- 5v buck // todo: which?

## specs

(tentative, accurate-ish)

- 10:1 two stage knee transmission
- 100mm upper and lower leg joints
- 700g mass
- 20cm jump height
- 30kmh top speed

## usage

currently i'm working on the robot model itself, there will be software soon i promise

### models

for the time being ria relies on a bunch of assets from the old version, you'll need to import (below). specifically, we the hip and head aren't parametric yet and we don't have motor models vendored.

```bash
python -m pip install -r requirements.txt
cd models
python main.py --import-source /path/to/ria.zip
```

then you can just run normally (build, help, test, respectively)

```bash
python main.py
python main.py --help
python -m pytest
```

building makes some stuff in `build`. namely, you'll want to look at `build/robot.glb` and print the parts listed in `build/print_manifest.json`; `build/printable` also contains fit coupons.

| file | responsibility |
|---|---|
| `src/config.py` | design inputs, tooth relationships, reductions and stack datums |
| `src/frame.py` | three flat-print frame parts, bolts and locating pins |
| `src/knee.py` | carrier, planets, integral sun/pulley and motor pulley |
| `src/gears.py`, `src/belt.py` | explicit involute profiles, inherited timing grooves, tangent belt path |
| `src/hardware.py`, `src/hip.py` | named bearings, pins, screws and retained hip hardware |
| `src/robot.py` | installed transforms and signed motion |
| `src/assets.py` | one-time reference import, provenance and hash checks |
| `src/export.py`, `src/render.py` | STEP, metre-scaled GLB, bed-oriented STLs and actual-geometry previews |
| `src/validate.py`, `src/regression.py` | geometry audits and comparison with the supplied build |

### printing the leg

`hip_link.stl`, `knee_backplate.stl` and `knee_ring.stl` replace the old one-piece leg. print two of each, in the supplied orientations. each leg adds three m3x25 screws with nuts/washers and two 3x25 mm steel locating dowels. the 100 mm centres and 10:1 drivetrain stay put.

`build/previews/frame_print_parts.png` shows the print faces; `frame_exploded.png` shows assembly. the knee pieces pass the layer overhang check; the retained hip bore has two short bridges to check in your slicer. assembly and fit notes are in [models/slop-docs.md](models/slop-docs.md#flat-print-leg-frame).
