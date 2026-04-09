import customtkinter as ctk
import threading
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
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
        self.glitch_active = False
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

        self.perf_frame = self._create_panel(self.left_panel, "OBSERVABILITY")
        self._add_metric(self.perf_frame, "CPU", "cpu_bar", "cpu_val", self.accent_color)
        self._add_metric(self.perf_frame, "RAM", "ram_bar", "ram_val", "#b000ff")

        # Extended Observability
        self.obs_data = ctk.CTkFrame(self.perf_frame, fg_color="transparent")
        self.obs_data.pack(fill="x", padx=10, pady=5)

        self.thread_lbl = ctk.CTkLabel(self.obs_data, text="THREADS: 0", font=("Orbitron", 8), text_color="#00ff7f")
        self.thread_lbl.pack(anchor="w")

        self.plugin_lbl = ctk.CTkLabel(self.obs_data, text="ACTIVE PLUGINS: 0", font=("Orbitron", 8), text_color="#00d4ff")
        self.plugin_lbl.pack(anchor="w")

        self.risk_lbl = ctk.CTkLabel(self.obs_data, text="GOVERNANCE: NOMINAL", font=("Orbitron", 8), text_color="#00ff7f")
        self.risk_lbl.pack(anchor="w")

        self.event_lbl = ctk.CTkLabel(self.obs_data, text="EVENT QUEUE: 0", font=("Orbitron", 8), text_color="#ffcc00")
        self.event_lbl.pack(anchor="w")

        self.rollback_lbl = ctk.CTkLabel(self.obs_data, text="ROLLBACK: INACTIVE", font=("Orbitron", 8), text_color="#555555")
        self.rollback_lbl.pack(anchor="w")

        self.self_heal_lbl = ctk.CTkLabel(self.obs_data, text="SELF-HEAL: INACTIVE", font=("Orbitron", 8), text_color="#555555")
        self.self_heal_lbl.pack(anchor="w")

        self.exec_frame = self._create_panel(self.left_panel, "EXECUTION CORE")
        self.exec_list = ctk.CTkTextbox(self.exec_frame, height=120, font=("Consolas", 9), fg_color="#050507", text_color="#cfd8dc")
        self.exec_list.pack(fill="both", expand=True, padx=5, pady=5)

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

        self.tactical_frame = ctk.CTkFrame(self.right_panel, height=60, fg_color="#0a0a15", border_width=1, border_color=self.border_color)
        self.tactical_frame.pack(fill="x", pady=(0, 10))
        self.tactical_lbl = ctk.CTkLabel(self.tactical_frame, text="TACTICAL STATUS: NOMINAL", font=("Orbitron", 9), text_color=self.accent_color)
        self.tactical_lbl.pack(pady=15)

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
        """Initializes 3D points for the rotating neural globe with connecting meshes."""
        self.canvas.delete("points", "lines")
        self.points = []
        self.radius = 130
        self.angle_y = 0

        num_points = 100
        phi = math.pi * (3. - math.sqrt(5.))

        for i in range(num_points):
            y = 1 - (i / float(num_points - 1)) * 2
            radius_at_y = math.sqrt(1 - y * y)
            theta = phi * i
            x = math.cos(theta) * radius_at_y
            z = math.sin(theta) * radius_at_y

            dot = self.canvas.create_oval(0, 0, 0, 0, fill=self.accent_color, outline="", tags="points")
            self.points.append({'id': dot, 'x': x, 'y': y, 'z': z, 'neighbors': []})

        # Pre-calculate nearest neighbors for mesh
        for i in range(len(self.points)):
            p1 = self.points[i]
            distances = []
            for j in range(len(self.points)):
                if i == j: continue
                p2 = self.points[j]
                d = math.sqrt((p1['x']-p2['x'])**2 + (p1['y']-p2['y'])**2 + (p1['z']-p2['z'])**2)
                distances.append((d, j))
            distances.sort()
            # Connect to 3 nearest
            for d, idx in distances[:3]:
                if d < 0.8:
                    line = self.canvas.create_line(0, 0, 0, 0, fill=self.accent_color, width=1, tags="lines", state="hidden")
                    p1['neighbors'].append({'idx': idx, 'line': line})

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
                dsk = psutil.disk_usage('/').percent

                # Network load (Simplified as activity indicator)
                net_io_1 = psutil.net_io_counters()
                time.sleep(1)
                net_io_2 = psutil.net_io_counters()
                # Use a log scale or simple cap for visibility
                net_activity = min(100, (net_io_2.bytes_sent + net_io_2.bytes_recv - net_io_1.bytes_sent - net_io_1.bytes_recv) / 10000)

                self.after(0, lambda c=cpu, r=ram, d=dsk, n=net_activity: self._update_metrics_ui(c, r, d, n))
            except Exception as e: pass
            time.sleep(2)

    def set_governance_risk(self, risk_level):
        colors = {"Low": "#00ff7f", "Moderate": "#ffcc00", "High": "#ff4b2b", "Critical": "#ff0000"}
        color = colors.get(risk_level, "#ffffff")
        self.risk_lbl.configure(text=f"RISK: {risk_level.upper()}", text_color=color)

    def set_rollback_state(self, active=True):
        if active:
            self.rollback_lbl.configure(text="ROLLBACK: ACTIVE", text_color=self.alert_color)
            self.set_state("alert")
        else:
            self.rollback_lbl.configure(text="ROLLBACK: INACTIVE", text_color="#555555")

    def set_self_heal_state(self, active=True):
        if active:
            self.self_heal_lbl.configure(text="SELF-HEAL: ACTIVE", text_color=self.think_color)
            self.set_state("thinking")
        else:
            self.self_heal_lbl.configure(text="SELF-HEAL: INACTIVE", text_color="#555555")

    def update_exec_visualizer(self, plan, current_step_idx=0):
        """Visualizes the multi-step execution plan on the HUD."""
        self.exec_list.configure(state="normal")
        self.exec_list.delete("1.0", "end")
        for i, step in enumerate(plan):
            marker = "►" if i == current_step_idx else ("✓" if i < current_step_idx else "○")
            color = self.speak_color if i == current_step_idx else (self.accent_color if i < current_step_idx else "#555555")
            self.exec_list.insert("end", f"{marker} Step {i+1}: {step['intent'].upper()}\n")
        self.exec_list.configure(state="disabled")

    def _update_metrics_ui(self, cpu, ram, dsk, net):
        self.cpu_bar.set(cpu/100)
        self.cpu_val.configure(text=f"{cpu}%")
        self.ram_bar.set(ram/100)
        self.ram_val.configure(text=f"{ram}%")

        # Update Extended Observability
        import threading
        from veda.core.registry import registry

        t_count = threading.active_count()
        self.thread_lbl.configure(text=f"THREADS: {t_count}")

        pm = registry.get("plugin_manager")
        if pm:
            self.plugin_lbl.configure(text=f"PLUGINS: {len(pm.plugins)}")

        assistant = registry.get("assistant")
        if assistant:
            self.event_lbl.configure(text=f"QUEUE: {len(assistant.execution_queue)}")

    def _network_worker(self):
        import requests
        prev_status = True
        while self.running:
            try:
                requests.get("https://www.google.com", timeout=2)
                self.online = True
            except Exception as e: self.online = False

            if self.online != prev_status:
                msg = "Connection restored. Systems online." if self.online else "Warning: Internet connection lost. Core functions limited."
                self.after(0, lambda m=msg: self.update_chat("System", m))
                prev_status = self.online

            self.after(0, self._update_status_ui)
            time.sleep(15)

    def _update_status_ui(self):
        if self.online:
            self.online_status.configure(text="● ONLINE", text_color="#00ff7f")
        else:
            self.online_status.configure(text="○ OFFLINE", text_color=self.alert_color)

    def stream_to_chat(self, token):
        """Appends a token to the currently active stream bubble with thread-safety."""
        if self.running and hasattr(self, '_stream_target') and self._stream_target:
            self.after(0, lambda: self._append_token(token))

    def _append_token(self, token):
        if not self.running: return
        try:
            current = self._stream_target.cget("text")
            self._stream_target.configure(text=current + token)
            self.chat_display._parent_canvas.yview_moveto(1.0)
        except Exception: pass

    def _camera_worker(self):
        """Manages the webcam resource and frame updates with safety."""
        while self.running:
            try:
                if self.camera_active:
                    if self.cap is None or not self.cap.isOpened():
                        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # Faster on Windows

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
            # Realistic Scanline Overlay
            draw = ImageDraw.Draw(pil_img)
            w, h = pil_img.size
            for i in range(0, h, 4):
                draw.line([(0, i), (w, i)], fill=(0, 212, 255, 30), width=1)

            img_tk = ImageTk.PhotoImage(image=pil_img)
            self.cam_label.img_tk = img_tk
            self.cam_label.configure(image=img_tk, text="")

    def _animate_loop(self):
        """Main animation loop for the rotating globe with advanced effects."""
        if not self.running: return
        t = time.time()

        # State-based parameters
        if self.veda_state == "thinking":
            color = self.think_color
            rotation_speed = 0.18
            pulse = (math.sin(t * 12) + 1) / 2
        elif self.veda_state == "speaking":
            color = self.speak_color
            rotation_speed = 0.12
            pulse = (math.sin(t * 6) + 1) / 2
        elif self.veda_state == "alert":
            color = self.alert_color
            rotation_speed = 0.25
            pulse = (math.sin(t * 18) + 1) / 2
        else: # idle (Heartbeat pulse)
            color = self.accent_color
            rotation_speed = 0.04
            # Double heartbeat effect
            pulse = math.pow(math.sin(t * 3), 10) * 0.4 + math.pow(math.sin(t * 3 - 0.5), 10) * 0.2

        # Random Digital Glitch Effect
        if random.random() < 0.01: self.glitch_active = True
        if self.glitch_active:
            if random.random() < 0.3:
                color = "#ffffff" # Glitch flash
            if random.random() < 0.2:
                self.glitch_active = False # End glitch

        self.angle_y += rotation_speed

        rotated_points = []
        for p in self.points:
            x = p['x'] * math.cos(self.angle_y) - p['z'] * math.sin(self.angle_y)
            z = p['x'] * math.sin(self.angle_y) + p['z'] * math.cos(self.angle_y)
            y = p['y']
            scale = (z + 2) / 3
            x_2d = 200 + x * self.radius * scale
            y_2d = 200 + y * self.radius * scale
            d_size = 1 + scale * 1.5 + (pulse * 2 if self.veda_state != "idle" else 0)

            self.canvas.coords(p['id'], x_2d - d_size, y_2d - d_size, x_2d + d_size, y_2d + d_size)
            self.canvas.itemconfig(p['id'], fill=color if scale > 0.6 else self.border_color)
            rotated_points.append({'x': x_2d, 'y': y_2d, 'scale': scale})

        # Draw connecting lines (Neural Mesh)
        for i, p in enumerate(self.points):
            p_rot = rotated_points[i]
            for neighbor in p['neighbors']:
                n_rot = rotated_points[neighbor['idx']]
                if p_rot['scale'] > 0.7 and n_rot['scale'] > 0.7:
                    self.canvas.coords(neighbor['line'], p_rot['x'], p_rot['y'], n_rot['x'], n_rot['y'])
                    self.canvas.itemconfig(neighbor['line'], state="normal", fill=color)
                else:
                    self.canvas.itemconfig(neighbor['line'], state="hidden")

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
        self._play_ui_sound("listen")
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

    def _update_chat_ui(self, sender, message, is_streaming=False):
        """Thread-safe UI update for the chat HUD with content safety."""
        if not self.running: return
        is_user = sender.lower() == "user"
        is_system = sender.lower() == "system"

        # 1. Content Safety: Length Truncation for UI stability
        MAX_UI_LEN = 1500
        if len(message) > MAX_UI_LEN:
            message = message[:MAX_UI_LEN] + "\n\n[Tactical Truncation: Output exceeds HUD capacity.]"

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

        # Realism: Glass-morphism effect via subtle opacity and highlights

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
        msg_lbl = ctk.CTkLabel(bubble, text=message, font=("Consolas", 11), text_color="#cfd8dc",
                               wraplength=300, justify="left")
        msg_lbl.pack(padx=12, pady=8)

        if is_streaming:
            self._stream_target = msg_lbl

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
        # HUD-only suggestion to prevent chat spam
        self.tactical_lbl.configure(text=f"SUGGESTION: {text.upper()}", text_color=self.think_color)
        self.after(5000, lambda: self.tactical_lbl.configure(text="TACTICAL STATUS: NOMINAL", text_color=self.accent_color))

    def update_tactical_status(self, text, color=None):
        color = color or self.think_color
        self.tactical_lbl.configure(text=text.upper(), text_color=color)
        self.after(10000, lambda: self.tactical_lbl.configure(text="TACTICAL STATUS: NOMINAL", text_color=self.accent_color))

    def set_theme_color(self, mood="calm"):
        # Play tactical blip on theme change
        self._play_ui_sound("confirm")

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
        if not self.running: return
        deltax = event.x - self._drag_data["x"]
        deltay = event.y - self._drag_data["y"]
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def _play_ui_sound(self, sound_type):
        """Tactical HUD Sound Effects."""
        try:
            import pygame
            if not pygame.mixer.get_init(): pygame.mixer.init()
            # In a real impl we'd load .wav files. Simulating blips.
        except Exception: pass

    def on_closing(self):
        """Clean shutdown procedure."""
        self.running = False
        self.veda_state = "idle"

        if self.on_closing_callback:
            try:
                self.on_closing_callback()
            except Exception as e:
                from veda.utils.logger import logger
                logger.error(f"Sovereign Shutdown Error: {e}")

        # Release resources
        if self.cap is not None:
            self.cap.release()
            self.cap = None

        self.destroy()
