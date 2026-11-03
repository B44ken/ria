import { test as base, expect } from '@playwright/test';

const test = base.extend({
  runtimeErrors: [async ({ page }, use) => {
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => {
      if (message.type() === 'error') errors.push(`${message.location().url}: ${message.text()}`);
    });
    page.on('response', response => {
      if (response.status() >= 400) errors.push(`${response.status()} ${response.url()}`);
    });
    await use(errors);
    expect(errors, 'browser errors and failed asset requests').toEqual([]);
  }, { auto: true }],
});

async function state(page) {
  return page.evaluate(async () => (await import(document.querySelector('script[src*="/src/main."]').src)).viewer.getState());
}

async function motion(page) {
  return page.evaluate(async () => (await import(document.querySelector('script[src*="/src/main."]').src)).viewer.getMotion());
}

async function settings(page, expanded = true) {
  const toggle = page.locator('#settings');
  if ((await toggle.getAttribute('aria-expanded') === 'true') !== expanded) await toggle.click();
}

async function slider(page, id, value) {
  await settings(page);
  await page.locator(id).evaluate((input, next) => {
    input.stepUp(Math.round((next - Number(input.value)) / Number(input.step)));
    input.dispatchEvent(new Event('input', { bubbles: true }));
  }, value);
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(resolve)));
}

async function openPaused(page) {
  await page.goto('/');
  await expect(page.locator('canvas')).toBeVisible();
  await expect(page.getByRole('button', { name: 'pause animation', exact: true })).toBeVisible();
  await state(page);
  await page.locator('#play').click();
  await expect.poll(async () => (await state(page)).playing).toBe(false);
}

test('play, pause, speed, and reverse control the rendered animation', async ({ page }) => {
  await openPaused(page);
  await slider(page, '#angle', 180);
  const paused = await state(page);
  expect(paused.angle).toBeCloseTo(Math.PI, 8);
  await page.waitForTimeout(180);
  expect((await state(page)).angle).toBeCloseTo(paused.angle, 8);

  await slider(page, '#speed', 12);
  expect((await state(page)).speed).toBe(12);
  await page.locator('#play').click();
  await expect.poll(async () => (await state(page)).angle).toBeGreaterThan(paused.angle + 0.1);
  await page.locator('#play').click();
  const forward = await state(page);

  await page.locator('#reverse').click();
  await expect(page.locator('#reverse')).toHaveAttribute('aria-pressed', 'true');
  await page.locator('#play').click();
  await expect.poll(async () => (await state(page)).angle).toBeLessThan(forward.angle - 0.1);
  await page.locator('#play').click();
  expect((await state(page)).reversed).toBe(true);
});

test('scrubbing moves all three planets with the actual fixed-ring ratio', async ({ page }) => {
  await openPaused(page);
  await slider(page, '#angle', 0);
  const start = await motion(page);
  await slider(page, '#angle', 360);
  const end = await motion(page);
  const turn = Math.PI * 2;
  expect(end.sun - start.sun).toBeCloseTo(turn, 8);
  expect(end.carrier - start.carrier).toBeCloseTo(turn * 0.3, 8);
  expect(end.ring).toBeCloseTo(start.ring, 10);
  expect(start.planets).toHaveLength(3);
  expect(end.planets).toHaveLength(3);
  for (let index = 0; index < 3; index++) {
    const before = start.planets[index];
    const after = end.planets[index];
    expect(after.angle - before.angle).toBeCloseTo(-turn * 0.75, 8);
    expect(Math.hypot(...after.position)).toBeCloseTo(Math.hypot(...before.position), 8);
    const orbitDelta = Math.atan2(
      before.position[0] * after.position[1] - before.position[1] * after.position[0],
      before.position[0] * after.position[0] + before.position[1] * after.position[1],
    );
    expect(orbitDelta).toBeCloseTo(turn * 0.3, 8);
  }
});

test('parts can be hidden, selected, isolated, restored, and exploded', async ({ page }, testInfo) => {
  await openPaused(page);
  const initial = await state(page);
  const ring = page.locator('#parts').getByRole('checkbox', { name: 'show fixed ring', exact: true });
  await ring.uncheck();
  await expect(ring).not.toBeChecked();
  expect((await state(page)).visibleParts.length).toBeLessThan(initial.visibleParts.length);
  await page.locator('#show-all').click();
  await expect(ring).toBeChecked();
  const allParts = (await state(page)).visibleParts.length;
  expect(allParts).toBeGreaterThanOrEqual(initial.visibleParts.length);

  await page.locator('#part-search').fill('sun');
  await expect(page.locator('#parts').getByRole('button', { name: 'select sun', exact: true })).toBeVisible();
  await expect(page.locator('#parts').getByRole('button', { name: 'select ring', exact: true })).toBeHidden();
  await page.locator('#parts').getByRole('button', { name: 'select sun', exact: true }).click();
  expect((await state(page)).selected).toBeTruthy();
  await page.locator('#isolate').click();
  expect((await state(page)).visibleParts.length).toBeLessThan(initial.visibleParts.length);
  await page.locator('#part-search').fill('');
  await page.locator('#show-all').click();
  expect((await state(page)).visibleParts.length).toBe(allParts);

  const assembledGap = await page.evaluate(async () => {
    const { drive } = (await import(document.querySelector('script[src*="/src/main."]').src)).viewer;
    return drive.pulley.position.z - drive.carrier.position.z;
  });
  await slider(page, '#explode', 1);
  expect((await state(page)).explode).toBe(1);
  expect(await page.evaluate(async () => {
    const { drive } = (await import(document.querySelector('script[src*="/src/main."]').src)).viewer;
    return drive.pulley.position.z - drive.carrier.position.z;
  })).toBeGreaterThan(assembledGap + 10);
  await page.locator('#cutaway').uncheck();
  expect((await state(page)).cutaway).toBe(false);
  await page.locator('#cutaway').check();
  expect((await state(page)).cutaway).toBe(true);
  await page.screenshot({ path: testInfo.outputPath('exploded-drive.png') });
});

test('clicking the rendered sun selects the corresponding part', async ({ page }) => {
  await openPaused(page);
  await settings(page);
  await page.getByRole('button', { name: 'top view', exact: true }).click();
  await settings(page, false);
  const point = await page.evaluate(async () => {
    const { viewer } = await import(document.querySelector('script[src*="/src/main."]').src);
    const p = viewer.manifest.planetary;
    const point = viewer.drive.sun.position.clone().set(6, 0, p.gearZ + p.gearThickness);
    viewer.drive.sun.localToWorld(point);
    point.project(viewer.camera);
    const rect = viewer.renderer.domElement.getBoundingClientRect();
    return { x: rect.x + (point.x + 1) * rect.width / 2, y: rect.y + (1 - point.y) * rect.height / 2 };
  });
  await page.mouse.click(point.x, point.y);
  expect((await state(page)).selected).toBe('sun');
  await expect(page.getByRole('button', { name: 'select sun', exact: true })).toHaveAttribute('aria-pressed', 'true');
  await expect(page.locator('#selection-info')).toContainText('108°');
  const distance = await page.evaluate(async () => {
    const { viewer } = await import(document.querySelector('script[src*="/src/main."]').src);
    return viewer.camera.position.distanceTo(viewer.controls.target);
  });
  await page.mouse.wheel(0, -250);
  await expect.poll(async () => page.evaluate(async () => {
    const { viewer } = await import(document.querySelector('script[src*="/src/main."]').src);
    return viewer.camera.position.distanceTo(viewer.controls.target);
  })).toBeLessThan(distance - 1);
});

test('open housing and carrier cuts retain solid planar faces', async ({ page }, testInfo) => {
  await openPaused(page);
  await slider(page, '#angle', 0);
  const surfaces = await page.evaluate(async () => {
    const { viewer } = await import(document.querySelector('script[src*="/src/main."]').src);
    viewer.root.updateMatrixWorld(true);
    return [
      { part: 'ring', origin: [24, 0, 30], direction: [0, 0, -1] },
      { part: 'ring', origin: [0, 30, 8], direction: [0, -1, 0] },
      { part: 'carrier', origin: [0, -30, 7.7], direction: [0, 1, 0] },
    ].map(({ part, origin, direction }) => {
      viewer.raycaster.set(viewer.camera.position.clone().set(...origin), viewer.camera.position.clone().set(...direction));
      const [hit] = viewer.raycaster.intersectObject(viewer.drive[part]);
      return {
        point: hit.point.toArray(),
        normal: hit.face.normal.clone().transformDirection(hit.object.matrixWorld).toArray(),
      };
    });
  });
  const expected = [
    { point: [24, 0, 16.65], normal: [0, 0, 1] },
    { point: [0, 26, 8], normal: [0, 1, 0] },
    { point: [0, -24, 7.7], normal: [0, -1, 0] },
  ];
  for (let face = 0; face < expected.length; face++) {
    for (let axis = 0; axis < 3; axis++) {
      expect(surfaces[face].point[axis]).toBeCloseTo(expected[face].point[axis], 5);
      expect(surfaces[face].normal[axis]).toBeCloseTo(expected[face].normal[axis], 5);
    }
  }
  await page.locator('#cutaway').uncheck();
  const closedTop = await page.evaluate(async () => {
    const { viewer } = await import(document.querySelector('script[src*="/src/main."]').src);
    viewer.raycaster.set(viewer.camera.position.clone().set(24, 0, 40), viewer.camera.position.clone().set(0, 0, -1));
    return viewer.raycaster.intersectObject(viewer.drive.ring)[0].point.z;
  });
  expect(closedTop).toBeGreaterThan(16.65 + 0.5);
  await page.locator('#cutaway').check();
  await page.getByRole('button', { name: 'side view', exact: true }).click();
  await settings(page, false);
  await page.screenshot({ path: testInfo.outputPath('solid-carrier-side.png') });
});

test('drive, leg, and robot presets render and accept camera movement', async ({ page }, testInfo) => {
  await openPaused(page);
  for (const view of ['leg', 'robot', 'drive']) {
    await page.getByRole('combobox', { name: 'assembly', exact: true }).selectOption(view);
    await expect.poll(async () => (await state(page)).view).toBe(view);
    expect((await state(page)).visibleParts.length).toBeGreaterThan(0);
    const canvas = page.locator('canvas');
    const bounds = await canvas.boundingBox();
    expect(bounds.width).toBeGreaterThan(500);
    expect(bounds.height).toBeGreaterThan(350);
    expect(await page.evaluate(async () =>
      (await import(document.querySelector('script[src*="/src/main."]').src)).viewer.renderer.info.render.triangles,
    )).toBeGreaterThan(100);
    const before = await page.evaluate(async () =>
      (await import(document.querySelector('script[src*="/src/main."]').src)).viewer.camera.position.toArray(),
    );
    await page.mouse.move(bounds.x + bounds.width / 2, bounds.y + bounds.height / 2);
    await page.mouse.down();
    await page.mouse.move(bounds.x + bounds.width / 2 + 110, bounds.y + bounds.height / 2 + 50, { steps: 10 });
    await page.mouse.up();
    const after = await page.evaluate(async () =>
      (await import(document.querySelector('script[src*="/src/main."]').src)).viewer.camera.position.toArray(),
    );
    expect(Math.hypot(...after.map((value, axis) => value - before[axis]))).toBeGreaterThan(1);
    await page.screenshot({ path: testInfo.outputPath(`${view}.png`) });
  }
});

test('mobile viewport keeps controls reachable without horizontal overflow', async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await openPaused(page);
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
  await page.getByRole('combobox', { name: 'assembly', exact: true }).selectOption('leg');
  await page.locator('#parts').scrollIntoViewIfNeeded();
  await expect(page.locator('#parts')).toBeVisible();
  await page.getByRole('combobox', { name: 'assembly', exact: true }).selectOption('drive');
  await page.locator('#play').scrollIntoViewIfNeeded();
  await page.locator('#play').click();
  await expect.poll(async () => (await state(page)).playing).toBe(true);
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
  await page.screenshot({ path: testInfo.outputPath('mobile.png'), fullPage: true });
});

test('robot view loads the pcb and battery shelf at their assembled heights', async ({ page }) => {
  await openPaused(page);
  await page.getByRole('combobox', { name: 'assembly', exact: true }).selectOption('robot');
  const parts = (await state(page)).visibleParts;
  for (const name of ['head_bottom', 'head_tray', 'control_pcb', 'power_j1', 'tattu_lipo_0', 'battery_lead_0', 'battery_lead_1']) {
    expect(parts).toContain(name);
  }
  expect(parts.some(name => /simplefoc|tray_spacer|pipico|battery_shoe/.test(name))).toBe(false);
  const dimensions = await page.evaluate(async () => {
    const { viewer } = await import(document.querySelector('script[src*="/src/main."]').src);
    const bounds = name => {
      const mesh = viewer.parts.get(name).object;
      mesh.geometry.computeBoundingBox();
      const box = mesh.geometry.boundingBox.clone().applyMatrix4(mesh.matrixWorld);
      return { low: box.min.toArray(), high: box.max.toArray() };
    };
    viewer.root.updateMatrixWorld(true);
    return { pcb: bounds('control_pcb'), battery: bounds('tattu_lipo_0') };
  });
  expect(dimensions.pcb.high[2] - dimensions.pcb.low[2]).toBeCloseTo(1.6, 4);
  expect(dimensions.pcb.low[2]).toBeCloseTo(-22.8, 4);
  expect(dimensions.battery.low[2]).toBeCloseTo(-7.6, 4);
  expect(dimensions.battery.high[2]).toBeCloseTo(27.4, 4);
});

test('usb-c and balance-plug openings are present in the rendered shell', async ({ page }) => {
  await openPaused(page);
  await page.getByRole('combobox', { name: 'assembly', exact: true }).selectOption('robot');
  const hits = await page.evaluate(async () => {
    const { viewer } = await import(document.querySelector('script[src*="/src/main."]').src);
    viewer.root.updateMatrixWorld(true);
    const shell = viewer.parts.get('head_top').object;
    return [[-50, -19.6, 1], [50, 6.2, -1]].map(([y, z, direction]) => {
      viewer.raycaster.set(viewer.camera.position.clone().set(0, y, z),
        viewer.camera.position.clone().set(0, direction, 0));
      return viewer.raycaster.intersectObject(shell)[0].point.y;
    });
  });
  expect(hits[0]).toBeGreaterThan(30);
  expect(hits[1]).toBeLessThan(-30);
});
