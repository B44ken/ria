import { Fragment } from 'react'
import type { FanoutTracePath } from '@tscircuit/props'
import { TYPE_C_31_M_12 } from './imports/TYPE_C_31_M_12'
import { MotorBullets, MotorDriver, motorCsPins, motorPwmPins } from './motors'
import { ICM_42688_P_TOKMAS_ } from './imports/ICM_42688_P_TOKMAS_'
import { AP63300WU_7 } from './imports/AP63300WU_7'
import { USBLC6_2SC6 } from './imports/USBLC6_2SC6'
import { XT60PW_M } from './imports/XT60PW_M'
import { TS_1088_AR02016 } from './imports/TS_1088_AR02016'
import { SS34 } from './imports/SS34'
import { FNR5040S4R7MT } from './imports/FNR5040S4R7MT'

// escape the sensor pads outward before global routing.
const imuFanoutPaths: FanoutTracePath[] = [
  { connection: 'IMU-U1.SDO', route: [{ route_type: 'wire', x: -0.750062, y: -1.392428, width: 0.12, layer: 'top' }, { route_type: 'wire', x: -0.750062, y: -2.15, width: 0.12, layer: 'top' }] },
  { connection: 'IMU-U1.MSDA', route: [{ route_type: 'wire', x: -0.249936, y: -1.392428, width: 0.12, layer: 'top' }, { route_type: 'wire', x: -0.249936, y: -2.15, width: 0.12, layer: 'top' }] },
  { connection: 'IMU-U1.MCLK', route: [{ route_type: 'wire', x: 0.249936, y: -1.392428, width: 0.12, layer: 'top' }, { route_type: 'wire', x: 0.249936, y: -2.15, width: 0.12, layer: 'top' }] },
  { connection: 'IMU-U1.INT1', route: [{ route_type: 'wire', x: 0.750062, y: -1.392428, width: 0.12, layer: 'top' }, { route_type: 'wire', x: 0.750062, y: -2.15, width: 0.12, layer: 'top' }] },
  { connection: 'IMU-U1.VDDIO', route: [{ route_type: 'wire', x: 1.142492, y: -0.500126, width: 0.12, layer: 'top' }, { route_type: 'wire', x: 2.15, y: -0.500126, width: 0.12, layer: 'top' }] },
  { connection: 'IMU-U1.GND', route: [{ route_type: 'wire', x: 1.142492, y: 0, width: 0.12, layer: 'top' }, { route_type: 'wire', x: 2.15, y: 0, width: 0.12, layer: 'top' }] },
  { connection: 'IMU-U1.RESV1', route: [{ route_type: 'wire', x: 1.142492, y: 0.499872, width: 0.12, layer: 'top' }, { route_type: 'wire', x: 2.15, y: 0.499872, width: 0.12, layer: 'top' }] },
  { connection: 'IMU-U1.VDD', route: [{ route_type: 'wire', x: 0.750062, y: 1.392428, width: 0.12, layer: 'top' }, { route_type: 'wire', x: 0.750062, y: 2.15, width: 0.12, layer: 'top' }] },
  { connection: 'IMU-U1.SENB', route: [{ route_type: 'wire', x: -1.142492, y: 0.499872, width: 0.12, layer: 'top' }, { route_type: 'wire', x: -2.15, y: 0.499872, width: 0.12, layer: 'top' }] },
  { connection: 'IMU-U1.SCK', route: [{ route_type: 'wire', x: -1.142492, y: 0, width: 0.12, layer: 'top' }, { route_type: 'wire', x: -2.15, y: 0, width: 0.12, layer: 'top' }] },
  { connection: 'IMU-U1.SDA', route: [{ route_type: 'wire', x: -1.142492, y: -0.500126, width: 0.12, layer: 'top' }, { route_type: 'wire', x: -2.15, y: -0.500126, width: 0.12, layer: 'top' }] },
]

const ClusterESP = () => <group schMatchAdapt pcbRelative pcbX={-13} pcbY={18}>
  <resistor name='ESP-R1' pcbX={0} pcbY={2} resistance='10k' footprint='0603' connections={{ pin1: 'net.V3_3', pin2: 'net.ESP_EN' }} />
  <capacitor name='ESP-C3' pcbX={0} pcbY={0} pcbRotation={180} capacitance='1uF' maxVoltageRating={10} footprint='0603' connections={{ pin1: 'net.ESP_EN', pin2: 'net.GND' }} />
  <resistor name='ESP-R2' pcbX={0} pcbY={-2} resistance='10k' footprint='0603' connections={{ pin1: 'net.V3_3', pin2: 'net.ESP_BOOT' }} />
</group>

const ClusterUSB = () => <>
  <resistor name='USB-RCC1' pcbX={-5} pcbY={-10} resistance='5.1k' footprint='0603' connections={{ pin1: 'net.USB_CC1', pin2: 'net.GND' }} />
  <resistor name='USB-RCC2' pcbX={-5} pcbY={-7.5} resistance='5.1k' footprint='0603' connections={{ pin1: 'net.USB_CC2', pin2: 'net.GND' }} />
</>

const ClusterPower = () => <>
  <AP63300WU_7 name='POWER-U1' pcbRotation={270} connections={{ VIN: 'net.VIN', EN: 'net.VIN', GND: 'net.GND', SW: 'net.POWER_SW', BST: 'net.POWER_BST', FB: 'net.POWER_FB' }} />
  <SS34 name='POWER-D1' pcbRotation={270} schRotation={90} connections={{ anode: 'net.BAT', cathode: 'net.VIN' }} />
  <SS34 name='POWER-D2' pcbRotation={270} schRotation={90} connections={{ anode: 'net.USB_VBUS', cathode: 'net.VIN' }} />
  <FNR5040S4R7MT name='POWER-L1' pcbRotation={90} connections={{ pin1: 'net.POWER_SW', pin2: 'net.V3_3' }} />
  <capacitor name='POWER-C1' pcbRotation={90} capacitance='22uF' maxVoltageRating={25} supplierPartNumbers={{ jlcpcb: ['C12891'] }} footprint='1206' connections={{ pin1: 'net.VIN', pin2: 'net.GND' }} />
  <capacitor name='POWER-C2' pcbRotation={90} maxDecouplingTraceLength={3} capacitance='100nF' maxVoltageRating={25} footprint='0603' connections={{ pin1: 'net.VIN', pin2: 'net.GND' }} />
  <capacitor name='POWER-C3' schRotation={180} pcbRotation={90} capacitance='100nF' maxVoltageRating={16} footprint='0603' connections={{ pin1: 'net.POWER_BST', pin2: 'net.POWER_SW' }} />
  <capacitor name='POWER-C4' pcbRotation={180} capacitance='22uF' maxVoltageRating={25} supplierPartNumbers={{ jlcpcb: ['C12891'] }} footprint='1206' connections={{ pin1: 'net.V3_3', pin2: 'net.GND' }} />
  <capacitor name='POWER-C5' pcbRotation={180} capacitance='22uF' maxVoltageRating={25} supplierPartNumbers={{ jlcpcb: ['C12891'] }} footprint='1206' connections={{ pin1: 'net.V3_3', pin2: 'net.GND' }} />
  <resistor name='POWER-R1' resistance='75k' supplierPartNumbers={{ jlcpcb: ['C23242'] }} footprint='0603' connections={{ pin1: 'net.V3_3', pin2: 'net.POWER_FB' }} />
  <resistor name='POWER-R2' resistance='24k' supplierPartNumbers={{ jlcpcb: ['C23352'] }} footprint='0603' connections={{ pin1: 'net.POWER_FB', pin2: 'net.GND' }} />
  <constraint pcb centerToCenter left='POWER-U1' right='POWER-R1' xDist={0} />
  <constraint pcb centerToCenter left='POWER-U1' right='POWER-R2' xDist={0} />
  <constraint pcb centerToCenter top='POWER-U1' bottom='POWER-R1' yDist={3.4} />
  <constraint pcb centerToCenter top='POWER-U1' bottom='POWER-R2' yDist={5} />
  <constraint pcb centerToCenter left='POWER-U1' right='POWER-C1' xDist={6.4} />
  <constraint pcb centerToCenter top='POWER-U1' bottom='POWER-C1' yDist={0} />
  <constraint pcb centerToCenter left='POWER-U1' right='POWER-C2' xDist={3.2} />
  <constraint pcb centerToCenter left='POWER-U1' right='POWER-L1' xDist={0} />
  <constraint pcb centerToCenter top='POWER-U1' bottom='POWER-C2' yDist={0} />
  <constraint pcb centerToCenter top='POWER-L1' bottom='POWER-U1' yDist={5.5} />
  <constraint pcb centerToCenter left='POWER-C3' right='POWER-U1' xDist={3.8} />
  <constraint pcb centerToCenter top='POWER-C3' bottom='POWER-U1' yDist={1.2} />
  <constraint pcb centerToCenter left='POWER-C4' right='POWER-U1' xDist={5.1} />
  <constraint pcb centerToCenter top='POWER-C4' bottom='POWER-U1' yDist={8} />
  <constraint pcb centerToCenter left='POWER-C4' right='POWER-C5' xDist={0} />
  <constraint pcb centerToCenter top='POWER-C4' bottom='POWER-C5' yDist={3} />
  <constraint pcb centerToCenter left='POWER-D1' right='POWER-U1' xDist={3.8} />
  <constraint pcb centerToCenter top='POWER-U1' bottom='POWER-D1' yDist={6.4} />
  <constraint pcb centerToCenter left='POWER-U1' right='POWER-D2' xDist={3.6} />
  <constraint pcb centerToCenter top='POWER-U1' bottom='POWER-D2' yDist={6.4} />
</>

// sdo high selects 0x37; the as5600 encoders use 0x36. use the tokmas register map.
const ClusterIMU = () => <>
  <fanout name='IMU-FANOUT' pcbTracePaths={imuFanoutPaths}>
  <ICM_42688_P_TOKMAS_ name='IMU-U1' pcbX={0} pcbY={0} connections={{
    VDD: 'net.V3_3', VDDIO: 'net.V3_3', SENB: 'net.V3_3', SDO: 'net.V3_3', MSDA: 'net.V3_3', MCLK: 'net.V3_3', GND: 'net.GND', RESV1: 'net.GND', SDA: 'net.SDA0', SCK: 'net.SCL0', INT1: 'net.IMU_INT',
  }} />
  </fanout>
  <capacitor name='IMU-C1' schRotation={270} schX={-12.29} schY={2.934} pcbX={-3.5} pcbY={0} pcbRotation={90} capacitance='100nF' maxVoltageRating={16} footprint='0603' connections={{ pin1: 'net.V3_3', pin2: 'net.GND' }} />
  <capacitor name='IMU-C2' schRotation={270} schX={-10.25} schY={2.934} pcbX={3.5} pcbY={-1.3} capacitance='100nF' maxVoltageRating={16} footprint='0603' connections={{ pin1: 'net.V3_3', pin2: 'net.GND' }} />
</>

// one hardware and three software i2c buses keep the four 0x36 encoders separate.
const ClusterEncoders = () => <>
  {[0, 1, 2, 3].map(i => <Fragment key={i}>
    <resistor name={`ENC-RD${i}`} pcbX={13.5} pcbY={-12 + i * 3.2} pcbRotation={90} resistance='4.7k' footprint='0603' connections={{ pin1: 'net.V3_3', pin2: `net.SDA${i}` }} />
    <resistor name={`ENC-RC${i}`} pcbX={16.5} pcbY={-12 + i * 3.2} pcbRotation={90} resistance='4.7k' footprint='0603' connections={{ pin1: 'net.V3_3', pin2: `net.SCL${i}` }} />
  </Fragment>)}
</>

export default () => <board schMatchAdapt width={50} height={62.8} boardAnchorPosition={{ x: 0, y: -8.6 }} outline={[{ x: -25, y: -40 }, { x: 25, y: -40 }, { x: 25, y: 22.8 }, { x: -25, y: 22.8 }]} layers={2} thickness={1.6} schPack pcbRelative minPadEdgeToPadEdgeClearance={0.09} minViaEdgeToPadEdgeClearance={0.15} pcbStyle={{ viaHoleDiameter: 0.3, viaPadDiameter: 0.6 }} minViaHoleDiameter={0.3} minViaPadDiameter={0.6}>
  <ClusterESP />
  <USBLC6_2SC6 name='USB-U2' pcbY={-30.5} pcbRotation={90} connections={{ pin1: 'net.USB_DP', pin6: 'net.USB_DP', pin3: 'net.USB_DM', pin4: 'net.USB_DM', pin2: 'net.GND', pin5: 'net.USB_VBUS' }} />
  <capacitor name='USB-C1' schRotation={270} schX={0.89} schY={-24.7} pcbX={5} pcbY={-31} capacitance='100nF' maxVoltageRating={25} footprint='0603' connections={{ pin1: 'net.USB_VBUS', pin2: 'net.GND' }} />
  <group schMatchAdapt pcbRelative pcbX={18} pcbY={-34}>
  <TS_1088_AR02016 name='ESP-SW1' pcbX={-5} pcbY={0} connections={{ pin1: 'net.ESP_EN', pin2: 'net.GND' }} />
  <TS_1088_AR02016 name='ESP-SW2' pcbX={3} pcbY={0} connections={{ pin1: 'net.ESP_BOOT', pin2: 'net.GND' }} />
  </group>
  <net name='GND' isGroundNet />
  <net name='V3_3' isPowerNet />
  <net name='VIN' isPowerNet />
  <net name='BAT' isPowerNet nominalTraceWidth={1.5} />
  <net name='USB_VBUS' isPowerNet />
  <chip name='ESP-U1' manufacturerPartNumber='ESP32-S3-WROOM-1-N8' supplierPartNumbers={{ jlcpcb: ['C2913198'] }} footprint='kicad:RF_Module/ESP32-S3-WROOM-1' pcbY={16.8} schX={29.99} schY={-36.58} schHeight={4.2} noConnect={['IO3', 'IO45', 'IO46']} pinLabels={{
    pin1: 'GND1', pin2: 'VCC', pin3: 'EN', pin4: 'IO4', pin5: 'IO5', pin6: 'IO6', pin7: 'IO7', pin8: 'IO15', pin9: 'IO16', pin10: 'IO17', pin11: 'IO18', pin12: 'IO8', pin13: 'IO19', pin14: 'IO20', pin15: 'IO3', pin16: 'IO46',
    pin17: 'IO9', pin18: 'IO10', pin19: 'IO11', pin20: 'IO12', pin21: 'IO13', pin22: 'IO14', pin23: 'IO21', pin24: 'IO47', pin25: 'IO48', pin26: 'IO45', pin27: 'IO0', pin28: 'IO35', pin29: 'IO36', pin30: 'IO37',
    pin31: 'IO38', pin32: 'IO39', pin33: 'IO40', pin34: 'IO41', pin35: 'IO42', pin36: 'RXD0', pin37: 'TXD0', pin38: 'IO2', pin39: 'IO1', pin40: 'GND2', pin41: 'EP',
  }} pinAttributes={{ VCC: { requiresPower: true }, GND1: { requiresGround: true }, GND2: { requiresGround: true }, EP: { requiresGround: true } }} connections={{
    VCC: 'net.V3_3', GND1: 'net.GND', GND2: 'net.GND', EP: 'net.GND', EN: 'net.ESP_EN', IO0: 'net.ESP_BOOT',
    IO4: 'net.SDA0', IO5: 'net.SCL0', IO6: 'net.SDA1', IO7: 'net.SCL1', IO8: 'net.SDA2', IO9: 'net.SCL2', IO10: 'net.SDA3', IO11: 'net.SCL3', IO12: 'net.IMU_INT', IO19: 'ESP-R3.pin2', IO20: 'ESP-R4.pin2',
    IO40: 'net.MOTOR_SCLK', IO41: 'net.MOTOR_MOSI', IO42: 'net.MOTOR_MISO', IO47: 'net.MOTOR_ENABLE', RXD0: 'net.MOTOR_FAULT',
    ...Object.fromEntries(motorPwmPins.flatMap((pins, i) => pins.map((pin, j) => [`IO${pin}`, `net.MOTOR${i + 1}_PWM_${['A', 'B', 'C'][j]}`]))),
    ...Object.fromEntries(motorCsPins.map((pin, i) => [pin, `net.MOTOR${i + 1}_CS`])),
  }} />
  <keepout shape='rect' pcbX={0} pcbY={27} width={20} height={8} layers={['top', 'bottom']} excludeRefs={['.ESP-U1']} />
  <TYPE_C_31_M_12 name='USB-J1' pcbY={-36} schX={35.01} schY={-36.58} connections={{ EH1: 'net.GND', EH2: 'net.GND', EH3: 'net.GND', EH4: 'net.GND', GND1: 'net.GND', GND2: 'net.GND', VBUS1: 'net.USB_VBUS', VBUS2: 'net.USB_VBUS', CC1: 'net.USB_CC1', CC2: 'net.USB_CC2', DP1: 'net.USB_DP', DP2: 'net.USB_DP', DN1: 'net.USB_DM', DN2: 'net.USB_DM' }} />
  <XT60PW_M name='POWER-J1' pcbX={-15} pcbY={-34.7} pcbRotation={90} connections={{ pin1: 'net.GND', pin2: 'net.BAT' }} />
  {[1, 2].map(i => <pinheader key={i} name={`MOTOR-J${i}`} pcbX={i === 1 ? -21 : 21} pcbY={i === 1 ? 16 : -11} pcbRotation={90} pinCount={3} pitch={2.54} pinLabels={['A', 'B', 'C']} connections={{ pin1: `net.MOTOR${i}_A`, pin2: `net.MOTOR${i}_B`, pin3: `net.MOTOR${i}_C` }} />)}
  <MotorBullets motor={3} pcbX={-18.5} />
  <MotorBullets motor={4} pcbX={4.5} />
  {[[-11, 9], [11, 9], [-11, -8.3], [11, -8.3]].map(([x, y], i) => <MotorDriver key={i} motor={i + 1} pcbX={x} pcbY={y} />)}
  <resistor name='MOTOR-RE' pcbX={-14} pcbY={11} resistance='10k' footprint='0603' connections={{ pin1: 'net.MOTOR_ENABLE', pin2: 'net.GND' }} />
  <resistor name='MOTOR-RS' pcbX={-14} pcbY={7} resistance='10k' footprint='0603' connections={{ pin1: 'net.V3_3', pin2: 'net.MOTOR_MISO' }} />
  <group schMatchAdapt pcbRelative>
    {[1, 2, 3, 4].map((i, j) => <pinheader key={i} name={`ENC-J${i}`} pcbX={j % 2 === 0 ? 18.8 : 22.7} pcbY={j < 2 ? 6 : 17.5} pinCount={4} pitch={2.54} pcbRotation={90} connections={{ pin1: 'net.V3_3', pin2: 'net.GND', pin3: `net.SDA${i - 1}`, pin4: `net.SCL${i - 1}` }} />)}
  </group>
  <group schMatchAdapt pcbRelative>
    <capacitor name='ESP-C1' pcbX={-17} pcbY={21.5} pcbRotation={180} capacitance='10uF' maxVoltageRating={10} footprint='0805' connections={{ pin1: 'net.V3_3', pin2: 'net.GND' }} />
    <capacitor name='ESP-C2' pcbX={-17} pcbY={19.5} pcbRotation={180} capacitance='100nF' maxVoltageRating={16} footprint='0603' connections={{ pin1: 'net.V3_3', pin2: 'net.GND' }} />
    <resistor name='ESP-R3' schRotation={0} pcbX={-13} pcbY={13} pcbRotation={180} schX={-8.68} schY={-22.87} resistance='22' footprint='0603' connections={{ pin1: 'net.USB_DM' }} />
    <resistor name='ESP-R4' pcbX={-13} pcbY={14.5} pcbRotation={180} resistance='22' footprint='0603' connections={{ pin1: 'net.USB_DP' }} />
  </group>
  <group schMatchAdapt pcbPack pcbX={-16} pcbY={-2}>
    <ClusterPower />
  </group>
  <group schMatchAdapt pcbRelative pcbX={0} pcbY={0}>
    <ClusterIMU />
    <ClusterEncoders />
  </group>
  <group schMatchAdapt pcbRelative pcbX={0} pcbY={-22}><ClusterUSB /></group>
  <copperpour connectsTo='net.GND' layer='top' clearance={0.15} boardEdgeMargin={0.25} />
  <copperpour connectsTo='net.GND' layer='bottom' clearance={0.15} boardEdgeMargin={0.25} />
  <net name='USB_DP' nominalTraceWidth={0.25} />
  <net name='USB_DM' nominalTraceWidth={0.25} />
</board>
