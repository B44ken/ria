"""check the native pcb against kicad's schematic netlist."""
import subprocess
import tempfile
from collections import defaultdict
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
for via in (item for item in board.GetTracks() if item.GetClass() == "PCB_VIA"):
    assert via.GetDrillValue() >= pcbnew.FromMM(0.3), "routing via drill below 0.3 mm"
    assert via.GetWidth(pcbnew.F_Cu) >= pcbnew.FromMM(0.6), "routing via land below 0.6 mm"
footprints = {f.GetReference(): f for f in board.GetFootprints()}
components = {c.attrib["ref"]: c for c in schematic.findall("components/comp")}
assert footprints.keys() == components.keys()
assert len(footprints) == 69
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
                assert ref == "ESP-U1" and not pad.GetNumber()
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
assert len(thermal) == 0, "lean design must not reintroduce module cooling holes"
assert any(p.GetNumber() == "41" and p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD for p in footprints["ESP-U1"].Pads()), "retain soldered module ground land"
for window in paste:
    for hole in thermal:
        assert not window.GetEffectiveShape(pcbnew.F_Paste).Collide(hole.GetEffectiveHoleShape(), 0)
assert pcb_nets == schematic_nets
assert len(pcb_nets) == 59
pin_nets = {node: name for name, nodes in pcb_nets.items() for node in nodes}
for channel in range(1, 5):
    ref = f"MOTOR{channel}-U1"
    driver = footprints[ref]
    assert driver.GetValue() == "SS6343M-QF-TP"
    assert driver.GetFPID().GetLibItemName() == "SS6343M-QF-TP"
    assert {pad.GetNumber() for pad in driver.Pads()} == {str(n) for n in range(1, 26)}
    for pin in [1, 2, 3, 24]:
        assert pin_nets[ref, str(pin)] == "MOTOR_ENABLE"
    for pin in [7, 13, 16]:
        assert pin_nets[ref, str(pin)] == "BAT"
    for pin in [8, 12, 15, 25]:
        assert pin_nets[ref, str(pin)] == "GND"
    for pwm, phase in zip([4, 5, 6], "ABC"):
        assert pin_nets[ref, str(pwm)] == f"MOTOR{channel}_PWM_{phase}"
    for output, phase in zip([9, 10, 11], "ABC"):
        assert pin_nets[ref, str(output)] == f"MOTOR{channel}_{phase}"
    assert pin_nets[ref, "20"] == "MOTOR_FAULT"
    assert pcb_nets[f"MOTOR{channel}_VCP"] == {(ref, "14"), (f"MOTOR{channel}-C2", "1")}
    assert pin_nets[f"MOTOR{channel}-C2", "2"] == "BAT"
    assert pcb_nets[f"MOTOR{channel}_V3P3"] == {(ref, "18"), (f"MOTOR{channel}-C6", "1")}
    assert footprints[f"MOTOR{channel}-C6"].GetValue() == "4.7uF"
    assert pin_nets[f"MOTOR{channel}-C6", "2"] == "GND"
assert pcb_nets["MOTOR_FAULT"] == {
    ("ESP-U1", "36"), ("MOTOR-R2", "2"),
    *[(f"MOTOR{channel}-U1", "20") for channel in range(1, 5)],
}
assert pin_nets["MOTOR-R2", "1"] == "V3_3"
for pin in [25, 33, 34, 35, 37, 38, 39]:
    assert ("ESP-U1", str(pin)) not in pin_nets
assert pin_nets["ESP-U1", "13"] == "ESP_USB_DM"
assert pin_nets["ESP-U1", "14"] == "ESP_USB_DP"
assert pin_nets["ESP-U1", "24"] == "MOTOR_ENABLE"
assert pin_nets["ESP-U1", "27"] == "ESP_BOOT"
assert not {"MOTOR_MISO", "MOTOR_MOSI", "MOTOR_SCLK"} & pcb_nets.keys()
assert board.GetCopperLayerCount() == 4
outline = pcbnew.SHAPE_POLY_SET()
assert board.GetBoardPolygonOutlines(outline, False)
assert outline.BBox().GetWidth() == pcbnew.FromMM(50)
assert outline.BBox().GetHeight() == pcbnew.FromMM(69.45)
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
    ("ENC-J1", "ENC-J3"), ("ENC-J2", "ENC-J4"),
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
assert xt60.GetPosition() == pcbnew.VECTOR2I(pcbnew.FromMM(83.4), pcbnew.FromMM(75.7))
assert xt60.GetOrientationDegrees() == -90
assert xt60.GetValue() == "XT60PW-M"
assert components["POWER-J1"].findtext("fields/field[@name='LCSC']") == "C98732"
power_pads = {pad.GetNumber(): pad for pad in xt60.Pads()}
assert power_pads.keys() == {"1", "2", "3", "4"}
assert pin_nets["POWER-J1", "1"] == "GND"
assert pin_nets["POWER-J1", "2"] == "BAT"
for number in ["1", "2"]:
    drill = power_pads[number].GetDrillSize()
    assert abs(drill.x - pcbnew.FromMM(2.9)) <= pcbnew.FromMM(0.00005)
    assert drill.x == drill.y
negative, positive = power_pads["1"].GetPosition(), power_pads["2"].GetPosition()
assert abs(positive.x - negative.x - pcbnew.FromMM(7.2)) <= pcbnew.FromMM(0.0002)
assert positive.y == negative.y
# amass c98732, 2025v0: 0.8 x 1.9 mm tab slots, 13.5 mm pitch, 6 mm behind pins.
left, right = power_pads["4"].GetPosition(), power_pads["3"].GetPosition()
assert abs(right.x - left.x - pcbnew.FromMM(13.5)) <= pcbnew.FromMM(0.0002)
assert left.y == right.y
assert abs(negative.y - left.y - pcbnew.FromMM(6)) <= pcbnew.FromMM(0.00005)
local_power = pcbnew.FootprintLoad(str(root / "ria.pretty"), "POWER-J1")
for pad in [power_pads["3"], power_pads["4"], *[p for p in local_power.Pads() if p.GetNumber() in {"3", "4"}]]:
    assert pad.GetDrillSize() == pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(1.9))
    assert pad.GetSize() == pcbnew.VECTOR2I(pcbnew.FromMM(1.4), pcbnew.FromMM(2.5))
for ref, x, angle in [("MOTOR-J1", 78.5, -90), ("MOTOR-J2", 121.5, 90)]:
    header = footprints[ref]
    assert header.GetPosition() == pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(89))
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
print("four layers, inner ground/battery planes, 69 top-mounted components, 59 connected nets, ss6343m pinout, mirrored 5.08 mm motor connectors and antenna-notch outline match")
