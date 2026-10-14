# ria

ria is a small wheeled biped built for jumping and fast ground motion.

### bom

- 2x 5010 260kv bldc
- 2x gbm2804 145kv bldc
- 2x sg90 servo
- 1x custom esp32-s3 pcb with four drv8316ct motor drivers and an icm-42688-p imu
- funfly 1300 4s lipo
- m2, m3 screws
- 6x 693zz bearings (planet gears)
- 2x gt3 300 mm closed belt

### specs


- 10:1 two stage knee transmission
- 100mm upper and lower legs
- 720g mass
  - 150g/side motors, 200g plastic, 150g battery, 70g everything else
- 20cm jump height, 30kmh top speed (tentative, accurate-ish)

# printed parts
ria is built mostly from 3d printed parts designed in cadquery.

```bash
cd models
python3 main.py
# outputs build/ria.glb and build/stl/*.stl
```

the glb preserves the assembled cad layout. stls use their owning link's joint
frame; `models/util/frames.py` defines the knee and wheel origins in millimetres.
`ria.xml` assigns meshes to links, and `bot.json` (also at `software/bot.json`)
loads those same local meshes in botblocks. tests compare both models against
the cad assembly and check articulated ground contact.

# pcb
open `pcb/ria.kicad_pro` in kicad or backplane. the 50×65mm four-layer sensorless revision has a doit esp32-s3 module with 4mb flash, four drv8316ct motor drivers, eight filtered phase-current adc inputs, usb-c data, a vertical xt60pb input and an imu. all components mount on top; motor headers use 5.08mm pitch. the encoder headers are removed. the schematic has 104 components and 93 connected nets. native checks report zero erc violations, zero pcb errors, zero unrouted connections and zero schematic mismatches; remaining warnings and fabrication review items are in `pcb/README.md`. sensorless firmware and bench operation are not verified. local symbols, footprints and 3d models are included; `ts-pcb/` preserves the original tscircuit source and generated outputs.

see `pcb/README.md` for the pin map, checks and fabrication review requirements.

# software
botblocks impl coming soon...

`ria.xml` is the mujoco model. mesh geoms render and collide; mujoco derives
inertia from part masses and an effective plastic density of 700 kg/m³.
printed parts use mesh volume; bought parts use convex-hull mass approximations.

```bash
python3 -m mujoco.viewer --mjcf=ria.xml
python3 -m pytest tests
```
