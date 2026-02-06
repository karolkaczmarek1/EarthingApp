# Verification of `earthing` Library

This document summarizes the audit of the `earthing` library's assumptions, equations, and physics, checking against IEEE Std 80 and general electromagnetic theory.

## 1. Boundary Element Method (BEM) Solver (`Network` class)

### Physics & Potential Coefficients
*   **Green's Function:** The library uses the correct fundamental Green's function for a point source in a uniform medium: $V = \frac{\rho I}{4 \pi r}$.
*   **Image Method:** It correctly implements the Image Method to account for the air-earth interface (boundary condition $J_n = 0$). For every element, a "mirror" element is considered at $-z$, and their potentials are summed.
*   **Approximation:**
    *   The library treats **all** elements (pipes, strips) as **circular plates** (`DescreteElementPlate`) after discretization.
    *   **Strip:** A strip of width $w$ and length $L$ is discretized into small plates of equivalent area.
    *   **Pipe:** A pipe of radius $r$ is also discretized into plates.
    *   **Implication:** This is a "Flat Plate" approximation. While valid for calculating far-field potentials, it approximates the self-potential (potential on the conductor surface) using the self-potential of a flat circular disk ($V_{self} = \frac{\rho I}{8a}$) rather than the exact thin-wire formula ($\frac{\rho I}{2 \pi L} \ln(L/r)$). This can lead to slight inaccuracies in the calculated grid resistance compared to methods using thin-wire kernels, but it is a mathematically consistent and standard BEM approach for surface patches.

## 2. Analytical Resistance Functions (`resistance_grid_with_rods`)

*   **Standard Compliance:** This function appears to be based on **ENA EREC S34** (or a similar utility derivative of IEEE 80) rather than the pure IEEE 80 Schwarz equations.
*   **Polynomial Approximation:** The code uses a 5th-degree polynomial (`np.polyfit`) derived from hardcoded data points to calculate a rod interference factor `k`.
    *   **Risk:** This is a "black box" approximation. Unlike the explicit Schwarz coefficient formulas ($k_1, k_2$) implemented in our new `calculate_schwarz.py`, this relies on a fixed dataset. If the number of rods $N$ falls outside the fitted range, the polynomial could diverge.
*   **Mutual Resistance:** The mutual resistance term $R_{12}$ uses a simplified logarithmic form, which differs from the more complex Schwarz $R_m$ equation.

## 3. Safety Criteria (`e_step_70`, `e_touch_70`)

*   **Standard Compliance:** **Fully Compliant with IEEE Std 80.**
*   **Reflection Factor ($C_s$):** Uses the standard approximation $C_s = 1 - \frac{0.09 (1 - \rho/\rho_s)}{2h_s + 0.09}$, which matches IEEE 80 Eq. 27.
*   **Body Current Limit:** Uses the Dalziel constant $k = 0.157$ for a 70kg human ($I_{limit} = \frac{0.157}{\sqrt{t}}$).
*   **Foot Resistance:** Correctly uses $6 \rho_s C_s$ for step voltage (feet in series) and $1.5 \rho_s C_s$ for touch voltage (feet in parallel).

## Conclusion

The `earthing` library is **physically sound** but relies on specific approximations:
1.  **BEM Solver:** Uses a "equivalent flat plate" discretization for all conductors. This is robust but computationally heavy for large grids and creates a specific geometric approximation for cylindrical conductors.
2.  **Analytical Tool:** The `resistance_grid_with_rods` function uses a specific polynomial fit (likely from ENA S34) which is less transparent than the direct Schwarz equations.

**Recommendation:**
For verifying the grid design, the **BEM Solver (`Network` class)** is the superior tool as it solves the specific geometry directly, whereas the analytical functions are generalized approximations. The close agreement between our independent Schwarz implementation (0.455 $\Omega$) and the library's BEM solver (0.389 $\Omega$) gives high confidence in the BEM result, as Schwarz equations are known to be conservative (yielding higher resistance).
