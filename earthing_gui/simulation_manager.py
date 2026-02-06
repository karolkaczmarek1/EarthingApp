
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .translations import t
from .simulation_adapter import SimulationAdapter
from .exporter import export_html
from .draw_objects import Rod, Strip, Mesh, Plate

class SimulationManager:
    def __init__(self, main_window):
        self.mw = main_window
        self.adapter = SimulationAdapter()
        self.last_network = None
        self.last_results = {}

    def export_data(self):
        export_html(self.mw.root, self.last_results, self.last_network)

    def run(self):
        objects = self.mw.canvas_manager.objects
        if not objects:
            messagebox.showwarning(t('app_title'), "No objects to simulate.")
            return

        try:
            # Get Global Rho
            try:
                rho = float(self.mw.rho_var.get())
            except ValueError:
                messagebox.showerror(t('error'), "Invalid Resistivity Value")
                return

            self.mw.result_text.delete(1.0, tk.END)
            self.mw.result_text.insert(tk.END, t('generating') + "\n")
            self.mw.root.update()

            network = self.adapter.run(objects, rho)
            self.last_network = network

            self.mw.result_text.insert(tk.END, t('solving') + "\n")
            self.mw.root.update()

            res = network.get_resistance()
            gpr = network.gpr()

            self.last_results = {
                'resistance': res,
                'gpr': gpr
            }

            self.mw.result_text.insert(tk.END, f"{t('resistance')}: {res} Ohm\n")
            self.mw.result_text.insert(tk.END, f"{t('gpr')}: {gpr} V\n")
            self.mw.result_text.insert(tk.END, t('done') + "\n")

            self.show_plots(network)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.mw.result_text.insert(tk.END, f"{t('error')}: {str(e)}\n")
            messagebox.showerror(t('error'), str(e))

    def show_plots(self, network):
        plot_window = tk.Toplevel(self.mw.root)
        plot_window.title(t('results'))
        plot_window.geometry("800x600")

        notebook = ttk.Notebook(plot_window)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Surface Potential (2D)
        frame1 = ttk.Frame(notebook)
        notebook.add(frame1, text=t('plot_surface'))

        self.plot_surface_potential(network, frame1)

    def calculate_bounds(self):
        objects = self.mw.canvas_manager.objects
        if not objects:
            return (-20, 20), (-20, 20)

        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')

        found = False
        for obj in objects:
            if isinstance(obj, Rod):
                min_x = min(min_x, obj.x)
                max_x = max(max_x, obj.x)
                min_y = min(min_y, obj.y)
                max_y = max(max_y, obj.y)
                found = True
            elif isinstance(obj, Plate):
                min_x = min(min_x, obj.x - obj.width/2)
                max_x = max(max_x, obj.x + obj.width/2)
                min_y = min(min_y, obj.y - obj.height/2)
                max_y = max(max_y, obj.y + obj.height/2)
                found = True
            elif isinstance(obj, Mesh):
                min_x = min(min_x, obj.x)
                max_x = max(max_x, obj.x + obj.width)
                min_y = min(min_y, obj.y)
                max_y = max(max_y, obj.y + obj.height)
                found = True
            elif isinstance(obj, Strip):
                for px, py in obj.points:
                    min_x = min(min_x, px)
                    max_x = max(max_x, px)
                    min_y = min(min_y, py)
                    max_y = max(max_y, py)
                if obj.points:
                    found = True

        if not found:
            return (-20, 20), (-20, 20)

        # Add margin
        margin_x = max(5, (max_x - min_x) * 0.2)
        margin_y = max(5, (max_y - min_y) * 0.2)

        return (min_x - margin_x, max_x + margin_x), (min_y - margin_y, max_y + margin_y)

    def plot_surface_potential(self, network, parent):
        fig = plt.Figure(figsize=(5, 4), dpi=100)

        xlim, ylim = self.calculate_bounds()

        # Calculate grid size roughly to have reasonable resolution but not too slow
        # Aim for e.g. 50x50
        network.solve_surface_potential_fast(grid=(50,50), xlim=xlim, ylim=ylim)

        ax = fig.add_subplot(111)

        XX = network.XX
        YY = network.YY
        V = network.Vg

        contour_plot = ax.contourf(XX, YY, V, 20, cmap="plasma")
        fig.colorbar(contour_plot, ax=ax)

        ax.set_title(t('plot_surface'))
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
