import customtkinter as ctk
import tkinter as tk
import math
import threading
import random
import time
import logging
from veda.ui.base import VedaPanel
from veda.ui.theme import VedaTheme, VedaState

logger = logging.getLogger("VEDA")

class CenterPanel(VedaPanel):
    def __init__(self, master, assistant, theme: VedaTheme, state: VedaState):
        super().__init__(master, "Neural Core", theme, state)
        self.assistant = assistant
        self.colors = {"idle": theme.idle, "thinking": theme.thinking, "speaking": theme.speaking, "alert": theme.alert}

        self.canvas = tk.Canvas(self, bg=theme.bg_main, highlightthickness=0)
        self.canvas.pack(expand=True, fill="both", padx=10, pady=10)

        self.controls = ctk.CTkFrame(self, fg_color="transparent")
        self.controls.pack(fill="x", side="bottom", pady=15)

        self.btn_cam = ctk.CTkButton(self.controls, text="CAM", width=50, font=theme.font_header, border_width=1, command=self._toggle_cam)
        self.btn_cam.pack(side="left", padx=10); self.register_accent_widget(self.btn_cam, "border")

        self.btn_mic = ctk.CTkButton(self.controls, text="MIC", width=50, font=theme.font_header, border_width=1)
        self.btn_mic.pack(side="left", padx=5); self.register_accent_widget(self.btn_mic, "border")

        self.points = []; self.neighbors = []; self.angle_y = 0; self.angle_x = 0
        self.globe_cx = 200; self.globe_cy = 200; self.calibrating = True

        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.create_text(200, 200, text="CALIBRATING NEURAL MESH...", fill=theme.idle, font=theme.font_data, tags="status")

        threading.Thread(target=self._init_sphere, daemon=True).start()

    def _on_resize(self, event):
        self.globe_cx, self.globe_cy = event.width / 2, event.height / 2
        self._draw_grid()

    def _draw_grid(self):
        self.canvas.delete("grid")
        size = 25
        for x in range(0, int(self.globe_cx*2) + size, size * 2):
            for y in range(0, int(self.globe_cy*2) + size, int(size * 1.5)):
                offset = size if (y // int(size * 1.5)) % 2 == 1 else 0
                self._draw_hex(x + offset, y, size)

    def _draw_hex(self, x, y, size):
        pts = [x + size * math.cos(math.radians(i*60+30)) for i in range(6) for _ in (0,1)]
        # flat zip alternative
        pts = []
        for i in range(6):
            ang = math.radians(i*60+30)
            pts.extend([x + size * math.cos(ang), y + size * math.sin(ang)])
        self.canvas.create_polygon(pts, outline="#1a1a25", fill="", tags="grid")

    def _init_sphere(self):
        n = 100; phi = math.pi * (3. - math.sqrt(5.))
        for i in range(n):
            y = 1 - (i / float(n - 1)) * 2; radius = math.sqrt(1 - y * y); theta = phi * i
            self.points.append([math.cos(theta) * radius, y, math.sin(theta) * radius])
        for i in range(n):
            dists = sorted([(math.dist(self.points[i], self.points[j]), j) for j in range(n) if i != j])
            self.neighbors.append([d[1] for d in dists[:3]])
        self.calibrating = False; self.after(0, self._animate)

    def _animate(self):
        self.canvas.delete("globe"); self.canvas.delete("status")
        color = self.colors.get(self.state.status, self.theme.idle)
        speed = {"idle": 0.01, "thinking": 0.06, "speaking": 0.02, "alert": 0.15}.get(self.state.status, 0.01)
        self.angle_y += speed

        t = time.time(); pulse = 1.0
        if self.state.status == "idle": pulse = 1.0 + 0.05 * (math.pow(math.sin(t*2), 10) + math.pow(math.sin(t*2.1), 10))
        scale = min(self.globe_cx, self.globe_cy) * 0.7 * pulse

        proj = []
        for p in self.points:
            x, y, z = p
            nx = x * math.cos(self.angle_y) - z * math.sin(self.angle_y)
            nz = x * math.sin(self.angle_y) + z * math.cos(self.angle_y)
            proj.append((nx * scale + self.globe_cx, y * scale + self.globe_cy, nz))

        for i, pt in enumerate(proj):
            if pt[2] < -0.2: continue
            for n_idx in self.neighbors[i]:
                n_pt = proj[n_idx]
                if n_pt[2] < -0.2: continue
                self.canvas.create_line(pt[0], pt[1], n_pt[0], n_pt[1], fill=color, tags="globe", stipple="gray50" if pt[2] < 0.2 else "")
            self.canvas.create_oval(pt[0]-2, pt[1]-2, pt[0]+2, pt[1]+2, fill=color, outline="", tags="globe")

        if random.random() > 0.99: self.canvas.create_rectangle(0,0,1000,1000, fill="white", tags="globe")
        self.after(40, self._animate)

    def _toggle_cam(self):
        self.state.camera_active = not self.state.camera_active
        self.btn_cam.configure(text_color=self.theme.idle if self.state.camera_active else "grey")
