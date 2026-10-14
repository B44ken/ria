import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["D_POS"],
  pin2: ["D_NEG"],
  pin3: ["GND"]
} as const

const pinAttributes = {
  pin3: {requiresGround: true}
} as const

export const TPD2EUSB30DRTR = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      pinAttributes={pinAttributes}
      supplierPartNumbers={{
  "jlcpcb": [
    "C97502"
  ]
}}
      manufacturerPartNumber="TPD2EUSB30DRTR"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="0.499999mm" pcbY="-0.350012mm" width="0.2999994mm" height="0.1999996mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="0.499999mm" pcbY="0.350012mm" width="0.2999994mm" height="0.1999996mm" shape="rect" />
<smtpad portHints={["pin3"]} pcbX="-0.499999mm" pcbY="0mm" width="0.2999994mm" height="0.1999996mm" shape="rect" />
<silkscreenpath route={[{"x":0.3998467999999775,"y":0.018872200000146222},{"x":0.3998467999999775,"y":-0.018846799999892028}]} />
<silkscreenpath route={[{"x":-0.40010080000013204,"y":0.4999990000000025},{"x":-0.40010080000013204,"y":0.3311398000000736}]} />
<silkscreenpath route={[{"x":-0.40010080000013204,"y":-0.3311397999999599},{"x":-0.40010080000013204,"y":-0.49999899999988884}]} />
<silkscreenpath route={[{"x":-0.40010080000013204,"y":0.4999990000000025},{"x":0.12428219999992507,"y":0.4999990000000025}]} />
<silkscreenpath route={[{"x":-0.40010080000013204,"y":-0.49999899999988884},{"x":0.12428219999992507,"y":-0.49999899999988884}]} />
<silkscreentext text="{NAME}" pcbX="0.101473mm" pcbY="1.508mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-0.9105270000001155,"y":0.7580000000000382},{"x":1.1134729999998854,"y":0.7580000000000382},{"x":1.1134729999998854,"y":-0.783399999999915},{"x":-0.9105270000001155,"y":-0.783399999999915},{"x":-0.9105270000001155,"y":0.7580000000000382}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C97502.obj?uuid=7e46175b4c3341ab8d7b74e33c98b337",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C97502.step?uuid=7e46175b4c3341ab8d7b74e33c98b337",
        pcbRotationOffset: 90,
        modelOriginPosition: { x: 0.000012700000070253736, y: 0, z: 0 },
      }}
      {...props}
    />
  )
}