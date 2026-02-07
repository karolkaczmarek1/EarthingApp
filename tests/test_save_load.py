import unittest
import os
import tempfile
from earthing_gui.draw_objects import Rod, Strip
from earthing_gui.file_handler import save_to_json, load_from_json

class TestFileHandler(unittest.TestCase):
    def test_save_load(self):
        # Create objects
        rod = Rod(x=1, y=2, radius=0.01, length=3)
        strip = Strip(points=[(0,0), (10,10)], width=0.03, profile_type='flat')

        objects = [rod, strip]
        params = {'rho': '150.0', 'ig': '2000.0'}

        # Save
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
            filepath = tmp.name

        try:
            save_to_json(filepath, objects, params)

            # Load
            loaded_objects, loaded_params = load_from_json(filepath)

            # Verify Params
            self.assertEqual(loaded_params['rho'], '150.0')
            self.assertEqual(loaded_params['ig'], '2000.0')

            # Verify Objects
            self.assertEqual(len(loaded_objects), 2)

            # Verify Rod
            l_rod = loaded_objects[0]
            self.assertIsInstance(l_rod, Rod)
            self.assertAlmostEqual(l_rod.x, 1)
            self.assertAlmostEqual(l_rod.y, 2)

            # Verify Strip
            l_strip = loaded_objects[1]
            self.assertIsInstance(l_strip, Strip)
            self.assertEqual(len(l_strip.points), 2)
            self.assertAlmostEqual(l_strip.points[1][0], 10)
            self.assertEqual(l_strip.profile_type, 'flat')

        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

if __name__ == '__main__':
    unittest.main()
