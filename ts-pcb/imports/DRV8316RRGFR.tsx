import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["NC1"],
  pin2: ["AGND1"],
  pin3: ["FB_BK"],
  pin4: ["GND_BK"],
  pin5: ["SW_BK"],
  pin6: ["CPL"],
  pin7: ["CPH"],
  pin8: ["CP"],
  pin9: ["VM1"],
  pin10: ["VM2"],
  pin11: ["VM3"],
  pin12: ["PGND1"],
  pin13: ["OUTA1"],
  pin14: ["OUTA2"],
  pin15: ["PGND2"],
  pin16: ["OUTB1"],
  pin17: ["OUTB2"],
  pin18: ["PGND3"],
  pin19: ["OUTC1"],
  pin20: ["OUTC2"],
  pin21: ["DRVOFF"],
  pin22: ["nFAULT"],
  pin23: ["nSLEEP"],
  pin24: ["NC2"],
  pin25: ["AVDD"],
  pin26: ["AGND2"],
  pin27: ["INHA"],
  pin28: ["INLA"],
  pin29: ["INHB"],
  pin30: ["INLB"],
  pin31: ["INHC"],
  pin32: ["INLC"],
  pin33: ["SDO"],
  pin34: ["SDI"],
  pin35: ["SCLK"],
  pin36: ["nSCS"],
  pin37: ["pin37"],
  pin38: ["SOC"],
  pin39: ["SOB"],
  pin40: ["SOA"],
  pin41: ["EP"]
} as const

const pinAttributes = {
  pin1: {doNotConnect: true},
  pin2: {requiresGround: true},
  pin12: {requiresGround: true},
  pin15: {requiresGround: true},
  pin18: {requiresGround: true},
  pin24: {doNotConnect: true},
  pin26: {requiresGround: true}
} as const

export const DRV8316RRGFR = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      pinAttributes={pinAttributes}
      supplierPartNumbers={{
  "jlcpcb": [
    "C5218861"
  ]
}}
      manufacturerPartNumber="DRV8316RRGFR"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-2.400046mm" pcbY="2.7499818mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="-2.400046mm" pcbY="2.2500844mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin3"]} pcbX="-2.400046mm" pcbY="1.7499584mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin4"]} pcbX="-2.400046mm" pcbY="1.250061mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin5"]} pcbX="-2.400046mm" pcbY="0.749935mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin6"]} pcbX="-2.400046mm" pcbY="0.250063mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin7"]} pcbX="-2.400046mm" pcbY="-0.2500884mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin8"]} pcbX="-2.400046mm" pcbY="-0.7499604mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin9"]} pcbX="-2.400046mm" pcbY="-1.2501118mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin10"]} pcbX="-2.400046mm" pcbY="-1.7499838mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin11"]} pcbX="-2.400046mm" pcbY="-2.2501352mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin12"]} pcbX="-2.400046mm" pcbY="-2.7500072mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin13"]} pcbX="-1.75006mm" pcbY="-3.400044mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin14"]} pcbX="-1.249934mm" pcbY="-3.400044mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin15"]} pcbX="-0.750062mm" pcbY="-3.400044mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin16"]} pcbX="-0.249936mm" pcbY="-3.400044mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin17"]} pcbX="0.249936mm" pcbY="-3.400044mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin18"]} pcbX="0.750062mm" pcbY="-3.400044mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin19"]} pcbX="1.249934mm" pcbY="-3.400044mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin20"]} pcbX="1.75006mm" pcbY="-3.400044mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin21"]} pcbX="2.400046mm" pcbY="-2.7500072mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin22"]} pcbX="2.400046mm" pcbY="-2.2501352mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin23"]} pcbX="2.400046mm" pcbY="-1.7499838mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin24"]} pcbX="2.400046mm" pcbY="-1.2501118mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin25"]} pcbX="2.400046mm" pcbY="-0.7499604mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin26"]} pcbX="2.400046mm" pcbY="-0.2500884mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin27"]} pcbX="2.400046mm" pcbY="0.250063mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin28"]} pcbX="2.400046mm" pcbY="0.749935mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin29"]} pcbX="2.400046mm" pcbY="1.250061mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin30"]} pcbX="2.400046mm" pcbY="1.7499584mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin31"]} pcbX="2.400046mm" pcbY="2.2500844mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin32"]} pcbX="2.400046mm" pcbY="2.7500072mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin33"]} pcbX="1.75006mm" pcbY="3.400044mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin34"]} pcbX="1.249934mm" pcbY="3.400044mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin35"]} pcbX="0.750062mm" pcbY="3.400044mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin36"]} pcbX="0.249936mm" pcbY="3.400044mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin37"]} pcbX="-0.249936mm" pcbY="3.400044mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin38"]} pcbX="-0.750062mm" pcbY="3.400044mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin39"]} pcbX="-1.249934mm" pcbY="3.400044mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin40"]} pcbX="-1.75006mm" pcbY="3.400044mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin41"]} pcbX="0mm" pcbY="0mm" width="3.6999926mm" height="5.6999886mm" shape="rect" />
<silkscreenpath route={[{"x":-2.1062187999998514,"y":3.499916800000051},{"x":-2.4999950000000126,"y":3.499916800000051}]} />
<silkscreenpath route={[{"x":2.4999442000000727,"y":3.499916800000051},{"x":2.1061171999999715,"y":3.499916800000051}]} />
<silkscreenpath route={[{"x":2.4999442000000727,"y":2.9810710000001563},{"x":2.4999442000000727,"y":3.499916800000051}]} />
<silkscreenpath route={[{"x":2.1061171999999715,"y":-3.500018399999817},{"x":2.4999442000000727,"y":-3.500018399999817},{"x":2.4999442000000727,"y":-3.2312101999998504}]} />
<silkscreenpath route={[{"x":-2.4999950000000126,"y":-3.2312101999998504},{"x":-2.4999950000000126,"y":-3.500018399999817},{"x":-2.1062187999998514,"y":-3.500018399999817}]} />
<silkscreenpath route={[{"x":-2.4999950000000126,"y":3.499916800000051},{"x":-2.4999950000000126,"y":2.9810710000001563}]} />
<silkscreencircle pcbX="-3.08991mm" pcbY="2.639822mm" radius="0.116586mm" />
<silkscreentext text="{NAME}" pcbX="-0.25908mm" pcbY="4.700526mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-3.468180000000075,"y":3.9505260000000817},{"x":2.950019999999995,"y":3.9505260000000817},{"x":2.950019999999995,"y":-3.9408739999997806},{"x":-3.468180000000075,"y":-3.9408739999997806},{"x":-3.468180000000075,"y":3.9505260000000817}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C5218861.obj?uuid=f5c88ed9b9bd431ea66868c32d137cdb",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C5218861.step?uuid=f5c88ed9b9bd431ea66868c32d137cdb",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0, y: 0, z: -0.02 },
      }}
      {...props}
    />
  )
}