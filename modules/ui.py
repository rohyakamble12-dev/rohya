import customtkinter as ctk
import tkinter as tk
import threading
import time
import os

class VedaHUD(ctk.CTk):
    def __init__(self, config, assistant):
        super().__init__()
        self.config = config
        self.assistant = assistant

        # 1. Production Stable Configuration
        self.overrideredirect(True)
        self.attributes("-alpha", 0.98)
        self.attributes("-topmost", True)
        self.geometry("1100x680")
        self.configure(fg_color="#050508")

        # 2. Optimized Grid Layout (Stability over Complexity)
        self.grid_columnconfigure(0, weight=1, minsize=260) # Side Dashboard
        self.grid_columnconfigure(1, weight=3) # Command/Chat Terminal
        self.grid_rowconfigure(0, weight=1)

        self._init_top_header()
        self._init_sidebar()
        self._init_main_terminal()

        # Interaction Logic
        self.bind("<Button-1>", self._start_drag)
        self.bind("<B1-Motion>", self._drag)

        self.status = "idle"

    def _init_top_header(self):
        self.header = ctk.CTkFrame(self, fg_color="#08080c", height=32, corner_radius=0)
        self.header.place(relx=0, rely=0, relwidth=1)

        ctk.CTkLabel(self.header, text="VEDA SOVEREIGN EDITION v5.2", font=("Orbitron", 9, "bold"), text_color="#00d4ff").pack(side="left", padx=20)

        # Window Controls
        ctk.CTkButton(self.header, text="✕", width=32, height=32, fg_color="transparent", hover_color="#ff3e3e",
                       text_color="#666666", corner_radius=0, command=self.destroy).pack(side="right")
        ctk.CTkButton(self.header, text="—", width=32, height=32, fg_color="transparent", hover_color="#1a1a25",
                       text_color="#666666", corner_radius=0, command=self.iconify).pack(side="right")

    def _init_sidebar(self):
        self.side = ctk.CTkFrame(self, fg_color="#08080c", corner_radius=0, border_width=1, border_color="#1a1a25")
        self.side.grid(row=0, column=0, sticky="nsew", padx=(2, 0), pady=(34, 2))

        # 1. System Link Dashboard (Real-time telemetry)
        ctk.CTkLabel(self.side, text="SYSTEM TELEMETRY", font=("Orbitron", 10, "bold"), text_color="#00d4ff").pack(pady=(20, 10))
        self.links = {}
        for link in ["NEURAL", "OPTIC", "VOICE", "DATA"]:
            f = ctk.CTkFrame(self.side, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=4)
            ctk.CTkLabel(f, text=link, font=("Consolas", 9), text_color="#666666").pack(side="left")
            val = ctk.CTkLabel(f, text="SYNCING...", font=("Consolas", 9, "bold"), text_color="#ff8c00")
            val.pack(side="right")
            self.links[link] = val

        # 2. Hardware Resource Metrics
        self.metrics_f = ctk.CTkFrame(self.side, fg_color="transparent")
        self.metrics_f.pack(fill="x", padx=20, pady=20)
        self.cpu_bar = self._add_metric("CPU LOAD")
        self.ram_bar = self._add_metric("MEM ALLOC")

        # 3. Verified System Commands
        ctk.CTkLabel(self.side, text="TACTICAL OVERRIDE", font=("Orbitron", 10, "bold"), text_color="#00d4ff").pack(pady=(20, 5))
        self._add_btn("SYSTEM DIAGNOSTIC", lambda: self.assistant.process_command("mark 42 status"))
        self._add_btn("CLEAN SLATE", lambda: self.assistant.process_command("clean slate protocol"))
        self._add_btn("TAKE SCREENSHOT", lambda: self.assistant.process_command("screenshot"), "#1f1f2e", "#ff8c00")
        self._add_btn("REBOOT KERNEL", lambda: self.assistant.process_command("restart"), "#201010", "#ff3e3e")

    def _add_btn(self, text, cmd, fg="#121217", hover="#1a1a25"):
        ctk.CTkButton(self.side, text=text, font=("Orbitron", 8), width=220, fg_color=fg, border_width=1, border_color="#1a1a25",
                       hover_color=hover, command=cmd).pack(pady=4)

    def _add_metric(self, label):
        ctk.CTkLabel(self.metrics_f, text=label, font=("Orbitron", 8), text_color="#666666").pack(anchor="w", pady=(8, 2))
        bar = ctk.CTkProgressBar(self.metrics_f, height=6, progress_color="#00d4ff", fg_color="#121217")
        bar.pack(fill="x")
        bar.set(0.1)
        return bar

    def _init_main_terminal(self):
        self.main_f = ctk.CTkFrame(self, fg_color="#0a0a0f", corner_radius=0, border_width=1, border_color="#1a1a25")
        self.main_f.grid(row=0, column=1, sticky="nsew", padx=(0, 2), pady=(34, 2))

        # Header with utility controls
        self.main_h = ctk.CTkFrame(self.main_f, fg_color="transparent", height=40)
        self.main_h.pack(fill="x")

        # New: Help button
        ctk.CTkButton(self.main_h, text="COMMAND LIST", font=("Orbitron", 7), width=100, height=22, fg_color="transparent", border_width=1, border_color="#1a1a25",
                       command=lambda: self.add_message("System", "Available commands: open [app], volume [n], screenshot, health, restart, wikipedia [topic], search [query], translate [text] to [lang], add todo [task], show todo, mark 42 status, clean slate.")).pack(side="left", padx=10, pady=10)

        ctk.CTkButton(self.main_h, text="PURGE LOG", font=("Orbitron", 7), width=80, height=22, fg_color="transparent", border_width=1, border_color="#1a1a25",
                       command=self._clear_chat).pack(side="right", padx=10, pady=10)

        # Chat Stream
        self.chat_scroll = ctk.CTkScrollableFrame(self.main_f, fg_color="transparent")
        self.chat_scroll.pack(expand=True, fill="both", padx=15, pady=5)

        # Optimized Input Section
        self.bottom_bar = ctk.CTkFrame(self.main_f, fg_color="#08080c", height=70, corner_radius=0)
        self.bottom_bar.pack(fill="x", side="bottom")

        self.input_entry = ctk.CTkEntry(self.bottom_bar, placeholder_text="Awaiting operator command...", font=("Consolas", 12),
                                        fg_color="#121217", border_color="#1a1a25", corner_radius=8)
        self.input_entry.place(relx=0.45, rely=0.5, relwidth=0.82, anchor="center")
        self.input_entry.bind("<Return>", self._send_command)

        self.typing_label = ctk.CTkLabel(self.main_f, text="", font=("Segoe UI", 9, "italic"), text_color="#666666")
        self.typing_label.pack(side="bottom", anchor="w", padx=25, pady=2)

        self.mic_btn = ctk.CTkButton(self.bottom_bar, text="🎤", width=40, height=40, corner_radius=8, fg_color="#121217", hover_color="#1a1a25",
                                     text_color="#00d4ff", font=("Segoe UI", 16), command=self._on_voice)
        self.mic_btn.place(relx=0.93, rely=0.5, anchor="center")

    def _clear_chat(self):
        for widget in self.chat_scroll.winfo_children():
            widget.destroy()

    def _on_voice(self):
        threading.Thread(target=self.assistant._trigger_mic, daemon=True).start()

    def add_message(self, role, text):
        align = "e" if role == "User" else "w"
        bg_color = "#1a1a20" if role == "User" else "#0a0a0f" # Deep colors for professional look
        text_color = "#ffffff"

        frame = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        frame.pack(fill="x", pady=4, padx=10)

        bubble = ctk.CTkFrame(frame, fg_color=bg_color, corner_radius=8, border_width=1, border_color="#1a1a25")
        bubble.pack(anchor=align, padx=5)

        if role != "User":
            label = "✦ VEDA" if role == "Veda" else f"◈ {role.upper()}"
            ctk.CTkLabel(bubble, text=label, font=("Orbitron", 8, "bold"), text_color="#00d4ff").pack(anchor="w", padx=12, pady=(6, 0))

        msg = ctk.CTkLabel(bubble, text=text, font=("Segoe UI", 11), text_color=text_color, wraplength=480, justify="left")
        msg.pack(padx=12, pady=(2, 8))

        self.chat_scroll._parent_canvas.yview_moveto(1.0)

    def set_state(self, status):
        valid_states = ["idle", "thinking", "speaking", "alert"]
        self.status = status if status in valid_states else "idle"

        if self.status == "thinking":
            self.typing_label.configure(text="Veda is analyzing tactical data...")
        elif self.status == "speaking":
            self.typing_label.configure(text="Veda is formulating response...")
        else:
            self.typing_label.configure(text="")

    def _send_command(self, event):
        cmd = self.input_entry.get()
        if cmd:
            self.input_entry.delete(0, "end")
            self.add_message("User", cmd)
            threading.Thread(target=self.assistant.process_command, args=(cmd,), daemon=True).start()

    def _start_drag(self, event):
        self.x = event.x; self.y = event.y

    def _drag(self, event):
        self.geometry(f"+{self.winfo_x() + event.x - self.x}+{self.winfo_y() + event.y - self.y}")

    def start(self):
        self.mainloop()
