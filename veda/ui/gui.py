import customtkinter as ctk
import threading
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import psutil
import time

class VedaGUI(ctk.CTk):
    def __init__(self, on_send_callback, on_voice_callback):
        super().__init__()

        self.on_send_callback = on_send_callback
        self.on_voice_callback = on_voice_callback
        self.protocol_callback = None

        # HUD Configuration - Wide Dashboard
        self.title("VEDA CORE INTERFACE")
        self.geometry("1200x700")
        self.overrideredirect(True) # Remove standard title bar
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.95)
        self.configure(fg_color="#0a0a0c") # Very dark black

        # Colors
        self.accent_color = "#00d4ff" # Jarvis Cyan
        self.alert_color = "#ff4b2b"
        self.text_color = "#e0f7fa"
        self.bg_secondary = "#121217"

        # State
        self.pulse_active = False
        self.camera_active = True
        self.cap = None
        self.last_raw_frame = None

        # Protocol Variables for Assistant sync
        self.deep_search_var = tk.BooleanVar(value=False)
        self.private_var = tk.BooleanVar(value=False)
        self.context_var = tk.BooleanVar(value=True)

        # Dragging functionality
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.do_move)

        self._setup_layout()
        self._start_background_tasks()

    def _setup_layout(self):
        self.grid_columnconfigure(0, weight=1, minsize=250) # Left: Visual/Metrics
        self.grid_columnconfigure(1, weight=2, minsize=500) # Center: Core
        self.grid_columnconfigure(2, weight=1, minsize=350) # Right: Transcript
        self.grid_rowconfigure(1, weight=1)

        # --- TOP NAVIGATION BAR ---
        self.top_bar = ctk.CTkFrame(self, height=50, fg_color="#050507", corner_radius=0)
        self.top_bar.grid(row=0, column=0, columnspan=3, sticky="ew")

        # Left side buttons
        self.nav_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.nav_frame.pack(side="left", padx=20)

        self.btn_dash = self._create_nav_btn("DASHBOARD", active=True)
        self.btn_contacts = self._create_nav_btn("CONTACTS")
        self.btn_notes = self._create_nav_btn("NOTES")
        self.btn_connect = self._create_nav_btn("CONNECT")
        self.btn_phone = self._create_nav_btn("PHONE")

        # Right side status
        self.status_indicators = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.status_indicators.pack(side="right", padx=20)

        self.online_status = ctk.CTkLabel(self.status_indicators, text="● ONLINE", text_color="#00ff7f", font=("Orbitron", 10))
        self.online_status.pack(side="left", padx=10)

        self.sys_ready = ctk.CTkLabel(self.status_indicators, text="SYSTEM READY", text_color=self.accent_color, font=("Orbitron", 10))
        self.sys_ready.pack(side="left", padx=10)

        # --- LEFT COLUMN: VISUAL & METRICS ---
        self.left_col = ctk.CTkFrame(self, fg_color="transparent")
        self.left_col.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Visual Input
        self.vis_frame = self._create_section_frame(self.left_col, "VISUAL INPUT")
        self.cam_label = tk.Label(self.vis_frame, bg="black")
        self.cam_label.pack(fill="both", expand=True, padx=5, pady=5)
        self.cam_off_label = ctk.CTkLabel(self.cam_label, text="VIDEO FEED OFFLINE", text_color="grey")

        # System Metrics
        self.metrics_frame = self._create_section_frame(self.left_col, "SYSTEM METRICS")

        self.cpu_usage_frame = ctk.CTkFrame(self.metrics_frame, fg_color="transparent")
        self.cpu_usage_frame.pack(fill="x", padx=10, pady=5)
        self.cpu_label = ctk.CTkLabel(self.cpu_usage_frame, text="CPU LOAD", font=("Consolas", 11))
        self.cpu_label.pack(side="left")
        self.cpu_val = ctk.CTkLabel(self.cpu_usage_frame, text="0%", font=("Consolas", 11, "bold"), text_color=self.accent_color)
        self.cpu_val.pack(side="right")
        self.cpu_bar = ctk.CTkProgressBar(self.metrics_frame, progress_color=self.accent_color)
        self.cpu_bar.set(0)
        self.cpu_bar.pack(fill="x", padx=10, pady=(0, 10))

        self.ram_usage_frame = ctk.CTkFrame(self.metrics_frame, fg_color="transparent")
        self.ram_usage_frame.pack(fill="x", padx=10, pady=5)
        self.ram_label = ctk.CTkLabel(self.ram_usage_frame, text="RAM USAGE", font=("Consolas", 11))
        self.ram_label.pack(side="left")
        self.ram_val = ctk.CTkLabel(self.ram_usage_frame, text="0%", font=("Consolas", 11, "bold"), text_color="#b000ff")
        self.ram_val.pack(side="right")
        self.ram_bar = ctk.CTkProgressBar(self.metrics_frame, progress_color="#b000ff")
        self.ram_bar.set(0)
        self.ram_bar.pack(fill="x", padx=10, pady=(0, 10))

        # Top Processes
        self.proc_frame = self._create_section_frame(self.left_col, "TOP PROCESSES")
        self.proc_text = ctk.CTkTextbox(self.proc_frame, height=120, font=("Consolas", 10), fg_color="transparent")
        self.proc_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Protocols
        self.proto_frame = self._create_section_frame(self.left_col, "SYSTEM PROTOCOLS")
        self.cb_research = ctk.CTkCheckBox(self.proto_frame, text="DEEP RESEARCH", variable=self.deep_search_var,
                                           command=self._on_proto_change, font=("Orbitron", 8), text_color=self.accent_color)
        self.cb_research.pack(anchor="w", padx=10, pady=2)

        self.cb_secure = ctk.CTkCheckBox(self.proto_frame, text="SECURE MODE", variable=self.private_var,
                                         command=self._on_proto_change, font=("Orbitron", 8), text_color=self.accent_color)
        self.cb_secure.pack(anchor="w", padx=10, pady=2)

        self.cb_context = ctk.CTkCheckBox(self.proto_frame, text="REAL-TIME CONTEXT", variable=self.context_var,
                                          command=self._on_proto_change, font=("Orbitron", 8), text_color=self.accent_color)
        self.cb_context.pack(anchor="w", padx=10, pady=2)

        # --- CENTER COLUMN: CORE SYSTEM ---
        self.center_col = ctk.CTkFrame(self, fg_color="#0d0d12", border_width=1, border_color="#1f1f26")
        self.center_col.grid(row=1, column=1, padx=5, pady=10, sticky="nsew")

        self.core_label = ctk.CTkLabel(self.center_col, text="(( CORE SYSTEM ))", font=("Orbitron", 12), text_color=self.accent_color)
        self.core_label.pack(pady=10)

        # Core Animation Canvas
        self.canvas = tk.Canvas(self.center_col, width=400, height=400, bg="#0d0d12", highlightthickness=0)
        self.canvas.pack(pady=20, expand=True)
        self._draw_core_base()

        # Center Controls
        self.controls_frame = ctk.CTkFrame(self.center_col, fg_color="transparent")
        self.controls_frame.pack(pady=20)

        self.btn_cam_toggle = ctk.CTkButton(self.controls_frame, text="📷", width=50, fg_color="#1f1f26", command=self.toggle_camera)
        self.btn_cam_toggle.pack(side="left", padx=10)

        self.btn_end = ctk.CTkButton(self.controls_frame, text="U END", width=120, fg_color=self.alert_color, font=("Orbitron", 14, "bold"), command=self.destroy)
        self.btn_end.pack(side="left", padx=10)

        self.btn_mic = ctk.CTkButton(self.controls_frame, text="🎤", width=50, fg_color="#1f1f26", command=self.trigger_voice)
        self.btn_mic.pack(side="left", padx=10)

        # --- RIGHT COLUMN: TRANSCRIPT ---
        self.right_col = ctk.CTkFrame(self, fg_color="transparent")
        self.right_col.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        self.trans_frame = self._create_section_frame(self.right_col, "TRANSCRIPT")
        self.chat_display = ctk.CTkTextbox(self.trans_frame, font=("Consolas", 12), fg_color="#08080a", text_color="#cfd8dc")
        self.chat_display.pack(fill="both", expand=True, padx=5, pady=5)
        self.chat_display.configure(state="disabled")

        # Input Area
        self.input_frame = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.input_frame.pack(fill="x", pady=(10, 0))
        self.input_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Awaiting command...", height=40,
                                        fg_color="#08080a", border_color=self.accent_color)
        self.input_entry.pack(fill="x")
        self.input_entry.bind("<Return>", lambda e: self.send_message())

    def _create_nav_btn(self, text, active=False):
        color = self.accent_color if active else "transparent"
        btn = ctk.CTkButton(self.nav_frame, text=text, width=100, height=30,
                             fg_color=color, text_color="white" if active else "grey",
                             hover_color="#1f1f26", corner_radius=5, font=("Orbitron", 9))
        btn.pack(side="left", padx=2)
        return btn

    def _create_section_frame(self, parent, title):
        frame = ctk.CTkFrame(parent, fg_color="#0d0d12", border_width=1, border_color="#1f1f26")
        frame.pack(fill="both", expand=True, pady=5)

        label_frame = ctk.CTkFrame(frame, height=25, fg_color="#16161d", corner_radius=0)
        label_frame.pack(fill="x")

        title_lbl = ctk.CTkLabel(label_frame, text=f"■ {title}", font=("Orbitron", 10, "bold"), text_color=self.accent_color)
        title_lbl.pack(side="left", padx=10)

        return frame

    def _draw_core_base(self):
        """Draws the initial core UI with multiple rings and particles."""
        self.canvas.delete("all")
        # Rings for rotation effect
        self.ring1 = self.canvas.create_oval(30, 30, 370, 370, outline="#1f1f26", width=1, dash=(5, 10))
        self.ring2 = self.canvas.create_oval(60, 60, 340, 340, outline="#00d4ff", width=1, dash=(2, 4))
        self.ring3 = self.canvas.create_oval(80, 80, 320, 320, outline="#1f1f26", width=2)

        # Inner glowing orb (to be animated)
        self.core_orb = self.canvas.create_oval(120, 120, 280, 280, fill="#002b36", outline=self.accent_color, width=2)

        # Particle placeholders
        self.particles = []
        import random
        for _ in range(80):
            x = random.randint(150, 250)
            y = random.randint(150, 250)
            p = self.canvas.create_oval(x, y, x+2, y+2, fill=self.accent_color, outline="")
            self.particles.append({'id': p, 'speed': random.uniform(0.5, 2.0), 'angle': random.uniform(0, 6.28)})

    def _start_background_tasks(self):
        threading.Thread(target=self._update_metrics_loop, daemon=True).start()
        threading.Thread(target=self._update_camera_loop, daemon=True).start()
        self._animate_core_loop()

    def _update_metrics_loop(self):
        while True:
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent

                # Check internet connectivity
                import requests
                try:
                    requests.get("https://www.google.com", timeout=1)
                    online = True
                except:
                    online = False

                # Get top processes
                processes = sorted(psutil.process_iter(['name', 'cpu_percent']),
                                  key=lambda p: p.info['cpu_percent'], reverse=True)[:5]
                proc_str = "APP NAME          CPU\n" + "-"*25 + "\n"
                for p in processes:
                    proc_str += f"{p.info['name'][:15]:<16} {p.info['cpu_percent']:>5}%\n"

                self.after(0, lambda: self._update_metrics_ui(cpu, ram, proc_str, online))
            except:
                pass
            time.sleep(2)

    def _update_metrics_ui(self, cpu, ram, proc_str, online):
        self.cpu_bar.set(cpu/100)
        self.cpu_val.configure(text=f"{cpu}%")
        self.ram_bar.set(ram/100)

        if online:
            self.online_status.configure(text="● ONLINE", text_color="#00ff7f")
        else:
            self.online_status.configure(text="○ OFFLINE", text_color=self.alert_color)

        self.ram_val.configure(text=f"{ram}%")
        self.proc_text.configure(state="normal")
        self.proc_text.delete("1.0", "end")
        self.proc_text.insert("1.0", proc_str)
        self.proc_text.configure(state="disabled")

    def _update_camera_loop(self):
        self.cap = cv2.VideoCapture(0)
        while True:
            if self.camera_active and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    self.last_raw_frame = frame.copy()
                    # Resize to fit the label
                    frame = cv2.resize(frame, (240, 160))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame)
                    img_tk = ImageTk.PhotoImage(image=img)
                    self.after(0, lambda: self._update_cam_ui(img_tk))
            else:
                self.after(0, lambda: self.cam_label.configure(image=""))
            time.sleep(0.05)

    def _update_cam_ui(self, img_tk):
        self.cam_label.img_tk = img_tk
        self.cam_label.configure(image=img_tk)
        self.cam_off_label.pack_forget()

    def _animate_core_loop(self):
        """Animates the central core with rotation, pulsing, and particle movement."""
        import math
        import random

        t = time.time()

        # Rotation logic for rings (visual only via dash shift if possible, or just skip for now)
        # Pulse intensity increases when Veda is speaking
        speed_mult = 5 if self.pulse_active else 2
        pulse = (math.sin(t * speed_mult) + 1) / 2

        size_base = 120
        size_adj = pulse * (20 if self.pulse_active else 8)
        self.canvas.coords(self.core_orb,
                           200 - (size_base + size_adj), 200 - (size_base + size_adj),
                           200 + (size_base + size_adj), 200 + (size_base + size_adj))

        # Color shift
        if self.pulse_active:
            self.canvas.itemconfig(self.core_orb, fill="#005d7a", outline="#ffffff")
        else:
            self.canvas.itemconfig(self.core_orb, fill="#001a21", outline=self.accent_color)

        # Move particles in circular patterns
        for p_data in self.particles:
            p = p_data['id']
            p_data['angle'] += 0.05 * p_data['speed']
            dist = 60 + pulse * 40
            x = 200 + math.cos(p_data['angle']) * dist
            y = 200 + math.sin(p_data['angle']) * dist
            self.canvas.coords(p, x-1, y-1, x+1, y+1)

            # Random twinkle
            if random.random() > 0.9:
                self.canvas.itemconfig(p, fill="white" if self.pulse_active else self.accent_color)

        self.after(40, self._animate_core_loop)

    def toggle_camera(self):
        self.camera_active = not self.camera_active
        if not self.camera_active:
            self.cam_off_label.pack(expand=True)
        else:
            self.cam_off_label.pack_forget()

    def set_theme_color(self, mood="calm"):
        """Changes the HUD accent color based on Veda's 'mood' or system state."""
        moods = {
            "calm": "#00d4ff",     # Jarvis Cyan
            "alert": "#ff4b2b",    # Alert Red
            "success": "#00ff7f",  # Success Green
            "focus": "#ffff00",    # Focus Yellow
            "stealth": "#707070"   # Stealth Grey
        }
        color = moods.get(mood.lower(), moods["calm"])
        self.accent_color = color

        # Update UI elements
        self.sys_ready.configure(text_color=color)
        self.cpu_val.configure(text_color=color)
        self.cpu_bar.configure(progress_color=color)
        self.input_entry.configure(border_color=color)
        self.btn_mic.configure(fg_color=color if self.pulse_active else "#1f1f26")

        # Update checkbox colors
        self.cb_research.configure(text_color=color)
        self.cb_secure.configure(text_color=color)
        self.cb_context.configure(text_color=color)

    def set_voice_active(self, active):
        self.pulse_active = active
        if active:
            self.btn_mic.configure(fg_color=self.accent_color)
        else:
            self.btn_mic.configure(fg_color="#1f1f26")

    def update_chat(self, sender, message):
        self.after(0, self._update_chat_ui, sender, message)

    def _update_chat_ui(self, sender, message):
        self.chat_display.configure(state="normal")
        color = self.accent_color if sender.lower() == "veda" else "#ffffff"
        self.chat_display.insert("end", f"{sender.upper()}: ", ("sender",))
        self.chat_display.insert("end", f"{message}\n\n")
        self.chat_display.tag_config("sender", foreground=color, font=("Consolas", 12, "bold"))
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def send_message(self):
        message = self.input_entry.get()
        if message:
            self.update_chat("User", message)
            self.input_entry.delete(0, "end")
            threading.Thread(target=self.on_send_callback, args=(message,), daemon=True).start()

    def trigger_voice(self):
        self.sys_ready.configure(text="LISTENING...", text_color=self.alert_color)
        threading.Thread(target=self.on_voice_callback, daemon=True).start()

    def reset_voice_button(self):
        self.after(0, lambda: self.sys_ready.configure(text="SYSTEM READY", text_color=self.accent_color))

    def show_suggestion(self, text):
        # We can show this in the transcript or a dedicated tooltip
        self.update_chat("System", f"Suggestion: {text}")

    def _on_proto_change(self):
        if self.protocol_callback:
            self.protocol_callback()

    def on_protocol_toggle(self, name):
        """Called externally to update UI state if protocol changes via voice."""
        self._on_proto_change()

    # Window movement
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    def stop_move(self, event):
        self.x = None
        self.y = None
    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")
