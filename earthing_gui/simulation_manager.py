
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
                ig = float(self.mw.ig_var.get())
                t_s = float(self.mw.ts_var.get())
                rho_s = float(self.mw.rhos_var.get())
                h_s = float(self.mw.hs_var.get())
            except ValueError:
                messagebox.showerror(t('error'), "Invalid Parameter Value")
                return

            self.mw.result_text.delete(1.0, tk.END)
            self.mw.result_text.insert(tk.END, t('generating') + "\n")
            self.mw.root.update()

            network = self.adapter.run(objects, rho, ig)
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

        # Tab 5: Geometry 3D
        frame5 = ttk.Frame(notebook)
        notebook.add(frame5, text=t('plot_geometry'))
        self.plot_geometry_3d_embedded(network, frame5)

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
        cbar = fig.colorbar(contour_plot, ax=ax)
        cbar.set_label('Voltage (V)')

        ax.set_title(t('plot_surface'))
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.grid(True, linestyle='--', alpha=0.5)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def plot_geometry_3d_embedded(self, network, parent):
        fig = plt.Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111, projection='3d')

        # Plot geometry similar to library logic
        from earthing import NetworkElementStrip, NetworkElementPipe, NetworkElementPlate
        from earthing import plot_cycler

        styler = plot_cycler()
        for subnet, style in zip(network.elements, styler):
            for element in subnet:
                if isinstance(element, NetworkElementStrip) \
                   or isinstance(element, NetworkElementPipe):
                    start = element.loc
                    end = element.loc_end
                    X = [start[0], end[0]]
                    Y = [start[1], end[1]]
                    Z = [start[2], end[2]]
                    ax.plot(X, Y, Z, **style, linewidth=2)
                if isinstance(element, NetworkElementPlate):
                    c1 = element.loc - element.w_cap*element.w/2 - element.h_cap*element.h/2
                    c2 = c1 + element.w_cap * element.w
                    c3 = c2 + element.h_cap * element.h
                    c4 = c3 - element.w_cap * element.w
                    X = [c1[0], c2[0], c3[0], c4[0], c1[0]]
                    Y = [c1[1], c2[1], c3[1], c4[1], c1[1]]
                    Z = [c1[2], c2[2], c3[2], c4[2], c1[2]]
                    ax.plot(X, Y, Z, **style, linewidth=2)

        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title(t('plot_geometry'))

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def plot_current_density(self, network, parent):
        fig = plt.Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111, projection='3d')

        X, Y, Z = [], [], []
        if network.descrete_elements:
            for element in network.descrete_elements:
                loc = element.loc
                X.append(loc[0])
                Y.append(loc[1])
                Z.append(loc[2])

            scat_plot = ax.scatter(X, Y, Z, c=network.I, s=10, cmap='inferno')
            cbar = fig.colorbar(scat_plot, ax=ax)
            cbar.set_label('Current (A)')

        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title(t('plot_current'))

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def plot_touch_voltage(self, network, parent):
        fig = plt.Figure(figsize=(5, 4), dpi=100)

        if network.Vg is None:
             xlim, ylim = self.calculate_bounds()
             network.solve_surface_potential_fast(grid=(50,50), xlim=xlim, ylim=ylim)

        gpr = network.gpr()
        if hasattr(gpr, '__iter__'):
             gpr = max(gpr)

        V_touch = gpr - network.Vg

        ax = fig.add_subplot(111)
        # Use more levels for better gradient
        contour_plot = ax.contourf(network.XX, network.YY, V_touch, 30, cmap="Reds")
        cbar = fig.colorbar(contour_plot, ax=ax)
        cbar.set_label('Voltage (V)')

        # Add safety limit contour if available
        limit = self.last_results.get('e_touch_limit')
        if limit:
            try:
                ax.contour(network.XX, network.YY, V_touch, levels=[limit], colors='blue', linewidths=2, linestyles='dashed')
                ax.text(network.XX[0,0], network.YY[0,0], f"Limit: {limit}V", color='blue')
            except: pass

        ax.set_title(t('plot_touch'))
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.grid(True, linestyle='--', alpha=0.5)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def plot_step_voltage(self, network, parent):
        fig = plt.Figure(figsize=(5, 4), dpi=100)

        if network.Vg is None:
             xlim, ylim = self.calculate_bounds()
             network.solve_surface_potential_fast(grid=(50,50), xlim=xlim, ylim=ylim)

        import numpy as np
        dx = network.XX[0,1] - network.XX[0,0]
        dy = network.YY[1,0] - network.YY[0,0]
        Vy, Vx = np.gradient(network.Vg, dy, dx)
        V_step = np.sqrt(Vx**2 + Vy**2) * 1.0

        ax = fig.add_subplot(111)
        contour_plot = ax.contourf(network.XX, network.YY, V_step, 30, cmap="Oranges")
        cbar = fig.colorbar(contour_plot, ax=ax)
        cbar.set_label('Voltage (V)')

        limit = self.last_results.get('e_step_limit')
        if limit:
            try:
                ax.contour(network.XX, network.YY, V_step, levels=[limit], colors='blue', linewidths=2, linestyles='dashed')
            except: pass

        ax.set_title(t('plot_step'))
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.grid(True, linestyle='--', alpha=0.5)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
