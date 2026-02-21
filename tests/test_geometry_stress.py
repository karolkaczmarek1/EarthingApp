
import sys
import os
import unittest
import numpy as np

# Add repo root to path to find modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from earthing_gui.simulation_adapter import SimulationAdapter
from earthing_gui.draw_objects import Rod, Strip, Mesh, Plate

class TestGeometryStress(unittest.TestCase):
    def setUp(self):
        self.adapter = SimulationAdapter()
        self.rho = 100.0
        self.ig = 1000.0

    def run_simulation(self, objects):
        network = self.adapter.run(objects, self.rho, self.ig)
        res = network.get_resistance()
        # Check validity
        self.assertIsNotNone(res)
        if hasattr(res, '__iter__'):
            self.assertTrue(all(r > 0 and not np.isnan(r) and not np.isinf(r) for r in res))
        else:
            self.assertTrue(res > 0 and not np.isnan(res) and not np.isinf(res))
        return res

    def test_narrow_plate(self):
        print("\nTesting Narrow Plate (4cm x 400cm)...")
        # Plate 0.04m width, 4.0m length
        plate = Plate(x=0, y=0, width=0.04, height=4.0, depth=0.5)
        res = self.run_simulation([plate])
        print(f"  Resistance: {res} Ohm")

    def test_long_strip(self):
        print("\nTesting Long Strip (100m)...")
        strip = Strip(points=[(0,0), (100,0)], width=0.03, depth=0.5, profile_type='flat')
        res = self.run_simulation([strip])
        print(f"  Resistance: {res} Ohm")

    def test_tiny_rod(self):
        print("\nTesting Tiny Rod (0.1m)...")
        rod = Rod(x=0, y=0, length=0.1, radius=0.008, depth=0.5)
        res = self.run_simulation([rod])
        print(f"  Resistance: {res} Ohm")

    def test_wire_mesh_manual(self):
        print("\nTesting Wire Mesh (constructed from Round Strips)...")
        # Construct a 2x2 mesh manually using round wires
        objects = []
        # Horizontal
        objects.append(Strip(points=[(0,0), (10,0)], diameter=0.01, depth=0.5, profile_type='round'))
        objects.append(Strip(points=[(0,10), (10,10)], diameter=0.01, depth=0.5, profile_type='round'))
        # Vertical
        objects.append(Strip(points=[(0,0), (0,10)], diameter=0.01, depth=0.5, profile_type='round'))
        objects.append(Strip(points=[(10,0), (10,10)], diameter=0.01, depth=0.5, profile_type='round'))

        res = self.run_simulation(objects)
        print(f"  Resistance: {res} Ohm")

    def test_mixed_geometry(self):
        print("\nTesting Mixed Geometry (Rod + Strip + Plate)...")
        objects = []
        # Rod at origin
        objects.append(Rod(x=0, y=0, length=3.0, radius=0.008, depth=0.5))
        # Strip connecting Rod to Plate
        objects.append(Strip(points=[(0,0), (10,0)], width=0.03, depth=0.5, profile_type='flat'))
        # Plate at end
        objects.append(Plate(x=10, y=0, width=1.0, height=1.0, depth=0.5))

        res = self.run_simulation(objects)
        print(f"  Resistance: {res} Ohm")

    def test_normal_mesh(self):
        print("\nTesting Normal Mesh (10x10m)...")
        mesh = Mesh(x=0, y=0, width=10, height=10, nx=3, ny=3, depth=0.5)
        res = self.run_simulation([mesh])
        print(f"  Resistance: {res} Ohm")

    def test_deep_rod(self):
        print("\nTesting Deep Rod (Depth 100m)...")
        # Top at z=-100m
        rod = Rod(x=0, y=0, depth=100.0, length=3.0, radius=0.008)
        res = self.run_simulation([rod])
        print(f"  Resistance: {res} Ohm")

    def test_overlapping_elements(self):
        print("\nTesting Overlapping Elements (Crossed Strips)...")
        objects = []
        objects.append(Strip(points=[(0,5), (10,5)], width=0.03, depth=0.5))
        objects.append(Strip(points=[(5,0), (5,10)], width=0.03, depth=0.5))
        res = self.run_simulation(objects)
        print(f"  Resistance: {res} Ohm")

if __name__ == '__main__':
    unittest.main()
