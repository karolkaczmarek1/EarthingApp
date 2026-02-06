
import numpy as np

def calculate_schwarz():
    """
    Calculate grounding resistance using IEEE Std 80 Schwarz Equations.
    """
    # Parameters
    rho = 100.0          # Resistivity (Ohm-m)

    # Grid Dimensions
    Lx = 120.0           # Length (m)
    Ly = 100.0           # Width (m)
    Area = Lx * Ly       # Area (m^2)

    # Grid Conductors
    dx = 15.0            # Spacing x (m)
    dy = 10.0            # Spacing y (m)

    # Number of lines
    nx = int(Lx / dx) + 1  # 9 lines of length Ly
    ny = int(Ly / dy) + 1  # 11 lines of length Lx

    # Total length of horizontal grid conductors (Lc)
    Lc = (nx * Ly) + (ny * Lx)

    h = 0.8              # Grid depth (m)
    d_c = 0.01           # Conductor diameter (m)
    r_c = d_c / 2.0      # Conductor radius (m)

    # Rods
    nr = 99              # Number of rods
    Lr = 6.0             # Length of single rod (m)
    d_r = 0.02           # Rod diameter (m)
    r_r = d_r / 2.0      # Rod radius (m)

    # -------------------------------------------------------------------------
    # Analytical Coefficients k1 and k2 (IEEE Std 80, Eq C.1 & C.2)
    # -------------------------------------------------------------------------
    # For a rectangular grid, k1 and k2 are functions of the length-to-width ratio.
    # L is the longer side, W is the shorter side.

    L_grid = max(Lx, Ly)
    W_grid = min(Lx, Ly)
    ratio = L_grid / W_grid

    # Analytical formulas (Curve-fitted from Schwarz's data)
    k1 = 1.43 - 0.05 * ratio
    k2 = 5.50 + 0.15 * ratio

    print(f"Parameters:")
    print(f"  Rho: {rho} Ohm-m")
    print(f"  Area: {Area} m^2 ({Lx}x{Ly})")
    print(f"  Grid Lc: {Lc} m")
    print(f"  Depth h: {h} m")
    print(f"  Rods nr: {nr}, Length: {Lr} m")
    print(f"  Aspect Ratio (L/W): {ratio:.2f}")
    print(f"  Coefficients (Analytical IEEE 80):")
    print(f"    k1 = {k1:.4f}")
    print(f"    k2 = {k2:.4f}")

    # -------------------------------------------------------------------------
    # Schwarz Equations
    # -------------------------------------------------------------------------

    # 1. Grid Resistance (R1) - IEEE 80 Eq 32 (modified for Schwarz)
    # R1 = (rho / (pi * Lc)) * (ln(2*Lc / a') + k1 * Lc / sqrt(A) - k2)
    #
    # a' is the geometric mean radius of the grid conductor at depth h.
    # a' = sqrt(r * 2h)  (for conductors buried at depth h)

    a_prime = np.sqrt(r_c * 2 * h)

    term1_R1 = np.log(2 * Lc / a_prime)
    term2_R1 = (k1 * Lc) / np.sqrt(Area)
    term3_R1 = k2

    R1 = (rho / (np.pi * Lc)) * (term1_R1 + term2_R1 - term3_R1)

    # 2. Rod Bed Resistance (R2) - IEEE 80 Eq 33
    # R2 = (rho / (2 * pi * nr * Lr)) * (ln(4 * Lr / b) - 1 + (2 * k1 * Lr / sqrt(A)) * (sqrt(nr) - 1)^2)
    # b is the radius of the rod (r_r)

    term1_R2 = np.log(4 * Lr / r_r) - 1
    term2_R2 = (2 * k1 * Lr / np.sqrt(Area)) * (np.sqrt(nr) - 1)**2

    R2 = (rho / (2 * np.pi * nr * Lr)) * (term1_R2 + term2_R2)

    # 3. Mutual Resistance (Rm) - IEEE 80 Eq 34
    # Rm = (rho / (pi * Lc)) * (ln(2 * Lc / Lr) + k1 * Lc / sqrt(A) - k2 + 1)

    term1_Rm = np.log(2 * Lc / Lr)
    term2_Rm = (k1 * Lc) / np.sqrt(Area) # Same as in R1
    term3_Rm = k2                        # Same as in R1

    Rm = (rho / (np.pi * Lc)) * (term1_Rm + term2_Rm - term3_Rm + 1)

    # 4. Total Resistance (Rg) - IEEE 80 Eq 35
    # Rg = (R1 * R2 - Rm^2) / (R1 + R2 - 2 * Rm)

    Rg = (R1 * R2 - Rm**2) / (R1 + R2 - 2 * Rm)

    print("-" * 30)
    print(f"Results (Schwarz Method):")
    print(f"  R1 (Grid Resistance): {R1:.4f} Ohms")
    print(f"  R2 (Rod Bed Resistance): {R2:.4f} Ohms")
    print(f"  Rm (Mutual Resistance): {Rm:.4f} Ohms")
    print(f"  Rg (Total Resistance): {Rg:.4f} Ohms")

    return Rg

if __name__ == "__main__":
    calculate_schwarz()
