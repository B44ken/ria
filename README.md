# ria

ria is a small wheeled biped built for jumping and fast ground motion.

### bom

- 2x 5010 260kv bldc
- 2x gbm2804 145kv bldc
- 2x sg90 servo
- 2x simplefocmini dual
- mpu6050, tca9548a, mp1584, 4x as5600
- raspberry pi pico 2w
- funfly 1300 4s lipo
- m2, m3 screws
- 6x 693zz bearings (planet gears)
- 2x gt3 300 mm closed belt

### specs

(tentative, accurate-ish)

- 10:1 two stage knee transmission
- 100mm upper and lower leg joints
- 700g mass
- 20cm jump height
- 30kmh top speed

# printed parts
ria is built mostly from 3d printed parts designed in cadquery.

```bash
cd models
python3 main.py
# outputs build/ria.glb
```

# pcb
the pcb is a 50x60mm esp32-based board, built in tscircuit. it has usb c (pd and data), xt60 input (up to 25v), four spi headers for encoders, and an imu.

```bash
tsci build
```

# software
botblocks impl coming soon...
