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
python main.py --import-source /path/to/ria.zip
```

then you can just run normally (build, help, test, respectively)

```bash
python main.py
python main.py --help
python -m pytest
```

building makes some stuff in `build`. namely, you'll want to look at `build/robot.glb` and 3d print everything in `build/printable`.

| file | responsibility |
|---|---|
| `ria/config.py` | design inputs, tooth relationships, reductions and stack datums |
| `ria/knee.py` | frame, carrier, planets, integral sun/pulley and motor pulley |
| `ria/gears.py`, `ria/belt.py` | explicit involute profiles, inherited timing grooves, tangent belt path |
| `ria/hardware.py`, `ria/hip.py` | named bearings, pins, screws and retained hip hardware |
| `ria/robot.py` | installed transforms and signed motion |
| `ria/assets.py` | one-time reference import, provenance and hash checks |
| `ria/export.py`, `ria/render.py` | STEP, metre-scaled GLB, bed-oriented STLs and actual-geometry previews |
| `ria/validate.py`, `ria/regression.py` | geometry audits and comparison with the supplied build |