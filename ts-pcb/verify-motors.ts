import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import type { AnyCircuitElement } from 'circuit-json'
import { getSourcePortConnectivityMapFromCircuitJson } from 'circuit-json-to-connectivity-map'

const circuit = JSON.parse(readFileSync(process.argv[2] ?? 'dist/index/circuit.json', 'utf8')) as AnyCircuitElement[]
const components = circuit.filter(x => x.type === 'source_component')
const ports = circuit.filter(x => x.type === 'source_port')
const pcbPorts = circuit.filter(x => x.type === 'pcb_port')
const map = getSourcePortConnectivityMapFromCircuitJson(circuit)
const component = (name: string) => components.find(c => c.name === name)!
const port = (name: string, pin: number) => ports.find(p => p.source_component_id === component(name).source_component_id && p.pin_number === pin)!
const physical = (name: string, pin: number) => {
  const source = port(name, pin)
  const pcb = pcbPorts.find(p => p.source_port_id === source.source_port_id)
  assert.ok(pcb, `physical port: ${name}.${pin}`)
  assert.ok(circuit.some(p => (p.type === 'pcb_smtpad' || p.type === 'pcb_plated_hole') && p.pcb_port_id === pcb.pcb_port_id), `physical pad: ${name}.${pin}`)
}
const connected = (...pins: [string, number][]) => assert.ok(map.areAllIdsConnected(pins.map(([name, pin]) => port(name, pin).source_port_id)), `connected: ${JSON.stringify(pins)}`)
const separate = (...pins: [string, number][]) => assert.equal(new Set(pins.map(([name, pin]) => map.getNetConnectedToId(port(name, pin).source_port_id))).size, pins.length, `separate: ${JSON.stringify(pins)}`)

assert.equal(component('ESP-U1').manufacturer_part_number, 'ESP32-S3-WROOM-1-N8')
for (let pin = 1; pin <= 41; pin++) physical('ESP-U1', pin)
const pwmPins = [[21, 22, 8], [9, 10, 11], [23, 28, 29], [30, 31, 32]]
const csPins = [39, 38, 37, 25]
const phasePins = [[13, 14], [16, 17], [19, 20]]
const outputs: [string, number][] = []
for (let m = 1; m <= 4; m++) {
  const driver = `MOTOR${m}-U1`
  assert.equal(component(driver).manufacturer_part_number, 'DRV8316RRGFR')
  for (let pin = 1; pin <= 41; pin++) physical(driver, pin)
  for (const pin of [9, 10, 11]) connected([driver, pin], ['POWER-J1', 2])
  for (const pin of [2, 4, 12, 15, 18, 21, 26, 41]) connected([driver, pin], ['POWER-J1', 1])
  for (let p = 0; p < 3; p++) {
    connected([driver, 27 + p * 2], ['ESP-U1', pwmPins[m - 1][p]])
    connected([driver, 28 + p * 2], ['ESP-U1', 2])
    const output: [string, number] = m <= 2 ? [`MOTOR-J${m}`, p + 1] : [`MOTOR-J${m}${'ABC'[p]}`, 1]
    physical(...output)
    connected(output, [driver, phasePins[p][0]], [driver, phasePins[p][1]])
    outputs.push(output)
  }
  connected([driver, 35], ['ESP-U1', 33])
  connected([driver, 34], ['ESP-U1', 34])
  connected([driver, 33], ['ESP-U1', 35], ['MOTOR-RS', 2])
  connected([driver, 36], ['ESP-U1', csPins[m - 1]], [`MOTOR${m}-R2`, 2])
  connected([driver, 23], ['ESP-U1', 24], ['MOTOR-RE', 1])
  connected([driver, 22], ['ESP-U1', 36], [`MOTOR${m}-R3`, 2])
  connected([driver, 25], [`MOTOR${m}-R3`, 1])
  connected([driver, 25], [driver, 37], [`MOTOR${m}-C6`, 1], [`MOTOR${m}-C7`, 1])
  separate([driver, 25], ['ESP-U1', 2], ['POWER-J1', 2], ['POWER-J1', 1])
  connected([driver, 8], [`MOTOR${m}-C2`, 1])
  connected([driver, 7], [`MOTOR${m}-C1`, 1])
  connected([driver, 6], [`MOTOR${m}-C1`, 2])
  connected([driver, 5], [`MOTOR${m}-R1`, 1])
  connected([driver, 3], [`MOTOR${m}-R1`, 2], [`MOTOR${m}-C8`, 1])
  separate([driver, 5], [driver, 3], ['POWER-J1', 1])
  for (const pin of [1, 24, 38, 39, 40]) assert.equal(map.getNetConnectedToId(port(driver, pin).source_port_id), undefined)
}
separate(...outputs, ['POWER-J1', 1], ['POWER-J1', 2], ['ESP-U1', 2])
separate(...csPins.map(pin => ['ESP-U1', pin] as [string, number]))
const enablePulldown = component('MOTOR-RE')
assert.equal(enablePulldown.ftype, 'simple_resistor')
assert.ok(enablePulldown.ftype === 'simple_resistor' && enablePulldown.resistance === 10000)
connected(['MOTOR-RE', 2], ['POWER-J1', 1])
const encoderPins = [[4, 5], [6, 7], [12, 17], [18, 19]]
for (let e = 1; e <= 4; e++) {
  connected([`ENC-J${e}`, 1], ['ESP-U1', 2])
  connected([`ENC-J${e}`, 2], ['POWER-J1', 1])
  connected([`ENC-J${e}`, 3], ['ESP-U1', encoderPins[e - 1][0]])
  connected([`ENC-J${e}`, 4], ['ESP-U1', encoderPins[e - 1][1]])
}
connected(['IMU-U1', 13], ['ENC-J1', 4])
connected(['IMU-U1', 14], ['ENC-J1', 3])
console.log('motor power, control, phase isolation and encoder connectivity passed')
