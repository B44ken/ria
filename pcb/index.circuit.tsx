import { Fragment } from 'react'
import { TYPE_C_31_M_12 } from './imports/TYPE_C_31_M_12'
import { ESP32_S3_WROOM_1_N8 } from './imports/ESP32_S3_WROOM_1_N8'
import { LSM6DSOTR } from './imports/LSM6DSOTR'
import { TCA9548APWR } from './imports/TCA9548APWR'
import { TPS25730DREFR } from './imports/TPS25730DREFR'
import { AP63203WU_7 } from './imports/AP63203WU_7'
import { TPD2EUSB30DRTR } from './imports/TPD2EUSB30DRTR'
import { XT60PW_M } from './imports/XT60PW_M'
import { TS_1088_AR02016 } from './imports/TS_1088_AR02016'
import { SS34 } from './imports/SS34'
import { FNR5040S3R9NT } from './imports/FNR5040S3R9NT'

const ClusterESP = () => <group pcbPack pcbPackGap={0.6} pcbX={-17} pcbY={19} width={10} height={8}>
  <resistor name='ESP-R1' resistance='10k' footprint='0603' connections={{ pin1: 'net.V3_3', pin2: 'net.ESP_EN' }} />
  <capacitor name='ESP-C3' capacitance='1uF' maxVoltageRating={10} footprint='0603' connections={{ pin1: 'net.ESP_EN', pin2: 'net.GND' }} />
  <resistor name='ESP-R2' resistance='10k' footprint='0603' connections={{ pin1: 'net.V3_3', pin2: 'net.ESP_BOOT' }} />
</group>

const ClusterUSB = () => <>
  <TPS25730DREFR name='USB-U1' connections={{ LDO_3V3: 'net.USB_LDO3', N_FAULT_IN: 'net.USB_LDO3', LDO_1V5: 'net.USB_LDO1', VIN_3V3: 'net.V3_3', PLUG_EVENT: 'net.USB_ATTACHED', I2Ct_SDA: 'net.GND', I2Ct_SCL: 'net.GND', CC1: 'net.USB_CC1', CC2: 'net.USB_CC2', GND1: 'net.GND', GND2: 'net.GND', GND3: 'net.GND', GND4: 'net.GND', GND5: 'net.GND', GND6: 'net.GND', GND7: 'net.GND', GND8: 'net.GND', GND9: 'net.GND', ADCIN1: 'net.GND', ADCIN2: 'net.USB_MAX_V', ADCIN3: 'net.GND', ADCIN4: 'net.GND', RESERVED1: 'net.GND', RESERVED2: 'net.GND', RESERVED3: 'net.GND', DRAIN1: 'net.USB_DRAIN', DRAIN2: 'net.USB_DRAIN', DRAIN3: 'net.USB_DRAIN', PPHV1: 'net.USB_POWER', PPHV2: 'net.USB_POWER', PPHV3: 'net.USB_POWER', VBUS_IN1: 'net.USB_VBUS', VBUS_IN2: 'net.USB_VBUS', VBUS_IN3: 'net.USB_VBUS', VBUS1: 'net.USB_VBUS', VBUS2: 'net.USB_VBUS' }} />
  <resistor name='USB-R1' resistance='191k' footprint='0603' connections={{ pin1: 'net.USB_LDO3', pin2: 'net.USB_MAX_V' }} />
  <resistor name='USB-R2' resistance='9.53k' footprint='0603' connections={{ pin1: 'net.USB_MAX_V', pin2: 'net.GND' }} />
  <resistor name='USB-R3' resistance='10k' footprint='0603' connections={{ pin1: 'net.V3_3', pin2: 'net.USB_ATTACHED' }} />
  <capacitor name='USB-C1' pcbRotation={180} capacitance='22uF' maxVoltageRating={10} footprint='0805' connections={{ pin1: 'net.USB_LDO3', pin2: 'net.GND' }} />
  <capacitor name='USB-C2' pcbRotation={180} capacitance='10uF' maxVoltageRating={10} footprint='0805' connections={{ pin1: 'net.USB_LDO1', pin2: 'net.GND' }} />
  <capacitor name='USB-C3' pcbRotation={0} maxDecouplingTraceLength={3} capacitance='22uF' maxVoltageRating={10} footprint='0805' connections={{ pin1: 'net.V3_3', pin2: 'net.GND' }} />
  <capacitor name='USB-C4' capacitance='4.7uF' maxVoltageRating={16} footprint='0805' connections={{ pin1: 'net.USB_VBUS', pin2: 'net.GND' }} />
  <capacitor name='USB-C5' capacitance='22uF' maxVoltageRating={16} footprint='1210' connections={{ pin1: 'net.USB_POWER', pin2: 'net.GND' }} />
  <capacitor name='USB-C6' capacitance='22uF' maxVoltageRating={16} footprint='1210' connections={{ pin1: 'net.USB_POWER', pin2: 'net.GND' }} />
  <capacitor name='USB-C7' pcbRotation={90} capacitance='330pF' maxVoltageRating={16} footprint='0603' connections={{ pin1: 'net.USB_CC1', pin2: 'net.GND' }} />
  <capacitor name='USB-C8' capacitance='330pF' maxVoltageRating={16} footprint='0603' connections={{ pin1: 'net.USB_CC2', pin2: 'net.GND' }} />
  <SS34 name='USB-D1' connections={{ anode: 'net.GND', cathode: 'net.USB_VBUS' }} />
  <constraint pcb centerToCenter left='USB-C1' right='USB-U1' xDist={5.8} />
  <constraint pcb centerToCenter top='USB-C1' bottom='USB-U1' yDist={1.5} />
  <constraint pcb centerToCenter left='USB-C2' right='USB-U1' xDist={5.8} />
  <constraint pcb centerToCenter top='USB-U1' bottom='USB-C2' yDist={1.8} />
  <constraint pcb centerToCenter left='USB-C3' right='USB-U1' xDist={2.4} />
  <constraint pcb centerToCenter top='USB-C3' bottom='USB-U1' yDist={3.5} />
  <constraint pcb centerToCenter left='USB-U1' right='USB-C4' xDist={5.5} />
  <constraint pcb centerToCenter top='USB-C4' bottom='USB-U1' yDist={1.5} />
  <constraint pcb centerToCenter left='USB-U1' right='USB-C5' xDist={6} />
  <constraint pcb centerToCenter top='USB-U1' bottom='USB-C5' yDist={2.1} />
  <constraint pcb centerToCenter left='USB-U1' right='USB-C6' xDist={6} />
  <constraint pcb centerToCenter top='USB-U1' bottom='USB-C6' yDist={6.2} />
  <constraint pcb centerToCenter left='USB-U1' right='USB-C7' xDist={1.6} />
  <constraint pcb centerToCenter top='USB-C7' bottom='USB-U1' yDist={4.3} />
</>

const ClusterPower = () => <>
  <AP63203WU_7 name='POWER-U1' connections={{ VIN: 'net.VIN', EN: 'net.VIN', GND: 'net.GND', SW: 'net.POWER_SW', BST: 'net.POWER_BST', FB: 'net.V3_3' }} />
  <SS34 name='POWER-D1' pcbRotation={180} schRotation={90} connections={{ anode: 'net.BAT', cathode: 'net.VIN' }} />
  <SS34 name='POWER-D2' schRotation={90} connections={{ anode: 'net.USB_POWER', cathode: 'net.VIN' }} />
  <FNR5040S3R9NT name='POWER-L1' pcbRotation={90} connections={{ pin1: 'net.POWER_SW', pin2: 'net.V3_3' }} />
  <capacitor name='POWER-C1' pcbRotation={90} capacitance='10uF' maxVoltageRating={25} footprint='1210' connections={{ pin1: 'net.VIN', pin2: 'net.GND' }} />
  <capacitor name='POWER-C2' pcbRotation={90} maxDecouplingTraceLength={3} capacitance='100nF' maxVoltageRating={25} footprint='0603' connections={{ pin1: 'net.VIN', pin2: 'net.GND' }} />
  <capacitor name='POWER-C3' pcbRotation={90} capacitance='100nF' maxVoltageRating={16} footprint='0603' connections={{ pin1: 'net.POWER_BST', pin2: 'net.POWER_SW' }} />
  <capacitor name='POWER-C4' pcbRotation={180} capacitance='22uF' maxVoltageRating={10} footprint='0805' connections={{ pin1: 'net.V3_3', pin2: 'net.GND' }} />
  <capacitor name='POWER-C5' pcbRotation={180} capacitance='22uF' maxVoltageRating={10} footprint='0805' connections={{ pin1: 'net.V3_3', pin2: 'net.GND' }} />
  <constraint pcb centerToCenter left='POWER-U1' right='POWER-C1' xDist={6.4} />
  <constraint pcb centerToCenter top='POWER-U1' bottom='POWER-C1' yDist={0} />
  <constraint pcb centerToCenter left='POWER-U1' right='POWER-C2' xDist={3.2} />
  <constraint pcb centerToCenter left='POWER-U1' right='POWER-L1' xDist={0} />
  <constraint pcb centerToCenter top='POWER-U1' bottom='POWER-C2' yDist={0} />
  <constraint pcb centerToCenter top='POWER-L1' bottom='POWER-U1' yDist={5.5} />
  <constraint pcb centerToCenter left='POWER-C3' right='POWER-U1' xDist={3.8} />
  <constraint pcb centerToCenter top='POWER-C3' bottom='POWER-U1' yDist={1.2} />
  <constraint pcb centerToCenter left='POWER-C4' right='POWER-U1' xDist={4.5} />
  <constraint pcb centerToCenter top='POWER-C4' bottom='POWER-U1' yDist={8} />
  <constraint pcb centerToCenter left='POWER-C4' right='POWER-C5' xDist={0} />
  <constraint pcb centerToCenter top='POWER-C4' bottom='POWER-C5' yDist={3} />
  <constraint pcb centerToCenter left='POWER-D1' right='POWER-U1' xDist={3.8} />
  <constraint pcb centerToCenter top='POWER-U1' bottom='POWER-D1' yDist={5.5} />
  <constraint pcb centerToCenter left='POWER-U1' right='POWER-D2' xDist={3.6} />
  <constraint pcb centerToCenter top='POWER-U1' bottom='POWER-D2' yDist={5.5} />
</>

const ClusterIMU = () => <>
  <LSM6DSOTR name='IMU-U1' connections={{
    VDD: 'net.V3_3', VDDIO: 'net.V3_3', CS: 'net.V3_3', GND1: 'net.GND', GND2: 'net.GND', pin1: 'net.GND', SDX: 'net.GND', SCX: 'net.GND', SDA: 'net.SDA', SCL: 'net.SCL', INT1: 'net.IMU_INT',
  }} />
  <capacitor name='IMU-C1' capacitance='100nF' maxVoltageRating={16} footprint='0603' connections={{ pin1: 'net.V3_3', pin2: 'net.GND' }} />
  <capacitor name='IMU-C2' pcbRotation={90} capacitance='100nF' maxVoltageRating={16} footprint='0603' connections={{ pin1: 'net.V3_3', pin2: 'net.GND' }} />
  <constraint pcb centerToCenter left='IMU-C1' right='IMU-U1' xDist={0.5} />
  <constraint pcb centerToCenter top='IMU-U1' bottom='IMU-C1' yDist={2.7} />
  <constraint pcb centerToCenter left='IMU-U1' right='IMU-C2' xDist={3} />
  <constraint pcb centerToCenter top='IMU-U1' bottom='IMU-C2' yDist={1} />
</>

const ClusterMux = () => <>
  <TCA9548APWR name='MUX-U1' connections={{ VCC: 'net.V3_3', GND: 'net.GND', A0: 'net.GND', A1: 'net.GND', A2: 'net.GND', N_RESET: 'net.MUX_RESET', SDA: 'net.SDA', SCL: 'net.SCL', SD0: 'net.SDA0', SC0: 'net.SCL0', SD1: 'net.SDA1', SC1: 'net.SCL1', SD2: 'net.SDA2', SC2: 'net.SCL2', SD3: 'net.SDA3', SC3: 'net.SCL3' }} />
  <capacitor name='MUX-C1' capacitance='100nF' maxVoltageRating={16} footprint='0603' connections={{ pin1: 'net.V3_3', pin2: 'net.GND' }} />
  <resistor name='MUX-R1' resistance='10k' footprint='0603' connections={{ pin1: 'net.V3_3', pin2: 'net.MUX_RESET' }} />
  <resistor name='MUX-R2' resistance='4.7k' footprint='0603' connections={{ pin1: 'net.V3_3', pin2: 'net.SDA' }} />
  <resistor name='MUX-R3' resistance='4.7k' footprint='0603' connections={{ pin1: 'net.V3_3', pin2: 'net.SCL' }} />
  {[0, 1, 2, 3].map(i => <Fragment key={i}>
    <resistor name={`MUX-RD${i}`} resistance='4.7k' footprint='0603' connections={{ pin1: 'net.V3_3', pin2: `net.SDA${i}` }} />
    <resistor name={`MUX-RC${i}`} pcbX={i === 3 ? 3.260908789473685 : undefined} pcbY={i === 3 ? -9.005 : undefined} pcbRotation={i === 3 ? 90 : undefined} resistance='4.7k' footprint='0603' connections={{ pin1: 'net.V3_3', pin2: `net.SCL${i}` }} />
  </Fragment>)}
  <constraint pcb centerToCenter left='MUX-C1' right='MUX-U1' xDist={3.5} />
  <constraint pcb centerToCenter top='MUX-C1' bottom='MUX-U1' yDist={5.3} />
</>

export default () => <board width={50} height={60} layers={4} thickness={1.6} schPack pcbRelative minPadEdgeToPadEdgeClearance={0.09} pcbStyle={{ viaHoleDiameter: 0.3, viaPadDiameter: 0.6 }} minViaHoleDiameter={0.3} minViaPadDiameter={0.6}>
  <ClusterESP />
  <TPD2EUSB30DRTR name='USB-U2' pcbY={-21.5} pcbRotation={90} connections={{ pin1: 'net.USB_DP', pin2: 'net.USB_DM', pin3: 'net.GND' }} />
  <group pcbPack pcbPackGap={0.6} width={8} height={12} pcbX={15} pcbY={19}>
  <TS_1088_AR02016 name='ESP-SW1' connections={{ pin1: 'net.ESP_EN', pin2: 'net.GND' }} />
  <TS_1088_AR02016 name='ESP-SW2' connections={{ pin1: 'net.ESP_BOOT', pin2: 'net.GND' }} />
  </group>
  <net name='GND' isGroundNet />
  <net name='V3_3' isPowerNet />
  <net name='VIN' isPowerNet />
  <net name='BAT' isPowerNet />
  <net name='USB_VBUS' isPowerNet />
  <net name='USB_POWER' isPowerNet />
  <ESP32_S3_WROOM_1_N8 name='ESP-U1' pcbY={19} connections={{ pin2: 'net.V3_3', GND1: 'net.GND', GND2: 'net.GND', EP: 'net.GND', EN: 'net.ESP_EN', IO0: 'net.ESP_BOOT', IO8: 'net.SDA', IO9: 'net.SCL', IO4: 'net.IMU_INT', IO5: 'net.MUX_RESET', IO7: 'net.USB_ATTACHED', IO19: 'ESP-R3.pin2', IO20: 'ESP-R4.pin2' }} />
  <TYPE_C_31_M_12 name='USB-J1' pcbY={-26} connections={{ EH1: 'net.GND', EH2: 'net.GND', EH3: 'net.GND', EH4: 'net.GND', GND1: 'net.GND', GND2: 'net.GND', VBUS1: 'net.USB_VBUS', VBUS2: 'net.USB_VBUS', CC1: 'net.USB_CC1', CC2: 'net.USB_CC2', DP1: 'net.USB_DP', DP2: 'net.USB_DP', DN1: 'net.USB_DM', DN2: 'net.USB_DM' }} />
  <XT60PW_M name='POWER-J1' pcbX={-18} pcbY={-22} connections={{ pin1: 'net.GND', pin2: 'net.BAT' }} />
  <group pcbFlex pcbFlexDirection='column' pcbFlexGap={4} pcbX={22}>
    {[1, 2, 3, 4].map(i => <pinheader key={i} name={`MUX-J${i}`} pinCount={4} pitch={2.54} pcbRotation={90} connections={{ pin1: 'net.V3_3', pin2: 'net.GND', pin3: `net.SDA${i - 1}`, pin4: `net.SCL${i - 1}` }} />)}
  </group>
  <group pcbPack pcbX={-13} pcbY={26}>
    <capacitor name='ESP-C1' capacitance='10uF' maxVoltageRating={10} footprint='0805' connections={{ pin1: 'net.V3_3', pin2: 'net.GND' }} />
    <capacitor name='ESP-C2' capacitance='100nF' maxVoltageRating={16} footprint='0603' connections={{ pin1: 'net.V3_3', pin2: 'net.GND' }} />
  </group>
  <group pcbPack pcbX={-13} pcbY={13}>
    <resistor name='ESP-R3' resistance='22' footprint='0603' connections={{ pin1: 'net.USB_DM' }} />
    <resistor name='ESP-R4' resistance='22' footprint='0603' connections={{ pin1: 'net.USB_DP' }} />
  </group>
  <group pcbPack pcbX={-16} pcbY={0}>
    <ClusterPower />
  </group>
  <group pcbPack pcbX={0} pcbY={-12}>
    <ClusterUSB />
    <ClusterIMU />
    <ClusterMux />
  </group>
  <net name='USB_DP' nominalTraceWidth={0.25} />
  <net name='USB_DM' nominalTraceWidth={0.25} />
</board>
