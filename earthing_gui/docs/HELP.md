# User Manual (HELP.md)

## Getting Started

1.  **Launch the App**: Run `python run_gui.py`.
2.  **Set Language**: Use the **File** menu to switch between English and Polish.

## Toolbox (Drawing)

*   **Select**: Click to select objects. Drag to box-select multiple objects.
    *   **Right-Click Drag**: Pan the view.
    *   **Mouse Wheel**: Zoom in/out (centered on cursor).
    *   **Ctrl+C / Ctrl+V**: Copy and Paste selected objects.
    *   **Delete**: Delete selected objects.
*   **Strip (Bednarka/Drut)**: Click to start, click to add points. Double-click or Right-click to finish.
    *   *Properties*: Change "Profile Type" to switch between Flat Tape and Round Wire.
*   **Rod (Pręt)**: Click to place a vertical earth rod.
    *   *Properties*: Edit Diameter and Length.
*   **Mesh (Siatka)**: Drag to create a rectangular grid.
    *   *Actions*: Use "Explode Mesh" in properties to convert it into individual strips for fine editing.
*   **Plate (Płyta)**: Click to place a rectangular plate.
*   **Probe (Próbnik)**: Click anywhere on the canvas (after simulation) to see the potential (Voltage) at that point.

## Simulation & Results

1.  **Parameters**:
    *   **Resistivity (rho)**: Soil resistivity in Ohm-m.
    *   **Fault Current (Ig)**: The current flowing into the earth during a fault (Amps).
    *   **Discretization**: Step size for calculation. Smaller = more accurate but slower.
2.  **Safety Parameters (IEEE 80)**:
    *   **Fault Duration**: Time the fault persists (e.g., 0.5s).
    *   **Surface Layer**: Properties of the crushed rock/gravel layer (Rho and Thickness).
3.  **Running**: Click **Run Simulation**.
    *   Status "Generating..." -> "Solving..." -> "Done".
4.  **Results**:
    *   **Text**: Shows Resistance, GPR, and Safety Limits.
    *   **Plots**:
        *   *Surface Potential*: Voltage distribution map.
        *   *Touch Voltage*: Map showing where touch voltage exceeds safe limits.
        *   *Step Voltage*: Map showing step voltage risks.
        *   *Current Density*: 3D view showing which parts of the earthing carry the most current.
        *   *Geometry 3D*: Verification of the physical layout.

## Exporting

*   **Export Report**: Generates an HTML file containing all results and plots.
*   **Save/Load Model**: Saves your design to a `.json` file for later use.
