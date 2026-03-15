import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import threading
import psutil
import time
import logging
import random
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

        # 2. Metrics
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

        # 3. Audio Visualizer (Simulated)
        self.audio_label = ctk.CTkLabel(self, text="AUDIO FREQUENCY", font=("Orbitron", 10, "bold"))
        self.audio_label.pack(anchor="w", padx=10)
        self.audio_viz_frame = ctk.CTkFrame(self, height=50, fg_color="#050507", border_width=1, border_color="#1a1a20")
        self.audio_viz_frame.pack(fill="x", padx=10, pady=(2, 10))
        self.audio_bars = []
        for i in range(15):
            bar = ctk.CTkProgressBar(self.audio_viz_frame, orientation="vertical", width=8, height=40)
            bar.pack(side="left", padx=2, pady=5)
            bar.set(0)
            self.audio_bars.append(bar)
            self.register_accent_widget(bar, "progress")

        # 4. Subsystem Metrics
        self.obs_label = ctk.CTkLabel(self, text="COGNITIVE STATUS", font=("Orbitron", 10, "bold"))
        self.obs_label.pack(anchor="w", padx=10)
        self.obs_box = ctk.CTkTextbox(self, height=80, font=("Consolas", 10), fg_color="#050507", border_width=1, border_color="#1a1a20")
        self.obs_box.pack(fill="x", padx=10, pady=(2, 10))
        self._refresh_obs_text()
        self.obs_box.configure(state="disabled")

        # 5. Tactical Plan
        self.plan_label = ctk.CTkLabel(self, text="EXECUTION PLAN", font=("Orbitron", 10, "bold"))
        self.plan_label.pack(anchor="w", padx=10)
        self.plan_display = ctk.CTkTextbox(self, height=60, font=("Consolas", 9), fg_color="#050507", text_color="#aaaaaa")
        self.plan_display.pack(fill="x", padx=10, pady=(2, 10))
        self.plan_display.insert("0.0", "[IDLE] Waiting for Operator link...")
        self.plan_display.configure(state="disabled")

        self.start_workers()

    def _refresh_obs_text(self, threads=8, queue=0):
        self.obs_box.configure(state="normal")
        self.obs_box.delete("1.0", "end")
        text = f"THREADS: {threads} ACTIVE\n"
        text += f"PLUGINS: 18 LOADED\n"
        text += f"GOVERNANCE: PASSIVE\n"
        text += f"SELF-HEAL: ENABLED\n"
        text += f"ROLLBACK: STANDBY"
        self.obs_box.insert("1.0", text)
        self.obs_box.configure(state="disabled")

    def start_workers(self):
        threading.Thread(target=self._metrics_worker, daemon=True).start()
        threading.Thread(target=self._camera_worker, daemon=True).start()
        self._audio_viz_loop()

    def _metrics_worker(self):
        while True:
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                self.after(0, self._update_metrics_ui, cpu, ram)
            except Exception as e:
                logger.warning(f"Metrics link error: {e}")
            time.sleep(2)

    def _update_metrics_ui(self, cpu, ram):
        self.cpu_bar.set(cpu/100)
        self.ram_bar.set(ram/100)

    def _audio_viz_loop(self):
        if self.state == "speaking" or self.state == "thinking":
            for bar in self.audio_bars:
                bar.set(random.uniform(0.1, 0.9))
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

                    # Moving scanline
                    self.scanline_y = (self.scanline_y + 2) % 150
                    frame[self.scanline_y:self.scanline_y+2, :, :] = [0, 212, 255] # Cyan scanline

                    # Static scanlines every 4th row
                    frame[::4, :, :] = frame[::4, :, :] // 2

                    img = Image.fromarray(frame)
                    img_tk = ImageTk.PhotoImage(image=img)
                    self.after(0, self._update_cam_ui, img_tk)
                time.sleep(0.05)
            cap.release()
        except Exception as e:
            logger.warning(f"Optics failed: {e}")
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
