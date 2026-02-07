
import tkinter as tk
from tkinter import ttk, messagebox
from .draw_objects import Rod, Strip, Mesh, Plate
import copy
import numpy as np

class CanvasManager:
    def __init__(self, root, canvas, update_prop_callback=None, probe_callback=None, cursor_callback=None):
        self.root = root
        self.canvas = canvas
        self.update_prop_callback = update_prop_callback
        self.probe_callback = probe_callback
        self.cursor_callback = cursor_callback

        self.scale = 20.0
        self.offset_x = 400
        self.offset_y = 300
        self.grid_size = 1.0
        self.snap_enabled = True

        self.current_tool = "select"
        self.objects = []
        self.selected_objects = [] # List of selected objects
        self.clipboard = [] # For copy/paste

        # Format Painter state
        self.format_source = None
        self.is_format_painting = False

        # Drawing state
        self.start_x = 0
        self.start_y = 0
        self.points = []
        self.is_panning = False
        self.last_pan_x = 0
        self.last_pan_y = 0

        # Selection Box state
        self.box_start_x = 0
        self.box_start_y = 0
        self.is_selecting_box = False

        self.draw_grid()
        self.bind_events()

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.on_left_down)
        self.canvas.bind("<B1-Motion>", self.on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_up)

        self.canvas.bind("<Button-3>", self.on_right_down)
        self.canvas.bind("<B3-Motion>", self.on_right_drag)
        self.canvas.bind("<ButtonRelease-3>", self.on_right_up)

        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<Motion>", self.on_motion)

        # Zoom
        self.canvas.bind("<MouseWheel>", self.on_zoom) # Windows
        self.canvas.bind("<Button-4>", self.on_zoom) # Linux Scroll Up
        self.canvas.bind("<Button-5>", self.on_zoom) # Linux Scroll Down

    def set_tool(self, tool):
        self.current_tool = tool
        self.reset_temp()
        self.deselect_all()
        self.refresh_objects()
        # Change cursor based on tool
        if tool == "select":
            self.canvas.config(cursor="arrow")
        else:
            self.canvas.config(cursor="crosshair")

    def world_to_screen(self, wx, wy):
        sx = self.offset_x + wx * self.scale
        sy = self.offset_y - wy * self.scale
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

        min_wx, max_wy = self.screen_to_world(0, 0)
        max_wx, min_wy = self.screen_to_world(w, h)

        # Optimize grid drawing for large scales
        step = self.grid_size
        while step * self.scale < 10: # If grid lines are closer than 10px, double step
            step *= 2

        start_x = int(min_wx / step) * step
        start_y = int(min_wy / step) * step

        # Vertical lines
        x = start_x
        while x <= max_wx + step:
            sx, _ = self.world_to_screen(x, 0)
            self.canvas.create_line(sx, 0, sx, h, tag="grid", fill="#f0f0f0")
            x += step

        # Horizontal lines
        y = start_y
        while y <= max_wy + step:
            _, sy = self.world_to_screen(0, y)
            self.canvas.create_line(0, sy, w, sy, tag="grid", fill="#f0f0f0")
            y += step

        # Axes
        cx, cy = self.world_to_screen(0,0)
        self.canvas.create_line(cx, 0, cx, h, tag="grid", fill="#d0d0d0", width=2)
        self.canvas.create_line(0, cy, w, cy, tag="grid", fill="#d0d0d0", width=2)

        self.canvas.tag_lower("grid")

    def on_motion(self, event):
        wx, wy = self.screen_to_world(event.x, event.y)
        if self.cursor_callback:
            self.cursor_callback(wx, wy)

        # Optional: Highlight object under cursor
        # This would require expensive hit testing on every move.
        # Skip for performance unless requested.

    def on_zoom(self, event):
        # Zoom centered on cursor
        zoom_factor = 1.1
        if event.num == 5 or event.delta < 0:
            zoom_factor = 1.0 / zoom_factor

        old_scale = self.scale
        new_scale = old_scale * zoom_factor

        # Clamp scale
        if new_scale < 1.0: new_scale = 1.0
        if new_scale > 500.0: new_scale = 500.0

        if new_scale == old_scale: return

        # Adjust offset to keep mouse point stable
        # wx = (sx - off_x) / scale
        # sx = off_x + wx * scale
        # We want wx at event.x, event.y to remain same
        wx, wy = self.screen_to_world(event.x, event.y)

        self.scale = new_scale
        self.offset_x = event.x - wx * self.scale
        self.offset_y = event.y + wy * self.scale

        self.draw_grid()
        self.refresh_objects()
        if self.current_tool == "strip" and self.points:
            self.draw_temp_polyline()

    def on_right_down(self, event):
        self.is_panning = True
        self.last_pan_x = event.x
        self.last_pan_y = event.y

    def on_right_drag(self, event):
        if self.is_panning:
            dx = event.x - self.last_pan_x
            dy = event.y - self.last_pan_y
            self.offset_x += dx
            self.offset_y += dy
            self.last_pan_x = event.x
            self.last_pan_y = event.y
            self.draw_grid()
            self.refresh_objects()
            if self.current_tool == "strip" and self.points:
                self.draw_temp_polyline()

    def on_right_up(self, event):
        if self.is_panning:
            self.is_panning = False
            # If little movement, treat as Context Menu or Finish Polyline
            # For now, Finish Polyline if in strip tool
            if self.current_tool == "strip" and self.points:
                self.finish_polyline()

    def on_left_down(self, event):
        wx, wy = self.screen_to_world(event.x, event.y)
        snap_x, snap_y = self.snap(wx, wy)

        if self.current_tool == "select":
            # Format Painter Logic
            if self.is_format_painting and self.format_source:
                clicked = self.find_object_at(wx, wy)
                if clicked:
                    self.apply_format(self.format_source, clicked)
                    self.is_format_painting = False # Single shot? Or persistent? Let's say single shot for now.
                    self.deselect_all()
                    return

            # Selection Logic
            clicked = self.find_object_at(wx, wy)

            # Multi-select (Ctrl)
            # Not implemented fully yet (requires event.state check), assuming simple click for now
            # But let's support Drag Box if no object clicked
            if not clicked:
                self.deselect_all()
                self.is_selecting_box = True
                self.box_start_x = event.x
                self.box_start_y = event.y
            else:
                # Cycle selection or just select
                # If not selected, select it.
                if clicked not in self.selected_objects:
                    self.deselect_all()
                    clicked.selected = True
                    self.selected_objects = [clicked]
                # If already selected, maybe we want to drag it?
                # We handle drag in on_left_drag
                self.selected_object = clicked # Primary selection

            self.refresh_objects()
            self.notify_selection()

        elif self.current_tool == "rod":
            self.objects.append(Rod(x=snap_x, y=snap_y))
            self.refresh_objects()

        elif self.current_tool == "strip":
            if not self.points:
                self.points.append((snap_x, snap_y))
            if len(self.points) >= 1:
                self.points[-1] = (snap_x, snap_y)
                self.points.append((snap_x, snap_y))
            self.draw_temp_polyline()

        elif self.current_tool == "mesh":
            self.start_x, self.start_y = snap_x, snap_y
            self.points = [(snap_x, snap_y)]

        elif self.current_tool == "plate":
            self.objects.append(Plate(x=snap_x, y=snap_y))
            self.refresh_objects()

        elif self.current_tool == "probe":
            if self.probe_callback:
                self.probe_callback(snap_x, snap_y)

    def on_left_drag(self, event):
        wx, wy = self.screen_to_world(event.x, event.y)
        snap_x, snap_y = self.snap(wx, wy)

        if self.current_tool == "select":
            if self.is_selecting_box:
                # Draw selection box
                self.canvas.delete("sel_box")
                self.canvas.create_rectangle(self.box_start_x, self.box_start_y, event.x, event.y,
                                             outline="blue", dash=(2,2), tag="sel_box")
            elif self.selected_objects:
                # Move objects
                # Calculate delta from last position?
                # Need to store drag start position for objects.
                # Simplified: Just snap to cursor for the PRIMARY selected object,
                # others move relatively? Too complex for this iteration.
                # Let's implement Move for Single Object first correctly.
                if len(self.selected_objects) == 1:
                    obj = self.selected_objects[0]
                    if isinstance(obj, (Rod, Plate)):
                        obj.x, obj.y = snap_x, snap_y
                    elif isinstance(obj, Mesh):
                        obj.x, obj.y = snap_x, snap_y
                    # For Strip, we need to move points relative to start
                    # Complex. Let's skip drag-move for Strips/Multi for now or just primary.
                self.refresh_objects()
                self.notify_selection()

        elif self.current_tool == "strip" and self.points:
            self.points[-1] = (snap_x, snap_y)
            self.draw_temp_polyline()

        elif self.current_tool == "mesh" and self.points:
            sx1, sy1 = self.world_to_screen(self.start_x, self.start_y)
            sx2, sy2 = self.world_to_screen(snap_x, snap_y)
            self.canvas.delete("temp")
            self.canvas.create_rectangle(sx1, sy1, sx2, sy2, outline="blue", dash=(2,2), tag="temp")

    def on_left_up(self, event):
        wx, wy = self.screen_to_world(event.x, event.y)
        snap_x, snap_y = self.snap(wx, wy)

        if self.current_tool == "select":
            if self.is_selecting_box:
                self.canvas.delete("sel_box")
                self.is_selecting_box = False
                # Select objects inside box
                # Convert box to world coords
                wx1, wy1 = self.screen_to_world(self.box_start_x, self.box_start_y)
                wx2, wy2 = wx, wy
                x_min, x_max = min(wx1, wx2), max(wx1, wx2)
                y_min, y_max = min(wy1, wy2), max(wy1, wy2)

                self.deselect_all()
                for obj in self.objects:
                    # Simple center check or bounding box check
                    cx, cy = 0,0
                    if isinstance(obj, (Rod, Plate, Mesh)):
                        cx, cy = obj.x, obj.y
                    elif isinstance(obj, Strip):
                        if obj.points: cx, cy = obj.points[0] # Just start point check for now

                    if x_min <= cx <= x_max and y_min <= cy <= y_max:
                        obj.selected = True
                        self.selected_objects.append(obj)

                if self.selected_objects:
                    self.selected_object = self.selected_objects[0]
                self.refresh_objects()
                self.notify_selection()

        elif self.current_tool == "mesh" and self.points:
            self.canvas.delete("temp")
            width = abs(snap_x - self.start_x)
            height = abs(snap_y - self.start_y)
            x = min(self.start_x, snap_x)
            y = min(self.start_y, snap_y)
            if width > 0 and height > 0:
                self.objects.append(Mesh(x=x, y=y, width=width, height=height))
                self.refresh_objects()
            self.points = []

    def on_double_click(self, event):
        if self.current_tool == "strip":
            self.finish_polyline()

    def finish_polyline(self):
        if len(self.points) > 2:
            final_points = self.points[:-1]
            if len(final_points) >= 2:
                # Inherit properties from last strip if possible? No, defaults.
                self.objects.append(Strip(points=final_points))
                self.refresh_objects()
        self.reset_temp()

    def find_object_at(self, wx, wy):
        # Improved hit testing with cycling
        candidates = []
        for obj in self.objects:
            if obj.contains(wx, wy):
                candidates.append(obj)

        if not candidates: return None

        # If multiple, find one that isn't selected, or the next one after the currently selected
        # If currently selected is in candidates, return the next one in list (cycling)
        if self.selected_object in candidates:
            idx = candidates.index(self.selected_object)
            return candidates[(idx + 1) % len(candidates)]
        else:
            return candidates[-1] # Return top-most (last added)

    def deselect_all(self):
        for obj in self.objects:
            obj.selected = False
        self.selected_objects = []
        self.selected_object = None
        self.notify_selection()

    def notify_selection(self):
        if self.update_prop_callback:
            # If multiple, maybe pass the primary one, or a list?
            # Existing code expects single object or None
            self.update_prop_callback(self.selected_object)

    def copy_selection(self):
        self.clipboard = []
        for obj in self.selected_objects:
            # Deep copy data
            data = {
                'type': type(obj),
                'props': copy.deepcopy(obj.get_properties()),
                'points': copy.deepcopy(obj.points) if isinstance(obj, Strip) else None
            }
            self.clipboard.append(data)

    def paste_selection(self):
        if not self.clipboard: return
        self.deselect_all()
        offset = 1.0 # Offset pasted objects
        for item in self.clipboard:
            cls = item['type']
            props = item['props']
            points = item['points']

            if cls == Strip:
                # Offset points
                new_points = [(px+offset, py+offset) for px, py in points]
                new_obj = cls(points=new_points)
            else:
                new_obj = cls()
                # Offset x,y
                if 'x' in props: props['x'] += offset
                if 'y' in props: props['y'] += offset

            # Apply properties
            for k, v in props.items():
                new_obj.set_property(k, v)

            self.objects.append(new_obj)
            new_obj.selected = True
            self.selected_objects.append(new_obj)

        self.selected_object = self.selected_objects[0] if self.selected_objects else None
        self.refresh_objects()
        self.notify_selection()

    def activate_format_painter(self):
        if self.selected_object:
            self.format_source = self.selected_object
            self.is_format_painting = True
            # Change cursor?
            self.canvas.config(cursor="plus")

    def apply_format(self, source, target):
        props = source.get_properties()
        # Filter geometry properties (x, y, length etc should NOT be copied usually, but diameter/depth SHOULD)
        # Exclude: x, y, length, Lx, Ly, points
        exclude = ['x', 'y', 'Lx', 'Ly', 'length', 'points', 'nx', 'ny']

        for k, v in props.items():
            if k not in exclude:
                # Check if target has this property
                # Using set_property is safe
                target.set_property(k, v)

        self.refresh_objects()
        self.canvas.config(cursor="") # Reset cursor

    # ... retain other methods like draw_temp_polyline, refresh_objects ...
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
