
import sys
import os

# Ensure earthing can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from earthing import Network
except ImportError:
    # If not installed or not in path, assume running from repo root
    sys.path.append(os.getcwd())
    from earthing import Network

from .draw_objects import Rod, Strip, Mesh, Plate

class SimulationAdapter:
    def __init__(self):
        pass

    def run(self, objects, global_rho):
        if not objects:
            raise ValueError("No objects to simulate")

        rho = global_rho
        Ig = 1000 # Default injection current, can be parameterized later

        network = Network(rho, Ig)

        for obj in objects:
            if isinstance(obj, Rod):
                # add_rod(loc, radius, length)
                # Z is negative of depth
                z = -abs(obj.depth)
                network.add_rod([obj.x, obj.y, z], obj.radius, obj.length)

            elif isinstance(obj, Strip):
                # add_strip(loc_start, loc_end, w)
                # Points are list of (x,y). Z is constant depth.
                z = -abs(obj.depth)
                for i in range(len(obj.points)-1):
                    p1 = obj.points[i]
                    p2 = obj.points[i+1]
                    network.add_strip([p1[0], p1[1], z], [p2[0], p2[1], z], obj.width)

            elif isinstance(obj, Mesh):
                # add_mesh(loc, Lx, Ly, Nx, Ny, w)
                # loc is start coordinates
                z = -abs(obj.depth)
                network.add_mesh([obj.x, obj.y, z], obj.width, obj.height, obj.nx, obj.ny, obj.strip_width)

            elif isinstance(obj, Plate):
                # add_plate(loc, w, h, n_cap, h_cap)
                # loc is center? Library doc: "Coordinates of pipe (z coordinate defines the rod top)" copy-paste error in doc?
                # Library code:
                # c1 = element.loc - element.w_cap*element.w/2 - element.h_cap*element.h/2
                # So loc is center.
                z = -abs(obj.depth)
                network.add_plate([obj.x, obj.y, z], obj.width, obj.height, n_cap=[0,0,1], h_cap=[0,1,0]) # Horizontal plate

        # Generate model
        # Using fast method for speed in UI
        network.generate_model_fast()

        # Solve
        network.solve_model()

        return network
