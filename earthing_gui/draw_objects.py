from dataclasses import dataclass, field
from typing import List, Tuple
import tkinter as tk

@dataclass
class DrawObject:
    selected: bool = False

    def draw(self, canvas, manager):
        pass

    def contains(self, x, y):
        return False

    def get_properties(self):
        return {}

    def set_property(self, key, value):
        pass

@dataclass
class Rod(DrawObject):
    x: float = 0.0
    y: float = 0.0
    depth: float = 0.5
    radius: float = 0.04
    length: float = 3.0
    rho: float = 100.0

    def draw(self, canvas, manager):
        sx, sy = manager.world_to_screen(self.x, self.y)
        r = 5
        color = "red" if self.selected else "blue"
        canvas.create_oval(sx-r, sy-r, sx+r, sy+r, fill=color, tags="object")
        canvas.create_text(sx, sy+10, text="Rod", anchor="n", font=("Arial", 8), tags="object")

    def contains(self, wx, wy):
        # Hit test within 0.5m radius
        return (wx - self.x)**2 + (wy - self.y)**2 < 0.5**2

    def get_properties(self):
        return {
            'x': self.x,
            'y': self.y,
            'depth': self.depth,
            'radius': self.radius,
            'length': self.length,
            'rho': self.rho
        }

    def set_property(self, key, value):
        if hasattr(self, key):
            setattr(self, key, float(value))

@dataclass
class Strip(DrawObject):
    points: List[Tuple[float, float]] = field(default_factory=list)
    width: float = 0.025
    depth: float = 0.5
    rho: float = 100.0

    def draw(self, canvas, manager):
        if len(self.points) < 2: return
        screen_points = []
        for wx, wy in self.points:
            screen_points.extend(manager.world_to_screen(wx, wy))

        color = "red" if self.selected else "green"
        width = 3 if self.selected else 2
        canvas.create_line(*screen_points, fill=color, width=width, tags="object")

    def contains(self, wx, wy):
        # Simplified hit test: check distance to each segment
        threshold = 0.5
        for i in range(len(self.points)-1):
            p1 = self.points[i]
            p2 = self.points[i+1]
            dist = self.point_segment_distance(wx, wy, p1, p2)
            if dist < threshold:
                return True
        return False

    def point_segment_distance(self, px, py, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return ((px-x1)**2 + (py-y1)**2)**0.5

        t = ((px-x1)*dx + (py-y1)*dy) / (dx*dx + dy*dy)
        t = max(0, min(1, t))
        closest_x = x1 + t*dx
        closest_y = y1 + t*dy
        return ((px-closest_x)**2 + (py-closest_y)**2)**0.5

    def get_properties(self):
        return {
            'width': self.width,
            'depth': self.depth,
            'rho': self.rho
        }

    def set_property(self, key, value):
         if hasattr(self, key):
            setattr(self, key, float(value))

@dataclass
class Mesh(DrawObject):
    x: float = 0.0
    y: float = 0.0
    width: float = 10.0
    height: float = 10.0
    nx: int = 5
    ny: int = 5
    strip_width: float = 0.025
    depth: float = 0.5
    rho: float = 100.0

    def draw(self, canvas, manager):
        sx1, sy1 = manager.world_to_screen(self.x, self.y)
        sx2, sy2 = manager.world_to_screen(self.x + self.width, self.y + self.height)

        # Draw bounding box
        color = "red" if self.selected else "gray"
        # tkinter create_rectangle expects top-left, bottom-right but coords might be flipped
        canvas.create_rectangle(sx1, sy1, sx2, sy2, outline=color, tags="object")

        # Draw grid lines approximation
        # Vertical
        dx = (sx2 - sx1) / (self.nx - 1) if self.nx > 1 else 0
        for i in range(self.nx):
            x = sx1 + i * dx
            canvas.create_line(x, sy1, x, sy2, fill=color, dash=(2, 4), tags="object")

        # Horizontal
        dy = (sy2 - sy1) / (self.ny - 1) if self.ny > 1 else 0
        for i in range(self.ny):
            y = sy1 + i * dy
            canvas.create_line(sx1, y, sx2, y, fill=color, dash=(2, 4), tags="object")

        canvas.create_text((sx1+sx2)/2, (sy1+sy2)/2, text="Mesh", fill=color, tags="object")

    def contains(self, wx, wy):
        return (self.x <= wx <= self.x + self.width) and \
               (self.y <= wy <= self.y + self.height)

    def get_properties(self):
        return {
            'x': self.x,
            'y': self.y,
            'Lx': self.width,
            'Ly': self.height,
            'Nx': self.nx,
            'Ny': self.ny,
            'strip_width': self.strip_width,
            'depth': self.depth,
            'rho': self.rho
        }

    def set_property(self, key, value):
        if key in ['Nx', 'Ny', 'nx', 'ny']:
            setattr(self, key.lower(), int(float(value)))
        elif key == 'Lx':
            self.width = float(value)
        elif key == 'Ly':
            self.height = float(value)
        elif hasattr(self, key):
            setattr(self, key, float(value))

@dataclass
class Plate(DrawObject):
    x: float = 0.0
    y: float = 0.0
    width: float = 1.0
    height: float = 1.0
    depth: float = 1.0
    rho: float = 100.0

    def draw(self, canvas, manager):
        sx, sy = manager.world_to_screen(self.x, self.y)
        # Draw as a filled square centered at x,y
        # Plate dimensions in drawing might be small, so we use a fixed symbol size or real size
        # Let's use real size but with minimum
        w_px = max(10, self.width * manager.scale)
        h_px = max(10, self.height * manager.scale)

        color = "red" if self.selected else "orange"
        canvas.create_rectangle(sx - w_px/2, sy - h_px/2, sx + w_px/2, sy + h_px/2,
                                fill=color, tags="object")
        canvas.create_text(sx, sy, text="Plate", font=("Arial", 8), tags="object")

    def contains(self, wx, wy):
        return (self.x - self.width/2 <= wx <= self.x + self.width/2) and \
               (self.y - self.height/2 <= wy <= self.y + self.height/2)

    def get_properties(self):
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'depth': self.depth,
            'rho': self.rho
        }

    def set_property(self, key, value):
        if hasattr(self, key):
            setattr(self, key, float(value))
