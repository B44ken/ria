import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["SDO"],
  pin2: ["MSDA"],
  pin3: ["MCLK"],
  pin4: ["INT1"],
  pin5: ["VDDIO"],
  pin6: ["GND"],
  pin7: ["RESV1"],
  pin8: ["VDD"],
  pin9: ["INT2"],
  pin10: ["CSB2"],
  pin11: ["RESV2"],
  pin12: ["SENB"],
  pin13: ["SCK"],
  pin14: ["SDA"]
} as const

const pinAttributes = {
  pin5: {requiresPower: true},
  pin6: {requiresGround: true},
  pin8: {requiresPower: true}
} as const

export const ICM_42688_P_TOKMAS_ = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      pinAttributes={pinAttributes}
      supplierPartNumbers={{
  "jlcpcb": [
    "C54308212"
  ]
}}
      manufacturerPartNumber="ICM-42688-P(TOKMAS)"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-0.750062mm" pcbY="-1.392428mm" width="0.2800096mm" height="0.7850124mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="-0.249936mm" pcbY="-1.392428mm" width="0.2800096mm" height="0.7850124mm" shape="rect" />
<smtpad portHints={["pin3"]} pcbX="0.249936mm" pcbY="-1.392428mm" width="0.2800096mm" height="0.7850124mm" shape="rect" />
<smtpad portHints={["pin4"]} pcbX="0.750062mm" pcbY="-1.392428mm" width="0.2800096mm" height="0.7850124mm" shape="rect" />
<smtpad portHints={["pin5"]} pcbX="1.142492mm" pcbY="-0.500126mm" width="0.7850124mm" height="0.2800096mm" shape="rect" />
<smtpad portHints={["pin6"]} pcbX="1.142492mm" pcbY="0mm" width="0.7850124mm" height="0.2800096mm" shape="rect" />
<smtpad portHints={["pin7"]} pcbX="1.142492mm" pcbY="0.499872mm" width="0.7850124mm" height="0.2800096mm" shape="rect" />
<smtpad portHints={["pin8"]} pcbX="0.750062mm" pcbY="1.392428mm" width="0.2800096mm" height="0.7850124mm" shape="rect" />
<smtpad portHints={["pin9"]} pcbX="0.249936mm" pcbY="1.392428mm" width="0.2800096mm" height="0.7850124mm" shape="rect" />
<smtpad portHints={["pin10"]} pcbX="-0.249936mm" pcbY="1.392428mm" width="0.2800096mm" height="0.7850124mm" shape="rect" />
<smtpad portHints={["pin11"]} pcbX="-0.750062mm" pcbY="1.392428mm" width="0.2800096mm" height="0.7850124mm" shape="rect" />
<smtpad portHints={["pin12"]} pcbX="-1.142492mm" pcbY="0.499872mm" width="0.7850124mm" height="0.2800096mm" shape="rect" />
<smtpad portHints={["pin13"]} pcbX="-1.142492mm" pcbY="0mm" width="0.7850124mm" height="0.2800096mm" shape="rect" />
<smtpad portHints={["pin14"]} pcbX="-1.142492mm" pcbY="-0.500126mm" width="0.7850124mm" height="0.2800096mm" shape="rect" />
<silkscreenpath route={[{"x":-1.326210200000105,"y":0.830503799999974},{"x":-1.326210200000105,"y":1.5761970000000929},{"x":-1.0804906000000756,"y":1.5761970000000929}]} />
<silkscreenpath route={[{"x":1.3262101999999913,"y":0.830503799999974},{"x":1.3262101999999913,"y":1.5761970000000929},{"x":1.0804905999999619,"y":1.5761970000000929}]} />
<silkscreenpath route={[{"x":-1.326210200000105,"y":-0.8305037999998603},{"x":-1.326210200000105,"y":-1.5761969999999792},{"x":-1.0804906000000756,"y":-1.5761969999999792}]} />
<silkscreenpath route={[{"x":1.3262101999999913,"y":-0.8305037999998603},{"x":1.3262101999999913,"y":-1.5761969999999792},{"x":1.0804905999999619,"y":-1.5761969999999792}]} />
<silkscreencircle pcbX="-0.750062mm" pcbY="-2.085086mm" radius="0.07493mm" />
<silkscreentext text="{NAME}" pcbX="0.0127mm" pcbY="2.778mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-1.7740000000001146,"y":2.02800000000002},{"x":1.7993999999998778,"y":2.02800000000002},{"x":1.7993999999998778,"y":-2.408999999999878},{"x":-1.7740000000001146,"y":-2.408999999999878},{"x":-1.7740000000001146,"y":2.02800000000002}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C54308212.obj?uuid=f43373e142124ec98babb70d58d97864",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C54308212.step?uuid=f43373e142124ec98babb70d58d97864",
        pcbRotationOffset: 90,
        modelOriginPosition: { x: 0, y: -0.000012700000070253736, z: 0 },
      }}
      {...props}
    />
  )
}
