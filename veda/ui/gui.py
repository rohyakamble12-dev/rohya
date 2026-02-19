import customtkinter as ctk
import threading
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import psutil
import time
import math
import random

class VedaGUI(ctk.CTk):
    def __init__(self, on_send_callback, on_voice_callback):
        super().__init__()

        self.on_send_callback = on_send_callback
        self.on_voice_callback = on_voice_callback
        self.protocol_callback = None

        # HUD Configuration
        self.title("VEDA CORE")
        self.geometry("1100x650")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.92)
        self.configure(fg_color="#08080a")

        # Colors
        self.accent_color = "#00d4ff"
        self.alert_color = "#ff4b2b"
        self.text_color = "#e0f7fa"
        self.border_color = "#1a1a20"

        # State
        self.pulse_active = False
        self.camera_active = True
        self.cap = None
        self.last_raw_frame = None
        self.online = True

        # Protocol Variables
        self.deep_search_var = tk.BooleanVar(value=False)
        self.private_var = tk.BooleanVar(value=False)
        self.context_var = tk.BooleanVar(value=True)

        # Movement tracking
        self._drag_data = {"x": 0, "y": 0}

        self._setup_layout()
        self._start_background_tasks()

    def _setup_layout(self):
        self.grid_columnconfigure(0, weight=1, minsize=260)
        self.grid_columnconfigure(1, weight=2, minsize=480)
        self.grid_columnconfigure(2, weight=1, minsize=340)
        self.grid_rowconfigure(1, weight=1)

        # --- TOP BAR ---
        self.top_bar = ctk.CTkFrame(self, height=45, fg_color="#050507", corner_radius=0)
        self.top_bar.grid(row=0, column=0, columnspan=3, sticky="ew")
        self.top_bar.bind("<ButtonPress-1>", self._on_drag_start)
        self.top_bar.bind("<B1-Motion>", self._on_drag_motion)

        self.title_lbl = ctk.CTkLabel(self.top_bar, text="V E D A  -  C O R E  O S",
                                      font=("Orbitron", 12, "bold"), text_color=self.accent_color)
        self.title_lbl.pack(side="left", padx=20)

        self.status_indicators = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.status_indicators.pack(side="right", padx=10)

        self.online_status = ctk.CTkLabel(self.status_indicators, text="● ONLINE", text_color="#00ff7f", font=("Orbitron", 9))
        self.online_status.pack(side="left", padx=10)

        self.sys_ready = ctk.CTkLabel(self.status_indicators, text="SYSTEM READY", text_color=self.accent_color, font=("Orbitron", 9))
        self.sys_ready.pack(side="left", padx=10)

        # --- LEFT PANEL: VISUALS & TELEMETRY ---
        self.left_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.left_panel.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")

        # Visual Input (Fixed aspect ratio)
        self.vis_frame = self._create_panel(self.left_panel, "OPTICAL FEED")
        self.cam_label = tk.Label(self.vis_frame, bg="#050507")
        self.cam_label.pack(fill="both", expand=True, padx=2, pady=2)

        # Performance
        self.perf_frame = self._create_panel(self.left_panel, "TELEMETRY")
        self._add_metric(self.perf_frame, "CPU", "cpu_bar", "cpu_val", self.accent_color)
        self._add_metric(self.perf_frame, "RAM", "ram_bar", "ram_val", "#b000ff")

        # Protocols (Vertical checklist)
        self.proto_frame = self._create_panel(self.left_panel, "PROTOCOLS")
        self._add_proto_cb(self.proto_frame, "DEEP RESEARCH", self.deep_search_var)
        self._add_proto_cb(self.proto_frame, "SECURE MODE", self.private_var)
        self._add_proto_cb(self.proto_frame, "REAL-TIME CONTEXT", self.context_var)

        # --- CENTER PANEL: THE CORE ---
        self.center_panel = ctk.CTkFrame(self, fg_color="#0d0d12", border_width=1, border_color=self.border_color)
        self.center_panel.grid(row=1, column=1, pady=15, sticky="nsew")

        self.canvas = tk.Canvas(self.center_panel, width=400, height=400, bg="#0d0d12", highlightthickness=0)
        self.canvas.pack(pady=20, expand=True)
        self._init_core_animation()

        self.ctrl_frame = ctk.CTkFrame(self.center_panel, fg_color="transparent")
        self.ctrl_frame.pack(pady=20)

        self.btn_cam = self._create_icon_btn(self.ctrl_frame, "📷", self.toggle_camera)
        if self.camera_active:
            self.btn_cam.configure(fg_color=self.accent_color, border_color="#ffffff")

        self.btn_end = ctk.CTkButton(self.ctrl_frame, text="U N L O A D", width=120, height=35,
                                     fg_color="#201010", border_width=1, border_color=self.alert_color,
                                     hover_color=self.alert_color, font=("Orbitron", 11, "bold"), command=self.destroy)
        self.btn_end.pack(side="left", padx=15)
        self.btn_mic = self._create_icon_btn(self.ctrl_frame, "🎤", self.trigger_voice)

        # --- RIGHT PANEL: COMMS ---
        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=1, column=2, padx=15, pady=15, sticky="nsew")

        self.comm_frame = self._create_panel(self.right_panel, "COMMUNICATION LOG")
        self.chat_display = ctk.CTkTextbox(self.comm_frame, font=("Consolas", 11), fg_color="#050507", text_color="#cfd8dc")
        self.chat_display.pack(fill="both", expand=True, padx=5, pady=5)
        self.chat_display.configure(state="disabled")

        self.input_entry = ctk.CTkEntry(self.right_panel, placeholder_text="Enter command...", height=40,
                                        fg_color="#050507", border_color=self.accent_color)
        self.input_entry.pack(fill="x", pady=(10, 0))
        self.input_entry.bind("<Return>", lambda e: self.send_message())

    def _create_panel(self, parent, title):
        frame = ctk.CTkFrame(parent, fg_color="#0a0a0f", border_width=1, border_color=self.border_color)
        frame.pack(fill="both", expand=True, pady=5)
        header = ctk.CTkFrame(frame, height=22, fg_color="#121217", corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text=f" {title}", font=("Orbitron", 9, "bold"), text_color=self.accent_color).pack(side="left", padx=5)
        return frame

    def _add_metric(self, parent, name, bar_attr, val_attr, color):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(f, text=name, font=("Orbitron", 8)).pack(side="left")
        val = ctk.CTkLabel(f, text="0%", font=("Consolas", 9, "bold"), text_color=color)
        val.pack(side="right")
        setattr(self, val_attr, val)
        bar = ctk.CTkProgressBar(parent, height=6, progress_color=color)
        bar.set(0)
        bar.pack(fill="x", padx=10, pady=(0, 8))
        setattr(self, bar_attr, bar)

    def _add_proto_cb(self, parent, text, var):
        cb = ctk.CTkCheckBox(parent, text=text, variable=var, command=self._on_proto_change,
                             font=("Orbitron", 8), text_color=self.accent_color, checkbox_width=16, checkbox_height=16)
        cb.pack(anchor="w", padx=12, pady=6)

    def _create_icon_btn(self, parent, icon, cmd):
        btn = ctk.CTkButton(parent, text=icon, width=45, height=35, fg_color="#121217",
                             border_width=1, border_color=self.border_color, hover_color="#1a1a25", command=cmd)
        btn.pack(side="left", padx=5)
        return btn

    def _init_core_animation(self):
        self.canvas.delete("all")
        # Static rings
        self.canvas.create_oval(50, 50, 350, 350, outline="#121217", width=1)
        self.canvas.create_oval(80, 80, 320, 320, outline="#1a1a20", width=1)
        # Pulsing Core
        self.core_orb = self.canvas.create_oval(130, 130, 270, 270, fill="#001a21", outline=self.accent_color, width=2)
        # Particles (Optimized count)
        self.particles = []
        for _ in range(30):
            p = self.canvas.create_oval(0, 0, 2, 2, fill=self.accent_color, outline="")
            self.particles.append({'id': p, 'speed': random.uniform(0.3, 1.2), 'angle': random.uniform(0, 6.28), 'dist': random.randint(80, 140)})

    def _start_background_tasks(self):
        threading.Thread(target=self._metrics_worker, daemon=True).start()
        threading.Thread(target=self._camera_worker, daemon=True).start()
        threading.Thread(target=self._network_worker, daemon=True).start()
        self._animate_loop()

    def _metrics_worker(self):
        while True:
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                self.after(0, lambda c=cpu, r=ram: self._update_metrics_ui(c, r))
            except: pass
            time.sleep(3)

    def _update_metrics_ui(self, cpu, ram):
        self.cpu_bar.set(cpu/100)
        self.cpu_val.configure(text=f"{cpu}%")
        self.ram_bar.set(ram/100)
        self.ram_val.configure(text=f"{ram}%")

    def _network_worker(self):
        import requests
        while True:
            try:
                requests.get("https://www.google.com", timeout=2)
                self.online = True
            except: self.online = False
            self.after(0, self._update_status_ui)
            time.sleep(15)

    def _update_status_ui(self):
        if self.online:
            self.online_status.configure(text="● ONLINE", text_color="#00ff7f")
        else:
            self.online_status.configure(text="○ OFFLINE", text_color=self.alert_color)

    def _camera_worker(self):
        self.cap = cv2.VideoCapture(0)
        while True:
            if self.camera_active:
                if not self.cap or not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(0)

                if self.cap.isOpened():
                    ret, frame = self.cap.read()
                    if ret:
                        self.last_raw_frame = frame
                        # Resize is expensive, do it only as much as needed
                        small_frame = cv2.resize(frame, (250, 150))
                        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                        img = Image.fromarray(rgb_frame)
                        img_tk = ImageTk.PhotoImage(image=img)
                        self.after(0, lambda i=img_tk: self._update_cam_ui(i))
            else:
                if self.cap and self.cap.isOpened():
                    self.cap.release()
                    self.cap = None

            time.sleep(0.1) # 10 FPS for stability

    def _update_cam_ui(self, img_tk):
        if self.camera_active:
            self.cam_label.img_tk = img_tk
            self.cam_label.configure(image=img_tk, text="")

    def _animate_loop(self):
        t = time.time()
        # Smoother pulse
        speed = 4 if self.pulse_active else 1.5
        pulse = (math.sin(t * speed) + 1) / 2

        # Scale core
        s_base = 135
        s_adj = pulse * (15 if self.pulse_active else 5)
        self.canvas.coords(self.core_orb, 200-(s_base+s_adj), 200-(s_base+s_adj), 200+(s_base+s_adj), 200+(s_base+s_adj))

        if self.pulse_active:
            self.canvas.itemconfig(self.core_orb, fill="#004d61")
        else:
            self.canvas.itemconfig(self.core_orb, fill="#001015")

        # Particles
        for p in self.particles:
            p['angle'] += 0.03 * p['speed'] * (2 if self.pulse_active else 1)
            x = 200 + math.cos(p['angle']) * p['dist']
            y = 200 + math.sin(p['angle']) * p['dist']
            self.canvas.coords(p['id'], x-1, y-1, x+1, y+1)

        self.after(50, self._animate_loop)

    def toggle_camera(self):
        self.camera_active = not self.camera_active
        if not self.camera_active:
            self.cam_label.configure(image="", text="FEED PAUSED", fg="grey")
            self.btn_cam.configure(fg_color="#121217", border_color=self.border_color)
        else:
            self.cam_label.configure(text="INITIALIZING...")
            self.btn_cam.configure(fg_color=self.accent_color, border_color="#ffffff")

    def trigger_voice(self):
        self.sys_ready.configure(text="LISTENING...", text_color=self.alert_color)
        threading.Thread(target=self.on_voice_callback, daemon=True).start()

    def reset_voice_button(self):
        self.after(0, lambda: self.sys_ready.configure(text="SYSTEM READY", text_color=self.accent_color))

    def set_voice_active(self, active):
        self.pulse_active = active
        self.btn_mic.configure(fg_color=self.accent_color if active else "#121217")

    def update_chat(self, sender, message):
        self.after(0, lambda: self._update_chat_ui(sender, message))

    def _update_chat_ui(self, sender, message):
        self.chat_display.configure(state="normal")
        tag = "veda" if sender.lower() == "veda" else "user"
        self.chat_display.insert("end", f"{sender.upper()}: ", tag)
        self.chat_display.insert("end", f"{message}\n\n")
        self.chat_display.tag_config("veda", foreground=self.accent_color, font=("Consolas", 11, "bold"))
        self.chat_display.tag_config("user", foreground="#ffffff")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def send_message(self):
        msg = self.input_entry.get()
        if msg:
            self.update_chat("User", msg)
            self.input_entry.delete(0, "end")
            threading.Thread(target=self.on_send_callback, args=(msg,), daemon=True).start()

    def _on_proto_change(self):
        if self.protocol_callback: self.protocol_callback()

    def on_protocol_toggle(self, name):
        self._on_proto_change()

    def show_suggestion(self, text):
        self.update_chat("System", f"Info: {text}")

    def set_theme_color(self, mood="calm"):
        colors = {"calm": "#00d4ff", "alert": "#ff4b2b", "success": "#00ff7f", "focus": "#ffff00", "stealth": "#707070"}
        color = colors.get(mood.lower(), colors["calm"])
        self.accent_color = color
        self.title_lbl.configure(text_color=color)
        self.sys_ready.configure(text_color=color)
        self.cpu_val.configure(text_color=color)
        self.cpu_bar.configure(progress_color=color)
        self.input_entry.configure(border_color=color)
        self.canvas.itemconfig(self.core_orb, outline=color)
        for p in self.particles: self.canvas.itemconfig(p['id'], fill=color)

    # Window Dragging
    def _on_drag_start(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
    def _on_drag_motion(self, event):
        deltax = event.x - self._drag_data["x"]
        deltay = event.y - self._drag_data["y"]
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")
