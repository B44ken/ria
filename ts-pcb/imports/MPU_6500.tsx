import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["NC9"],
  pin2: ["NC1"],
  pin3: ["NC2"],
  pin4: ["NC3"],
  pin5: ["NC4"],
  pin6: ["NC10"],
  pin7: ["AUX_CL"],
  pin8: ["VDDIO"],
  pin9: ["AD0", "SDO"],
  pin10: ["REGOUT"],
  pin11: ["FSYNC"],
  pin12: ["INT"],
  pin13: ["VDD"],
  pin14: ["NC5"],
  pin15: ["NC6"],
  pin16: ["NC7"],
  pin17: ["NC8"],
  pin18: ["GND"],
  pin19: ["RESV2"],
  pin20: ["RESV1"],
  pin21: ["AUX_DA"],
  pin22: ["nCS"],
  pin23: ["SCL", "SCLK"],
  pin24: ["SDA", "SDI"]
} as const

const pinAttributes = {
  pin1: {doNotConnect: true},
  pin2: {doNotConnect: true},
  pin3: {doNotConnect: true},
  pin4: {doNotConnect: true},
  pin5: {doNotConnect: true},
  pin6: {doNotConnect: true},
  pin8: {requiresPower: true},
  pin13: {requiresPower: true},
  pin14: {doNotConnect: true},
  pin15: {doNotConnect: true},
  pin16: {doNotConnect: true},
  pin17: {doNotConnect: true},
  pin18: {requiresGround: true},
  pin19: {doNotConnect: true},
  pin20: {requiresGround: true}
} as const

export const MPU_6500 = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      pinAttributes={pinAttributes}
      supplierPartNumbers={{
  "jlcpcb": [
    "C50278"
  ]
}}
      manufacturerPartNumber="MPU-6500"
      footprint={<footprint>
        <smtpad portHints={["pin2"]} pcbX="-0.5999734mm" pcbY="-1.4274165mm" width="0.1999996mm" height="0.5050028mm" shape="rect" />
<smtpad portHints={["pin3"]} pcbX="-0.1999234mm" pcbY="-1.4274165mm" width="0.1999996mm" height="0.5050028mm" shape="rect" />
<smtpad portHints={["pin4"]} pcbX="0.1998726mm" pcbY="-1.4274165mm" width="0.1999996mm" height="0.5050028mm" shape="rect" />
<smtpad portHints={["pin5"]} pcbX="0.5999226mm" pcbY="-1.4274165mm" width="0.1999996mm" height="0.5050028mm" shape="rect" />
<smtpad portHints={["pin8"]} pcbX="1.4274546mm" pcbY="-0.5998845mm" width="0.5050028mm" height="0.1999996mm" shape="rect" />
<smtpad portHints={["pin9"]} pcbX="1.4274546mm" pcbY="-0.1998345mm" width="0.5050028mm" height="0.1999996mm" shape="rect" />
<smtpad portHints={["pin10"]} pcbX="1.4274546mm" pcbY="0.1999615mm" width="0.5050028mm" height="0.1999996mm" shape="rect" />
<smtpad portHints={["pin11"]} pcbX="1.4274546mm" pcbY="0.6000115mm" width="0.5050028mm" height="0.1999996mm" shape="rect" />
<smtpad portHints={["pin14"]} pcbX="0.5999226mm" pcbY="1.4275435mm" width="0.1999996mm" height="0.5050028mm" shape="rect" />
<smtpad portHints={["pin15"]} pcbX="0.1998726mm" pcbY="1.4275435mm" width="0.1999996mm" height="0.5050028mm" shape="rect" />
<smtpad portHints={["pin16"]} pcbX="-0.1999234mm" pcbY="1.4275435mm" width="0.1999996mm" height="0.5050028mm" shape="rect" />
<smtpad portHints={["pin17"]} pcbX="-0.5999734mm" pcbY="1.4275435mm" width="0.1999996mm" height="0.5050028mm" shape="rect" />
<smtpad portHints={["pin18"]} points={[{x: "-1.1000232mm", y: "1.6800449mm"}, {x: "-0.9000236mm", y: "1.6800449mm"}, {x: "-0.9000236mm", y: "1.1750421mm"}, {x: "-1.0000234mm", y: "1.1745341mm"}, {x: "-1.1000232mm", y: "1.2745339mm"}]} shape="polygon" />
<smtpad portHints={["pin20"]} pcbX="-1.4275054mm" pcbY="0.6000115mm" width="0.5050028mm" height="0.1999996mm" shape="rect" />
<smtpad portHints={["pin21"]} pcbX="-1.4275054mm" pcbY="0.1999615mm" width="0.5050028mm" height="0.1999996mm" shape="rect" />
<smtpad portHints={["pin22"]} pcbX="-1.4275054mm" pcbY="-0.1998345mm" width="0.5050028mm" height="0.1999996mm" shape="rect" />
<smtpad portHints={["pin23"]} pcbX="-1.4275054mm" pcbY="-0.5998845mm" width="0.5050028mm" height="0.1999996mm" shape="rect" />
{/* TDK AN-IVS-0002A-00: no solder or active traces under the exposed die pad. */}
<keepout shape="rect" pcbX={0} pcbY={0} width={2.3} height={2.3} layer="top" />
<keepout shape="rect" pcbX={0} pcbY={0} width={3.1} height={3.1} layers={["inner1", "inner2", "bottom"]} />
<smtpad portHints={["pin24"]} points={[{x: "-1.6800068mm", y: "-1.0999343mm"}, {x: "-1.2744958mm", y: "-1.0999343mm"}, {x: "-1.174496mm", y: "-1.0000107mm"}, {x: "-1.175004mm", y: "-0.9000109mm"}, {x: "-1.6800068mm", y: "-0.9000109mm"}]} shape="polygon" />
<smtpad portHints={["pin7"]} points={[{x: "1.6800068mm", y: "-1.1000105mm"}, {x: "1.2744958mm", y: "-1.1000105mm"}, {x: "1.1745214mm", y: "-1.0000107mm"}, {x: "1.175004mm", y: "-0.9000363mm"}, {x: "1.6800068mm", y: "-0.9000363mm"}]} shape="polygon" />
<smtpad portHints={["pin12"]} points={[{x: "1.6799306mm", y: "1.0999343mm"}, {x: "1.2744196mm", y: "1.0999343mm"}, {x: "1.1743944mm", y: "0.9999599mm"}, {x: "1.1749278mm", y: "0.9000109mm"}, {x: "1.6799306mm", y: "0.9000109mm"}]} shape="polygon" />
<smtpad portHints={["pin13"]} points={[{x: "1.1000232mm", y: "1.6799941mm"}, {x: "0.9000236mm", y: "1.6799941mm"}, {x: "0.9000236mm", y: "1.1749659mm"}, {x: "1.0000234mm", y: "1.1744325mm"}, {x: "1.1000232mm", y: "1.2744831mm"}]} shape="polygon" />
<smtpad portHints={["pin1"]} points={[{x: "-1.0998708mm", y: "-1.6800449mm"}, {x: "-0.8998966mm", y: "-1.6800449mm"}, {x: "-0.8998966mm", y: "-1.1750167mm"}, {x: "-0.999871mm", y: "-1.1744325mm"}, {x: "-1.0998708mm", y: "-1.2745339mm"}]} shape="polygon" />
<smtpad portHints={["pin6"]} points={[{x: "1.1000232mm", y: "-1.6799433mm"}, {x: "0.9000236mm", y: "-1.6799433mm"}, {x: "0.9000236mm", y: "-1.1749659mm"}, {x: "1.0000234mm", y: "-1.1744579mm"}, {x: "1.1000232mm", y: "-1.2744577mm"}]} shape="polygon" />
<smtpad portHints={["pin19"]} points={[{x: "-1.6800068mm", y: "1.1000613mm"}, {x: "-1.2744958mm", y: "1.1000613mm"}, {x: "-1.174496mm", y: "1.0000615mm"}, {x: "-1.175004mm", y: "0.9000617mm"}, {x: "-1.6800068mm", y: "0.9000617mm"}]} shape="polygon" />
<silkscreenpath route={[{"x":-1.576222400000006,"y":1.3025755000001027},{"x":-1.576222400000006,"y":1.5762605000002168},{"x":-1.3025374000000056,"y":1.5762605000002168}]} />
<silkscreenpath route={[{"x":1.5761715999999524,"y":1.3025755000001027},{"x":1.5761715999999524,"y":1.5762605000002168},{"x":1.3024866000000657,"y":1.5762605000002168}]} />
<silkscreenpath route={[{"x":-1.576222400000006,"y":-1.3024484999999686},{"x":-1.576222400000006,"y":-1.5761334999998553},{"x":-1.3025374000000056,"y":-1.5761334999998553}]} />
<silkscreenpath route={[{"x":1.5761715999999524,"y":-1.3024484999999686},{"x":1.5761715999999524,"y":-1.5761334999998553},{"x":1.3024866000000657,"y":-1.5761334999998553}]} />
<silkscreencircle pcbX="-1.0000234mm" pcbY="-1.9798665mm" radius="0.07493mm" />
<silkscreentext text="{NAME}" pcbX="-0.0000254mm" pcbY="2.6764635mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-1.9264253999998573,"y":1.9264635000001817},{"x":1.9263746000001447,"y":1.9264635000001817},{"x":1.9263746000001447,"y":-2.307336499999792},{"x":-1.9264253999998573,"y":-2.307336499999792},{"x":-1.9264253999998573,"y":1.9264635000001817}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C50278.obj?uuid=ee2e77f6ae6443fd8761dd68811b5307",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C50278.step?uuid=ee2e77f6ae6443fd8761dd68811b5307",
        pcbRotationOffset: 90,
        modelOriginPosition: { x: -0.000063500000123895, y: -0.000025399999913133797, z: 0 },
      }}
      {...props}
    />
  )
}