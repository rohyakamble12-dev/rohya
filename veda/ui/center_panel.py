import customtkinter as ctk
import tkinter as tk
import math
import threading
import random
import time
import logging
from veda.ui.base import VedaPanel

logger = logging.getLogger("VEDA")

class CenterPanel(VedaPanel):
    def __init__(self, master, assistant):
        super().__init__(master, "Neural Core")
        self.assistant = assistant
        self.state = "idle" # idle, thinking, speaking, alert
        self.colors = {"idle": "#00d4ff", "thinking": "#ffcc00", "speaking": "#00ff7f", "alert": "#ff4b2b"}

        self.canvas = tk.Canvas(self, bg="#08080a", highlightthickness=0)
        self.canvas.pack(expand=True, fill="both", padx=10, pady=10)

        self.controls = ctk.CTkFrame(self, fg_color="transparent")
        self.controls.pack(fill="x", side="bottom", pady=15)

        self.btn_cam = ctk.CTkButton(self.controls, text="CAM", width=50, font=("Orbitron", 10, "bold"), border_width=1)
        self.btn_cam.pack(side="left", padx=10)
        self.register_accent_widget(self.btn_cam, "border")

        self.btn_file = ctk.CTkButton(self.controls, text="FILE", width=50, font=("Orbitron", 10, "bold"), border_width=1)
        self.btn_file.pack(side="left", padx=5)
        self.register_accent_widget(self.btn_file, "border")

        self.btn_mic = ctk.CTkButton(self.controls, text="MIC", width=50, font=("Orbitron", 10, "bold"), border_width=1)
        self.btn_mic.pack(side="left", padx=5)
        self.register_accent_widget(self.btn_mic, "border")

        self.btn_unload = ctk.CTkButton(self.controls, text="UNLOAD", fg_color="#440000", hover_color="#ff4b2b", width=80, font=("Orbitron", 10, "bold"))
        self.btn_unload.pack(side="right", padx=15)

        self.points = []
        self.neighbors = []
        self.impulses = [] # Moving "Neural Firings"
        self.stars = []
        self.angle_y = 0
        self.angle_x = 0
        self.center_x = 200
        self.center_y = 200
        self.calibrating = True

        self.mouse_x = 0
        self.mouse_y = 0
        self.momentum_x = 0
        self.momentum_y = 0

        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self._init_stars()
        self.start_globe_init()

    def _on_resize(self, event):
        self.center_x = event.width / 2
        self.center_y = event.height / 2
        self._draw_hex_grid()

    def _on_mouse_move(self, event):
        self.momentum_x = (event.x - self.center_x) / 5000
        self.momentum_y = (event.y - self.center_y) / 5000

    def _init_stars(self):
        for _ in range(50):
            self.stars.append([random.randint(0, 800), random.randint(0, 600), random.uniform(0.5, 1.5)])

    def _draw_hex_grid(self):
        self.canvas.delete("grid")
        size = 35
        w, h = self.center_x * 2, self.center_y * 2
        for x in range(0, int(w) + size, size * 2):
            for y in range(0, int(h) + size, int(size * 1.5)):
                offset = size if (y // int(size * 1.5)) % 2 == 1 else 0
                self._draw_hex(x + offset, y, size)

    def _draw_hex(self, x, y, size):
        pts = []
        for i in range(6):
            ang = math.radians(i * 60 + 30)
            pts.append(x + size * math.cos(ang))
            pts.append(y + size * math.sin(ang))
        self.canvas.create_polygon(pts, outline="#0d0d12", fill="", tags="grid")

    def start_globe_init(self):
        self.canvas.delete("status")
        self.canvas.create_text(self.center_x, self.center_y, text="CALIBRATING NEURAL MESH...", fill="#00d4ff", font=("Orbitron", 10), tags="status")
        threading.Thread(target=self._init_fibonacci_sphere, daemon=True).start()

    def _init_fibonacci_sphere(self):
        try:
            n = 100
            phi = math.pi * (3. - math.sqrt(5.))
            for i in range(n):
                y = 1 - (i / float(n - 1)) * 2
                radius = math.sqrt(1 - y * y)
                theta = phi * i
                x = math.cos(theta) * radius
                z = math.sin(theta) * radius
                self.points.append([x, y, z])

            for i in range(n):
                dists = []
                for j in range(n):
                    if i == j: continue
                    d = math.sqrt((self.points[i][0]-self.points[j][0])**2 +
                                  (self.points[i][1]-self.points[j][1])**2 +
                                  (self.points[i][2]-self.points[j][2])**2)
                    dists.append((d, j))
                dists.sort()
                self.neighbors.append([d[1] for d in dists[:3]])

            self.calibrating = False
            self.after(0, self._animate)
        except Exception as e:
            logger.warning(f"Globe initialization failure: {e}")

    def _animate(self):
        try:
            self.canvas.delete("globe")
            self.canvas.delete("status")
            self.canvas.delete("star")
            color = self.colors.get(self.state, "#00d4ff")

            # Draw Starfield
            for s in self.stars:
                s[0] = (s[0] + s[2]) % (self.center_x * 2)
                self.canvas.create_oval(s[0], s[1], s[0]+1, s[1]+1, fill="#22222a", tags="star")

            speed_map = {"idle": 0.012, "thinking": 0.06, "speaking": 0.03, "alert": 0.18}
            self.angle_y += speed_map.get(self.state, 0.01) + self.momentum_x
            self.angle_x += self.momentum_y

            t = time.time()
            pulse = 1.0
            if self.state == "idle":
                 pulse = 1.0 + 0.07 * (math.pow(math.sin(t*2.5), 10) + math.pow(math.sin(t*2.6), 10))
            elif self.state == "thinking":
                 if int(t*15) % 2 == 0: color = "#ffffff"
            elif self.state == "speaking":
                 pulse = 1.0 + 0.18 * math.sin(t*15)

            scale = min(self.center_x, self.center_y) * 0.78 * pulse

            proj_points = []
            for p in self.points:
                x, y, z = p
                ry_x = x * math.cos(self.angle_y) - z * math.sin(self.angle_y)
                ry_z = x * math.sin(self.angle_y) + z * math.cos(self.angle_y)
                rx_y = y * math.cos(self.angle_x) - ry_z * math.sin(self.angle_x)
                rx_z = y * math.sin(self.angle_x) + ry_z * math.cos(self.angle_x)
                proj_points.append((ry_x * scale + self.center_x, rx_y * scale + self.center_y, rx_z))

            # Render Mesh
            for i, pt in enumerate(proj_points):
                if pt[2] < -0.4: continue
                for n_idx in self.neighbors[i]:
                    n_pt = proj_points[n_idx]
                    if n_pt[2] < -0.4: continue
                    self.canvas.create_line(pt[0], pt[1], n_pt[0], n_pt[1], fill=color, width=1, stipple="gray50", tags="globe")
                self.canvas.create_oval(pt[0]-2, pt[1]-2, pt[0]+2, pt[1]+2, fill=color, outline="", tags="globe")

            # Neural Firings (Impulses)
            if random.random() > 0.90:
                 self.impulses.append([random.randint(0, 99), 0])

            new_impulses = []
            for imp in self.impulses:
                pt_idx, progress = imp
                if progress < 1.0:
                    start_pt = proj_points[pt_idx]
                    target_idx = self.neighbors[pt_idx][0]
                    end_pt = proj_points[target_idx]
                    ix = start_pt[0] + (end_pt[0] - start_pt[0]) * progress
                    iy = start_pt[1] + (end_pt[1] - start_pt[1]) * progress
                    self.canvas.create_oval(ix-2, iy-2, ix+2, iy+2, fill="#ffffff", tags="globe")
                    imp[1] += 0.1
                    new_impulses.append(imp)
            self.impulses = new_impulses

            glitch_chance = 0.992 if self.state != "alert" else 0.94
            if random.random() > glitch_chance:
                 g_color = random.choice(["#ffffff", color, "#ff00ff"])
                 self.canvas.create_rectangle(0, 0, self.center_x*2, self.center_y*2, fill=g_color, tags="globe")

            self.after(30, self._animate)
        except Exception as e:
            logger.warning(f"Globe render cycle error: {e}")
            self.after(100, self._animate)

    def set_state(self, state):
        self.state = state
        self.refresh_theme(self.colors.get(state, "#00d4ff"))

    def refresh_theme(self, color):
        super().refresh_theme(color)
        self.btn_mic.configure(border_color=color)
        self.btn_cam.configure(border_color=color)
        self.btn_file.configure(border_color=color)
