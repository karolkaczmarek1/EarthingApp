
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

    # Grid Counts (from Image)
    Nx = 11
    Ny = 9

    # Spacing
    dx = Lx / (Nx - 1)
    dy = Ly / (Ny - 1)

    # Total length of horizontal grid conductors (Lc)
    # Nx lines of length Ly + Ny lines of length Lx
    Lc = (Nx * Ly) + (Ny * Lx)

    h = 0.8              # Grid depth (m)

    # Conductor: Strip 25mm
    w = 0.025
    # Equivalent diameter for strip
    # IEEE Std 80-2000, Table 1: d = 2*w/pi?
    # Or simplified d = w/2.
    # IEEE 80 Eq 32 for a' (Geometric Mean Radius):
    # a' = sqrt(d*h) for round wire? No, a' = sqrt(r*2h).
    # For strip, the equivalent diameter d_eff is often taken as w/2.
    # Let's use d_c = w / 2 for the diameter approximation in the logarithmic term.

    d_c = w / 2.0        # Equivalent diameter (approx)
    r_c = d_c / 2.0      # Equivalent radius

    # Rods
    nr = Nx * Ny         # 99 rods
    Lr = 6.0             # Length of single rod (m)
    d_r = 0.02           # Rod diameter (m)
    r_r = d_r / 2.0      # Rod radius (m)

    # -------------------------------------------------------------------------
    # Analytical Coefficients k1 and k2 (IEEE Std 80, Eq C.1 & C.2)
    # -------------------------------------------------------------------------
    L_grid = max(Lx, Ly)
    W_grid = min(Lx, Ly)
    ratio = L_grid / W_grid

    k1 = 1.43 - 0.05 * ratio
    k2 = 5.50 + 0.15 * ratio

    print(f"Parameters:")
    print(f"  Rho: {rho} Ohm-m")
    print(f"  Area: {Area} m^2 ({Lx}x{Ly})")
    print(f"  Grid Lc: {Lc} m")
    print(f"  Depth h: {h} m")
    print(f"  Conductor: Strip w={w}m (Equiv d={d_c}m)")
    print(f"  Rods nr: {nr}, Length: {Lr} m")
    print(f"  Aspect Ratio (L/W): {ratio:.2f}")
    print(f"  Coefficients (Analytical IEEE 80):")
    print(f"    k1 = {k1:.4f}")
    print(f"    k2 = {k2:.4f}")

    # -------------------------------------------------------------------------
    # Schwarz Equations
    # -------------------------------------------------------------------------

    # 1. Grid Resistance (R1)
    # a' = sqrt(r_c * 2 * h)
    a_prime = np.sqrt(r_c * 2 * h)

    term1_R1 = np.log(2 * Lc / a_prime)
    term2_R1 = (k1 * Lc) / np.sqrt(Area)
    term3_R1 = k2

    R1 = (rho / (np.pi * Lc)) * (term1_R1 + term2_R1 - term3_R1)

    # 2. Rod Bed Resistance (R2)
    term1_R2 = np.log(4 * Lr / r_r) - 1
    term2_R2 = (2 * k1 * Lr / np.sqrt(Area)) * (np.sqrt(nr) - 1)**2

    R2 = (rho / (2 * np.pi * nr * Lr)) * (term1_R2 + term2_R2)

    # 3. Mutual Resistance (Rm)
    term1_Rm = np.log(2 * Lc / Lr)
    term2_Rm = (k1 * Lc) / np.sqrt(Area)
    term3_Rm = k2

    Rm = (rho / (np.pi * Lc)) * (term1_Rm + term2_Rm - term3_Rm + 1)

    # 4. Total Resistance (Rg)
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
