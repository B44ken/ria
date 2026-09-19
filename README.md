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

the head, lid, hip mounts and printed gears are parametric python. the supplied 5010 and sg90 models are vendored in `models/assets/motors`; a fresh clone needs no old archive or import step.

```bash
python -m pip install -r requirements.txt
python models/main.py
```

outputs go to `models/build`. help and tests:

```bash
python models/main.py --help
cd models && python -m pytest
```

for example, change the head dimensions without editing source:

```bash
python models/main.py --head-size 84 80 70 --head-wall 3 --output models/build-wide
```

`HeadConfig`, `HipConfig` and `HipGears` in `models/src/config.py` hold the dimensions. the lid and both hip installations follow the head size; motor/servo mounting patterns and the 28t/36t hip mesh remain fixed hardware interfaces. `--hip-mount-radius` adjusts the printed motor plate, not the motor itself.

building makes some stuff in `build`. namely, you'll want to look at `build/robot.glb` and print the parts listed in `build/print_manifest.json`; `build/printable` also contains fit coupons.

| file | responsibility |
|---|---|
| `src/config.py` | head/hip dimensions, gear relationships and stack datums |
| `src/head.py` | shell, lid, bearing housings and integral hip sectors |
| `src/frame.py` | three flat-print frame parts, bolts and locating pins |
| `src/knee.py` | carrier, planets, integral sun/pulley and motor pulley |
| `src/gears.py`, `src/belt.py` | explicit involute profiles, inherited timing grooves, tangent belt path |
| `src/hardware.py`, `src/hip.py` | parametric hip mount/pinion/spacers, bearings and screws |
| `src/robot.py` | installed transforms and signed motion |
| `src/assets.py` | hash-checked vendored motor CAD; archive reader for optional regression only |
| `src/export.py`, `src/render.py` | STEP, metre-scaled GLB, bed-oriented STLs and actual-geometry previews |
| `src/validate.py`, `src/regression.py` | geometry audits and comparison with the supplied build |

### printing the leg

`hip_link.stl`, `knee_backplate.stl` and `knee_ring.stl` replace the old one-piece leg. print two of each, in the supplied orientations. each leg adds three m3x25 screws with nuts/washers and two 3x25 mm steel locating dowels. the 100 mm centres and 10:1 drivetrain stay put.

`build/previews/frame_print_parts.png` shows the print faces; `frame_exploded.png` shows assembly. the knee pieces pass the layer overhang check; the retained hip bore has two short bridges to check in your slicer. assembly and fit notes are in [models/slop-docs.md](models/slop-docs.md#flat-print-leg-frame).
