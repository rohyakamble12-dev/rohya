import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import threading
import psutil
from veda.ui.base import VedaPanel

class LeftPanel(VedaPanel):
    def __init__(self, master, assistant):
        super().__init__(master, "Observability")
        self.assistant = assistant

        # 1. Optical Feed
        self.cam_frame = ctk.CTkFrame(self, fg_color="black", height=150)
        self.cam_frame.pack(fill="x", padx=10, pady=10)
        self.cam_label = ctk.CTkLabel(self.cam_frame, text="NO SIGNAL", font=("Consolas", 10))
        self.cam_label.pack(expand=True, fill="both")

        # 2. Metrics
        self.metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.metrics_frame.pack(fill="x", padx=10, pady=5)

        self.cpu_bar = ctk.CTkProgressBar(self.metrics_frame, progress_color="#00d4ff")
        self.cpu_bar.pack(fill="x", pady=2)
        self.cpu_label = ctk.CTkLabel(self.metrics_frame, text="CPU: 0%", font=("Consolas", 10))
        self.cpu_label.pack(side="left")

        self.ram_bar = ctk.CTkProgressBar(self.metrics_frame, progress_color="#00d4ff")
        self.ram_bar.pack(fill="x", pady=2)
        self.ram_label = ctk.CTkLabel(self.metrics_frame, text="RAM: 0%", font=("Consolas", 10))
        self.ram_label.pack(side="left")

        # 3. Observability Block
        self.obs_box = ctk.CTkTextbox(self, height=120, font=("Consolas", 10), fg_color="#050507")
        self.obs_box.pack(fill="x", padx=10, pady=10)
        self.obs_box.insert("0.0", "> Governance: ACTIVE\n> Self-Heal: ENABLED\n> Rollback: STANDBY\n> Event Queue: [0]")
        self.obs_box.configure(state="disabled")

        # 4. Protocols
        self.proto_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.proto_frame.pack(fill="x", padx=10, pady=5)
        self.chk_stealth = ctk.CTkCheckBox(self.proto_frame, text="Stealth", font=("Orbitron", 10))
        self.chk_stealth.pack(side="left", padx=5)
        self.chk_governance = ctk.CTkCheckBox(self.proto_frame, text="Governance", font=("Orbitron", 10))
        self.chk_governance.pack(side="left", padx=5)

        self.start_workers()

    def start_workers(self):
        threading.Thread(target=self._metrics_worker, daemon=True).start()
        threading.Thread(target=self._camera_worker, daemon=True).start()

    def _metrics_worker(self):
        while True:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            self.after(0, self._update_metrics_ui, cpu, ram)
            import time
            time.sleep(2)

    def _update_metrics_ui(self, cpu, ram):
        self.cpu_bar.set(cpu/100)
        self.cpu_label.configure(text=f"CPU: {cpu}%")
        self.ram_bar.set(ram/100)
        self.ram_label.configure(text=f"RAM: {ram}%")

    def _camera_worker(self):
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, (200, 120))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Cyan scanline overlay simulation
                frame[::4, :, 0] = 0
                img = Image.fromarray(frame)
                img_tk = ImageTk.PhotoImage(image=img)
                self.after(0, self._update_cam_ui, img_tk)
            import time
            time.sleep(0.05)
        cap.release()

    def _update_cam_ui(self, img_tk):
        self.cam_label.configure(image=img_tk, text="")
        self.cam_label.image = img_tk

    def refresh_theme(self, color):
        super().refresh_theme(color)
        self.cpu_bar.configure(progress_color=color)
        self.ram_bar.configure(progress_color=color)
