import React, { useEffect, useReducer, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { App, Btn, Card, D, Input, Muted, Select } from 'b44ui';
import { RobotViewer } from './scene.js';
import './style.css';

export let viewer: RobotViewer;

// b44ui buttons are divs; give them the same keyboard behavior as native buttons.
function Action({ onClick, disabled = false, children, ...props }) {
  return <Btn sm minHt={32} role="button" tabIndex={disabled ? -1 : 0} aria-disabled={disabled}
    opacity={disabled ? .4 : 1} onClick={disabled ? undefined : onClick}
    onKeyDown={event => {
      if (!disabled && (event.key === 'Enter' || event.key === ' ')) {
        event.preventDefault();
        event.currentTarget.click();
      }
    }} {...props}>{children}</Btn>;
}

const notes = {
  ring: 'fixed · 42 teeth',
  sun: '360° input → 108° output',
  planets: '12 teeth · reverse spin',
  carrier: 'output · 3⅓:1 reduction',
  pulley: '48 teeth · sun input',
  hardware: 'bearings + screws',
};

function ModelViewer() {
  const host = useRef<HTMLDivElement>(null);
  const angleInput = useRef<HTMLInputElement>(null);
  const angleOutput = useRef<HTMLOutputElement>(null);
  const state = useRef({ view: 'drive', playing: true, angle: 0, speed: 8, reversed: false, explode: 0, cutaway: true, selected: null as string | null }).current;
  const [, refresh] = useReducer(value => value + 1, 0);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState('');
  const [settings, setSettings] = useState(false);
  const [search, setSearch] = useState('');
  const [camera, setCamera] = useState('perspective');

  function syncAngle() {
    const degrees = state.angle * 180 / Math.PI;
    if (angleInput.current) angleInput.current.value = String(degrees);
    if (angleOutput.current) angleOutput.current.textContent = `${Math.round(degrees)}°`;
  }

  function update(patch = {}) {
    Object.assign(state, patch);
    viewer.update(state.angle, state.explode, state.cutaway);
    syncAngle();
    refresh();
  }

  function selectPart(key: string) {
    state.selected = key;
    viewer.select(key);
    refresh();
  }

  useEffect(() => {
    viewer = new RobotViewer(host.current);
    viewer.getState = () => ({
      ...state,
      visibleParts: [...viewer.parts].filter(([, part]) => part.object.visible).map(([key]) => key),
    });
    const canvas = viewer.renderer.domElement;
    let down: number[];
    const pointerDown = event => { down = [event.clientX, event.clientY]; };
    const pointerUp = event => {
      if (down && Math.hypot(event.clientX - down[0], event.clientY - down[1]) < 5) {
        const key = viewer.pick(event);
        if (key) selectPart(key);
      }
    };
    const keyboard = event => {
      if (event.code === 'Space' && event.target === document.body && state.view === 'drive') {
        event.preventDefault();
        update({ playing: !state.playing });
      }
    };
    canvas.addEventListener('pointerdown', pointerDown);
    canvas.addEventListener('pointerup', pointerUp);
    document.addEventListener('keydown', keyboard);
    let lastTime = performance.now();
    const visible = () => { lastTime = performance.now(); };
    document.addEventListener('visibilitychange', visible);
    viewer.load().then(() => {
      update();
      setReady(true);
      // Ten sun turns return the square socket and every gear to their start pose.
      const cycle = 20 * Math.PI;
      lastTime = performance.now();
      viewer.renderer.setAnimationLoop(time => {
        const elapsed = (time - lastTime) / 1000;
        lastTime = time;
        if (state.playing && state.view === 'drive' && !document.hidden) {
          state.angle += elapsed * state.speed * Math.PI / 30 * (state.reversed ? -1 : 1);
          state.angle = ((state.angle % cycle) + cycle) % cycle;
          viewer.update(state.angle, state.explode, state.cutaway);
          syncAngle();
        }
        viewer.render();
      });
    }).catch(error => {
      setError(error.message);
      throw error;
    });
    return () => {
      viewer.renderer.setAnimationLoop(null);
      viewer.resizeObserver.disconnect();
      viewer.controls.dispose();
      viewer.renderer.dispose();
      canvas.remove();
      document.removeEventListener('keydown', keyboard);
      document.removeEventListener('visibilitychange', visible);
    };
  }, []);

  function changeView(view: string) {
    state.view = view;
    state.selected = null;
    viewer.setView(view);
    setSearch('');
    setCamera('perspective');
    update();
  }

  function showAll() {
    for (const part of viewer.parts.values()) part.object.visible = true;
    refresh();
  }

  function isolate() {
    for (const [key, part] of viewer.parts) part.object.visible = key === state.selected;
    viewer.focusSelected();
    refresh();
  }

  const drive = state.view === 'drive';
  return <App p={0} gap={0} wd="100%" minHt="100dvh" align="top" fontFamily="system-ui, sans-serif">
    <main className="workspace">
      <section id="viewport" aria-label="robot model">
        <div id="canvas-host" ref={host} />
        {!ready && <D id="loading" role="status">{error || 'loading model'}</D>}
        {ready && <>
          <D className="toolbar" row align="left mid" gap={8}>
            <label className="assembly-picker"><span className="sr-only">assembly</span>
              <Select state={[state.view, changeView]} options={{ 'planetary drive': 'drive', 'leg assembly': 'leg', 'whole robot': 'robot' }} />
            </label>
            {drive && <Action id="play" onClick={() => update({ playing: !state.playing })}
              aria-label={`${state.playing ? 'pause' : 'play'} animation`}>{state.playing ? 'pause' : 'play'}</Action>}
            <Action id="settings" aria-expanded={settings} aria-controls="settings-panel" onClick={() => setSettings(!settings)}>settings</Action>
          </D>
          {settings && <Card id="settings-panel" className="settings-panel" p={16} gap={20} role="region" aria-label="settings"
            onKeyDown={event => { if (event.key === 'Escape') { setSettings(false); document.getElementById('settings').focus(); } }}>
            <D col gap={8}>
              <Muted>camera</Muted>
              <D row gap={8} flexWrap="wrap">
                {['perspective', 'top', 'side', 'fit'].map(mode => <Action key={mode} data-camera={mode}
                  aria-label={mode === 'fit' ? 'fit model' : `${mode} view`} aria-pressed={mode === camera}
                  onClick={() => { viewer.fit(mode); setCamera(mode); }}>
                  {mode === 'perspective' ? '3d' : mode}
                </Action>)}
              </D>
            </D>
            {drive && <>
              <D col gap={16}>
                <D row align="between mid">
                  <label htmlFor="cutaway">open housing</label>
                  <input id="cutaway" type="checkbox" checked={state.cutaway} onChange={event => update({ cutaway: event.target.checked })} />
                </D>
                <D col gap={6}>
                  <label className="range-label" htmlFor="explode">explode<output id="explode-value">{Math.round(state.explode * 100)}%</output></label>
                  <input id="explode" type="range" min="0" max="1" step="0.01" value={state.explode} onInput={event => update({ explode: Number(event.currentTarget.value) })} />
                </D>
              </D>
              <D id="motion" col gap={16}>
                <D col gap={6}>
                  <label className="range-label" htmlFor="speed">input speed<output id="speed-value">{state.speed} rpm</output></label>
                  <input id="speed" type="range" min="1" max="30" step="1" value={state.speed} onInput={event => update({ speed: Number(event.currentTarget.value) })} />
                </D>
                <D col gap={6}>
                  <label className="range-label" htmlFor="angle">rotation<output id="angle-value" ref={angleOutput}>{Math.round(state.angle * 180 / Math.PI)}°</output></label>
                  <input id="angle" type="range" min="0" max="3600" step="0.1" ref={angleInput}
                    defaultValue={state.angle * 180 / Math.PI} onInput={event => update({ playing: false, angle: Number(event.currentTarget.value) * Math.PI / 180 })} />
                </D>
                <D row gap={8}>
                  <Action id="reverse" aria-pressed={state.reversed} onClick={() => update({ reversed: !state.reversed })}>reverse</Action>
                  <Action id="reset" onClick={() => update({ angle: 0, playing: false })}>reset</Action>
                </D>
                <Muted id="output-speed">{(state.speed * viewer.manifest.planetary.sun / (viewer.manifest.planetary.sun + viewer.manifest.planetary.ring)).toFixed(1)} rpm output</Muted>
              </D>
            </>}
          </Card>}
        </>}
      </section>
      {ready && <aside id="parts-panel" aria-label="parts">
        <D row align="between mid" gap={8}>
          <Muted>parts</Muted>
          <Action id="show-all" onClick={showAll}>show all</Action>
        </D>
        <Input id="part-search" role="searchbox" aria-label="find a part" state={[search, setSearch]} placeholder="find a part" />
        <D id="parts" col gap={4}>
          {[...viewer.parts].filter(([, part]) => part.label.toLowerCase().includes(search.toLowerCase())).map(([key, part]) =>
            <D key={key} className="part-row" data-part={key} row align="left mid" gap={8}>
              <input type="checkbox" aria-label={`show ${part.label}`} checked={part.object.visible}
                onChange={event => { part.object.visible = event.target.checked; refresh(); }} />
              <Action className="part-name" aria-label={`select ${key}`} aria-pressed={state.selected === key}
                background={state.selected === key ? '#444' : 'transparent'} border="none" p="6px 4px" minWd={0} flex={1} align="left mid"
                onClick={() => selectPart(key)}>
                <D wd={7} ht={7} flexShrink={0} borderRadius={2} background={part.color} />
                <span>{part.label}</span>
              </Action>
            </D>
          )}
        </D>
        <Action id="isolate" disabled={!state.selected} onClick={isolate}>isolate selected</Action>
        {state.selected && <Muted id="selection-info">{drive ? notes[state.selected] : viewer.parts.get(state.selected).label}</Muted>}
      </aside>}
    </main>
  </App>;
}

createRoot(document.getElementById('root')).render(<ModelViewer />);
