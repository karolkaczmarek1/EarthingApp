
import numpy as np
import earthing
from earthing import Network

def calculate():
    rho = 100.0
    Ig = 1000.0  # 1kA injection current

    net = Network(rho, Ig)

    # Grid Parameters from Image
    Lx = 120.0
    Ly = 100.0
    Nx = 11  # Number of conductors along X (parallel to Y)
    Ny = 9   # Number of conductors along Y (parallel to X)

    # Spacing
    # If Nx lines are distributed along Lx (from 0 to Lx), there are Nx-1 spaces.
    dx = Lx / (Nx - 1)
    dy = Ly / (Ny - 1)

    depth = 0.8
    z = -depth

    # Conductor: Strip 25mm
    strip_width = 0.025

    # Rods: 6m length, diameter not specified in image, sticking to previous 0.02m
    rod_len = 6.0
    rod_dia = 0.02
    rod_rad = rod_dia / 2.0

    # Add Grid Conductors (Strips)

    # Lines parallel to Y-axis (spaced along X)
    # x = 0, dx, 2dx, ...
    for i in range(Nx):
        x = i * dx
        start = np.array([x, 0.0, z])
        end = np.array([x, Ly, z])
        net.add_strip(start, end, strip_width)

    # Lines parallel to X-axis (spaced along Y)
    # y = 0, dy, 2dy, ...
    for i in range(Ny):
        y = i * dy
        start = np.array([0.0, y, z])
        end = np.array([Lx, y, z])
        net.add_strip(start, end, strip_width)

    # Add Rods at every intersection
    rod_count = 0
    for i in range(Nx):
        x = i * dx
        for j in range(Ny):
            y = j * dy
            loc = (x, y, z)
            net.add_rod(loc, rod_rad, rod_len)
            rod_count += 1

    print(f"Grid: {Lx}x{Ly}m")
    print(f"Conductors: {Nx} vertical (dx={dx}m), {Ny} horizontal (dy={dy}m)")
    print(f"Added {rod_count} rods.")

    print("Generating model... (this may take a moment)")
    # Using desc_size=1.0 as established previously
    net.generate_model(desc_size=1.0)

    print("Solving model...")
    net.solve_model()

    R = net.get_resistance()
    print(f"Total Resistance: {R} Ohms")

    return R

if __name__ == "__main__":
    calculate()
