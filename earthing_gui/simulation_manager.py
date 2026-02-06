
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .translations import t
from .simulation_adapter import SimulationAdapter
from .exporter import export_html
from earthing import e_touch_70, e_step_70
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
                t_s = float(self.mw.ts_var.get())
                rho_s = float(self.mw.rhos_var.get())
                h_s = float(self.mw.hs_var.get())
            except ValueError:
                messagebox.showerror(t('error'), "Invalid Parameter Value")
                return

            self.mw.result_text.delete(1.0, tk.END)
            self.mw.result_text.insert(tk.END, t('generating') + "\n")
            self.mw.root.update()

            network = self.adapter.run(objects, rho)
            self.last_network = network

            self.mw.result_text.insert(tk.END, t('solving') + "\n")
            self.mw.root.update()

            res = network.get_resistance()
            gpr = network.gpr() # Usually array if multiple subnets
            # If multiple subnets, gpr() returns array. We take max for safety?
            # Or usually single connected grid.
            if hasattr(gpr, '__iter__'):
                gpr_val = max(gpr)
            else:
                gpr_val = gpr

            # Safety Limits
            e_touch_limit = e_touch_70(rho, rho_s, h_s, t_s)
            e_step_limit = e_step_70(rho, rho_s, h_s, t_s)

            self.last_results = {
                'resistance': res,
                'gpr': gpr_val,
                'e_touch_limit': round(e_touch_limit, 2),
                'e_step_limit': round(e_step_limit, 2)
            }

            self.mw.result_text.insert(tk.END, f"{t('resistance')}: {res} Ohm\n")
            self.mw.result_text.insert(tk.END, f"{t('gpr')}: {gpr_val} V\n")
            self.mw.result_text.insert(tk.END, "-"*20 + "\n")
            self.mw.result_text.insert(tk.END, f"{t('safety_limits')}\n")
            self.mw.result_text.insert(tk.END, f"{t('e_touch_limit')}: {round(e_touch_limit, 2)} V\n")
            self.mw.result_text.insert(tk.END, f"{t('e_step_limit')}: {round(e_step_limit, 2)} V\n")
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

        # Tab 2: Touch Voltage
        frame2 = ttk.Frame(notebook)
        notebook.add(frame2, text=t('plot_touch'))
        self.plot_touch_voltage(network, frame2)

        # Tab 3: Step Voltage
        frame3 = ttk.Frame(notebook)
        notebook.add(frame3, text=t('plot_step'))
        self.plot_step_voltage(network, frame3)

        # Tab 4: Current Density (3D)
        frame4 = ttk.Frame(notebook)
        notebook.add(frame4, text=t('plot_current'))
        self.plot_current_density(network, frame4)

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

    def plot_current_density(self, network, parent):
        fig = plt.Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111, projection='3d')

        # Plot problem geometry with current as weight
        # Based on network.plot_geometry_3d implementation
        X = []
        Y = []
        Z = []
        if network.descrete_elements:
            for slno, element in enumerate(network.descrete_elements):
                loc = element.loc
                X.append(loc[0])
                Y.append(loc[1])
                Z.append(loc[2])

            scat_plot = ax.scatter(X, Y, Z, c=network.I, s=5, cmap='viridis')
            fig.colorbar(scat_plot, ax=ax)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(t('plot_current'))

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def plot_touch_voltage(self, network, parent):
        fig = plt.Figure(figsize=(5, 4), dpi=100)

        # Touch Voltage ~= GPR - Surface Potential (simplified definition often used)
        # More accurately: V_touch = V_grid - V_surface_at_feet
        # Assuming V_grid is GPR of the main grid.

        # Ensure surface potential is solved (it was solved in plot_surface_potential call,
        # or we solve it again if that tab wasn't called?
        # Actually show_plots calls plot_surface_potential first which solves it.
        # But if we change order or make it lazy, we need to check.
        if network.Vg is None:
             xlim, ylim = self.calculate_bounds()
             network.solve_surface_potential_fast(grid=(50,50), xlim=xlim, ylim=ylim)

        gpr = network.gpr()
        if hasattr(gpr, '__iter__'):
             gpr = max(gpr)

        # V_touch map
        V_touch = gpr - network.Vg

        ax = fig.add_subplot(111)
        contour_plot = ax.contourf(network.XX, network.YY, V_touch, 20, cmap="Reds")
        fig.colorbar(contour_plot, ax=ax)

        ax.set_title(t('plot_touch'))
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def plot_step_voltage(self, network, parent):
        fig = plt.Figure(figsize=(5, 4), dpi=100)

        # Step Voltage: Max difference between points 1m apart.
        # Library has `step_voltage` function but it finds MAX in a polygon.
        # We want a map.
        # We can approximate step voltage map by taking gradient of Vg * 1m.
        # Grad V = (dV/dx, dV/dy). Step voltage ~= |Grad V| * 1m

        if network.Vg is None:
             xlim, ylim = self.calculate_bounds()
             network.solve_surface_potential_fast(grid=(50,50), xlim=xlim, ylim=ylim)

        import numpy as np
        # Calculate gradient
        # Vg is 2D array.
        # spacing depends on grid size and xlim.
        # network.XX is meshgrid.
        # dx = XX[0,1] - XX[0,0]
        dx = network.XX[0,1] - network.XX[0,0]
        dy = network.YY[1,0] - network.YY[0,0]

        Vy, Vx = np.gradient(network.Vg, dy, dx)
        V_step = np.sqrt(Vx**2 + Vy**2) * 1.0 # E field * 1m step

        ax = fig.add_subplot(111)
        contour_plot = ax.contourf(network.XX, network.YY, V_step, 20, cmap="Oranges")
        fig.colorbar(contour_plot, ax=ax)

        ax.set_title(t('plot_step'))
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
