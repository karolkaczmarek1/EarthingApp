# Earthing Design GUI Tool

A standalone Graphical User Interface (GUI) for the `earthing` Python library, designed for electrical engineers to model, simulate, and analyze earthing systems.

## Features

*   **CAD-like Drawing**: Interactive canvas with Zoom, Pan, Snap-to-Grid, and Box Selection.
*   **Drawing Tools**:
    *   **Strip**: Create flat tapes ("Bednarka") or round wires ("Drut") with configurable dimensions.
    *   **Rod**: Place vertical earth rods with specific length and diameter.
    *   **Mesh**: Automatically generate grid meshes with options to "Explode" into individual strips.
    *   **Plate**: Add rectangular earthing plates.
*   **Simulation**:
    *   Calculates Total Resistance ($R_g$) and Ground Potential Rise (GPR).
    *   Performs IEEE 80 safety analysis (Touch and Step Voltages).
    *   Visualizes Surface Potential, Touch/Step Voltage Maps, and Current Density in 3D.
*   **Safety Analysis**: Auto-calculates $E_{touch}$ and $E_{step}$ limits based on user-provided Fault Duration and Surface Layer parameters.
*   **Import/Export**: Save designs to JSON and export comprehensive HTML reports.
*   **Localization**: Full support for English and Polish.

## Installation

1.  Ensure you have Python 3.8+ installed.
2.  Install dependencies:
    ```bash
    pip install numpy matplotlib
    # tkinter is usually included with Python, on Linux you might need: sudo apt-get install python3-tk
    ```

## Usage

### Running the GUI
Run the startup script from the root directory:
```bash
python3 run_gui.py
```

### Running Headless Simulation
You can run a simulation from a saved JSON model file without the GUI:
```bash
python3 run_simulation.py my_model.json
```

## Documentation
*   [User Manual (HELP.md)](HELP.md)
*   [Developer/Agent Guide (AGENTS.md)](AGENTS.md)
*   [Product Requirements (PRD.md)](PRD.md)
