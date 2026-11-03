import sys
import unittest
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh
from trimesh.transformations import rotation_matrix

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import head
import battery
import pcb
from config import config


class HeadFit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts = {name: part.obj.val().moved(part.loc)
                     for name, part in head.head().traverse() if part.obj is not None}
        cls.e = config.electronics
        cls.board_z = head.floor_z + cls.e.pcb_z

    def test_printed_parts(self):
        for name in ('head_bottom', 'head_top', 'head_tray'):
            with self.subTest(part=name):
                shape = self.parts[name]
                self.assertTrue(shape.isValid())
                self.assertEqual(len(shape.Solids()), 1)
        # both internal parts have an uninterrupted planar underside for printing.
        for name, area in [('head_bottom', 5000), ('head_tray', 4000)]:
            bottom = cq.Workplane(obj=self.parts[name]).faces('<Z').vals()
            self.assertGreater(sum(f.Area() for f in bottom), area)

    def test_bullet_pockets(self):
        bottom = self.parts['head_bottom']
        self.assertEqual(len(pcb.contacts), 6)
        for (_, (px, py), diameter), (x, y) in zip(pcb.contacts, head.bullet_points()):
            with self.subTest(contact=(px, py)):
                self.assertAlmostEqual(diameter, 3.6)
                px, py = head.pcb_xy((px, py))
                np.testing.assert_allclose((x, y), (px, py), atol=1e-10)
                self.assertAlmostEqual(np.hypot(x-px, y-py)+self.e.bullet_d/2, diameter/2)
                pocket = cq.Workplane('XY', origin=(x, y, self.board_z)).circle(1.8).extrude(-6).val()
                self.assertLess(bottom.intersect(pocket).Volume(), 1e-6)
                # the full bore has a closed floor, and a wall immediately outside its radius.
                self.assertTrue(bottom.isInside(cq.Vector(x, y, self.board_z-6.1)))
                self.assertTrue(bottom.isInside(cq.Vector(x+1.9, y, self.board_z-3)))

    def test_continuous_insertion(self):
        # sweeping bounding boxes is conservative: even the empty space between pins clears.
        moving = [self.parts['control_pcb']]
        moving += [shape for name, shape in self.parts.items() if name not in
                   ('head_top', 'head_bottom', 'head_tray', 'control_pcb', 'battery_lead_0', 'battery_lead_1')]
        for shape in moving:
            b = shape.BoundingBox()
            swept = cq.Solid.makeBox(b.xlen, b.ylen+75, b.zlen, cq.Vector(b.xmin, b.ymin, b.zmin))
            self.assertLess(swept.intersect(self.parts['head_bottom']).Volume(), 1e-5)

    def test_fasteners_clear_each_other(self):
        for x, y in self.e.posts:
            vertical = cq.Workplane('XY', origin=(x, y, self.e.shelf_z+self.e.plate_t)) \
                .circle(1.5).extrude(-8).val()
            side = np.sign(x)
            plane = cq.Plane(origin=(side*config.head.width/2, y, self.e.side_screw_z), normal=(-side, 0, 0))
            horizontal = cq.Workplane(plane).circle(1.5).extrude(8).val()
            self.assertGreater(vertical.distance(horizontal), .5)

    def test_port_access(self):
        usb = self.parts['usb_j1'].BoundingBox()
        probes = {
            'usb-c': cq.Solid.makeBox(10.5, 30, 6, cq.Vector((usb.xmin+usb.xmax)/2-5.25,
                                                            usb.ymin-30, (usb.zmin+usb.zmax)/2-3)),
            'xhp-5': cq.Solid.makeBox(14.8, 30, 5.7, cq.Vector(self.e.balance_x-7.4,
                                   config.head.depth/2-15, head.floor_z+self.e.balance_z-2.85)),
        }
        for port, probe in probes.items():
            self.assertLess(probe.intersect(head.battery_envelope().val()).Volume(), 1e-5)
            for name in self.parts:
                with self.subTest(port=port, part=name):
                    self.assertLess(probe.intersect(self.parts[name]).Volume(), 1e-5)

    def test_cradle_screw_seats(self):
        for x, y in self.e.posts:
            seat = cq.Workplane('XY', origin=(x, y, head.floor_z+self.e.shelf_z+.1)) \
                .circle(2.8).circle(1.8).extrude(.2).val()
            self.assertGreater(seat.intersect(self.parts['head_tray']).Volume()/seat.Volume(), .99)

    def test_battery_leads(self):
        samples = np.linspace(0, 1, 10001)
        for i, curve in enumerate(battery.curves):
            with self.subTest(lead=i):
                path = battery.path(i)
                self.assertAlmostEqual(path.Length(), 70, places=3)
                straight = next(edge for edge in path.Edges() if edge.geomType() == 'LINE')
                self.assertAlmostEqual(straight.Length(), 13)
                np.testing.assert_allclose(straight.tangentAt(0).toTuple(), (0, 0, -1), atol=1e-7)
                start = curve(0)
                a = np.radians(self.e.battery_angle)
                expected = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]]) @ [15, 37.5]
                np.testing.assert_allclose(start[:2], expected+[self.e.battery_x, self.e.battery_y], atol=1e-6)
                launch = curve(0, nu=1)
                launch /= np.linalg.norm(launch)
                self.assertAlmostEqual(launch[2], 0)
                self.assertAlmostEqual(np.degrees(np.arccos(launch @ [-np.sin(a), np.cos(a), 0])), 30, places=4)
                d, dd = curve(samples, nu=1), curve(samples, nu=2)
                curvature = np.linalg.norm(np.cross(d, dd), axis=1)/np.linalg.norm(d, axis=1)**3
                self.assertGreaterEqual(1/curvature.max(), 8)
                # reliefs retain at least 1.2 mm of the original outside wall.
                pts = curve(samples)
                q = np.abs(pts[:, :2])-[config.head.width/2-config.head.corner_r, config.head.depth/2-config.head.corner_r]
                distance = config.head.corner_r-np.linalg.norm(np.maximum(q, 0), axis=1)-np.minimum(q.max(axis=1), 0)
                self.assertGreaterEqual(distance.min()-2.8, 1.2)
                self.assertGreaterEqual(config.head.height-pts[:, 2].max()-2.8, 1.2)
                lead = self.parts[f'battery_lead_{i}']
                self.assertTrue(lead.isValid())
                self.assertEqual(len(lead.Solids()), 1)
                pins = pcb.entries(pcb.footprints['POWER-J1'], 'pad')
                target = head.pcb_xy(pcb.position(pcb.footprints['POWER-J1'], pcb.value(pins[i], 'at')[:2]))
                np.testing.assert_allclose(straight.endPoint().toTuple()[:2], target, atol=1e-6)
        self.assertGreater(self.parts['battery_lead_0'].distance(self.parts['battery_lead_1']), .15)

    def test_assembled_clearance(self):
        printed = ['head_top', 'head_bottom', 'head_tray']
        for i, name in enumerate(printed):
            for other in printed[i+1:]:
                self.assertLess(self.parts[name].intersect(self.parts[other]).Volume(), 1e-5)
        for name, shape in self.parts.items():
            if name in printed:
                continue
            for other in printed:
                with self.subTest(part=name, against=other):
                    self.assertLess(shape.intersect(self.parts[other]).Volume(), 1e-5)
        asset, transform = head.meshes[0]
        battery = trimesh.load(Path(head.__file__).parent / 'assets' / f'{asset}.glb').to_mesh() \
            .apply_scale(1000).apply_transform(transform)
        lo, hi = battery.bounds
        aligned = battery.copy().apply_transform(rotation_matrix(np.radians(-self.e.battery_angle), (0, 0, 1)))
        np.testing.assert_allclose(aligned.extents, self.e.battery_size, atol=1e-5)
        envelope = head.battery_envelope().val()
        for name in printed:
            self.assertLess(envelope.intersect(self.parts[name]).Volume(), 1e-5)
        self.assertAlmostEqual(lo[2], head.floor_z+self.e.shelf_z+self.e.plate_t, places=5)
        ceiling = config.head.height/2 - config.wall/2
        self.assertGreaterEqual(ceiling-hi[2], 1.19)


if __name__ == '__main__':
    unittest.main()
