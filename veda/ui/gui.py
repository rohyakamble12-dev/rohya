import customtkinter as ctk
from veda.ui.left_panel import LeftPanel
from veda.ui.center_panel import CenterPanel
from veda.ui.right_panel import RightPanel

class VedaGUI(ctk.CTk):
    def __init__(self, on_send_callback, on_voice_callback):
        super().__init__()

        self.on_send_callback = on_send_callback
        self.on_voice_callback = on_voice_callback

        # Sci-Fi Setup
        self.overrideredirect(True)
        self.attributes("-alpha", 0.92)
        self.geometry("1100x650")
        self.configure(fg_color="#08080a")

        self.grid_columnconfigure(0, weight=1) # Left
        self.grid_columnconfigure(1, weight=2) # Center
        self.grid_columnconfigure(2, weight=1) # Right
        self.grid_rowconfigure(0, weight=1)

        self.left = LeftPanel(self, None)
        self.left.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        self.center = CenterPanel(self, None)
        self.center.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)

        self.right = RightPanel(self, None)
        self.right.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)

        # Draggable logic
        self.bind("<Button-1>", self._start_drag)
        self.bind("<B1-Motion>", self._drag)

    def _start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def _drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def update_chat(self, sender, message):
        is_user = sender.lower() == "operator"
        self.after(0, lambda: self.right.add_message(sender, message, is_user))

    def set_state(self, state):
        self.after(0, lambda: self.center.set_state(state))
        self.after(0, lambda: self.left.refresh_theme(self.center.colors[state]))
        self.after(0, lambda: self.right.refresh_theme(self.center.colors[state]))

    def trigger_voice(self):
        self.set_state("speaking")
        # Actual trigger would go through on_voice_callback

    def reset_voice_button(self):
        self.set_state("idle")
