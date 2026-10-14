import { Fragment } from 'react'

export const motorPwmPins = [[13, 14, 15], [16, 17, 18], [21, 35, 36], [37, 38, 39]]
export const motorCsPins = ['IO1', 'IO2', 'TXD0', 'IO48']

// ti drv8316 rev b, sections 8.3.2.2 and 8.3.4: 3-pwm, local buck termination.
export const MotorDriver = ({ motor, pcbX, pcbY }: { motor: number; pcbX: number; pcbY: number }) => {
  const n = (suffix: string) => `MOTOR${motor}_${suffix}`
  const net = (suffix: string) => `net.${n(suffix)}`
  const name = (suffix: string) => `MOTOR${motor}-${suffix}`
  return <group name={name('DRIVER')} schMatchAdapt pcbRelative pcbX={pcbX} pcbY={pcbY}>
    <chip name={name('U1')} manufacturerPartNumber='DRV8316RRGFR' supplierPartNumbers={{ jlcpcb: ['C5218861'] }} footprint='jlcpcb:C5218861' layer='bottom' schHeight={4.2} noConnect={['NC1', 'NC2', 'SOA', 'SOB', 'SOC']} pinLabels={{
      pin1: 'NC1', pin2: 'AGND1', pin3: 'FB_BK', pin4: 'GND_BK', pin5: 'SW_BK', pin6: 'CPL', pin7: 'CPH', pin8: 'CP', pin9: 'VM1', pin10: 'VM2', pin11: 'VM3', pin12: 'PGND1',
      pin13: 'OUTA1', pin14: 'OUTA2', pin15: 'PGND2', pin16: 'OUTB1', pin17: 'OUTB2', pin18: 'PGND3', pin19: 'OUTC1', pin20: 'OUTC2', pin21: 'DRVOFF', pin22: 'nFAULT', pin23: 'nSLEEP', pin24: 'NC2',
      pin25: 'AVDD', pin26: 'AGND2', pin27: 'INHA', pin28: 'INLA', pin29: 'INHB', pin30: 'INLB', pin31: 'INHC', pin32: 'INLC', pin33: 'SDO', pin34: 'SDI', pin35: 'SCLK', pin36: 'nSCS', pin37: 'VREF', pin38: 'SOC', pin39: 'SOB', pin40: 'SOA', pin41: 'EP',
    }} pinAttributes={{ VM1: { requiresPower: true }, VM2: { requiresPower: true }, VM3: { requiresPower: true }, AGND1: { requiresGround: true }, AGND2: { requiresGround: true }, EP: { requiresGround: true }, NC1: { doNotConnect: true }, NC2: { doNotConnect: true } }} connections={{
      AGND1: 'net.GND', AGND2: 'net.GND', GND_BK: 'net.GND', PGND1: 'net.GND', PGND2: 'net.GND', PGND3: 'net.GND', EP: 'net.GND',
      VM1: 'net.BAT', VM2: 'net.BAT', VM3: 'net.BAT',
      OUTA1: net('A'), OUTA2: net('A'), OUTB1: net('B'), OUTB2: net('B'), OUTC1: net('C'), OUTC2: net('C'),
      INHA: net('PWM_A'), INHB: net('PWM_B'), INHC: net('PWM_C'), INLA: 'net.V3_3', INLB: 'net.V3_3', INLC: 'net.V3_3',
      SCLK: 'net.MOTOR_SCLK', SDI: 'net.MOTOR_MOSI', SDO: 'net.MOTOR_MISO', nSCS: net('CS'), nSLEEP: 'net.MOTOR_ENABLE', nFAULT: 'net.MOTOR_FAULT', DRVOFF: 'net.GND',
      CPH: net('CPH'), CPL: net('CPL'), CP: net('CP'), AVDD: net('AVDD'), VREF: net('AVDD'), SW_BK: net('BUCK_SW'), FB_BK: net('BUCK'),
    }} />
    <capacitor name={name('C1')} layer='bottom' pcbX={-4.4} pcbY={0} pcbRotation={270} capacitance='47nF' maxVoltageRating={50} footprint='0603' connections={{ pin1: net('CPH'), pin2: net('CPL') }} />
    <capacitor name={name('C2')} layer='bottom' pcbX={-4.4} pcbY={-3} pcbRotation={90} capacitance='1uF' maxVoltageRating={16} footprint='0603' connections={{ pin1: net('CP'), pin2: 'net.BAT' }} />
    <capacitor name={name('C3')} layer='bottom' pcbX={-5} pcbY={-5.5} capacitance='100nF' maxVoltageRating={50} footprint='0603' connections={{ pin1: 'net.BAT', pin2: 'net.GND' }} />
    <capacitor name={name('C4')} layer='bottom' pcbX={-6.5} pcbY={-1.9} pcbRotation={90} capacitance='100nF' maxVoltageRating={50} footprint='0603' connections={{ pin1: 'net.BAT', pin2: 'net.GND' }} />
    <capacitor name={name('C5')} layer='bottom' pcbX={-6.3} pcbY={6.3} capacitance='10uF' maxVoltageRating={50} footprint='1210' connections={{ pin1: 'net.BAT', pin2: 'net.GND' }} />
    <capacitor name={name('C6')} layer='bottom' pcbX={5} pcbY={-0.5} capacitance='1uF' maxVoltageRating={16} footprint='0603' connections={{ pin1: net('AVDD'), pin2: 'net.GND' }} />
    <capacitor name={name('C7')} layer='bottom' pcbX={0} pcbY={5.2} capacitance='100nF' maxVoltageRating={16} footprint='0603' connections={{ pin1: net('AVDD'), pin2: 'net.GND' }} />
    <resistor name={name('R1')} layer='bottom' pcbX={-5} pcbY={3.1} pcbRotation={90} resistance='22' footprint='0603' connections={{ pin1: net('BUCK_SW'), pin2: net('BUCK') }} />
    <capacitor name={name('C8')} layer='bottom' pcbX={-7.2} pcbY={1.5} pcbRotation={90} schX={-1.5} schY={-10} schRotation={270} capacitance='1uF' maxVoltageRating={16} footprint='0603' connections={{ pin1: net('BUCK'), pin2: 'net.GND' }} />
    <resistor name={name('R2')} layer='bottom' pcbX={5} pcbY={3.2} schX={1.5} schY={-10} schRotation={270} resistance='10k' footprint='0603' connections={{ pin1: 'net.V3_3', pin2: net('CS') }} />
    <resistor name={name('R3')} layer='bottom' pcbX={5} pcbY={-3.2} resistance='5.1k' footprint='0603' connections={{ pin1: net('AVDD'), pin2: 'net.MOTOR_FAULT' }} />
    {[-0.9, 0.9].flatMap(x => [-1.5, 0, 1.5].map(y => <Fragment key={`${x},${y}`}><via name={name(`V${x},${y}`)} pcbX={x} pcbY={y} holeDiameter={0.3} outerDiameter={0.6} fromLayer='top' toLayer='bottom' connectsTo='net.GND' /></Fragment>))}
    {['A', 'B', 'C'].map(phase => <Fragment key={phase}><net name={n(phase)} nominalTraceWidth={1} /></Fragment>)}
  </group>
}

// amass gc3510-f: 3.5 mm socket, 4.2 mm barrel, 4.7 mm shoulder (v1.2 drawing).
export const MotorBullets = ({ motor, pcbX }: { motor: number; pcbX: number }) => <group schMatchAdapt pcbRelative pcbX={pcbX} pcbY={-24}>
  {['A', 'B', 'C'].map((phase, i) => <connector key={phase} name={`MOTOR-J${motor}${phase}`} manufacturerPartNumber='GC3510-F' supplierPartNumbers={{ jlcpcb: ['C964714'] }} pinLabels={{ pin1: phase }} connections={{ pin1: `net.MOTOR${motor}_${phase}` }} footprint={<footprint insertionDirection='from_above'>
    <platedhole portHints={['pin1']} shape='circle' holeDiameter={4.4} outerDiameter={6.4} />
    <silkscreencircle radius={3.4} strokeWidth={0.15} />
    <silkscreentext text={phase} pcbY={-4.3} fontSize={1.2} />
  </footprint>} pcbX={i * 7.2} />)}
</group>
