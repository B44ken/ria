# ria

ria is a small wheeled biped built for jumping and fast ground motion.

### bom

- 2x 5010 260kv bldc
- 2x gbm2804 145kv bldc
- 2x sg90 servo
- 2x simplefocmini dual
- 4x as5600
- 4x mpu6050
- tca9548a
- raspberry pi pico 2w
- mp1584
- funfly 1300 4s lipo
- ?x m3 screws
- ?x m2 screws
- ?x 693zz bearings
- ?x 685zz bearings

## specs

(tentative, accurate-ish)

- 10:1 two stage knee transmission
- 100mm upper and lower leg joints
- 700g mass
- 20cm jump height
- 30kmh top speed

# usage

ria is built from 3d printed parts designed in cadquery.

```bash
cd models
python3 main.py
# outputs build/ria.glb
```

currently i'm working on the robot model itself, there will be software soon...
