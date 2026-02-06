
import numpy as np
import earthing
from earthing import Network

def calculate():
    rho = 100.0
    Ig = 1000.0  # 1kA injection current

    net = Network(rho, Ig)

    # Grid Parameters
    Lx = 120.0
    Ly = 100.0
    dx = 15.0  # Spacing along X (so lines are parallel to Y)
    dy = 10.0  # Spacing along Y (so lines are parallel to X)
    depth = 0.8
    z = -depth

    cond_dia = 0.01
    cond_rad = cond_dia / 2.0

    rod_len = 6.0
    rod_dia = 0.02
    rod_rad = rod_dia / 2.0

    # Add Grid Conductors
    # The library doesn't have a generic add_pipe method for horizontal pipes,
    # so we manually instantiate NetworkElementPipe and add to the subnet.

    # Lines parallel to X-axis (spaced along Y)
    # y = 0, 10, ..., 100
    ny = int(Ly / dy) + 1
    for i in range(ny):
        y = i * dy
        start = np.array([0.0, y, z])
        end = np.array([Lx, y, z])
        pipe = earthing.NetworkElementPipe(start, rho, cond_rad, end)
        net.elements[0].append(pipe)

    # Lines parallel to Y-axis (spaced along X)
    # x = 0, 15, ..., 120
    nx = int(Lx / dx) + 1
    for i in range(nx):
        x = i * dx
        start = np.array([x, 0.0, z])
        end = np.array([x, Ly, z])
        pipe = earthing.NetworkElementPipe(start, rho, cond_rad, end)
        net.elements[0].append(pipe)

    # Add Rods at corners
    corners = [
        (0.0, 0.0),
        (Lx, 0.0),
        (0.0, Ly),
        (Lx, Ly)
    ]

    for x, y in corners:
        loc = (x, y, z)
        net.add_rod(loc, rod_rad, rod_len)

    print("Generating model... (this may take a moment)")
    # Using desc_size=2.0 for reasonable speed/accuracy trade-off
    # Default is 0.25 which would be very slow for this size
    net.generate_model(desc_size=1.0)

    print("Solving model...")
    net.solve_model()

    R = net.get_resistance()
    print(f"Total Resistance: {R} Ohms")

    return R

if __name__ == "__main__":
    calculate()
