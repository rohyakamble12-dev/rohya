import customtkinter as ctk
import cv2
import psutil
import threading
import time
import logging
import sys
import random
from PIL import Image, ImageTk
from veda.ui.base import VedaPanel
from veda.ui.theme import VedaTheme, VedaState

logger = logging.getLogger("VEDA")

class LeftPanel(VedaPanel):
    def __init__(self, master, assistant, theme: VedaTheme, state: VedaState):
        super().__init__(master, "Observability", theme, state)
        self.assistant = assistant
        self.running = True
        self.cap = None

        # 1. Optical Feed with Scanline Overlay
        self.cam_frame = ctk.CTkFrame(self, fg_color="black", height=150, border_width=1, border_color=theme.border_main)
        self.cam_frame.pack(fill="x", padx=10, pady=10)
        self.cam_label = ctk.CTkLabel(self.cam_frame, text="INITIATING OPTICAL LINK...", font=theme.font_data)
        self.cam_label.pack(expand=True, fill="both")
        self.scanline_y = 0

        # 2. Tactical ECG (Pulse)
        self.pulse_canvas = ctk.CTkCanvas(self, height=40, bg="#050507", highlightthickness=0)
        self.pulse_canvas.pack(fill="x", padx=10)
        self.pulse_points = [20] * 50

        # 3. Metrics HUD (CPU, RAM, DISK, NET)
        self.metrics_container = ctk.CTkFrame(self, fg_color="transparent")
        self.metrics_container.pack(fill="x", padx=10, pady=5)
        self.metrics = {}
        self._add_metric("CPU", "cpu")
        self._add_metric("RAM", "ram")
        self._add_metric("DSK", "dsk")
        self._add_metric("NET", "net")

        # 4. Subsystem Console
        self.obs_box = ctk.CTkTextbox(self, height=100, font=theme.font_chat, fg_color="#050507", border_width=1, border_color=theme.border_main)
        self.obs_box.pack(fill="x", padx=10, pady=10)
        self.obs_box.configure(state="disabled")

        # 5. Execution Plan Visualizer
        self.plan_box = ctk.CTkTextbox(self, height=60, font=("Consolas", 9), fg_color="#050507", text_color="#666666")
        self.plan_box.pack(fill="x", padx=10, pady=(0, 10))
        self.update_plan("Standby.")

    def _add_metric(self, label_text, key):
        frame = ctk.CTkFrame(self.metrics_container, fg_color="transparent")
        frame.pack(fill="x", pady=2)
        lbl = ctk.CTkLabel(frame, text=label_text, font=self.theme.font_data, width=40)
        lbl.pack(side="left")
        bar = ctk.CTkProgressBar(frame, height=6)
        bar.pack(side="left", fill="x", expand=True, padx=5)
        bar.set(0)
        self.metrics[key] = bar
        self.register_accent_widget(bar, "progress")

    def start_background_tasks(self):
        threading.Thread(target=self._metrics_worker, daemon=True).start()
        threading.Thread(target=self._camera_worker, daemon=True).start()
        self._pulse_loop()

    def _metrics_worker(self):
        while self.running:
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                dsk = psutil.disk_usage('/').percent
                net = (psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv) % 1000 / 1000
                self.after(0, lambda c=cpu, r=ram, d=dsk, n=net: self._update_metrics_ui(c, r, d, n))
            except Exception as e:
                logger.warning(f"Metrics worker error: {e}")
            time.sleep(2)

    def _update_metrics_ui(self, cpu, ram, dsk, net):
        self.metrics['cpu'].set(cpu/100)
        self.metrics['ram'].set(ram/100)
        self.metrics['dsk'].set(dsk/100)
        self.metrics['net'].set(net)

        self.obs_box.configure(state="normal")
        self.obs_box.delete("1.0", "end")
        self.obs_box.insert("1.0", f"THREADS: {threading.active_count()} ACTIVE\nGOVERNANCE: PASSIVE\nSELF-HEAL: ENABLED\nROLLBACK: READY")
        self.obs_box.configure(state="disabled")

    def _camera_worker(self):
        backend = cv2.CAP_DSHOW if sys.platform == "win32" else cv2.CAP_ANY
        self.cap = cv2.VideoCapture(0, backend)
        while self.running and self.cap.isOpened():
            if not self.state.camera_active:
                time.sleep(0.5); continue
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (240, 150))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Cinematic scanlines
                self.scanline_y = (self.scanline_y + 2) % 150
                frame[self.scanline_y:self.scanline_y+1, :, :] = [0, 212, 255]
                frame[::4, :, :] = frame[::4, :, :] // 2

                img = Image.fromarray(frame)
                img_tk = ImageTk.PhotoImage(image=img)
                self.after(0, lambda i=img_tk: self._update_cam_ui(i))
            time.sleep(0.04)
        self.cap.release()

    def _update_cam_ui(self, img_tk):
        self.cam_label.configure(image=img_tk, text="")
        self.cam_label.img_tk = img_tk

    def _pulse_loop(self):
        if not self.running: return
        self.pulse_canvas.delete("pulse")
        self.pulse_points.pop(0)
        val = random.uniform(15, 25) if self.state.status == "idle" else random.uniform(5, 35)
        self.pulse_points.append(val)
        w = 240; step = w / len(self.pulse_points)
        for i in range(len(self.pulse_points)-1):
            self.pulse_canvas.create_line(i*step, self.pulse_points[i], (i+1)*step, self.pulse_points[i+1], fill=self.accent_color, tags="pulse")
        self.after(60, self._pulse_loop)

    def update_plan(self, text):
        self.after(0, lambda: (self.plan_box.configure(state="normal"), self.plan_box.delete("1.0", "end"), self.plan_box.insert("1.0", f"> {text}"), self.plan_box.configure(state="disabled")))

    def release_camera(self):
        self.running = False
        if self.cap: self.cap.release()
