import customtkinter as ctk
import tkinter as tk
import numpy as np
import math
import threading
import random
from veda.ui.base import VedaPanel

class CenterPanel(VedaPanel):
    def __init__(self, master, assistant):
        super().__init__(master, "Neural Core")
        self.assistant = assistant
        self.state = "idle" # idle, thinking, speaking, alert
        self.colors = {"idle": "#00d4ff", "thinking": "#ffcc00", "speaking": "#00ff7f", "alert": "#ff4b2b"}

        self.canvas = tk.Canvas(self, bg="#08080a", highlightthickness=0)
        self.canvas.pack(expand=True, fill="both", padx=10, pady=10)

        self.controls = ctk.CTkFrame(self, fg_color="transparent")
        self.controls.pack(fill="x", side="bottom", pady=10)

        self.btn_mic = ctk.CTkButton(self.controls, text="MIC", width=60, font=("Orbitron", 10, "bold"))
        self.btn_mic.pack(side="left", padx=10)

        self.btn_unload = ctk.CTkButton(self.controls, text="UNLOAD", fg_color="#ff4b2b", width=80, font=("Orbitron", 10, "bold"))
        self.btn_unload.pack(side="right", padx=10)

        self.points = []
        self.neighbors = []
        self.angle_y = 0

        self.canvas.bind("<Configure>", self._on_resize)
        self.start_globe_init()

    def _on_resize(self, event):
        self.width = event.width
        self.height = event.height

    def start_globe_init(self):
        threading.Thread(target=self._init_fibonacci_sphere, daemon=True).start()

    def _init_fibonacci_sphere(self):
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
                d = math.dist(self.points[i], self.points[j])
                dists.append((d, j))
            dists.sort()
            self.neighbors.append([d[1] for d in dists[:3]])

        self.after(0, self._animate)

    def _animate(self):
        self.canvas.delete("globe")
        color = self.colors.get(self.state, "#00d4ff")

        # Rotation logic
        speed = 0.02
        if self.state == "thinking": speed = 0.05
        elif self.state == "alert": speed = 0.1
        self.angle_y += speed

        # Pulse logic
        t = time.time()
        pulse = 1.0
        if self.state == "idle":
             pulse = 1.0 + 0.1 * (math.sin(t*2)**10 + math.sin(t*2.1)**10) # Heartbeat

        cx, cy = self.width/2, self.height/2
        scale = min(cx, cy) * 0.7 * pulse

        proj_points = []
        for p in self.points:
            x, y, z = p
            # Rotate Y
            nx = x * math.cos(self.angle_y) - z * math.sin(self.angle_y)
            nz = x * math.sin(self.angle_y) + z * math.cos(self.angle_y)

            px = nx * scale + cx
            py = y * scale + cy
            proj_points.append((px, py, nz))

        # Draw Mesh
        for i, pt in enumerate(proj_points):
            if pt[2] < 0: continue # Basic z-buffer
            for n_idx in self.neighbors[i]:
                n_pt = proj_points[n_idx]
                self.canvas.create_line(pt[0], pt[1], n_pt[0], n_pt[1], fill=color, alpha=0.3, tags="globe")
            self.canvas.create_oval(pt[0]-2, pt[1]-2, pt[0]+2, pt[1]+2, fill=color, outline="", tags="globe")

        # Glitch effect
        if random.random() > 0.99:
             self.canvas.create_rectangle(0, 0, self.width, self.height, fill="white", tags="globe")

        self.after(30, self._animate)

    def set_state(self, state):
        self.state = state
        self.refresh_theme(self.colors.get(state, "#00d4ff"))

    def refresh_theme(self, color):
        super().refresh_theme(color)
        self.btn_mic.configure(fg_color=color)

import time
