import tkinter as tk
from tkinter import ttk, messagebox
from .draw_objects import Rod, Strip, Mesh, Plate

class CanvasManager:
    def __init__(self, root, canvas, update_prop_callback=None):
        self.root = root
        self.canvas = canvas
        self.update_prop_callback = update_prop_callback

        self.scale = 20.0  # Pixels per meter
        self.offset_x = 400
        self.offset_y = 300
        self.grid_size = 1.0 # meters
        self.snap_enabled = True

        self.current_tool = "select"
        self.objects = [] # List of drawing objects
        self.selected_object = None

        # Temporary drawing state
        self.temp_item = None
        self.start_x = 0
        self.start_y = 0
        self.points = [] # For polyline

        # Pan/Zoom
        self.last_pan_x = 0
        self.last_pan_y = 0

        self.draw_grid()
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Double-Button-1>", self.on_double_click) # Finish polyline

        # Right click for panning or finishing polyline
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B3-Motion>", self.on_right_drag)

    def set_tool(self, tool):
        self.current_tool = tool
        self.reset_temp()
        self.deselect_all()
        self.refresh_objects()

    def set_snap(self, enabled):
        self.snap_enabled = enabled

    def set_grid_size(self, size):
        try:
            self.grid_size = float(size)
            self.draw_grid()
        except ValueError:
            pass

    def world_to_screen(self, wx, wy):
        sx = self.offset_x + wx * self.scale
        sy = self.offset_y - wy * self.scale # Y up in world, down in screen
        return sx, sy

    def screen_to_world(self, sx, sy):
        wx = (sx - self.offset_x) / self.scale
        wy = (self.offset_y - sy) / self.scale
        return wx, wy

    def snap(self, wx, wy):
        if not self.snap_enabled:
            return wx, wy
        return round(wx / self.grid_size) * self.grid_size, round(wy / self.grid_size) * self.grid_size

    def draw_grid(self):
        self.canvas.delete("grid")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10: w = 800
        if h < 10: h = 600

        # Center in world is 0,0
        # Determine range of visible world coordinates
        min_wx, max_wy = self.screen_to_world(0, 0)
        max_wx, min_wy = self.screen_to_world(w, h)

        start_x = int(min_wx / self.grid_size) * self.grid_size
        start_y = int(min_wy / self.grid_size) * self.grid_size

        # Vertical lines
        x = start_x
        while x <= max_wx + self.grid_size:
            sx, _ = self.world_to_screen(x, 0)
            self.canvas.create_line(sx, 0, sx, h, tag="grid", fill="#f0f0f0")
            x += self.grid_size

        # Horizontal lines
        y = start_y
        while y <= max_wy + self.grid_size:
            _, sy = self.world_to_screen(0, y)
            self.canvas.create_line(0, sy, w, sy, tag="grid", fill="#f0f0f0")
            y += self.grid_size

        # Draw axes
        cx, cy = self.world_to_screen(0,0)
        self.canvas.create_line(cx, 0, cx, h, tag="grid", fill="#d0d0d0", width=2)
        self.canvas.create_line(0, cy, w, cy, tag="grid", fill="#d0d0d0", width=2)

        self.canvas.tag_lower("grid")

    def reset_temp(self):
        self.canvas.delete("temp")
        self.points = []

    def on_click(self, event):
        wx, wy = self.screen_to_world(event.x, event.y)
        wx, wy = self.snap(wx, wy)

        if self.current_tool == "select":
            self.select_at(wx, wy)

        elif self.current_tool == "rod":
            self.objects.append(Rod(x=wx, y=wy))
            self.refresh_objects()

        elif self.current_tool == "strip":
            if not self.points:
                self.points.append((wx, wy))
            # Only add a new point if it's significantly different from the last fixed point
            # However, for the 'rubber band' effect, we need a tracking point.
            # My logic: points[0] is start. points[-1] is the moving point.
            # When we click, we want to fix the current tracking point and add a NEW tracking point.
            if len(self.points) >= 1:
                # Update the last point to be exactly where clicked (fixing it)
                self.points[-1] = (wx, wy)
                # Add a new tracking point that will move with mouse
                self.points.append((wx, wy))
            self.draw_temp_polyline()

        elif self.current_tool == "mesh":
            self.start_x, self.start_y = wx, wy
            self.points = [(wx, wy)] # Store start

        elif self.current_tool == "plate":
            self.objects.append(Plate(x=wx, y=wy))
            self.refresh_objects()

    def on_drag(self, event):
        wx, wy = self.screen_to_world(event.x, event.y)
        wx, wy = self.snap(wx, wy)

        if self.current_tool == "strip" and self.points:
            self.points[-1] = (wx, wy)
            self.draw_temp_polyline()

        elif self.current_tool == "mesh" and self.points:
            # Draw temp rectangle
            sx1, sy1 = self.world_to_screen(self.start_x, self.start_y)
            sx2, sy2 = self.world_to_screen(wx, wy)
            self.canvas.delete("temp")
            self.canvas.create_rectangle(sx1, sy1, sx2, sy2, outline="blue", dash=(2,2), tag="temp")

        elif self.current_tool == "select" and self.selected_object:
            # Simple move implementation
            if isinstance(self.selected_object, (Rod, Plate)):
                self.selected_object.x = wx
                self.selected_object.y = wy
            elif isinstance(self.selected_object, Mesh):
                # Move top-left corner
                self.selected_object.x = wx
                self.selected_object.y = wy
                # If we wanted to resize, we would need drag handles.
                # For now, just moving origin.
            self.refresh_objects()
            if self.update_prop_callback:
                self.update_prop_callback(self.selected_object)

    def on_release(self, event):
        wx, wy = self.screen_to_world(event.x, event.y)
        wx, wy = self.snap(wx, wy)

        if self.current_tool == "strip":
            if len(self.points) > 1:
                # Clicked to add a segment
                # If clicked on same spot, ignored by logic but we keep adding points
                # Actually, standard behavior: Click start, Move, Click next node.
                # So on release (click up), we confirm the point and prepare for next.
                # My implementation logic in on_click adds a point.
                pass

        elif self.current_tool == "mesh" and self.points:
            self.canvas.delete("temp")
            width = abs(wx - self.start_x)
            height = abs(wy - self.start_y)
            x = min(self.start_x, wx)
            y = min(self.start_y, wy)
            if width > 0 and height > 0:
                self.objects.append(Mesh(x=x, y=y, width=width, height=height))
                self.refresh_objects()
            self.points = []

    def on_double_click(self, event):
        if self.current_tool == "strip" and len(self.points) > 2:
            # Finish polyline
            # Remove the last tracking point if duplicate
            final_points = self.points[:-1]
            if len(final_points) >= 2:
                self.objects.append(Strip(points=final_points))
                self.refresh_objects()
            self.reset_temp()

    def on_right_click(self, event):
        if self.current_tool == "strip":
            self.on_double_click(event)
        else:
            self.last_pan_x = event.x
            self.last_pan_y = event.y

    def on_right_drag(self, event):
        dx = event.x - self.last_pan_x
        dy = event.y - self.last_pan_y
        self.offset_x += dx
        self.offset_y += dy
        self.last_pan_x = event.x
        self.last_pan_y = event.y
        self.draw_grid()
        self.refresh_objects()

    def draw_temp_polyline(self):
        self.canvas.delete("temp")
        screen_points = []
        for wx, wy in self.points:
            screen_points.extend(self.world_to_screen(wx, wy))
        if len(screen_points) >= 4:
            self.canvas.create_line(*screen_points, fill="blue", dash=(2,2), tag="temp")

    def refresh_objects(self):
        self.canvas.delete("object")
        for obj in self.objects:
            obj.draw(self.canvas, self)

    def select_at(self, wx, wy):
        self.deselect_all()
        for obj in reversed(self.objects):
            if obj.contains(wx, wy):
                obj.selected = True
                self.selected_object = obj
                if self.update_prop_callback:
                    self.update_prop_callback(obj)
                break
        self.refresh_objects()

    def deselect_all(self):
        for obj in self.objects:
            obj.selected = False
        self.selected_object = None
        if self.update_prop_callback:
            self.update_prop_callback(None)
