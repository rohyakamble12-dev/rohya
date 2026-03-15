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
        self.angle_y = 0
        self.center_x = 200
        self.center_y = 200
        self.calibrating = True

        self.canvas.bind("<Configure>", self._on_resize)
        self.start_globe_init()

    def _on_resize(self, event):
        self.center_x = event.width / 2
        self.center_y = event.height / 2

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

            # Pre-calculate neighbors
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
            color = self.colors.get(self.state, "#00d4ff")

            # Rotation speed per state
            speed_map = {"idle": 0.012, "thinking": 0.05, "speaking": 0.025, "alert": 0.12}
            self.angle_y += speed_map.get(self.state, 0.01)

            # Pulse per state (Heartbeat double-beat for idle)
            t = time.time()
            pulse = 1.0
            if self.state == "idle":
                 pulse = 1.0 + 0.07 * (math.pow(math.sin(t*2.5), 10) + math.pow(math.sin(t*2.6), 10))
            elif self.state == "thinking":
                 if int(t*12) % 2 == 0: color = "#ffffff" # Gold strobe sim
            elif self.state == "speaking":
                 pulse = 1.0 + 0.15 * math.sin(t*12)

            scale = min(self.center_x, self.center_y) * 0.75 * pulse

            proj_points = []
            for p in self.points:
                x, y, z = p
                nx = x * math.cos(self.angle_y) - z * math.sin(self.angle_y)
                nz = x * math.sin(self.angle_y) + z * math.cos(self.angle_y)

                px = nx * scale + self.center_x
                py = y * scale + self.center_y
                proj_points.append((px, py, nz))

            # Render Mesh
            for i, pt in enumerate(proj_points):
                if pt[2] < -0.3: continue # Back-face cull

                for n_idx in self.neighbors[i]:
                    n_pt = proj_points[n_idx]
                    if n_pt[2] < -0.3: continue
                    self.canvas.create_line(pt[0], pt[1], n_pt[0], n_pt[1], fill=color, width=1, stipple="gray50", tags="globe")

                self.canvas.create_oval(pt[0]-2, pt[1]-2, pt[0]+2, pt[1]+2, fill=color, outline="", tags="globe")

            # 1% HUD Glitch
            if random.random() > 0.99:
                 self.canvas.create_rectangle(0, 0, self.center_x*2, self.center_y*2, fill="#ffffff", tags="globe")

            self.after(35, self._animate)
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
