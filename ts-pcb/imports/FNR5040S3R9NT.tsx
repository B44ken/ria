import type { InductorProps } from "@tscircuit/props"

export const FNR5040S3R9NT = (props: Omit<InductorProps, "inductance">) => {
  return (
    <inductor
      inductance="3.9uH"
      supplierPartNumbers={{
  "jlcpcb": [
    "C167962"
  ]
}}
      manufacturerPartNumber="FNR5040S3R9NT"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-2.149983mm" pcbY="0mm" width="1.7999964mm" height="4.1999916mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="2.149983mm" pcbY="0mm" width="1.7999964mm" height="4.1999916mm" shape="rect" />
<silkscreenpath route={[{"x":-2.499918799999932,"y":2.4999950000000126},{"x":2.5000711999998657,"y":2.4999950000000126}]} />
<silkscreenpath route={[{"x":-2.499918799999932,"y":-2.4999950000001263},{"x":2.5000711999998657,"y":-2.4999950000001263}]} />
<silkscreenpath route={[{"x":-2.499918799999932,"y":2.4999950000000126},{"x":-2.499918799999932,"y":2.33113579999997}]} />
<silkscreenpath route={[{"x":-2.499918799999932,"y":-2.33113579999997},{"x":-2.499918799999932,"y":-2.4999950000001263}]} />
<silkscreenpath route={[{"x":2.5000711999998657,"y":-2.4999950000001263},{"x":2.5000711999998657,"y":-2.33113579999997}]} />
<silkscreenpath route={[{"x":2.5000711999998657,"y":2.33113579999997},{"x":2.5000711999998657,"y":2.4999950000000126}]} />
<silkscreentext text="{NAME}" pcbX="-0.008509mm" pcbY="3.4892mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-3.3065090000000055,"y":2.7392000000000962},{"x":3.289490999999998,"y":2.7392000000000962},{"x":3.289490999999998,"y":-2.7899999999999636},{"x":-3.3065090000000055,"y":-2.7899999999999636},{"x":-3.3065090000000055,"y":2.7392000000000962}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C167962.obj?uuid=16215264b43040e7af8a95ab774880e3",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C167962.step?uuid=16215264b43040e7af8a95ab774880e3",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0, y: 0.00005000000011379235, z: 0 },
      }}
      {...props}
    />
  )
}