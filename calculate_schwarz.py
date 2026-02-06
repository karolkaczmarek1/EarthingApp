
import numpy as np

def calculate_schwarz():
    # Parameters
    rho = 100.0          # Resistivity (Ohm-m)

    # Grid Dimensions
    Lx = 120.0
    Ly = 100.0
    Area = Lx * Ly

    # Grid Conductors
    dx = 15.0
    dy = 10.0

    # Number of lines
    nx = int(Lx / dx) + 1  # 9 lines of length Ly
    ny = int(Ly / dy) + 1  # 11 lines of length Lx

    # Total length of grid conductors (Lc)
    # 9 lines * 100m + 11 lines * 120m
    Lc = (nx * Ly) + (ny * Lx)

    h = 0.8              # Depth (m)
    d_c = 0.01           # Conductor diameter (m)
    r_c = d_c / 2.0      # Conductor radius

    # Rods
    nr = 99              # Number of rods
    Lr = 6.0             # Length of rod (m)
    d_r = 0.02           # Rod diameter (m)
    r_r = d_r / 2.0      # Rod radius (b)

    # Coefficients k1 and k2
    # Based on Length-to-Width ratio L/W
    # Lx is longer side? 120 vs 100. Yes.
    ratio = Lx / Ly

    # Standard IEEE 80 approximations for Box/Rectangular grids
    k1 = 1.43 - 0.05 * ratio
    k2 = 5.50 + 0.15 * ratio

    print(f"Parameters:")
    print(f"  Rho: {rho}")
    print(f"  Area: {Area} m2 ({Lx}x{Ly})")
    print(f"  Lc: {Lc} m")
    print(f"  h: {h} m")
    print(f"  nr: {nr}")
    print(f"  Lr: {Lr} m")
    print(f"  k1: {k1:.4f}")
    print(f"  k2: {k2:.4f}")

    # Schwarz Equations

    # 1. Grid Resistance (R1)
    # R1 = (rho / (pi * Lc)) * (ln(2*Lc / a_prime) + k1 * Lc / sqrt(Area) - k2)
    # a_prime = sqrt(d_c * h) for conductors at depth h?
    # IEEE 80 Eq 32 defines a' for conductors buried at depth h as:
    # a' = sqrt(r_c * 2 * h)  <-- This is common geometric mean radius for depth
    # Let's verify: a' is "geometric mean radius of grid conductor combined with its image at depth h"
    # a' = sqrt(r * 2h)

    a_prime = np.sqrt(r_c * 2 * h)

    term1_R1 = np.log(2 * Lc / a_prime)
    term2_R1 = (k1 * Lc) / np.sqrt(Area)
    term3_R1 = k2

    R1 = (rho / (np.pi * Lc)) * (term1_R1 + term2_R1 - term3_R1)

    # 2. Rod Bed Resistance (R2)
    # R2 = (rho / (2 * pi * nr * Lr)) * (ln(4 * Lr / r_r) - 1 + (2 * k1 * Lr / sqrt(Area)) * (sqrt(nr) - 1)**2)

    term1_R2 = np.log(4 * Lr / r_r) - 1
    term2_R2 = (2 * k1 * Lr / np.sqrt(Area)) * (np.sqrt(nr) - 1)**2

    R2 = (rho / (2 * np.pi * nr * Lr)) * (term1_R2 + term2_R2)

    # 3. Mutual Resistance (Rm)
    # Rm = (rho / (pi * Lc)) * (ln(2 * Lc / Lr) + k1 * Lc / sqrt(Area) - k2 + 1)

    term1_Rm = np.log(2 * Lc / Lr)
    term2_Rm = (k1 * Lc) / np.sqrt(Area) # Same as R1
    term3_Rm = k2                        # Same as R1

    Rm = (rho / (np.pi * Lc)) * (term1_Rm + term2_Rm - term3_Rm + 1)

    # 4. Total Resistance (Rg)
    # Rg = (R1 * R2 - Rm**2) / (R1 + R2 - 2 * Rm)

    Rg = (R1 * R2 - Rm**2) / (R1 + R2 - 2 * Rm)

    print("-" * 30)
    print(f"Results (Schwarz):")
    print(f"  R1 (Grid): {R1:.4f} Ohms")
    print(f"  R2 (Rods): {R2:.4f} Ohms")
    print(f"  Rm (Mutual): {Rm:.4f} Ohms")
    print(f"  Rg (Total): {Rg:.4f} Ohms")

    return Rg

if __name__ == "__main__":
    calculate_schwarz()
