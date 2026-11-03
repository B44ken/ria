# ria parts viewer

```sh
bun install
bun run dev
```

open http://127.0.0.1:5173. the included model runs independently of the rest of the repo.

- planetary drive: play/pause, reverse, speed, rotation scrub, open housing, and exploded view.
- leg / robot: inspect the full cad assembly. click parts to select them; use the checkboxes or isolate button to see inside.
- drag to orbit, scroll to zoom, right-drag to pan. top, side, and fit reset the camera. space toggles animation when the page itself has focus.

the 18/12/42-tooth drive uses fixed-ring kinematics: carrier speed is 0.3× the sun speed; planet spin is −0.75× in the stationary frame. the carrier arm is cropped in the drive detail. exploded positions are illustrative; this is not a dynamics or collision simulator. leg and robot views are static.

to refresh the bundled model from the adjacent ria sources:

```sh
bun run refresh-model
```

this needs ria's python cad dependencies. it exports a temporary source snapshot without changing the repo's `build/` files. the model manifest records the source hash and dimensions.

```sh
bun run test
bun run test:e2e
bun run build
```

browser tests use installed google chrome. `dist/` is a standalone static site after building. rendering uses [three.js](https://threejs.org/docs/) and its [orbit controls](https://threejs.org/docs/pages/OrbitControls).
