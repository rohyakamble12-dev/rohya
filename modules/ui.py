import customtkinter as ctk
import tkinter as tk
import math
import random
import threading
import time
import os

class VedaHUD(ctk.CTk):
    def __init__(self, config, on_command_callback):
        super().__init__()
        self.config = config
        self.on_command = on_command_callback

        # 1. Base Config
        self.overrideredirect(True)
        self.attributes("-alpha", 0.92)
        self.attributes("-topmost", True)
        self.geometry("1200x700")
        self.configure(fg_color="#08080a")

        # Dragging support
        self.bind("<Button-1>", self._start_drag)
        self.bind("<B1-Motion>", self._drag)

        # 2. Grid Layout
        self.grid_columnconfigure(0, weight=1, minsize=280) # Left: Status
        self.grid_columnconfigure(1, weight=2, minsize=500) # Center: Core
        self.grid_columnconfigure(2, weight=1, minsize=320) # Right: Chat
        self.grid_rowconfigure(0, weight=1)

        # 3. PANELS
        self._init_left_panel()
        self._init_center_panel()
        self._init_right_panel()

        # State
        self.glitch_active = False

    def _init_left_panel(self):
        self.left = ctk.CTkFrame(self, fg_color="#0a0a0f", border_width=1, border_color="#1a1a20", corner_radius=0)
        self.left.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        ctk.CTkLabel(self.left, text="TACTICAL STATUS", font=("Orbitron", 12, "bold"), text_color="#00d4ff").pack(pady=10)

        # Link Status
        self.links = {}
        for link in ["NEURAL", "OPTIC", "VOICE", "DATA"]:
            f = ctk.CTkFrame(self.left, fg_color="transparent")
            f.pack(fill="x", padx=15, pady=5)
            ctk.CTkLabel(f, text=link, font=("Consolas", 10), text_color="#666666").pack(side="left")
            val = ctk.CTkLabel(f, text="LINKING...", font=("Consolas", 10), text_color="#ff8c00")
            val.pack(side="right")
            self.links[link] = val

    def _init_center_panel(self):
        self.center = ctk.CTkFrame(self, fg_color="transparent")
        self.center.grid(row=0, column=1, sticky="nsew")

        self.canvas = tk.Canvas(self.center, bg="#08080a", highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")

        self.points = []; self.neighbors = []; self.angle_y = 0
        self.globe_cx = 250; self.globe_cy = 250

        threading.Thread(target=self._init_sphere, daemon=True).start()

    def _init_right_panel(self):
        self.right = ctk.CTkFrame(self, fg_color="#0a0a0f", border_width=1, border_color="#1a1a20", corner_radius=0)
        self.right.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)

        self.chat_log = ctk.CTkScrollableFrame(self.right, fg_color="transparent")
        self.chat_log.pack(expand=True, fill="both", padx=10, pady=10)

        self.input_entry = ctk.CTkEntry(self.right, placeholder_text="EXECUTE COMMAND >>", font=("Consolas", 11), border_width=1, corner_radius=0)
        self.input_entry.pack(fill="x", padx=10, pady=15)
        self.input_entry.bind("<Return>", self._send_command)

    def _init_sphere(self):
        n = 120; phi = math.pi * (3. - math.sqrt(5.))
        for i in range(n):
            y = 1 - (i / float(n - 1)) * 2; radius = math.sqrt(1 - y * y); theta = phi * i
            self.points.append([math.cos(theta) * radius, y, math.sin(theta) * radius])
        for i in range(n):
            dists = sorted([(math.dist(self.points[i], self.points[j]), j) for j in range(n) if i != j])
            self.neighbors.append([d[1] for d in dists[:3]])
        self.after(0, self._animate)

    def _animate(self):
        self.canvas.delete("globe")
        self.angle_y += 0.02
        scale = 180

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
                self.canvas.create_line(pt[0], pt[1], n_pt[0], n_pt[1], fill="#00d4ff", tags="globe", width=1)
            self.canvas.create_oval(pt[0]-2, pt[1]-2, pt[0]+2, pt[1]+2, fill="#00d4ff", outline="", tags="globe")

        if random.random() > 0.98: self._draw_glitch()
        self.after(40, self._animate)

    def _draw_glitch(self):
        for _ in range(2):
            x = random.randint(0, 1200); y = random.randint(0, 700)
            self.canvas.create_rectangle(x, y, x+100, y+2, fill="#00d4ff", outline="", tags="globe")

    def add_message(self, role, text):
        colors = {"Veda": "#00d4ff", "User": "#ffffff", "System": "#ff8c00", "Error": "#ff3e3e"}
        color = colors.get(role, "#ffffff")

        f = ctk.CTkFrame(self.chat_log, fg_color="transparent")
        f.pack(fill="x", pady=4)
        ctk.CTkLabel(f, text=f"[{role.upper()}]", font=("Orbitron", 9, "bold"), text_color=color).pack(anchor="w")
        ctk.CTkLabel(f, text=text, font=("Consolas", 10), text_color="#cccccc", wraplength=280, justify="left").pack(anchor="w", padx=10)
        self.chat_log._parent_canvas.yview_moveto(1.0)

    def _start_drag(self, event):
        self.x = event.x; self.y = event.y

    def _drag(self, event):
        self.geometry(f"+{self.winfo_x() + event.x - self.x}+{self.winfo_y() + event.y - self.y}")

    def start(self):
        self.mainloop()
