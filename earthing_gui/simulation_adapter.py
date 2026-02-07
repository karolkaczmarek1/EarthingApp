
import sys
import os

# Ensure earthing can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from earthing import Network, NetworkElementPipe
except ImportError:
    # If not installed or not in path, assume running from repo root
    sys.path.append(os.getcwd())
    from earthing import Network, NetworkElementPipe

from .draw_objects import Rod, Strip, Mesh, Plate
import numpy as np

class SimulationAdapter:
    def __init__(self):
        pass

    def run(self, objects, global_rho, global_ig, desc_size=0.25):
        if not objects:
            raise ValueError("No objects to simulate")

        rho = global_rho
        Ig = global_ig

        network = Network(rho, Ig)

        for obj in objects:
            if isinstance(obj, Rod):
                # add_rod(loc, radius, length)
                # Z is negative of depth
                z = -abs(obj.depth)
                network.add_rod([obj.x, obj.y, z], obj.radius, obj.length)

            elif isinstance(obj, Strip):
                # Points are list of (x,y). Z is constant depth.
                z = -abs(obj.depth)
                for i in range(len(obj.points)-1):
                    p1 = obj.points[i]
                    p2 = obj.points[i+1]

                    if obj.profile_type == 'round':
                        # Use NetworkElementPipe for arbitrary oriented round conductor
                        # Network has no helper for this, so we must manually create and append it
                        # loc start, rho, radius, loc end
                        start = np.array([p1[0], p1[1], z])
                        end = np.array([p2[0], p2[1], z])
                        radius = obj.diameter / 2.0

                        # Note: We need to use the same 'rho' as the network.
                        # Since we made rho global, we use the passed rho.
                        element = NetworkElementPipe(start, rho, radius, end)

                        # Add to the current subnet (last one)
                        if not network.elements:
                            network.elements.append([])
                        network.elements[-1].append(element)
                    else:
                        # Flat strip
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

        # Safety check: Ensure desc_size is valid for the smallest element to prevent crashes
        # This is primarily for headless mode (tests/scripts) where GUI validation is bypassed.
        min_dim = float('inf')
        for obj in objects:
            if isinstance(obj, Rod):
                min_dim = min(min_dim, obj.length)
            elif isinstance(obj, Strip):
                for i in range(len(obj.points)-1):
                    p1 = np.array(obj.points[i])
                    p2 = np.array(obj.points[i+1])
                    dist = np.linalg.norm(p1 - p2)
                    if dist > 0: min_dim = min(min_dim, dist)
            elif isinstance(obj, Mesh):
                if obj.nx > 1: min_dim = min(min_dim, obj.width / (obj.nx - 1))
                if obj.ny > 1: min_dim = min(min_dim, obj.height / (obj.ny - 1))
            elif isinstance(obj, Plate):
                min_dim = min(min_dim, obj.width, obj.height)

        if min_dim != float('inf') and desc_size > min_dim:
            # Auto-adjust if the provided size is unsafe
            safe_size = min_dim / 2.1
            # But don't go ridiculously small automatically to avoid freezing
            safe_size = max(0.001, safe_size)
            if desc_size > safe_size:
                print(f"Warning: Discretization step {desc_size} is too large for smallest element ({min_dim}). Reducing to {safe_size}.")
                desc_size = safe_size

        network.generate_model_fast(desc_size=desc_size)

        # Solve
        network.solve_model()

        return network
