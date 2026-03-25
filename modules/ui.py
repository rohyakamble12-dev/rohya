import customtkinter as ctk
import tkinter as tk
import math
import random
import threading
import time
import os
from PIL import Image, ImageTk

class VedaPanel(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

class SidebarPanel(VedaPanel):
    def __init__(self, parent, assistant):
        super().__init__(parent)
        self.assistant = assistant
        self.setup_ui()

    def setup_ui(self):
        # Optical Feed
        self._add_section_header("OPTICAL FEED")
        self.cam_box = ctk.CTkFrame(self, height=150, fg_color="black", border_width=1, border_color="#1a1a25")
        self.cam_box.pack(fill="x", pady=(5, 15))
        self.cam_label = ctk.CTkLabel(self.cam_box, text="")
        self.cam_label.pack(expand=True, fill="both")

        # Observability
        self._add_section_header("OBSERVABILITY")
        self.obs_box = ctk.CTkFrame(self, fg_color="#08080c", border_width=1, border_color="#1a1a25")
        self.obs_box.pack(fill="x", pady=5)

        self.cpu_bar = self._add_metric(self.obs_box, "CPU", "#00d4ff")
        self.ram_bar = self._add_metric(self.obs_box, "RAM", "#b026ff")

        self.stats_labels = {}
        for label, color in [("THREADS", "#00ffcc"), ("PLUGINS", "#00ffcc"), ("QUEUE", "#ffcc00")]:
            f = ctk.CTkFrame(self.obs_box, fg_color="transparent")
            f.pack(fill="x", padx=15, pady=1)
            ctk.CTkLabel(f, text=f"{label}:", font=("Orbitron", 7), text_color="#666666").pack(side="left")
            v = ctk.CTkLabel(f, text="0", font=("Consolas", 8, "bold"), text_color=color)
            v.pack(side="right")
            self.stats_labels[label] = v

        # Connectivity Links
        self._add_section_header("CONNECTIVITY")
        self.conn_box = ctk.CTkFrame(self, fg_color="#08080c", border_width=1, border_color="#1a1a25")
        self.conn_box.pack(fill="x", pady=5)
        self.links = {}
        for link in ["NEURAL", "DATA", "VOICE", "OPTIC"]:
            f = ctk.CTkFrame(self.conn_box, fg_color="transparent")
            f.pack(fill="x", padx=15, pady=1)
            ctk.CTkLabel(f, text=f"{link}:", font=("Orbitron", 7), text_color="#666666").pack(side="left")
            l = ctk.CTkLabel(f, text="OFFLINE", font=("Consolas", 7, "bold"), text_color="#ff3e3e")
            l.pack(side="right")
            self.links[link] = l

    def _add_section_header(self, text):
        ctk.CTkLabel(self, text=text, font=("Orbitron", 8, "bold"), text_color="#00d4ff").pack(anchor="w", pady=(5, 2))

    def _add_metric(self, parent, label, color):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=15, pady=(5, 0))
        ctk.CTkLabel(f, text=label, font=("Orbitron", 7), text_color="#666666").pack(side="left")
        bar = ctk.CTkProgressBar(parent, height=4, progress_color=color, fg_color="#1a1a25")
        bar.pack(fill="x", padx=15, pady=(0, 5))
        bar.set(0)
        return bar

class CenterPanel(VedaPanel):
    def __init__(self, parent, assistant):
        super().__init__(parent)
        self.assistant = assistant
        self.points = []
        self.angle_y = 0
        self.setup_ui()
        self._init_earth_mesh()

    def setup_ui(self):
        self.canvas = tk.Canvas(self, bg="#050508", highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")

        self.ctrl_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.ctrl_bar.pack(side="bottom", pady=20)

        btns = [
            ("💻", lambda: self.assistant.set_state("idle")),
            ("🗕", lambda: self.master.iconify()),
            ("📁", lambda: self.assistant.process_command("open documents")),
            ("🎤", lambda: self.assistant._trigger_mic())
        ]
        for txt, cmd in btns:
            ctk.CTkButton(self.ctrl_bar, text=txt, width=40, height=35, fg_color="#121217", border_width=1, border_color="#1a1a25", command=cmd).pack(side="left", padx=5)

        ctk.CTkButton(self.ctrl_bar, text="U N L O A D", width=100, height=40, fg_color="#121217", border_width=1, border_color="#ff3e3e",
                       font=("Orbitron", 9, "bold"), text_color="#ffffff", command=self.master.destroy).pack(side="left", padx=5)

    def _init_earth_mesh(self):
        # Fibonacci Sphere (100 points as requested in design spec)
        n = 100
        phi = math.pi * (3. - math.sqrt(5.)) # golden angle in radians
        for i in range(n):
            y = 1 - (i / float(n - 1)) * 2 # y goes from 1 to -1
            radius = math.sqrt(1 - y * y) # radius at y
            theta = phi * i # golden angle increment
            x = math.cos(theta) * radius
            z = math.sin(theta) * radius
            self.points.append([x, y, z])

class LogPanel(VedaPanel):
    def __init__(self, parent, assistant):
        super().__init__(parent)
        self.assistant = assistant
        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self, text="COMMUNICATION LOG", font=("Orbitron", 8, "bold"), text_color="#00d4ff").pack(anchor="w", pady=(5, 5))
        self.chat_scroll = ctk.CTkScrollableFrame(self, fg_color="#08080c", border_width=1, border_color="#1a1a25")
        self.chat_scroll.pack(expand=True, fill="both", pady=5)

        self.status_label = ctk.CTkLabel(self, text="TACTICAL STATUS: NOMINAL", font=("Orbitron", 7), text_color="#00d4ff")
        self.status_label.pack(pady=5)

        self.input_entry = ctk.CTkEntry(self, placeholder_text="Command...", font=("Consolas", 11),
                                        fg_color="#08080c", border_color="#00d4ff", border_width=1, height=40)
        self.input_entry.pack(fill="x", pady=(0, 10))
        self.input_entry.bind("<Return>", self._on_submit)

    def _on_submit(self, event):
        cmd = self.input_entry.get()
        if cmd:
            self.input_entry.delete(0, "end")
            self.add_message("User", cmd)
            threading.Thread(target=self.assistant.process_command, args=(cmd,), daemon=True).start()

    def add_message(self, role, text):
        color = "#00d4ff" if role == "Veda" else "#1a1a25"
        text_color = "#cccccc"
        font = ("Consolas", 9)

        if role == "Thought":
            color = "#333333"
            text_color = "#666666"
            font = ("Consolas", 8, "italic")

        f = ctk.CTkFrame(self.chat_scroll, fg_color="#08080c", border_width=1, border_color=color)
        f.pack(fill="x", pady=2, padx=5)
        lbl = ctk.CTkLabel(f, text=f"{role.upper()}: {text}", font=font, text_color=text_color, wraplength=250, justify="left")
        lbl.pack(padx=10, pady=5)
        self.chat_scroll._parent_canvas.yview_moveto(1.0)
        return lbl

class VedaHUD(ctk.CTk):
    def __init__(self, config, assistant):
        super().__init__()
        self.assistant = assistant
        self.overrideredirect(True)
        self.attributes("-alpha", 0.85, "-topmost", True)
        self.geometry("850x550")
        self.configure(fg_color="#050508")
        self.title("VEDA CORE")
        self.mic_level = 0
        self.status = "idle"

        self.grid_columnconfigure(0, weight=1, minsize=200)
        self.grid_columnconfigure(1, weight=2, minsize=350)
        self.grid_columnconfigure(2, weight=1, minsize=250)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = SidebarPanel(self, assistant)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.center = CenterPanel(self, assistant)
        self.center.grid(row=0, column=1, sticky="nsew")
        self.log = LogPanel(self, assistant)
        self.log.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        self.bind("<Button-1>", self._start_drag)
        self.bind("<B1-Motion>", self._drag)
        self._animate_loop()

    def _animate_loop(self):
        self._draw_earth()
        self.after(40, self._animate_loop)

    def _draw_earth(self):
        canvas = self.center.canvas
        canvas.delete("globe")

        # Resize-aware dimensions
        w, h = canvas.winfo_width(), canvas.winfo_height()
        if w < 10 or h < 10: return
        cx, cy = w // 2, h // 2

        speed = 0.05 if self.status == "thinking" else 0.02
        self.center.angle_y += speed

        scale = (min(w, h) // 4) * (1.0 + self.mic_level * 0.5)
        color = {"idle": "#00d4ff", "thinking": "#b026ff", "speaking": "#00ffcc"}.get(self.status, "#00d4ff")
        if "ALERT" in self.log.status_label.cget("text"): color = "#ff3e3e"

        # Quantum Glow Effect
        glow_width = 2 if self.status == "thinking" else 1

        # Projection
        proj = []
        for p in self.center.points:
            x, y, z = p
            # Rotate Y
            nx = x * math.cos(self.center.angle_y) - z * math.sin(self.center.angle_y)
            nz = x * math.sin(self.center.angle_y) + z * math.cos(self.center.angle_y)
            proj.append((nx * scale + cx, y * scale + cy, nz))

        # Draw Points & Connections (Nearest Neighbor logic)
        for i, pt in enumerate(proj):
            if pt[2] < 0: continue # Backface culling
            canvas.create_oval(pt[0]-1, pt[1]-1, pt[0]+1, pt[1]+1, fill=color, outline="", tags="globe")

            # Simple nearest neighbor connections for the mesh look
            for j in range(i + 1, min(i + 4, len(proj))):
                if proj[j][2] > 0:
                    canvas.create_line(pt[0], pt[1], proj[j][0], proj[j][1], fill=color, tags="globe", width=glow_width, stipple="gray50")

        # Scanline Effect (Requested overlay)
        for y in range(0, h, 4):
            canvas.create_line(0, y, w, y, fill="#00ffff", tags="globe", width=1, stipple="gray12")

    def set_state(self, status):
        self.status = status
        self.log.status_label.configure(text=f"TACTICAL STATUS: {status.upper()}")

    def add_message(self, role, text):
        self.log.add_message(role, text)

    def update_camera(self, frame):
        img = Image.fromarray(frame).resize((180, 120))
        imgtk = ImageTk.PhotoImage(image=img)
        self.sidebar.cam_label.imgtk = imgtk
        self.sidebar.cam_label.configure(image=imgtk)

    def _start_drag(self, event): self.x = event.x; self.y = event.y
    def _drag(self, event): self.geometry(f"+{self.winfo_x() + event.x - self.x}+{self.winfo_y() + event.y - self.y}")
    def start(self): self.mainloop()
