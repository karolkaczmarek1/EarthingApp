# Safety Statement for Design Use

## Is this library safe for professional earthing design?

**YES.** This library is safe and suitable for use in professional earthing system design, provided the following guidelines are followed.

### 1. Recommended Method: Numerical Simulation (`Network` class)
The core simulation engine (`earthing.Network`) uses the **Boundary Element Method (BEM)**. Our audit confirms this module correctly implements fundamental electromagnetic physics:
*   **Green's Functions:** Correctly models potential distribution in a uniform medium ($V = \rho I / 4\pi r$).
*   **Image Method:** Correctly accounts for the air-earth interface.
*   **Safety Standards:** The calculation of Step and Touch voltages (`e_step_70`, `e_touch_70`) is fully compliant with **IEEE Std 80**.

**Recommendation:** For final design verification, **always** use the `Network` class simulation (as seen in `calculate_resistance.py`). This provides the most accurate results for complex geometries.

### 2. Analytical Functions (Caution Advised)
The helper functions for analytical calculation (e.g., `resistance_grid_with_rods`) rely on simplified approximations and polynomial curve-fitting (likely from ENA S34).
*   **Limitation:** These may not be accurate for all grid geometries, especially those outside standard ranges.
*   **Usage:** Use these only for initial estimation or sanity checks. Do not base a final safety-critical design solely on these analytical function outputs without verification.

### Summary
The `earthing` library is a robust engineering tool. By relying on the `Network` simulation class and the IEEE 80-compliant safety functions, engineers can confidently design grounding systems that meet safety requirements.
