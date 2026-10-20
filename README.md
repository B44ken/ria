# ria

ria is a small wheeled biped built for jumping and fast ground motion.

![](screenshot.png)

### bom

- 2x 5010 260kv bldc
- 2x gbm2804 145kv bldc
- 2x sg90 servo
- control pcb: 4x ss6343m, doit esps3-32-n4, tokmas icm-42688-p, ap63301
- 4x as5600
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
ria is built mostly from parts designed in cadquery. nearly every part has a flat face so it should be easy to 3d print. you'll need some m3 screws of various sizes and some 693 bearings.

```bash
cd models
python3 main.py
```

# pcb

open [pcb/ria.kicad_pro](pcb/ria.kicad_pro) in kicad or backplane.

price-out command (kicad, python requests/gmalg, and an existing jlcone login required):

```bash
python3 pcb/priceout.py  # defaults to 5 pcbs, 2 assembled
```

each run validates a snapshot, uploads its gerbers/bom/cpl over http, selects the cheapest complete shipping service to canada, and saves a pre-coupon quote under `/tmp/ria-priceout-*`. it reuses the jlcone login without opening a browser or changing focus. it does not place an order. `--files-only` validates and exports without contacting jlcpcb.

manufacturing options come from the latest saved ria cart item. the command exchanges jlcone's existing sign-in for a fresh cart session in memory. failed runs save `quote_status: failed`; they never return a previous quote.

# software
ria is trained and driven in [botblocks.dev](https://botblocks.dev)

```bash
cd software
botblocks import robot bot.json --save myriafork/robot --root ..
botblocks run drive.py
```
