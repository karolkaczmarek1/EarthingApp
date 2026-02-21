# Developer & Agent Guidelines (AGENTS.md)

This document provides context for AI agents and developers modifying the `earthing_gui` codebase.

## Architecture Overview

The application is structured into the following modules:

*   **`main_window.py`**: The entry point for the UI. Manages the `tkinter` root, layout, menus, and coordinates interaction between the canvas and simulation manager. **Crucial**: Initializes `CanvasManager` before creating UI elements that bind to it.
*   **`canvas_manager.py`**: Handles all 2D drawing logic, event binding (mouse/keyboard), coordinate transformation (World <-> Screen), and tool state (Select, Strip, Rod, etc.).
*   **`draw_objects.py`**: Dataclasses representing the graphical elements (`Rod`, `Strip`, `Mesh`, `Plate`). These store geometric properties (x, y) and physical properties (radius, profile_type, depth). **Note**: Do NOT add a `type` field to these classes; `isinstance` is used for type checking.
*   **`simulation_manager.py`**: Orchestrates the simulation workflow. Validates inputs from the GUI, calls the adapter, and handles plotting of results (using `matplotlib` embedded in `tkinter`).
*   **`simulation_adapter.py`**: The bridge between the GUI objects and the `earthing` library.
    *   **Logic**: Iterates over `DrawObject`s and calls `network.add_rod`, `network.add_strip`, etc.
    *   **Round Wires**: Uses `NetworkElementPipe` explicitly for 'round' profile strips because `add_strip` defaults to flat tape.
    *   **Robustness**: Dynamically adjusts discretization step (`desc_size`) to prevent singularities with small elements.
*   **`file_handler.py`**: Handles JSON serialization/deserialization of the model.
*   **`exporter.py`**: Generates HTML reports.

## Key Patterns

*   **Coordinate System**:
    *   **World**: Meters (float). Y-axis increases Up.
    *   **Screen**: Pixels (int). Y-axis increases Down.
    *   `CanvasManager` handles `world_to_screen` and `screen_to_world`.
*   **Property Editing**:
    *   Properties are auto-committed using `tk.StringVar().trace_add`.
    *   The property panel is dynamically rebuilt based on `obj.get_properties()`.
*   **Localization**:
    *   All UI strings must use `t('key')` from `translations.py`.

## Testing

*   **Headless Tests**: Located in `tests/test_geometry_stress.py`. Always run these after changing simulation logic.
*   **Manual Verification**: Check tool switching, zooming, and saving/loading after major refactors.

## Known Limitations

*   **Earthing Library**: The underlying `earthing` library calculates interactions using BEM. It requires $O(N^2)$ memory/time. Very dense meshes may be slow.
*   **Discretization**: Elements smaller than the discretization step can cause division-by-zero errors in the library. The `SimulationAdapter` attempts to mitigate this, but users should be warned via the GUI validator.
