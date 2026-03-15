import customtkinter as ctk
import socket
import logging
import sys
import threading
from veda.ui.left_panel import LeftPanel
from veda.ui.center_panel import CenterPanel
from veda.ui.right_panel import RightPanel

logger = logging.getLogger("VEDA")

class VedaGUI(ctk.CTk):
    def __init__(self, on_send_callback, on_voice_callback):
        super().__init__()

        self.on_send_callback = on_send_callback
        self.on_voice_callback = on_voice_callback

        # 1. MCU Stark-Inspired HUD Configuration
        self.overrideredirect(True)
        self.attributes("-alpha", 0.92)
        self.geometry("1100x650")
        self.configure(fg_color="#08080a")

        # 2. Strategic Grid Layout
        self.grid_columnconfigure(0, weight=1, minsize=300) # LEFT: Metrics
        self.grid_columnconfigure(1, weight=2, minsize=400) # CENTER: Core
        self.grid_columnconfigure(2, weight=1, minsize=350) # RIGHT: Intelligence
        self.grid_rowconfigure(0, weight=1)

        # 3. Component Initialization
        self.left = LeftPanel(self, None)
        self.left.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        self.center = CenterPanel(self, None)
        self.center.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)

        self.right = RightPanel(self, None)
        self.right.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)

        # 4. Global Interactivity & Draggable Link
        self.bind("<Button-1>", self._start_drag)
        self.bind("<B1-Motion>", self._drag)

        self.center.btn_unload.configure(command=self.terminate)
        self.center.btn_mic.configure(command=self.on_voice_callback)

    def _start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def _drag(self, event):
        try:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.winfo_x() + deltax
            y = self.winfo_y() + deltay
            self.geometry(f"+{x}+{y}")
        except: pass

    def update_chat(self, sender, message):
        is_user = sender.lower() in ["operator", "you"]
        self.after(0, lambda: self.right.add_message(sender, message, is_user))

    def set_state(self, state):
        """Tiered states: idle (cyan), thinking (gold), speaking (green), alert (red)."""
        color = self.center.colors.get(state, "#00d4ff")
        self.after(0, lambda: self.center.set_state(state))
        self.after(0, lambda: self.left.refresh_theme(color))
        self.after(0, lambda: self.right.refresh_theme(color))

        if state == "thinking":
            self.after(0, lambda: self.right.show_typing(True))
        else:
            self.after(0, lambda: self.right.show_typing(False))

    def send_command(self):
        cmd = self.right.entry.get()
        if cmd:
            self.right.entry.delete(0, "end")
            self.update_chat("Operator", cmd)
            # Run in thread to keep HUD alive
            threading.Thread(target=self.on_send_callback, args=(cmd,), daemon=True).start()

    def check_network(self):
        """Lightweight tactical network probe."""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return True
        except:
            return False

    def terminate(self):
        print("[SYSTEM]: Termination sequence complete. Unloading VEDA CORE.")
        self.destroy()
        sys.exit(0)
