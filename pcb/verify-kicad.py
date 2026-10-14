"""check the native pcb against kicad's schematic netlist."""
import subprocess
import tempfile
from collections import defaultdict
from math import pi
from pathlib import Path
from xml.etree import ElementTree as ET

import wx

app = wx.App(False)
import pcbnew

root = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as directory:
    netlist = Path(directory) / "ria.xml"
    subprocess.run([
        "kicad-cli", "sch", "export", "netlist", "--format", "kicadxml",
        "-o", str(netlist), str(root / "ria.kicad_sch"),
    ], check=True)
    schematic = ET.parse(netlist).getroot()

board = pcbnew.LoadBoard(str(root / "ria.kicad_pcb"))
footprints = {f.GetReference(): f for f in board.GetFootprints()}
components = {c.attrib["ref"]: c for c in schematic.findall("components/comp")}
assert footprints.keys() == components.keys()
assert len(footprints) == 104
assert not any(ref.startswith("ENC-") for ref in footprints)
esp = components["ESP-U1"]
assert esp.findtext("value") == "ESPS3-32-N4"
assert esp.findtext("fields/field[@name='LCSC']") == "C49164655"
assert esp.findtext("fields/field[@name='Manufacturer']") == "DOIT"
for ref, footprint in footprints.items():
    assert footprint.GetLayer() == pcbnew.F_Cu, f"bottom-mounted component: {ref}"
    for pad in footprint.Pads():
        if pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD:
            layers = pad.GetLayerSet()
            if layers.Contains(pcbnew.F_Cu) or layers.Contains(pcbnew.B_Cu):
                assert layers.Contains(pcbnew.F_Cu) and not layers.Contains(pcbnew.B_Cu), (ref, pad.GetNumber())
            else:
                assert ref in {"ESP-U1", *[f"MOTOR{n}-U1" for n in range(1, 5)]} and not pad.GetNumber()
                assert list(layers.Seq()) == [pcbnew.F_Paste]
for ref, component in components.items():
    assert footprints[ref].GetValue() == component.findtext("value"), ref

pcb_nets = defaultdict(set)
for ref, footprint in footprints.items():
    for pad in footprint.Pads():
        name = pad.GetNetname()
        if name and not name.startswith("unconnected-"):
            pcb_nets[name].add((ref, pad.GetNumber()))

schematic_nets = {
    net.attrib["name"]: {(n.attrib["ref"], n.attrib["pin"]) for n in net.findall("node")}
    for net in schematic.findall("nets/net")
    if not net.attrib["name"].startswith("unconnected-")
}
paste = [pad for pad in footprints["ESP-U1"].Pads() if not pad.GetNumber()]
assert len(paste) == 9
thermal = [pad for pad in footprints["ESP-U1"].Pads() if pad.GetNumber() == "41" and pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
assert len(thermal) == 12
for window in paste:
    for hole in thermal:
        assert not window.GetEffectiveShape(pcbnew.F_Paste).Collide(hole.GetEffectiveHoleShape(), 0)
assert pcb_nets == schematic_nets
assert len(pcb_nets) == 93
pin_nets = {node: name for name, nodes in pcb_nets.items() for node in nodes}
pwm_module_pins = [("21", "22", "8"), ("9", "10", "11"), ("23", "28", "29"), ("30", "31", "32")]
for channel in range(1, 5):
    ref = f"MOTOR{channel}-U1"
    prefix = f"MOTOR{channel}"
    driver = footprints[ref]
    assert driver.GetValue() == "DRV8316CTRGFR"
    assert driver.GetFPID().GetLibItemName() == "DRV8316CTRGFR"
    assert components[ref].findtext("fields/field[@name='LCSC']") == "C6602057"
    assert {pad.GetNumber() for pad in driver.Pads() if pad.GetNumber()} == {str(n) for n in range(1, 42)}
    # the imported ti land pattern is rotated 180 degrees in its local frame.
    for pad in [pad for pad in driver.Pads() if pad.GetNumber() and pad.GetNumber() != "41"]:
        n = int(pad.GetNumber())
        if n <= 12:
            x, y, width, height = 2.4, 2.75 - 0.5 * (n - 1), 0.6, 0.25
        elif n <= 20:
            x, y, width, height = 1.75 - 0.5 * (n - 13), -3.4, 0.25, 0.6
        elif n <= 32:
            x, y, width, height = -2.4, -2.75 + 0.5 * (n - 21), 0.6, 0.25
        else:
            x, y, width, height = -1.75 + 0.5 * (n - 33), 3.4, 0.25, 0.6
        position, size = pad.GetFPRelativePosition(), pad.GetSize()
        # imported mil-to-mm conversion differs by at most 0.0002 mm.
        for actual, expected in [(position.x, x), (position.y, y), (size.x, width), (size.y, height)]:
            assert abs(actual - pcbnew.FromMM(expected)) <= pcbnew.FromMM(0.0002), (ref, n)
    ep = next(pad for pad in driver.Pads() if pad.GetNumber() == "41" and pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD)
    assert not ep.GetLayerSet().Contains(pcbnew.F_Paste)
    assert abs(ep.GetSize().x - pcbnew.FromMM(3.7)) <= 20
    assert abs(ep.GetSize().y - pcbnew.FromMM(5.7)) <= 20
    windows = [pad for pad in driver.Pads() if not pad.GetNumber()]
    assert len(windows) == 12
    # ti rgf0040e: 3 x 4 apertures, nominal 69% coverage; dimensions in mm.
    expected = {(pcbnew.FromMM(x), pcbnew.FromMM(y)) for x in [-1.25, 0, 1.25] for y in [-2.025, -0.675, 0.675, 2.025]}
    assert {(pad.GetFPRelativePosition().x, pad.GetFPRelativePosition().y) for pad in windows} == expected
    for window in windows:
        assert list(window.GetLayerSet().Seq()) == [pcbnew.F_Paste]
        assert window.GetShape() == pcbnew.PAD_SHAPE_ROUNDRECT
        assert window.GetSize() == pcbnew.VECTOR2I(pcbnew.FromMM(1.05), pcbnew.FromMM(1.15))
        assert window.GetRoundRectCornerRadius() == pcbnew.FromMM(0.05)
        assert window.GetFPRelativeOrientation().AsDegrees() % 360 == 0
    coverage = 12 * (1.05 * 1.15 - (4 - pi) * 0.05 ** 2) / (pcbnew.ToMM(ep.GetSize().x) * pcbnew.ToMM(ep.GetSize().y))
    assert 0.685 < coverage < 0.688
    holes = [via for via in board.GetTracks() if isinstance(via, pcbnew.PCB_VIA) and ep.GetEffectiveShape(pcbnew.F_Cu).Collide(via.GetEffectiveHoleShape(), 0)]
    expected_vias = set()
    for x in [-0.625, 0.625]:
        for y in [-1.35, 0, 1.35]:
            probe = pcbnew.PAD(driver)
            probe.SetFPRelativePosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
            expected_vias.add(tuple(probe.GetPosition()))
    assert {tuple(via.GetPosition()) for via in holes} == expected_vias
    for via in holes:
        assert via.GetNetname() == "GND"
        assert via.GetWidth(pcbnew.F_Cu) == pcbnew.FromMM(0.5)
        assert via.GetDrillValue() == pcbnew.FromMM(0.2)
        assert via.IsTented(pcbnew.F_Mask) and via.IsTented(pcbnew.B_Mask)
        # holes sit in the ti 0.2 mm paste gaps: zero nominal process clearance.
        for window in windows:
            assert not window.GetEffectiveShape(pcbnew.F_Paste).Collide(via.GetEffectiveHoleShape(), 0)
    for pin in [9, 10, 11]:
        assert pin_nets[ref, str(pin)] == "BAT"
    for pin in [2, 4, 12, 15, 18, 21, 24, 26, 34, 35, 41]:
        assert pin_nets[ref, str(pin)] == "GND"
    for pin in [25, 28, 30, 32, 37]:
        assert pin_nets[ref, str(pin)] == prefix + "_AVDD"
    assert prefix + "-C9" not in footprints
    assert pcb_nets[prefix + "_AVDD"] == {
        *[(ref, str(pin)) for pin in [25, 28, 30, 32, 37]],
        (prefix + "-C6", "1"), (prefix + "-R1", "1"), (prefix + "-R3", "1"),
    }
    for pin in [1, 36, 38]:
        assert (ref, str(pin)) not in pin_nets
    for pwm, esp_pin, phase in zip([27, 29, 31], pwm_module_pins[channel - 1], "ABC"):
        assert pin_nets[ref, str(pwm)] == prefix + f"_PWM_{phase}"
        assert pcb_nets[prefix + f"_PWM_{phase}"] == {(ref, str(pwm)), ("ESP-U1", esp_pin)}
    for outputs, phase in zip([(13, 14), (16, 17), (19, 20)], "ABC"):
        for output in outputs:
            assert pin_nets[ref, str(output)] == prefix + f"_{phase}"
    assert pin_nets[ref, "23"] == "MOTOR_ENABLE"
    assert pin_nets[ref, "22"] == prefix + "_FAULT"
    assert pin_nets[prefix + "-R3", "1"] == prefix + "_AVDD"
    assert pin_nets[prefix + "-R3", "2"] == prefix + "_FAULT"
    assert footprints[prefix + "-R3"].GetValue() == "5.1kΩ"
    assert pcb_nets[prefix + "_MODE"] == {(ref, "33"), (prefix + "-R1", "2")}
    assert footprints[prefix + "-R1"].GetValue() == "47kΩ"
    assert pin_nets[prefix + "-R1", "1"] == prefix + "_AVDD"
    assert pcb_nets[prefix + "_CP"] == {(ref, "8"), (prefix + "-C2", "1")}
    assert pin_nets[prefix + "-C2", "2"] == "BAT"
    assert footprints[prefix + "-C2"].GetValue() == "1uF"
    assert pcb_nets[prefix + "_CPH"] == {(ref, "7"), (prefix + "-C7", "1")}
    assert pcb_nets[prefix + "_CPL"] == {(ref, "6"), (prefix + "-C7", "2")}
    assert footprints[prefix + "-C7"].GetValue() == "47nF"
    assert pcb_nets[prefix + "_SW_BK"] == {(ref, "5"), (prefix + "-R2", "1")}
    assert pcb_nets[prefix + "_BUCK"] == {(ref, "3"), (prefix + "-R2", "2"), (prefix + "-C8", "1")}
    assert footprints[prefix + "-R2"].GetValue() == "22Ω"
    assert footprints[prefix + "-C8"].GetValue() == "22uF"
    assert pin_nets[prefix + "-C8", "2"] == "GND"
    assert components[prefix + "-C6"].findtext("fields/field[@name='LCSC']") == "C28323"
    assert footprints[prefix + "-C6"].GetValue() == "1uF"
    assert footprints[prefix + "-C6"].GetFPID().GetLibItemName() == "C_0805_2012Metric"
    assert pin_nets[prefix + "-C6", "1"] == prefix + "_AVDD"
    assert pin_nets[prefix + "-C6", "2"] == "GND"
    for suffix, value, lcsc, mpn, footprint in [
        ("C3", "100nF", "C14663", "CC0603KRX7R9BB104", "C_0603_1608Metric"),
        ("C5", "10uF", "C89632", "CL31B106KBHNNNE", "C_1206_3216Metric"),
        ("C10", "100nF", "C14663", "CC0603KRX7R9BB104", "C_0603_1608Metric"),
    ]:
        capacitor = prefix + "-" + suffix
        component = components[capacitor]
        assert footprints[capacitor].GetValue() == value
        assert footprints[capacitor].GetFPID().GetLibItemName() == footprint
        assert component.findtext("fields/field[@name='LCSC']") == lcsc
        assert component.findtext("fields/field[@name='MPN']") == mpn
        description = component.findtext("fields/field[@name='Description']")
        assert "50V" in description and "X7R" in description
        assert pin_nets[capacitor, "1"] == "BAT"
        assert pin_nets[capacitor, "2"] == "GND"
    for pin, phase, resistor, capacitor in [(40, "A", "R4", "C11"), (39, "B", "R5", "C12")]:
        raw = prefix + f"_ISENSE_{phase}_RAW"
        filtered = prefix + f"_ISENSE_{phase}"
        assert pcb_nets[raw] == {(ref, str(pin)), (prefix + "-" + resistor, "1")}
        assert pin_nets[prefix + "-" + resistor, "2"] == filtered
        assert footprints[prefix + "-" + resistor].GetValue() == "330Ω"
        assert pin_nets[prefix + "-" + capacitor, "1"] == filtered
        assert pin_nets[prefix + "-" + capacitor, "2"] == "GND"
        assert footprints[prefix + "-" + capacitor].GetValue() == "22pF"
adc_pins = [("4", "5"), ("39", "38"), ("6", "7"), ("12", "17")]
fault_pins = ["36", "25", "35", "19"]
for channel, (adc_pair, fault_pin) in enumerate(zip(adc_pins, fault_pins), 1):
    for pin, phase in zip(adc_pair, "AB"):
        assert pin_nets["ESP-U1", pin] == f"MOTOR{channel}_ISENSE_{phase}"
    assert pin_nets["ESP-U1", fault_pin] == f"MOTOR{channel}_FAULT"
assert pin_nets["ESP-U1", "33"] == "IMU_SDA"
assert pin_nets["ESP-U1", "34"] == "IMU_SCL"
assert pin_nets["ESP-U1", "18"] == "VBAT_SENSE"
assert pin_nets["SENSE-R1", "1"] == "BAT"
assert pin_nets["SENSE-R1", "2"] == "VBAT_SENSE"
assert pin_nets["SENSE-R2", "1"] == "VBAT_SENSE"
assert pin_nets["SENSE-R2", "2"] == "GND"
assert footprints["SENSE-R1"].GetValue() == "100kΩ"
assert footprints["SENSE-R2"].GetValue() == "20kΩ"
assert pin_nets["SENSE-C1", "1"] == "VBAT_SENSE"
assert pin_nets["SENSE-C1", "2"] == "GND"
assert footprints["SENSE-C1"].GetValue() == "100nF"
for pin in [15, 16, 26, 37]:
    assert ("ESP-U1", str(pin)) not in pin_nets
assert pin_nets["ESP-U1", "13"] == "ESP_USB_DM"
assert pin_nets["ESP-U1", "14"] == "ESP_USB_DP"
assert pin_nets["ESP-U1", "24"] == "MOTOR_ENABLE"
assert pin_nets["ESP-U1", "27"] == "ESP_BOOT"
assert not {"MOTOR_MISO", "MOTOR_MOSI", "MOTOR_SCLK", "MOTOR_FAULT", "SDA0", "SCL0"} & pcb_nets.keys()
assert board.GetCopperLayerCount() == 4
board_outline = pcbnew.SHAPE_POLY_SET()
assert board.GetBoardPolygonOutlines(board_outline, False)
outline = board_outline.BBox()
assert outline.GetWidth() == pcbnew.FromMM(50)
assert outline.GetHeight() == pcbnew.FromMM(65)
assert any(z.GetLayer() == pcbnew.In1_Cu and z.GetNetname() == "GND" for z in board.Zones())
assert any(z.GetLayer() == pcbnew.In2_Cu and z.GetNetname() == "BAT" for z in board.Zones())
antenna = list(footprints["ESP-U1"].Zones())
assert len(antenna) == 1 and antenna[0].GetIsRuleArea()
assert set(antenna[0].GetLayerSet().Seq()) == {
    pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu,
}
for kind in ("Tracks", "Vias", "Pads", "Footprints", "ZoneFills"):
    assert getattr(antenna[0], "GetDoNotAllow" + kind)()
for zone in [*board.Zones(), *antenna]:
    if zone.GetIsRuleArea():
        assert zone.GetLayerSet().Contains(pcbnew.In1_Cu)
        assert zone.GetLayerSet().Contains(pcbnew.In2_Cu)
for left, right in [
    ("MOTOR-J1", "MOTOR-J2"),
    ("MOTOR-J3", "MOTOR-J6"), ("MOTOR-J4", "MOTOR-J7"),
    ("MOTOR-J5", "MOTOR-J8"),
]:
    a, b = footprints[left].GetPosition(), footprints[right].GetPosition()
    assert a.x + b.x == pcbnew.FromMM(200) and a.y == b.y, (left, right)
usb = footprints["USB-J1"]
assert usb.GetPosition().x == pcbnew.FromMM(100) and usb.GetOrientationDegrees() == 0
assert usb.GetPosition().y > pcbnew.FromMM(135)
xt60 = footprints["POWER-J1"]
assert xt60.GetValue() == "XT60PB-M.G.Y"
assert components["POWER-J1"].findtext("fields/field[@name='LCSC']") == "C19268037"
power_pads = {pad.GetNumber(): pad for pad in xt60.Pads()}
assert power_pads.keys() == {"1", "2"}
assert pin_nets["POWER-J1", "1"] == "GND"
assert pin_nets["POWER-J1", "2"] == "BAT"
negative, positive = power_pads["1"], power_pads["2"]
assert positive.GetPosition().x - negative.GetPosition().x == pcbnew.FromMM(7.2)
assert positive.GetPosition().y == negative.GetPosition().y
for pad in power_pads.values():
    assert pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH
    assert pad.GetDrillSize() == pcbnew.VECTOR2I(pcbnew.FromMM(4.6), pcbnew.FromMM(4.6))
for ref, x, angle in [("MOTOR-J1", 78.5, -90), ("MOTOR-J2", 121.5, 90)]:
    header = footprints[ref]
    assert header.GetPosition() == pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(91))
    assert header.GetOrientationDegrees() == angle
    assert header.GetFPID().GetLibItemName() == "WJ2EDGR-5.08-03P-14-00A"
    assert components[ref].findtext("fields/field[@name='LCSC']") == "C70914"
    pads = sorted(header.Pads(), key=lambda pad: pad.GetNumber())
    assert len(pads) == 3
    for pad in pads:
        assert pad.GetDrillSize() == pcbnew.VECTOR2I(pcbnew.FromMM(1.7), pcbnew.FromMM(1.7))
        assert pad.GetSize() == pcbnew.VECTOR2I(pcbnew.FromMM(3), pcbnew.FromMM(3))
    for a, b in zip(pads, pads[1:]):
        assert abs(a.GetPosition().y - b.GetPosition().y) == pcbnew.FromMM(5.08)
        assert a.GetPosition().x == b.GetPosition().x
print(f"50 x 65 mm, four layers, {len(footprints)} top-mounted components, {len(pcb_nets)} connected nets, eight filtered current inputs, four drv8316ct configurations/faults, vertical xt60 and antenna keepout match")
