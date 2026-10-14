import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["FB"],
  pin2: ["EN"],
  pin3: ["VIN"],
  pin4: ["GND"],
  pin5: ["SW"],
  pin6: ["BST"]
} as const

const pinAttributes = {
  pin3: {requiresPower: true},
  pin4: {requiresGround: true}
} as const

export const AP63300WU_7 = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      pinAttributes={pinAttributes}
      supplierPartNumbers={{
  "jlcpcb": [
    "C2158012"
  ]
}}
      manufacturerPartNumber="AP63300WU-7"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="1.200023mm" pcbY="-0.94996mm" width="0.7999984mm" height="0.532003mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="1.200023mm" pcbY="0mm" width="0.7999984mm" height="0.532003mm" shape="rect" />
<smtpad portHints={["pin3"]} pcbX="1.200023mm" pcbY="0.94996mm" width="0.7999984mm" height="0.532003mm" shape="rect" />
<smtpad portHints={["pin4"]} pcbX="-1.200023mm" pcbY="0.94996mm" width="0.7999984mm" height="0.532003mm" shape="rect" />
<smtpad portHints={["pin5"]} pcbX="-1.200023mm" pcbY="0mm" width="0.7999984mm" height="0.532003mm" shape="rect" />
<smtpad portHints={["pin6"]} pcbX="-1.200023mm" pcbY="-0.94996mm" width="0.7999984mm" height="0.532003mm" shape="rect" />
<silkscreenpath route={[{"x":0.8760714000001144,"y":1.5262098000000606},{"x":-0.8763253999999279,"y":1.5262098000000606}]} />
<silkscreenpath route={[{"x":0.8760714000001144,"y":-1.5262097999999469},{"x":-0.8763253999999279,"y":-1.5262097999999469}]} />
<silkscreencircle pcbX="1.287399mm" pcbY="-1.668526mm" radius="0.150114mm" />
<silkscreentext text="{NAME}" pcbX="0.101473mm" pcbY="2.524mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-1.850326999999993,"y":1.774000000000001},{"x":2.053273000000104,"y":1.774000000000001},{"x":2.053273000000104,"y":-2.0787999999998874},{"x":-1.850326999999993,"y":-2.0787999999998874},{"x":-1.850326999999993,"y":1.774000000000001}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C2158012.obj?uuid=222e8593009c495bb3d3af0c08fa5e6a",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C2158012.step?uuid=222e8593009c495bb3d3af0c08fa5e6a",
        pcbRotationOffset: 180,
        modelOriginPosition: { x: -0.0001269999999067295, y: -0.000012699999956566899, z: 0.050795 },
      }}
      {...props}
    />
  )
}