import customtkinter as ctk
import tkinter as tk
import math
import random
import threading
import time
import os

class VedaHUD(ctk.CTk):
    def __init__(self, config, assistant):
        super().__init__()
        self.config = config
        self.assistant = assistant

        # Base UI Config
        self.overrideredirect(True)
        self.attributes("-alpha", 0.90)
        self.attributes("-topmost", True)
        self.geometry("950x650")
        self.configure(fg_color="#050508")

        # Grid System
        self.grid_columnconfigure(0, weight=1, minsize=240)
        self.grid_columnconfigure(1, weight=2, minsize=400)
        self.grid_columnconfigure(2, weight=1, minsize=280)
        self.grid_rowconfigure(0, weight=1)

        self.links = {}
        self._init_left_sidebar()
        self._init_center_core()
        self._init_right_log()

        # Security for attributes used in async threads
        self.speech_lock = threading.Lock()

        self.bind("<Button-1>", self._start_drag)
        self.bind("<B1-Motion>", self._drag)
        self.status = "idle"
        self._animate_loop()

    def _init_left_sidebar(self):
        self.left_f = ctk.CTkFrame(self, fg_color="transparent")
        self.left_f.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Optical Feed
        self._add_section_header(self.left_f, "OPTICAL FEED")
        self.cam_box = ctk.CTkFrame(self.left_f, height=180, fg_color="black", border_width=1, border_color="#1a1a25")
        self.cam_box.pack(fill="x", pady=(5, 20))

        # Observability
        self._add_section_header(self.left_f, "OBSERVABILITY")
        self.obs_box = ctk.CTkFrame(self.left_f, fg_color="#08080c", border_width=1, border_color="#1a1a25")
        self.obs_box.pack(fill="x", pady=5)

        self.cpu_bar = self._add_metric(self.obs_box, "CPU", "22.1%", "#00d4ff")
        self.ram_bar = self._add_metric(self.obs_box, "RAM", "51.0%", "#b026ff")

        self.stats_labels = {}
        stats = [("THREADS", "11", "#00ffcc"), ("PLUGINS", "19", "#00ffcc"),
                 ("GOVERNANCE", "NOMINAL", "#00ffcc"), ("QUEUE", "0", "#ffcc00")]
        for label, val, color in stats:
            f = ctk.CTkFrame(self.obs_box, fg_color="transparent")
            f.pack(fill="x", padx=15, pady=2)
            ctk.CTkLabel(f, text=f"{label}:", font=("Orbitron", 8), text_color=color).pack(side="left")
            v = ctk.CTkLabel(f, text=val, font=("Consolas", 9, "bold"), text_color=color)
            v.pack(side="left", padx=5)
            self.stats_labels[label] = v

        # Passive stats
        for p in ["ROLLBACK: INACTIVE", "SELF-HEAL: INACTIVE"]:
            ctk.CTkLabel(self.obs_box, text=p, font=("Consolas", 8), text_color="#444444").pack(anchor="w", padx=15)

        # Execution Core
        self._add_section_header(self.left_f, "EXECUTION CORE")
        self.exec_box = ctk.CTkFrame(self.left_f, height=150, fg_color="black", border_width=1, border_color="#1a1a25")
        self.exec_box.pack(fill="x", pady=(5, 20))

        # Connectivity Links
        self._add_section_header(self.left_f, "CONNECTIVITY")
        self.conn_box = ctk.CTkFrame(self.left_f, fg_color="#08080c", border_width=1, border_color="#1a1a25")
        self.conn_box.pack(fill="x", pady=5)

        for link in ["NEURAL", "DATA", "VOICE", "OPTIC"]:
            f = ctk.CTkFrame(self.conn_box, fg_color="transparent")
            f.pack(fill="x", padx=15, pady=2)
            ctk.CTkLabel(f, text=f"{link} LINK:", font=("Orbitron", 8), text_color="#666666").pack(side="left")
            l = ctk.CTkLabel(f, text="OFFLINE", font=("Consolas", 8, "bold"), text_color="#ff3e3e")
            l.pack(side="right")
            self.links[link] = l

        # Protocols
        self._add_section_header(self.left_f, "PROTOCOLS")
        self.proto_box = ctk.CTkFrame(self.left_f, height=100, fg_color="black", border_width=1, border_color="#1a1a25")
        self.proto_box.pack(fill="x", pady=5)

    def _init_center_core(self):
        self.center_f = ctk.CTkFrame(self, fg_color="transparent")
        self.center_f.grid(row=0, column=1, sticky="nsew")

        self.canvas = tk.Canvas(self.center_f, bg="#050508", highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")

        # Bottom Controls
        self.ctrl_bar = ctk.CTkFrame(self.center_f, fg_color="transparent")
        self.ctrl_bar.pack(side="bottom", pady=25)

        ctk.CTkButton(self.ctrl_bar, text="💻 OFF", width=80, height=35, fg_color="#121217", border_width=1, border_color="#1a1a25", font=("Orbitron", 7), command=lambda: self.set_state("idle")).pack(side="left", padx=5)
        ctk.CTkButton(self.ctrl_bar, text="📁", width=40, height=35, fg_color="#121217", border_width=1, border_color="#1a1a25", command=lambda: self.assistant.process_command("open documents")).pack(side="left", padx=5)
        ctk.CTkButton(self.ctrl_bar, text="U N L O A D", width=100, height=40, fg_color="#121217", border_width=1, border_color="#ff3e3e",
                       font=("Orbitron", 9, "bold"), text_color="#ffffff", command=self.destroy).pack(side="left", padx=5)
        ctk.CTkButton(self.ctrl_bar, text="🎤", width=40, height=35, fg_color="#121217", border_width=1, border_color="#1a1a25", command=self._on_voice).pack(side="left", padx=5)

        # Earth mesh setup
        self.points = []; self.angle_y = 0; self.globe_cx = 210; self.globe_cy = 240
        self._init_earth_mesh()

    def _init_right_log(self):
        self.right_f = ctk.CTkFrame(self, fg_color="transparent")
        self.right_f.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        self._add_section_header(self.right_f, "COMMUNICATION LOG")
        self.chat_scroll = ctk.CTkScrollableFrame(self.right_f, fg_color="#08080c", border_width=1, border_color="#1a1a25")
        self.chat_scroll.pack(expand=True, fill="both", pady=5)

        self.status_box = ctk.CTkFrame(self.right_f, height=80, fg_color="#08080c", border_width=1, border_color="#1a1a25")
        self.status_box.pack(fill="x", pady=15)
        self.status_label = ctk.CTkLabel(self.status_box, text="TACTICAL STATUS: NOMINAL", font=("Orbitron", 8), text_color="#00d4ff")
        self.status_label.place(relx=0.5, rely=0.5, anchor="center")

        self.input_entry = ctk.CTkEntry(self.right_f, placeholder_text="Enter command...", font=("Consolas", 12),
                                        fg_color="#08080c", border_color="#00d4ff", border_width=2, corner_radius=0, height=45)
        self.input_entry.pack(fill="x", pady=(0, 10))
        self.input_entry.bind("<Return>", self._send_command)

    def _add_section_header(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Orbitron", 10, "bold"), text_color="#00d4ff").pack(anchor="w", pady=(0, 5))

    def _add_metric(self, parent, label, val_text, color):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=15, pady=(10, 2))
        ctk.CTkLabel(f, text=label, font=("Orbitron", 8), text_color="#666666").pack(side="left")
        ctk.CTkLabel(f, text=val_text, font=("Consolas", 8), text_color=color).pack(side="right")
        bar = ctk.CTkProgressBar(parent, height=8, progress_color=color, fg_color="#1a1a25")
        bar.pack(fill="x", padx=15, pady=(0, 10))
        bar.set(0.3)
        return bar

    def _init_earth_mesh(self):
        lats = 12; longs = 18
        for i in range(lats):
            lat = math.pi * i / (lats - 1)
            for j in range(longs):
                lon = 2 * math.pi * j / longs
                self.points.append([math.sin(lat) * math.cos(lon), math.cos(lat), math.sin(lat) * math.sin(lon)])

    def _animate_loop(self):
        self._draw_hex_grid()
        self._draw_earth()
        self.after(40, self._animate_loop)

    def _draw_hex_grid(self):
        self.canvas.delete("grid")
        size = 30
        for x in range(0, 700, int(size * 1.5)):
            for y in range(0, 750, int(size * math.sqrt(3))):
                offset = (size * 0.75) if (y // int(size * math.sqrt(3))) % 2 == 1 else 0
                self._draw_hex(x + offset, y, size)

    def _draw_hex(self, x, y, size):
        pts = []
        for i in range(6):
            ang = math.radians(i * 60)
            pts.extend([x + size * math.cos(ang), y + size * math.sin(ang)])
        self.canvas.create_polygon(pts, outline="#1a1a25", fill="", tags="grid")

    def _draw_earth(self):
        self.canvas.delete("globe")
        speed = 0.05 if self.status == "thinking" else 0.02
        self.angle_y += speed
        scale = 110 if self.status == "speaking" else 100
        proj = []
        for p in self.points:
            x, y, z = p
            nx = x * math.cos(self.angle_y) - z * math.sin(self.angle_y)
            nz = x * math.sin(self.angle_y) + z * math.cos(self.angle_y)
            proj.append((nx * scale + self.globe_cx, y * scale + self.globe_cy, nz))
        for i, pt in enumerate(proj):
            if pt[2] < 0: continue
            next_lon = (i + 1) if (i + 1) % 18 != 0 else i - 17
            self.canvas.create_line(pt[0], pt[1], proj[next_lon][0], proj[next_lon][1], fill="#00d4ff", tags="globe", width=1)
            next_lat = i + 18
            if next_lat < len(proj):
                self.canvas.create_line(pt[0], pt[1], proj[next_lat][0], proj[next_lat][1], fill="#00d4ff", tags="globe", width=1)
            self.canvas.create_oval(pt[0]-1, pt[1]-1, pt[0]+1, pt[1]+1, fill="#00d4ff", outline="", tags="globe")

    def add_message(self, role, text):
        bg = "#08080c"; border = "#1a1a25"
        if role == "Veda": border = "#00d4ff"

        f = ctk.CTkFrame(self.chat_scroll, fg_color=bg, border_width=1, border_color=border, corner_radius=5)
        f.pack(fill="x", pady=5, padx=5)

        h = ctk.CTkFrame(f, fg_color="transparent")
        h.pack(fill="x", padx=10, pady=(5, 0))
        ctk.CTkLabel(h, text=role.upper(), font=("Orbitron", 8, "bold"), text_color="#00d4ff").pack(side="left")
        ctk.CTkLabel(h, text=time.strftime("%H:%M"), font=("Consolas", 7), text_color="#444444").pack(side="right")

        ctk.CTkLabel(f, text=text, font=("Consolas", 10), text_color="#cccccc", wraplength=320, justify="left").pack(padx=10, pady=(2, 10), anchor="w")
        self.chat_scroll._parent_canvas.yview_moveto(1.0)

    def set_state(self, status):
        self.status = status
        self.status_label.configure(text=f"TACTICAL STATUS: {status.upper()}")

    def _send_command(self, event):
        cmd = self.input_entry.get()
        if cmd:
            self.input_entry.delete(0, "end")
            self.add_message("User", cmd)
            threading.Thread(target=self.assistant.process_command, args=(cmd,), daemon=True).start()

    def _on_voice(self):
        threading.Thread(target=self.assistant._trigger_mic, daemon=True).start()

    def _start_drag(self, event):
        self.x = event.x; self.y = event.y
    def _drag(self, event):
        self.geometry(f"+{self.winfo_x() + event.x - self.x}+{self.winfo_y() + event.y - self.y}")
    def start(self):
        self.mainloop()
