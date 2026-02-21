import argparse
import sys
import os
from earthing_gui.file_handler import load_from_json
from earthing_gui.simulation_adapter import SimulationAdapter
from earthing import e_touch_70, e_step_70

def main():
    parser = argparse.ArgumentParser(description="Run Earthing Simulation from JSON model")
    parser.add_argument("model_file", help="Path to the JSON model file")
    args = parser.parse_args()

    if not os.path.exists(args.model_file):
        print(f"Error: File {args.model_file} not found.")
        sys.exit(1)

    print(f"Loading model from {args.model_file}...")
    objects, params = load_from_json(args.model_file)

    if objects is None:
        print("Error loading model.")
        sys.exit(1)

    if not objects:
        print("Warning: No objects in model.")

    print("Running simulation...")

    # Extract parameters with defaults
    rho = float(params.get('rho', 100.0))
    ig = float(params.get('ig', 1000.0))
    t_s = float(params.get('t_s', 0.5))
    rho_s = float(params.get('rho_s', 2500.0))
    h_s = float(params.get('h_s', 0.1))

    adapter = SimulationAdapter()
    try:
        network = adapter.run(objects, rho, ig)

        res = network.get_resistance()
        gpr = network.gpr()
        if hasattr(gpr, '__iter__'):
            gpr_val = max(gpr)
        else:
            gpr_val = gpr

        e_touch_limit = e_touch_70(rho, rho_s, h_s, t_s)
        e_step_limit = e_step_70(rho, rho_s, h_s, t_s)

        print("\n" + "="*30)
        print("SIMULATION RESULTS")
        print("="*30)
        print(f"Total Resistance: {res} Ohm")
        print(f"GPR: {gpr_val:.2f} V")
        print("-" * 20)
        print("Safety Limits (IEEE 80):")
        print(f"E_touch Limit: {e_touch_limit:.2f} V")
        print(f"E_step Limit: {e_step_limit:.2f} V")
        print("="*30 + "\n")

    except Exception as e:
        print(f"Simulation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
