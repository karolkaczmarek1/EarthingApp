# Product Requirements Document (PRD)

## Project Overview
A standalone GUI tool for designing earthing systems, aimed at electrical engineers.

## Functional Requirements

### 1. Drawing & Modeling
*   [x] **Canvas**: Infinite 2D canvas with grid and snap-to-grid.
*   [x] **Navigation**: Zoom (Mouse Wheel), Pan (Right-Click Drag).
*   [x] **Tools**:
    *   Strip (Polyline): Support Flat (30x4mm) and Round (d=6mm) profiles.
    *   Rod (Point): Configurable Diameter and Length.
    *   Mesh (Rectangle): Auto-generated grid.
    *   Plate (Rectangle).
*   [x] **Editing**:
    *   Select, Move (Drag), Delete.
    *   Copy/Paste (Ctrl+C/V).
    *   Format Painter (Copy properties).
    *   Explode Mesh (Convert grid to strips).
*   [x] **Properties**: Side panel to edit dimensions, depth, and material properties.

### 2. Simulation
*   [x] **Engine**: Integration with `earthing` Python library (BEM method).
*   [x] **Parameters**:
    *   Global Soil Resistivity ($\rho$).
    *   Fault Current ($I_g$).
    *   Discretization Step (validation included).
*   [x] **Robustness**: Auto-adjustment of simulation mesh for small elements.

### 3. Analysis & Results
*   [x] **Calculations**: Total Resistance, Ground Potential Rise (GPR).
*   [x] **Safety Analysis (IEEE 80)**:
    *   Calculate $E_{touch}$ and $E_{step}$ limits based on $t_s$, $\rho_s$, $h_s$.
    *   Compare simulated values against limits.
*   [x] **Visualization**:
    *   2D Heatmaps: Surface Potential, Touch Voltage, Step Voltage.
    *   3D Plots: Current Density, Geometry.
    *   Probe Tool: Query voltage at point.

### 4. Data Management
*   [x] **Persistence**: Save/Load models as JSON.
*   [x] **Export**: Generate HTML reports with embedded plots.
*   [x] **Headless Mode**: Run simulations from CLI using JSON models.

### 5. Non-Functional
*   [x] **Localization**: English and Polish.
*   [x] **Dependencies**: Minimal (numpy, matplotlib, tkinter).
