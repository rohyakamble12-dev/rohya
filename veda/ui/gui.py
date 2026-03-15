import customtkinter as ctk
import socket
import logging
import sys
import threading
from veda.ui.left_panel import LeftPanel
from veda.ui.center_panel import CenterPanel
from veda.ui.right_panel import RightPanel
from veda.utils.sounds import TacticalSoundEngine

logger = logging.getLogger("VEDA")

class VedaGUI(ctk.CTk):
    def __init__(self, on_send_callback, on_voice_callback):
        super().__init__()

        self.on_send_callback = on_send_callback
        self.sounds = TacticalSoundEngine()
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

        # 4. Overlay for Boot Sequence
        self.boot_overlay = ctk.CTkFrame(self, fg_color="#08080a", corner_radius=0)
        self.boot_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.boot_text = ctk.CTkTextbox(self.boot_overlay, fg_color="transparent", font=("Consolas", 10), text_color="#00d4ff")
        self.boot_text.pack(expand=True, fill="both", padx=50, pady=50)

        # 5. Global Interactivity & Draggable Link
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

    def run_boot_sequence(self):
        self.fade_in(0)
        steps = [
            "INITIALIZING VEDA KERNEL v4.1.0...",
            "LINKING NEURAL ARCHITECTURE: [OK]",
            "ESTABLISHING TACTICAL HUD: [OK]",
            "MOUNTING Modular Feature Set (18 Active)",
            "CALIBRATING OPTICAL SENSORS...",
            "LINKING OPERATOR INTERFACE...",
            "SYSTEM READY. TACTICAL CORE ONLINE."
        ]

        def display_step(idx):
            if idx < len(steps):
                self.boot_text.insert("end", f"> {steps[idx]}\n")
                self.boot_text.see("end")
                self.after(400, lambda: display_step(idx + 1))
            else:
                self.after(500, self.boot_overlay.destroy)

        display_step(0)

    def update_chat(self, sender, message):
        is_user = sender.lower() in ["operator", "you"]
        self.after(0, lambda: self.right.add_message(sender, message, is_user))

    def set_theme_color(self, color):
        """Forces a full UI re-theme to the specified color."""
        self.after(0, lambda: self.left.refresh_theme(color))
        self.after(0, lambda: self.center.refresh_theme(color))
        self.after(0, lambda: self.right.refresh_theme(color))

    def set_state(self, state):
        """Tiered states: idle, thinking, speaking, alert."""
        if state != self.center.state:
            self.sounds.play_system_blip(state)

        color = self.center.colors.get(state, "#00d4ff")
        self.after(0, lambda: self.left.set_state(state))
        self.after(0, lambda: self.center.set_state(state))
        self.set_theme_color(color)

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
            self.destroy()
            sys.exit(0)

    def terminate(self):
        print("[SYSTEM]: Termination sequence complete. Unloading VEDA CORE.")
        self.fade_out(0.92)
