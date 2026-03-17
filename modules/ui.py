import customtkinter as ctk
import tkinter as tk
import math
import logging
import threading
import time
import os

class VedaHUD(ctk.CTk):
    def __init__(self, config, on_command_callback):
        super().__init__()
        self.config = config
        self.on_command = on_command_callback

        # Window Config
        self.title("VEDA HUD")
        self.geometry("1100x650")
        self.overrideredirect(True)
        self.attributes("-topmost", config['preferences']['appearance']['always_on_top'])
        self.attributes("-alpha", config['preferences']['appearance']['transparency'])
        self.configure(fg_color="#08080a")

        # Make window draggable
        self.bind("<Button-1>", self._start_drag)
        self.bind("<B1-Motion>", self._drag)

        # Arc Reactor UI
        self.canvas = tk.Canvas(self, bg="#08080a", highlightthickness=0, width=200, height=200)
        self.canvas.place(relx=0.5, rely=0.3, anchor="center")
        self.arc_angle = 0

        # Chat Log
        self.chat_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", width=600, height=300)
        self.chat_frame.place(relx=0.5, rely=0.7, anchor="center")

        # Input
        self.input_entry = ctk.CTkEntry(self, placeholder_text="COMMAND >>", width=500, font=("Consolas", 12))
        self.input_entry.place(relx=0.5, rely=0.9, anchor="center")
        self.input_entry.bind("<Return>", self._send_command)

        # Waveform Canvas
        self.wave_canvas = tk.Canvas(self, bg="#08080a", highlightthickness=0, width=400, height=50)
        self.wave_canvas.place(relx=0.5, rely=0.96, anchor="center")

        self._animate_arc()

    def _start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def _drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def _animate_arc(self):
        self.canvas.delete("arc")
        self.arc_angle = (self.arc_angle + 5) % 360
        color = "#00d4ff"

        for i in range(0, 360, 45):
            start = (i + self.arc_angle) % 360
            self.canvas.create_arc(20, 20, 180, 180, start=start, extent=30,
                                   outline=color, width=4, style="arc", tags="arc")

        self.canvas.create_oval(70, 70, 130, 130, outline=color, width=2, tags="arc")
        self.after(30, self._animate_arc)

    def add_message(self, role, text):
        colors = {"Veda": "#00d4ff", "User": "#ffffff", "System": "#ffcc00", "Error": "#ff3e3e"}
        color = colors.get(role, "#ffffff")

        msg_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        msg_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(msg_frame, text=f"[{role.upper()}]:", font=("Orbitron", 10, "bold"), text_color=color).pack(side="left", padx=5)
        ctk.CTkLabel(msg_frame, text=text, font=("Consolas", 11), text_color="#cccccc", wraplength=500, justify="left").pack(side="left", padx=5)

        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def _send_command(self, event):
        cmd = self.input_entry.get()
        if cmd:
            self.input_entry.delete(0, "end")
            self.add_message("User", cmd)
            threading.Thread(target=self.on_command, args=(cmd,), daemon=True).start()

    def start(self):
        self.mainloop()
