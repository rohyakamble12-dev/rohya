import customtkinter as ctk
import os
import socket
import logging
import sys
import threading
from veda.ui.theme import VedaTheme, VedaState
from veda.ui.panels.top_bar import TopBar
from veda.ui.panels.left_panel import LeftPanel
from veda.ui.panels.center_panel import CenterPanel
from veda.ui.panels.right_panel import RightPanel

logger = logging.getLogger("VEDA")

class VedaGUI(ctk.CTk):
    def __init__(self, on_send_callback, on_voice_callback):
        # Apply Stark Theme before init
        ctk.set_appearance_mode("Dark")
        theme_path = os.path.join(os.path.dirname(__file__), "stark_theme.json")
        if os.path.exists(theme_path):
            ctk.set_default_color_theme(theme_path)

        super().__init__()
        self.theme = VedaTheme()
        self.state_ref = VedaState()
        self.on_send_callback = on_send_callback
        self.on_voice_callback = on_voice_callback

        # 1. Frameless HUD Config
        self.overrideredirect(True)
        self.attributes("-alpha", 0.92)
        self.geometry(f"{self.theme.window_width}x{self.theme.window_height}")
        self.configure(fg_color=self.theme.bg_main)

        # Initial state setup
        self.attributes("-topmost", self.state_ref.topmost)

        # 2. Structure
        self.top_bar = TopBar(self, self.theme, self.state_ref)
        self.top_bar.pack(fill="x", side="top")

        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True)

        self.main_content.grid_columnconfigure(0, weight=1, minsize=260)
        self.main_content.grid_columnconfigure(1, weight=2, minsize=480)
        self.main_content.grid_columnconfigure(2, weight=1, minsize=340)
        self.main_content.grid_rowconfigure(0, weight=1)

        self.left = LeftPanel(self.main_content, None, self.theme, self.state_ref)
        self.left.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        self.center = CenterPanel(self.main_content, None, self.theme, self.state_ref)
        self.center.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)

        self.right = RightPanel(self.main_content, None, self.theme, self.state_ref)
        self.right.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)

    def link_assistant(self, assistant):
        """Injects assistant reference after bidirectional initialization."""
        self.assistant = assistant
        self.left.assistant = assistant
        self.center.assistant = assistant
        self.right.assistant = assistant

        # 3. Interactivity
        self.top_bar.bind("<Button-1>", self._start_drag)
        self.top_bar.bind("<B1-Motion>", self._drag)
        self.bind("<Button-1>", self._start_drag)
        self.bind("<B1-Motion>", self._drag)

        self.after(1000, self._start_background_tasks)

    def _start_drag(self, event):
        self.drag_x = event.x; self.drag_y = event.y

    def _drag(self, event):
        try:
            dx = event.x - self.drag_x; dy = event.y - self.drag_y
            self.geometry(f"+{self.winfo_x() + dx}+{self.winfo_y() + dy}")
        except: pass

    def run_boot_sequence(self):
        self.fade_in(0)
        steps = [
            "INITIALIZING VEDA KERNEL v4.2.1...",
            "ESTABLISHING SECURE STARK PROTOCOL...",
            "LINKING NEURAL ARCHITECTURE: [OK]",
            "MOUNTING MODULAR FEATURE SET (46 INTENTS)",
            "CALIBRATING OPTICAL SENSORS...",
            "SYNCHRONIZING VOICELINE (AVA-NEURAL)...",
            "SYSTEM READY. TACTICAL CORE ONLINE."
        ]
        overlay = ctk.CTkFrame(self, fg_color="#08080a", corner_radius=0)
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        txt = ctk.CTkTextbox(overlay, fg_color="transparent", font=("Consolas", 10), text_color="#00d4ff")
        txt.pack(expand=True, fill="both", padx=50, pady=50)

        def display_step(idx):
            if idx < len(steps):
                txt.insert("end", f"[ {idx*15}% ] > {steps[idx]}\n")
                txt.see("end")
                self.after(400, lambda: display_step(idx + 1))
            else:
                self.after(800, overlay.destroy)
        display_step(0)

    def _start_background_tasks(self):
        self.left.start_background_tasks()
        threading.Thread(target=self._network_worker, daemon=True).start()

    def _network_worker(self):
        while True:
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=2)
                self.state_ref.network_up = True
            except:
                self.state_ref.network_up = False
            self.after(0, lambda: self.right.update_ticker(f"LINK: {'ONLINE' if self.state_ref.network_up else 'OFFLINE'}"))
            threading.Event().wait(10)

    def set_state(self, status):
        self.state_ref.status = status
        color = getattr(self.theme, status, self.theme.idle)
        self.set_theme_color(color)
        if status == "thinking": self.right.show_typing(True)
        else: self.right.show_typing(False)

    def set_theme_color(self, color):
        self.top_bar.refresh_theme(color)
        self.left.refresh_theme(color)
        self.center.refresh_theme(color)
        self.right.refresh_theme(color)

    def fade_in(self, alpha):
        if alpha < 0.92:
            alpha += 0.05
            self.attributes("-alpha", alpha)
            self.after(50, lambda: self.fade_in(alpha))

    def fade_out(self, alpha):
        if alpha > 0:
            alpha -= 0.05
            self.attributes("-alpha", alpha)
            self.after(30, lambda: self.fade_out(alpha))
        else:
            self.destroy(); sys.exit(0)

    def update_chat(self, sender, message):
        is_user = sender.lower() in ["operator", "you"]
        self.after(0, lambda: self.right.add_message(sender, message, is_user))

    def send_command(self):
        cmd = self.right.entry.get()
        if cmd:
            self.right.entry.delete(0, "end")
            self.update_chat("Operator", cmd)
            threading.Thread(target=self.on_send_callback, args=(cmd,), daemon=True).start()

    def terminate(self):
        self.left.stop()
        print("[SYSTEM]: Termination sequence complete.")
        self.fade_out(0.92)
