import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from .translations import current_translator, t
from .canvas_manager import CanvasManager
from .simulation_manager import SimulationManager
from .exporter import export_html

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title(t('app_title'))
        self.sim_manager = SimulationManager(self)
        self.root.geometry("1200x800")

        self.current_lang = 'pl'
        current_translator.set_language(self.current_lang)

        self.setup_ui()

    def setup_ui(self):
        # Top Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=t('file'), menu=file_menu)
        file_menu.add_command(label=t('export'), command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label=t('switch_lang'), command=self.toggle_language)

        # Main Layout
        # Left: Toolbox
        # Center: Canvas
        # Right: Properties & Results

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Toolbox
        toolbox_frame = ttk.LabelFrame(main_frame, text=t('tools'), width=150)
        toolbox_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.tool_var = tk.StringVar(value="select")

        tools = [
            ("select", t('select')),
            ("strip", t('strip')),
            ("rod", t('rod')),
            ("mesh", t('mesh')),
            ("plate", t('plate')),
        ]

        for key, label in tools:
            rb = ttk.Radiobutton(toolbox_frame, text=label, variable=self.tool_var, value=key,
                                 command=self.on_tool_change)
            rb.pack(anchor=tk.W, padx=5, pady=2)

        ttk.Separator(toolbox_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        # Grid settings in toolbox
        ttk.Label(toolbox_frame, text=t('grid_step')).pack(anchor=tk.W, padx=5)
        self.grid_step_var = tk.StringVar(value="1.0")
        entry = ttk.Entry(toolbox_frame, textvariable=self.grid_step_var, width=10)
        entry.pack(padx=5, pady=2)
        entry.bind("<Return>", self.update_grid)
        entry.bind("<FocusOut>", self.update_grid)

        self.snap_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(toolbox_frame, text=t('snap_to_grid'), variable=self.snap_var,
                        command=self.update_snap).pack(anchor=tk.W, padx=5)

        ttk.Button(toolbox_frame, text=t('clear'), command=self.clear_all).pack(fill=tk.X, padx=5, pady=10)

        # Canvas Area
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(canvas_frame, bg="white")
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)

        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas_manager = CanvasManager(self.root, self.canvas, self.update_properties_panel)
        self.canvas.bind("<Configure>", lambda e: self.canvas_manager.draw_grid())

        # Right Panel
        right_panel = ttk.Frame(main_frame, width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        # Properties
        prop_frame = ttk.LabelFrame(right_panel, text=t('properties'))
        prop_frame.pack(fill=tk.X, pady=5)
        self.prop_container = ttk.Frame(prop_frame)
        self.prop_container.pack(fill=tk.BOTH, padx=5, pady=5)

        ttk.Label(self.prop_container, text="No selection").pack()

        # Simulation
        sim_frame = ttk.LabelFrame(right_panel, text=t('simulate'))
        sim_frame.pack(fill=tk.X, pady=10)

        # Global Rho Setting
        rho_frame = ttk.Frame(sim_frame)
        rho_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(rho_frame, text=t('resistivity')).pack(anchor=tk.W)
        self.rho_var = tk.StringVar(value="100.0")
        ttk.Entry(rho_frame, textvariable=self.rho_var).pack(fill=tk.X)

        ttk.Button(sim_frame, text=t('run'), command=self.run_simulation).pack(fill=tk.X, padx=5, pady=5)

        # Results area
        res_frame = ttk.LabelFrame(right_panel, text=t('results'))
        res_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.result_text = tk.Text(res_frame, height=10, width=30)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def on_tool_change(self):
        self.canvas_manager.set_tool(self.tool_var.get())

    def update_grid(self, event=None):
        self.canvas_manager.set_grid_size(self.grid_step_var.get())

    def update_snap(self):
        self.canvas_manager.set_snap(self.snap_var.get())

    def toggle_language(self):
        new_lang = 'en' if self.current_lang == 'pl' else 'pl'
        self.current_lang = new_lang
        current_translator.set_language(new_lang)
        # Re-create UI to update text (simpler than updating all labels)
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_ui()

    def export_report(self):
        self.sim_manager.export_data()

    def run_simulation(self):
        self.sim_manager.run()

    def clear_all(self):
        self.canvas_manager.objects = []
        self.canvas_manager.refresh_objects()
        self.update_properties_panel(None)

    def update_properties_panel(self, obj):
        # Clear existing
        for widget in self.prop_container.winfo_children():
            widget.destroy()

        if not obj:
            ttk.Label(self.prop_container, text="No selection").pack()
            return

        # Create fields
        props = obj.get_properties()
        self.prop_entries = {}

        row = 0
        for key, value in props.items():
            # Translate label if possible
            label_text = t(key) if t(key) != key else key.capitalize()

            ttk.Label(self.prop_container, text=label_text).grid(row=row, column=0, padx=2, pady=2, sticky=tk.W)

            var = tk.StringVar(value=str(value))
            entry = ttk.Entry(self.prop_container, textvariable=var)
            entry.grid(row=row, column=1, padx=2, pady=2, sticky=tk.EW)

            # Bind update
            entry.bind("<Return>", lambda e, k=key, v=var: self.apply_property(k, v.get()))
            entry.bind("<FocusOut>", lambda e, k=key, v=var: self.apply_property(k, v.get()))

            self.prop_entries[key] = var
            row += 1

        ttk.Button(self.prop_container, text=t('delete'), command=self.delete_selected).grid(row=row, column=0, columnspan=2, pady=10)

    def apply_property(self, key, value):
        if self.canvas_manager.selected_object:
            try:
                self.canvas_manager.selected_object.set_property(key, value)
                self.canvas_manager.refresh_objects()
            except Exception as e:
                print(f"Error setting property: {e}")

    def delete_selected(self):
        if self.canvas_manager.selected_object:
            self.canvas_manager.objects.remove(self.canvas_manager.selected_object)
            self.canvas_manager.deselect_all()
            self.canvas_manager.refresh_objects()
