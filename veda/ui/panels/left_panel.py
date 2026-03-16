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
    def __init__(self, master, assistant, theme: VedaTheme, state_ref: VedaState, **kwargs):
        super().__init__(master, "Observability", theme, state_ref, **kwargs)
        self.assistant = assistant
        self.running = True
        self.cap = None

        # 1. Optical Feed with Scanline
        self.cam_frame = ctk.CTkFrame(self, fg_color="black", height=150, border_width=1, border_color=theme.border_main)
        self.cam_frame.pack(fill="x", padx=10, pady=10)
        self.cam_label = ctk.CTkLabel(self.cam_frame, text="LINKING OPTICS...", font=theme.font_data)
        self.cam_label.pack(expand=True, fill="both")
        self.scanline_y = 0

        # 2. Metrics HUD
        self.metrics_container = ctk.CTkFrame(self, fg_color="transparent")
        self.metrics_container.pack(fill="x", padx=10, pady=5)
        self.bars = {}
        self._create_metric("CPU", "cpu")
        self._create_metric("RAM", "ram")
        self._create_metric("DSK", "dsk")
        self._create_metric("NET", "net")

        # 3. Subsystem Metrics
        self.obs_box = ctk.CTkTextbox(self, height=100, font=theme.font_chat, fg_color="#050507", border_width=1, border_color=theme.border_main)
        self.obs_box.pack(fill="x", padx=10, pady=10)
        self.obs_box.configure(state="disabled")

        # 4. Tactical Plan
        self.plan_label = ctk.CTkLabel(self, text="TACTICAL PLAN", font=theme.font_header)
        self.plan_label.pack(anchor="w", padx=10)
        self.plan_display = ctk.CTkTextbox(self, height=60, font=("Consolas", 9), fg_color="#050507", text_color="#666666")
        self.plan_display.pack(fill="x", padx=10, pady=(2, 10))
        self.update_plan("Standby.")

        # 5. Protocol Toggles
        self.proto_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.proto_frame.pack(fill="x", padx=10, pady=5)
        self._add_proto("STEALTH", "private")
        self._add_proto("DEEP", "deep_search")
        self._add_proto("CTX", "context")

    def _create_metric(self, label, key):
        f = ctk.CTkFrame(self.metrics_container, fg_color="transparent")
        f.pack(fill="x", pady=2)
        ctk.CTkLabel(f, text=label, font=self.theme.font_label, width=40).pack(side="left")
        bar = ctk.CTkProgressBar(f, height=6)
        bar.pack(side="left", fill="x", expand=True, padx=5)
        bar.set(0)
        self.bars[key] = bar
        self.register_accent_widget(bar, "progress")

    def _add_proto(self, text, key):
        var = ctk.BooleanVar(value=self.state_ref.protocols[key])
        cb = ctk.CTkCheckBox(self.proto_frame, text=text, font=self.theme.font_label, variable=var,
                             command=lambda: self._toggle_proto(key, var.get()), border_width=1)
        cb.pack(side="left", padx=2)
        self.register_accent_widget(cb, "border")

    def _toggle_proto(self, key, val):
        self.state_ref.protocols[key] = val

    def start_background_tasks(self):
        threading.Thread(target=self._metrics_worker, daemon=True).start()
        threading.Thread(target=self._camera_worker, daemon=True).start()

    def _metrics_worker(self):
        while self.running:
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                dsk = psutil.disk_usage('/').percent
                net = (psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv) % 1000 / 1000
                self.after(0, lambda c=cpu, r=ram, d=dsk, n=net: self._update_ui(c, r, d, n))
            except Exception as e:
                logger.warning(f"Metrics worker error: {e}")
            time.sleep(2)

    def _update_ui(self, cpu, ram, dsk, net):
        self.bars['cpu'].set(cpu/100); self.bars['ram'].set(ram/100)
        self.bars['dsk'].set(dsk/100); self.bars['net'].set(net)

        self.obs_box.configure(state="normal")
        self.obs_box.delete("1.0", "end")
        self.obs_box.insert("1.0", f"THREADS: {threading.active_count()} ACTIVE\nGOVERNANCE: PASSIVE\nSELF-HEAL: ENABLED\nROLLBACK: READY")
        self.obs_box.configure(state="disabled")

    def _camera_worker(self):
        backend = cv2.CAP_DSHOW if sys.platform == "win32" else cv2.CAP_ANY
        self.cap = cv2.VideoCapture(0, backend)
        while self.running and self.cap.isOpened():
            if not self.state_ref.camera_active:
                time.sleep(0.5); continue
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (240, 150))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.scanline_y = (self.scanline_y + 2) % 150
                frame[self.scanline_y:self.scanline_y+1, :, :] = [0, 212, 255]
                frame[::4, :, :] = frame[::4, :, :] // 2
                img = Image.fromarray(frame)
                img_tk = ImageTk.PhotoImage(image=img)
                self.after(0, lambda i=img_tk: self._update_cam_ui(i))
            time.sleep(0.04)
        if self.cap: self.cap.release()

    def _update_cam_ui(self, img_tk):
        self.cam_label.configure(image=img_tk, text="")
        self.cam_label.img_tk = img_tk

    def update_plan(self, text):
        self.after(0, lambda: (self.plan_display.configure(state="normal"), self.plan_display.delete("1.0", "end"), self.plan_display.insert("1.0", f"> {text}"), self.plan_display.configure(state="disabled")))

    def stop(self):
        self.running = False
        if self.cap: self.cap.release()
        self.cam_label.img_tk = None
        self.cam_label.configure(image='')
