# ria

ria is a small wheeled biped built for jumping and fast ground motion.

![](screenshot.png)

### bom

- 2x 5010 260kv bldc
- 2x gbm2804 145kv bldc
- 2x sg90 servo
- 4x as5600
- funfly 1300 4s lipo
- m2, m3 screws
- 6x 693zz bearings (planet gears)
- 2x 687zz bearings (knee sprockets)
- 2x gt3 300 mm closed belt

### specs
- 10:1 two stage knee transmission
- custom pcb
- 100mm upper and lower legs
- 720g mass
  - 150g/side motors, 200g plastic, 150g battery, 70g everything else
- 20cm jump height, 30kmh top speed (tentative, accurate-ish)

# printed parts
ria is built mostly from parts designed in cadquery. nearly every part has a flat face so it should be easy to 3d print. you'll also need some m3 screws of various sizes and a handful of bearings.

```bash
cd models
python3 main.py
```

# pcb
the pcb is the most expensive part of the design, at roughly $100 (from jlcpcb assembly). i built it in backplane. the kicad project is at `pcb/ria.kicad_pro`

# software
ria is trained and driven in [botblocks.dev](https://botblocks.dev)

```bash
cd software
botblocks import robot bot.json --save $MY_FORK/robot
botblocks run drive.py
```
