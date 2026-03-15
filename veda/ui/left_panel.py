import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import threading
import psutil
import time
import logging
import random
import math
from veda.ui.base import VedaPanel

logger = logging.getLogger("VEDA")

class LeftPanel(VedaPanel):
    def __init__(self, master, assistant):
        super().__init__(master, "Observability")
        self.assistant = assistant
        self.state = "idle"

        # 1. Optical Feed with Moving Scanline
        self.cam_frame = ctk.CTkFrame(self, fg_color="black", height=180, border_width=1, border_color="#1a1a20")
        self.cam_frame.pack(fill="x", padx=10, pady=10)
        self.cam_label = ctk.CTkLabel(self.cam_frame, text="LINKING OPTICS...", font=("Consolas", 10))
        self.cam_label.pack(expand=True, fill="both")
        self.scanline_y = 0

        # 2. Tactical Pulse (ECG Monitor)
        self.pulse_canvas = ctk.CTkCanvas(self, height=60, bg="#050507", highlightthickness=0)
        self.pulse_canvas.pack(fill="x", padx=10, pady=5)
        self.pulse_points = [0] * 50

        # 3. Metrics
        self.metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.metrics_frame.pack(fill="x", padx=10, pady=5)

        self.cpu_label = ctk.CTkLabel(self.metrics_frame, text="CPU USAGE", font=("Orbitron", 10))
        self.cpu_label.pack(anchor="w")
        self.cpu_bar = ctk.CTkProgressBar(self.metrics_frame, height=8)
        self.cpu_bar.pack(fill="x", pady=(2, 8))
        self.register_accent_widget(self.cpu_bar, "progress")

        self.ram_label = ctk.CTkLabel(self.metrics_frame, text="RAM ALLOCATION", font=("Orbitron", 10))
        self.ram_label.pack(anchor="w")
        self.ram_bar = ctk.CTkProgressBar(self.metrics_frame, height=8)
        self.ram_bar.pack(fill="x", pady=(2, 10))
        self.register_accent_widget(self.ram_bar, "progress")

        # 4. Audio Visualizer (Simulated)
        self.audio_viz_frame = ctk.CTkFrame(self, height=50, fg_color="#050507", border_width=1, border_color="#1a1a20")
        self.audio_viz_frame.pack(fill="x", padx=10, pady=(2, 10))
        self.audio_bars = []
        for i in range(15):
            bar = ctk.CTkProgressBar(self.audio_viz_frame, orientation="vertical", width=8, height=40)
            bar.pack(side="left", padx=2, pady=5)
            bar.set(0)
            self.audio_bars.append(bar)
            self.register_accent_widget(bar, "progress")

        # 5. Subsystem Metrics
        self.obs_box = ctk.CTkTextbox(self, height=80, font=("Consolas", 10), fg_color="#050507", border_width=1, border_color="#1a1a20")
        self.obs_box.pack(fill="x", padx=10, pady=(2, 10))
        self._refresh_obs_text()
        self.obs_box.configure(state="disabled")

        # 6. Tactical Plan
        self.plan_display = ctk.CTkTextbox(self, height=40, font=("Consolas", 9), fg_color="#050507", text_color="#aaaaaa")
        self.plan_display.pack(fill="x", padx=10, pady=(2, 10))
        self.plan_display.insert("0.0", "> Systems Standby.")
        self.plan_display.configure(state="disabled")

        self.start_workers()

    def _refresh_obs_text(self, threads=8, queue=0):
        self.obs_box.configure(state="normal")
        self.obs_box.delete("1.0", "end")
        text = f"THREADS: {threads} ACTIVE\n"
        text += f"NEURAL CTX: 4.2k tokens\n"
        text += f"GOVERNANCE: PASSIVE\n"
        text += f"SELF-HEAL: ENABLED"
        self.obs_box.insert("1.0", text)
        self.obs_box.configure(state="disabled")

    def start_workers(self):
        threading.Thread(target=self._metrics_worker, daemon=True).start()
        threading.Thread(target=self._camera_worker, daemon=True).start()
        self._audio_viz_loop()
        self._pulse_loop()

    def _pulse_loop(self):
        self.pulse_canvas.delete("pulse")
        color = self.accent_color

        # Shift points
        self.pulse_points.pop(0)
        # Create heartbeat spike logic
        t = time.time()
        if math.sin(t*5) > 0.9:
             val = random.uniform(10, 40)
        else:
             val = random.uniform(25, 30)
        self.pulse_points.append(val)

        # Draw ECG
        w = 260
        step = w / len(self.pulse_points)
        for i in range(len(self.pulse_points)-1):
            self.pulse_canvas.create_line(i*step, self.pulse_points[i], (i+1)*step, self.pulse_points[i+1], fill=color, tags="pulse")

        self.after(50, self._pulse_loop)

    def _metrics_worker(self):
        while True:
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                self.after(0, self._update_metrics_ui, cpu, ram)
            except: pass
            time.sleep(2)

    def _update_metrics_ui(self, cpu, ram):
        self.cpu_bar.set(cpu/100)
        self.ram_bar.set(ram/100)

    def _audio_viz_loop(self):
        if self.state == "speaking" or self.state == "thinking":
            for bar in self.audio_bars: bar.set(random.uniform(0.1, 0.9))
        else:
            for bar in self.audio_bars:
                current = bar.get()
                if current > 0: bar.set(max(0, current - 0.1))
        self.after(100, self._audio_viz_loop)

    def _camera_worker(self):
        try:
            cap = cv2.VideoCapture(0)
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    frame = cv2.resize(frame, (240, 150))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.scanline_y = (self.scanline_y + 2) % 150
                    frame[self.scanline_y:self.scanline_y+2, :, :] = [0, 212, 255]
                    frame[::4, :, :] = frame[::4, :, :] // 2
                    img = Image.fromarray(frame)
                    img_tk = ImageTk.PhotoImage(image=img)
                    self.after(0, self._update_cam_ui, img_tk)
                time.sleep(0.05)
            cap.release()
        except:
            self.after(0, lambda: self.cam_label.configure(text="OPTICAL FEED OFFLINE"))

    def _update_cam_ui(self, img_tk):
        self.cam_label.configure(image=img_tk, text="")
        self.cam_label.image = img_tk

    def update_plan(self, plan_text):
        self.after(0, self._update_plan_ui, plan_text)

    def _update_plan_ui(self, text):
        self.plan_display.configure(state="normal")
        self.plan_display.delete("1.0", "end")
        self.plan_display.insert("1.0", f"> {text}")
        self.plan_display.configure(state="disabled")

    def set_state(self, state):
        self.state = state
