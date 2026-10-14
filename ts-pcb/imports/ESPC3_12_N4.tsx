import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["IO0"],
  pin2: ["IO1"],
  pin3: ["EN"],
  pin4: ["IO2"],
  pin5: ["IO3"],
  pin6: ["IO4"],
  pin7: ["IO5"],
  pin8: ["VCC"],
  pin9: ["NC1"],
  pin10: ["NC2"],
  pin11: ["NC3"],
  pin12: ["IO6"],
  pin13: ["IO7"],
  pin14: ["NC4"],
  pin15: ["GND"],
  pin16: ["IO8"],
  pin17: ["IO10"],
  pin18: ["IO9"],
  pin19: ["IO18"],
  pin20: ["IO19"],
  pin21: ["RX0"],
  pin22: ["TX0"]
} as const

const pinAttributes = {
  pin8: {requiresPower: true},
  pin9: {doNotConnect: true},
  pin10: {doNotConnect: true},
  pin11: {doNotConnect: true},
  pin14: {doNotConnect: true},
  pin15: {requiresGround: true}
} as const

export const ESPC3_12_N4 = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      pinAttributes={pinAttributes}
      supplierPartNumbers={{
  "jlcpcb": [
    "C19949072"
  ]
}}
      manufacturerPartNumber="ESPC3-12-N4"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-7.750048mm" pcbY="7.87504775mm" width="1.499997mm" height="0.999998mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="-7.750048mm" pcbY="5.87505175mm" width="1.499997mm" height="0.999998mm" shape="rect" />
<smtpad portHints={["pin3"]} pcbX="-7.750048mm" pcbY="3.87505575mm" width="1.499997mm" height="0.999998mm" shape="rect" />
<smtpad portHints={["pin4"]} pcbX="-7.750048mm" pcbY="1.87505975mm" width="1.499997mm" height="0.999998mm" shape="rect" />
<smtpad portHints={["pin5"]} pcbX="-7.750048mm" pcbY="-0.12493625mm" width="1.499997mm" height="0.999998mm" shape="rect" />
<smtpad portHints={["pin6"]} pcbX="-7.750048mm" pcbY="-2.12493225mm" width="1.499997mm" height="0.999998mm" shape="rect" />
<smtpad portHints={["pin7"]} pcbX="-7.750048mm" pcbY="-4.12492825mm" width="1.499997mm" height="0.999998mm" shape="rect" />
<smtpad portHints={["pin8"]} pcbX="-7.750048mm" pcbY="-6.12492425mm" width="1.499997mm" height="0.999998mm" shape="rect" />
<smtpad portHints={["pin9"]} pcbX="-4.99999mm" pcbY="-7.62504825mm" width="0.999998mm" height="1.499997mm" shape="rect" />
<smtpad portHints={["pin10"]} pcbX="-2.999994mm" pcbY="-7.62504825mm" width="0.999998mm" height="1.499997mm" shape="rect" />
<smtpad portHints={["pin11"]} pcbX="-0.999998mm" pcbY="-7.62504825mm" width="0.999998mm" height="1.499997mm" shape="rect" />
<smtpad portHints={["pin12"]} pcbX="0.999998mm" pcbY="-7.62504825mm" width="0.999998mm" height="1.499997mm" shape="rect" />
<smtpad portHints={["pin13"]} pcbX="2.999994mm" pcbY="-7.62504825mm" width="0.999998mm" height="1.499997mm" shape="rect" />
<smtpad portHints={["pin14"]} pcbX="4.99999mm" pcbY="-7.62504825mm" width="0.999998mm" height="1.499997mm" shape="rect" />
<smtpad portHints={["pin15"]} pcbX="7.750048mm" pcbY="-6.12492425mm" width="1.499997mm" height="0.999998mm" shape="rect" />
<smtpad portHints={["pin16"]} pcbX="7.750048mm" pcbY="-4.12492825mm" width="1.499997mm" height="0.999998mm" shape="rect" />
<smtpad portHints={["pin17"]} pcbX="7.750048mm" pcbY="-2.12493225mm" width="1.499997mm" height="0.999998mm" shape="rect" />
<smtpad portHints={["pin18"]} pcbX="7.750048mm" pcbY="-0.12493625mm" width="1.499997mm" height="0.999998mm" shape="rect" />
<smtpad portHints={["pin19"]} pcbX="7.750048mm" pcbY="1.87505975mm" width="1.499997mm" height="0.999998mm" shape="rect" />
<smtpad portHints={["pin20"]} pcbX="7.750048mm" pcbY="3.87505575mm" width="1.499997mm" height="0.999998mm" shape="rect" />
<smtpad portHints={["pin21"]} pcbX="7.750048mm" pcbY="5.87505175mm" width="1.499997mm" height="0.999998mm" shape="rect" />
<smtpad portHints={["pin22"]} pcbX="7.750048mm" pcbY="7.87504775mm" width="1.499997mm" height="0.999998mm" shape="rect" />
<silkscreenpath route={[{"x":7.99998400000004,"y":-6.856063250000034},{"x":7.99998400000004,"y":-7.624921250000057}]} />
<silkscreenpath route={[{"x":7.99998400000004,"y":-4.856067250000024},{"x":7.99998400000004,"y":-5.3937852500000645}]} />
<silkscreenpath route={[{"x":7.99998400000004,"y":-2.8560712500000136},{"x":7.99998400000004,"y":-3.3937892500000544}]} />
<silkscreenpath route={[{"x":7.99998400000004,"y":-0.8560752500000035},{"x":7.99998400000004,"y":-1.3937932500000443}]} />
<silkscreenpath route={[{"x":7.99998400000004,"y":1.143920749999893},{"x":7.99998400000004,"y":0.6062027499999658}]} />
<silkscreenpath route={[{"x":7.99998400000004,"y":3.1439167500000167},{"x":7.99998400000004,"y":2.606198749999976}]} />
<silkscreenpath route={[{"x":7.99998400000004,"y":5.143912750000027},{"x":7.99998400000004,"y":4.6061947500001}]} />
<silkscreenpath route={[{"x":7.99998400000004,"y":7.143908750000037},{"x":7.99998400000004,"y":6.606190749999882}]} />
<silkscreenpath route={[{"x":7.99998400000004,"y":16.375030750000064},{"x":7.99998400000004,"y":8.606186750000006}]} />
<silkscreenpath route={[{"x":5.73112900000001,"y":-7.624921250000057},{"x":7.99998400000004,"y":-7.624921250000057}]} />
<silkscreenpath route={[{"x":3.731133000000227,"y":-7.624921250000057},{"x":4.268851000000041,"y":-7.624921250000057}]} />
<silkscreenpath route={[{"x":1.7311369999999897,"y":-7.624921250000057},{"x":2.2688550000000305,"y":-7.624921250000057}]} />
<silkscreenpath route={[{"x":-0.2688589999999067,"y":-7.624921250000057},{"x":0.26885900000024776,"y":-7.624921250000057}]} />
<silkscreenpath route={[{"x":-2.268854999999803,"y":-7.624921250000057},{"x":-1.7311369999997623,"y":-7.624921250000057}]} />
<silkscreenpath route={[{"x":-4.268850999999813,"y":-7.624921250000057},{"x":-3.7311329999997724,"y":-7.624921250000057}]} />
<silkscreenpath route={[{"x":-7.999983999999813,"y":-7.624921250000057},{"x":-5.731128999999896,"y":-7.624921250000057}]} />
<silkscreenpath route={[{"x":-7.999983999999813,"y":-6.856088649999947},{"x":-7.999983999999813,"y":-7.624921250000057}]} />
<silkscreenpath route={[{"x":-7.999983999999813,"y":-4.8560926500000505},{"x":-7.999983999999813,"y":-5.393810649999978}]} />
<silkscreenpath route={[{"x":-7.999983999999813,"y":-2.8560966500000404},{"x":-7.999983999999813,"y":-3.393814650000081}]} />
<silkscreenpath route={[{"x":-7.999983999999813,"y":-0.8561006500000303},{"x":-7.999983999999813,"y":-1.3938186499999574}]} />
<silkscreenpath route={[{"x":-7.999983999999813,"y":1.1438953500000935},{"x":-7.999983999999813,"y":0.6061773500000527}]} />
<silkscreenpath route={[{"x":-7.999983999999813,"y":3.143891349999876},{"x":-7.999983999999813,"y":2.606173349999949}]} />
<silkscreenpath route={[{"x":-7.999983999999813,"y":5.14388735},{"x":-7.999983999999813,"y":4.606169349999959}]} />
<silkscreenpath route={[{"x":-7.999983999999813,"y":7.14388335000001},{"x":-7.999983999999813,"y":6.606165350000083}]} />
<silkscreenpath route={[{"x":-7.999983999999813,"y":16.375030750000064},{"x":-7.999983999999813,"y":8.606161349999866}]} />
<silkscreenpath route={[{"x":-7.999983999999813,"y":16.375030750000064},{"x":7.99998400000004,"y":16.375030750000064}]} />
<silkscreentext text="{NAME}" pcbX="-0.379984mm" pcbY="17.40487575mm" anchorAlignment="center" fontSize="1mm" />
<fabricationnotepath route={[{"x":-7.899984199999949,"y":8.424983150000003},{"x":-7.899984199999949,"y":16.32496734999995},{"x":7.899984200000063,"y":16.32496734999995},{"x":7.899984200000063,"y":8.424983150000003},{"x":7.799984400000085,"y":8.424983150000003},{"x":7.799984400000085,"y":16.224967549999974},{"x":-7.799984399999744,"y":16.224967549999974},{"x":-7.799984399999744,"y":8.424983150000003},{"x":-7.899984199999949,"y":8.424983150000003}]} strokeWidth="0.254mm" />
<courtyardoutline outline={[{"x":-9.519983999999795,"y":16.654875749999974},{"x":8.760016000000178,"y":16.654875749999974},{"x":8.760016000000178,"y":-8.635524250000003},{"x":-9.519983999999795,"y":-8.635524250000003},{"x":-9.519983999999795,"y":16.654875749999974}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C19949072.obj?uuid=b53268ad1d1146fa93a78daa350043eb",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C19949072.step?uuid=b53268ad1d1146fa93a78daa350043eb",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0, y: -4.388483350000013, z: -0.01 },
      }}
      {...props}
    />
  )
}