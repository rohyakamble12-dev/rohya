import customtkinter as ctk
import threading
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import psutil
import time
import math
import random
from datetime import datetime

class VedaGUI(ctk.CTk):
    def __init__(self, on_send_callback, on_voice_callback, on_upload_callback=None, on_closing_callback=None):
        super().__init__()

        self.on_send_callback = on_send_callback
        self.on_voice_callback = on_voice_callback
        self.on_upload_callback = on_upload_callback
        self.on_closing_callback = on_closing_callback
        self.protocol_callback = None

        # HUD Configuration
        self.title("VEDA CORE")
        self.geometry("1100x650")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.92)
        self.configure(fg_color="#08080a")

        # Colors
        self.accent_color = "#00d4ff" # Cyan (Idle)
        self.think_color = "#ffcc00"  # Gold (Thinking)
        self.speak_color = "#00ff7f"  # Green (Speaking)
        self.alert_color = "#ff4b2b"  # Red (Alert)
        self.text_color = "#e0f7fa"
        self.border_color = "#1a1a20"

        # State
        self.veda_state = "idle" # idle, thinking, speaking, alert
        self.pulse_active = False
        self.camera_active = False
        self.cap = None
        self.last_raw_frame = None
        self.online = True
        self.running = True

        # Protocol Variables
        self.deep_search_var = tk.BooleanVar(value=False)
        self.private_var = tk.BooleanVar(value=False)
        self.context_var = tk.BooleanVar(value=True)

        # Movement tracking
        self._drag_data = {"x": 0, "y": 0}

        self._setup_layout()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Delay background tasks until main loop is ready
        self.after(1000, self._start_background_tasks)

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

        self.title_lbl = ctk.CTkLabel(self.top_bar, text="V E D A  -  G L O B A L  I N T E L",
                                      font=("Orbitron", 12, "bold"), text_color=self.accent_color)
        self.title_lbl.pack(side="left", padx=20)

        self.status_indicators = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.status_indicators.pack(side="right", padx=10)

        self.online_status = ctk.CTkLabel(self.status_indicators, text="● ONLINE", text_color="#00ff7f", font=("Orbitron", 9))
        self.online_status.pack(side="left", padx=10)

        self.sys_ready = ctk.CTkLabel(self.status_indicators, text="SYSTEM READY", text_color=self.accent_color, font=("Orbitron", 9))
        self.sys_ready.pack(side="left", padx=10)

        # --- LEFT PANEL ---
        self.left_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.left_panel.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")

        self.vis_frame = self._create_panel(self.left_panel, "OPTICAL FEED")
        self.cam_label = tk.Label(self.vis_frame, bg="#050507")
        self.cam_label.pack(fill="both", expand=True, padx=2, pady=2)

        self.perf_frame = self._create_panel(self.left_panel, "TELEMETRY")
        self._add_metric(self.perf_frame, "CPU", "cpu_bar", "cpu_val", self.accent_color)
        self._add_metric(self.perf_frame, "RAM", "ram_bar", "ram_val", "#b000ff")

        self.proto_frame = self._create_panel(self.left_panel, "PROTOCOLS")
        self._add_proto_cb(self.proto_frame, "DEEP RESEARCH", self.deep_search_var)
        self._add_proto_cb(self.proto_frame, "SECURE MODE", self.private_var)
        self._add_proto_cb(self.proto_frame, "REAL-TIME CONTEXT", self.context_var)

        # --- CENTER PANEL: THE EARTH CORE ---
        self.center_panel = ctk.CTkFrame(self, fg_color="#0d0d12", border_width=1, border_color=self.border_color)
        self.center_panel.grid(row=1, column=1, pady=15, sticky="nsew")

        self.canvas = tk.Canvas(self.center_panel, width=400, height=400, bg="#0d0d12", highlightthickness=0)
        self.canvas.pack(pady=20, expand=True)
        self._draw_hex_grid()
        self._init_earth_animation()

        self.ctrl_frame = ctk.CTkFrame(self.center_panel, fg_color="transparent")
        self.ctrl_frame.pack(pady=20)

        self.btn_cam = self._create_icon_btn(self.ctrl_frame, "📷 OFF", self.toggle_camera)
        self.btn_cam.configure(width=80)

        self.btn_upload = self._create_icon_btn(self.ctrl_frame, "📁", self.trigger_upload)

        self.btn_end = ctk.CTkButton(self.ctrl_frame, text="U N L O A D", width=100, height=35,
                                     fg_color="#201010", border_width=1, border_color=self.alert_color,
                                     hover_color=self.alert_color, font=("Orbitron", 11, "bold"), command=self.destroy)
        self.btn_end.pack(side="left", padx=10)

        self.btn_mic = self._create_icon_btn(self.ctrl_frame, "🎤", self.trigger_voice)

        # --- RIGHT PANEL ---
        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=1, column=2, padx=15, pady=15, sticky="nsew")

        self.comm_frame = self._create_panel(self.right_panel, "COMMUNICATION LOG")
        self.chat_display = ctk.CTkScrollableFrame(self.comm_frame, fg_color="#050507", corner_radius=0)
        self.chat_display.pack(fill="both", expand=True, padx=2, pady=2)

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

    def _draw_hex_grid(self):
        """Draws a subtle tech-style hexagonal grid in the background."""
        w, h = 400, 400
        size = 25
        for row in range(-1, 10):
            for col in range(-1, 10):
                x = col * size * 1.5
                y = row * size * math.sqrt(3)
                if col % 2 == 1:
                    y += (size * math.sqrt(3)) / 2

                # Draw hex outline
                points = []
                for i in range(6):
                    angle = math.radians(i * 60)
                    px = x + size * math.cos(angle)
                    py = y + size * math.sin(angle)
                    points.extend([px, py])

                self.canvas.create_polygon(points, outline="#1a1a25", fill="", width=1, tags="grid")

    def _init_earth_animation(self):
        """Initializes 3D points for the rotating earth globe."""
        self.canvas.delete("points") # Only delete points, keep grid
        self.points = []
        self.radius = 120
        self.angle_y = 0

        # Generate points on a sphere (Fibonacci lattice)
        num_points = 120
        phi = math.pi * (3. - math.sqrt(5.)) # golden angle

        for i in range(num_points):
            y = 1 - (i / float(num_points - 1)) * 2 # y from 1 to -1
            radius_at_y = math.sqrt(1 - y * y)
            theta = phi * i

            x = math.cos(theta) * radius_at_y
            z = math.sin(theta) * radius_at_y

            # Create dot on canvas
            dot = self.canvas.create_oval(0, 0, 0, 0, fill=self.accent_color, outline="", tags="points")
            self.points.append({'id': dot, 'x': x, 'y': y, 'z': z})

    def _start_background_tasks(self):
        threading.Thread(target=self._metrics_worker, daemon=True).start()
        threading.Thread(target=self._camera_worker, daemon=True).start()
        threading.Thread(target=self._network_worker, daemon=True).start()
        self._animate_loop()

    def _metrics_worker(self):
        while self.running:
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
        while self.running:
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
        """Manages the webcam resource and frame updates."""
        while self.running:
            try:
                if self.camera_active:
                    if self.cap is None or not self.cap.isOpened():
                        self.cap = cv2.VideoCapture(0)

                    if self.cap and self.cap.isOpened():
                        ret, frame = self.cap.read()
                        if ret:
                            self.last_raw_frame = frame
                            small_frame = cv2.resize(frame, (250, 150))
                            rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                            img = Image.fromarray(rgb_frame)
                            self.after(0, lambda i=img: self._update_cam_ui(i))
                else:
                    if self.cap is not None:
                        if self.cap.isOpened(): self.cap.release()
                        self.cap = None
                        self.last_raw_frame = None
            except Exception as e:
                print(f"Camera Worker Error: {e}")
            time.sleep(0.1)

    def _update_cam_ui(self, pil_img):
        if self.camera_active:
            # Add a subtle tech-overlay/tint
            img_tk = ImageTk.PhotoImage(image=pil_img)
            self.cam_label.img_tk = img_tk
            self.cam_label.configure(image=img_tk, text="")

    def _animate_loop(self):
        """Main animation loop for the rotating globe."""
        if not self.running: return
        t = time.time()

        # State-based parameters
        if self.veda_state == "thinking":
            color = self.think_color
            rotation_speed = 0.15
            pulse = (math.sin(t * 10) + 1) / 2 # Fast pulse
        elif self.veda_state == "speaking":
            color = self.speak_color
            rotation_speed = 0.1
            pulse = (math.sin(t * 5) + 1) / 2 # Medium pulse
        elif self.veda_state == "alert":
            color = self.alert_color
            rotation_speed = 0.2
            pulse = (math.sin(t * 15) + 1) / 2 # Rapid pulse
        else: # idle
            color = self.accent_color
            rotation_speed = 0.03
            pulse = (math.sin(t * 2) + 1) / 2 # Slow pulse

        self.angle_y += rotation_speed

        for p in self.points:
            # Rotate around Y axis
            x = p['x'] * math.cos(self.angle_y) - p['z'] * math.sin(self.angle_y)
            z = p['x'] * math.sin(self.angle_y) + p['z'] * math.cos(self.angle_y)
            y = p['y']

            # Project to 2D
            scale = (z + 2) / 3 # depth factor 0.33 to 1.0
            x_2d = 200 + x * self.radius * scale
            y_2d = 200 + y * self.radius * scale

            # Dot size and brightness
            d_size = 1 + scale * 2 + (pulse * 2 if self.veda_state != "idle" else 0)

            # Update canvas item
            self.canvas.coords(p['id'], x_2d - d_size, y_2d - d_size, x_2d + d_size, y_2d + d_size)
            self.canvas.itemconfig(p['id'], fill=color if scale > 0.5 else self.border_color)

        self.after(40, self._animate_loop)

    def set_state(self, state):
        """Updates Veda's current activity state."""
        self.veda_state = state.lower()

    def toggle_camera(self):
        self.camera_active = not self.camera_active
        if not self.camera_active:
            self.cam_label.configure(image="", text="FEED PAUSED", fg="grey")
            self.btn_cam.configure(fg_color="#121217", border_color=self.border_color, text="📷 OFF")
        else:
            self.cam_label.configure(text="INITIALIZING...")
            self.btn_cam.configure(fg_color=self.accent_color, border_color="#ffffff", text="📷 ON")

    def trigger_voice(self):
        self.sys_ready.configure(text="LISTENING...", text_color=self.alert_color)
        threading.Thread(target=self.on_voice_callback, daemon=True).start()

    def reset_voice_button(self):
        self.after(0, lambda: self.sys_ready.configure(text="SYSTEM READY", text_color=self.accent_color))
        self.set_state("idle")

    def set_voice_active(self, active):
        self.pulse_active = active
        if active:
            self.set_state("speaking")
            self.btn_mic.configure(fg_color=self.speak_color)
        else:
            self.set_state("idle")
            self.btn_mic.configure(fg_color="#121217")

    def update_chat(self, sender, message):
        self.after(0, lambda: self._update_chat_ui(sender, message))

    def _update_chat_ui(self, sender, message):
        is_user = sender.lower() == "user"
        is_system = sender.lower() == "system"

        # Bubble Container
        bubble_frame = ctk.CTkFrame(self.chat_display, fg_color="transparent")
        bubble_frame.pack(fill="x", padx=5, pady=2)

        # Alignment logic
        anchor = "e" if is_user else "w"
        color = "#1a1a25" if is_user else "#0a0a15"
        border_col = "#333340"

        if is_user:
            border_col = self.accent_color
        elif is_system:
            color = "#201010"
            border_col = self.alert_color
        else:
            border_col = self.speak_color if self.veda_state == "speaking" else self.accent_color

        # The Bubble
        bubble = ctk.CTkFrame(bubble_frame, fg_color=color, corner_radius=12, border_width=1,
                              border_color=border_col)
        bubble.pack(side="right" if is_user else ("left" if not is_system else "top"), padx=10)

        # Sender & Time
        header_f = ctk.CTkFrame(bubble, fg_color="transparent")
        header_f.pack(fill="x", padx=10, pady=(5, 0))

        sender_lbl = ctk.CTkLabel(header_f, text=sender.upper(), font=("Orbitron", 8, "bold"),
                                  text_color=self.accent_color if not is_user else "#888899")
        sender_lbl.pack(side="left")

        timestamp = datetime.now().strftime("%H:%M")
        time_lbl = ctk.CTkLabel(header_f, text=timestamp, font=("Consolas", 7), text_color="#555566")
        time_lbl.pack(side="right", padx=(10, 0))

        # Message text - using label with wrap
        msg_lbl = ctk.CTkLabel(bubble, text=message, font=("Consolas", 10), text_color="#cfd8dc",
                               wraplength=220, justify="left")
        msg_lbl.pack(padx=10, pady=5)

        # Auto-scroll to bottom
        self.chat_display._parent_canvas.yview_moveto(1.0)

    def send_message(self):
        msg = self.input_entry.get()
        if msg:
            self.update_chat("User", msg)
            self.input_entry.delete(0, "end")
            threading.Thread(target=self.on_send_callback, args=(msg,), daemon=True).start()

    def trigger_upload(self):
        from tkinter import filedialog
        file_paths = filedialog.askopenfilenames(
            title="Select File(s) for Veda to Process",
            filetypes=[("Documents", "*.pdf *.txt *.docx *.csv *.json *.zip"), ("All Files", "*.*")]
        )
        if file_paths and self.on_upload_callback:
            count = len(file_paths)
            msg = f"Processing {count} file(s)..." if count > 1 else f"Processing file: {file_paths[0]}"
            self.update_chat("System", msg)
            threading.Thread(target=self.on_upload_callback, args=(file_paths,), daemon=True).start()

    def _on_proto_change(self):
        if self.protocol_callback: self.protocol_callback()

    def on_protocol_toggle(self, name):
        self._on_proto_change()

    def show_suggestion(self, text):
        self.update_chat("System", f"Info: {text}")

    def set_theme_color(self, mood="calm"):
        colors = {
            "calm": "#00d4ff",
            "alert": "#ff4b2b",
            "success": "#00ff7f",
            "focus": "#ffff00",
            "stealth": "#707070",
            "security": "#b000ff"
        }
        color = colors.get(mood.lower(), colors["calm"])
        self.accent_color = color

        if mood == "alert": self.set_state("alert")
        else: self.set_state("idle")

        self.title_lbl.configure(text_color=color)
        self.sys_ready.configure(text_color=color)
        self.cpu_val.configure(text_color=color)
        self.cpu_bar.configure(progress_color=color)
        self.input_entry.configure(border_color=color)

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

    def on_closing(self):
        """Clean shutdown procedure."""
        self.running = False
        self.veda_state = "idle"

        if self.on_closing_callback:
            try: self.on_closing_callback()
            except: pass

        # Release resources
        if self.cap is not None:
            self.cap.release()
            self.cap = None

        self.destroy()
