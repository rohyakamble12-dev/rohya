import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import threading
import psutil
import time
import logging
from veda.ui.base import VedaPanel

logger = logging.getLogger("VEDA")

class LeftPanel(VedaPanel):
    def __init__(self, master, assistant):
        super().__init__(master, "Observability")
        self.assistant = assistant

        # 1. Optical Feed with Scanline Overlay
        self.cam_frame = ctk.CTkFrame(self, fg_color="black", height=180, border_width=1, border_color="#1a1a20")
        self.cam_frame.pack(fill="x", padx=10, pady=10)
        self.cam_label = ctk.CTkLabel(self.cam_frame, text="LINKING OPTICS...", font=("Consolas", 10))
        self.cam_label.pack(expand=True, fill="both")

        # 2. Metrics (Progress Bars)
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

        # 3. Observability Block
        self.obs_label = ctk.CTkLabel(self, text="SUBSYSTEM METRICS", font=("Orbitron", 10, "bold"))
        self.obs_label.pack(anchor="w", padx=10)
        self.obs_box = ctk.CTkTextbox(self, height=120, font=("Consolas", 10), fg_color="#050507", border_width=1, border_color="#1a1a20")
        self.obs_box.pack(fill="x", padx=10, pady=(2, 10))
        self._refresh_obs_text()
        self.obs_box.configure(state="disabled")

        # 4. Execution Plan Visualizer
        self.plan_label = ctk.CTkLabel(self, text="TACTICAL PLAN", font=("Orbitron", 10, "bold"))
        self.plan_label.pack(anchor="w", padx=10)
        self.plan_display = ctk.CTkTextbox(self, height=80, font=("Consolas", 9), fg_color="#050507", text_color="#aaaaaa")
        self.plan_display.pack(fill="x", padx=10, pady=(2, 10))
        self.plan_display.insert("0.0", "[IDLE] Waiting for Operator link...")
        self.plan_display.configure(state="disabled")

        # 5. Protocol Toggles
        self.proto_label = ctk.CTkLabel(self, text="PROTOCOLS", font=("Orbitron", 10, "bold"))
        self.proto_label.pack(anchor="w", padx=10)
        self.proto_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.proto_frame.pack(fill="x", padx=10, pady=5)

        self.chk_stealth = ctk.CTkCheckBox(self.proto_frame, text="STEALTH", font=("Orbitron", 9), border_width=1)
        self.chk_stealth.pack(side="left", padx=2)
        self.register_accent_widget(self.chk_stealth, "border")

        self.chk_gov = ctk.CTkCheckBox(self.proto_frame, text="GOV", font=("Orbitron", 9), border_width=1)
        self.chk_gov.pack(side="left", padx=2)
        self.register_accent_widget(self.chk_gov, "border")

        self.chk_heal = ctk.CTkCheckBox(self.proto_frame, text="HEAL", font=("Orbitron", 9), border_width=1)
        self.chk_heal.pack(side="left", padx=2)
        self.register_accent_widget(self.chk_heal, "border")

        self.start_workers()

    def _refresh_obs_text(self, threads=5, queue=0):
        self.obs_box.configure(state="normal")
        self.obs_box.delete("1.0", "end")
        text = f"THREADS: {threads} ACTIVE\n"
        text += f"PLUGINS: 18 LOADED\n"
        text += f"GOVERNANCE: PASSIVE\n"
        text += f"EVENT QUEUE: [{queue}]\n"
        text += f"SELF-HEAL: ENABLED\n"
        text += f"ROLLBACK: STANDBY"
        self.obs_box.insert("1.0", text)
        self.obs_box.configure(state="disabled")

    def start_workers(self):
        threading.Thread(target=self._metrics_worker, daemon=True).start()
        threading.Thread(target=self._camera_worker, daemon=True).start()

    def _metrics_worker(self):
        while True:
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                self.after(0, self._update_metrics_ui, cpu, ram)
            except Exception as e:
                logger.warning(f"Metrics worker link failed: {e}")
            time.sleep(2)

    def _update_metrics_ui(self, cpu, ram):
        self.cpu_bar.set(cpu/100)
        self.ram_bar.set(ram/100)

    def _camera_worker(self):
        try:
            cap = cv2.VideoCapture(0)
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    frame = cv2.resize(frame, (240, 150))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # HUD Scanline simulation
                    frame[::4, :, :] = frame[::4, :, :] // 2
                    frame[::4, :, 2] = 255 # Blue boost

                    img = Image.fromarray(frame)
                    img_tk = ImageTk.PhotoImage(image=img)
                    self.after(0, self._update_cam_ui, img_tk)
                time.sleep(0.05)
            cap.release()
        except Exception as e:
            logger.warning(f"Optical link unstable: {e}")
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
