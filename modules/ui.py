import customtkinter as ctk
import tkinter as tk
import math
import random
import threading
import time
import os

class VedaHUD(ctk.CTk):
    def __init__(self, config, assistant):
        super().__init__()
        self.config = config
        self.assistant = assistant

        # 1. Base Config
        self.overrideredirect(True)
        self.attributes("-alpha", 0.95)
        self.attributes("-topmost", True)
        self.geometry("1200x750")
        self.configure(fg_color="#050508")

        # Grid
        self.grid_columnconfigure(0, weight=1, minsize=280)
        self.grid_columnconfigure(1, weight=3, minsize=550)
        self.grid_columnconfigure(2, weight=1, minsize=320)
        self.grid_rowconfigure(0, weight=1)

        self._init_sidebar()
        self._init_neural_core()
        self._init_chat_interface()

        # Interaction
        self.bind("<Button-1>", self._start_drag)
        self.bind("<B1-Motion>", self._drag)

        self.status = "idle"
        self.pulse = 0
        self.glitch_active = False
        self._animate_system()

    def _init_sidebar(self):
        self.side = ctk.CTkFrame(self, fg_color="#08080c", corner_radius=0, border_width=1, border_color="#1a1a25")
        self.side.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        # Optic
        self.cam_f = ctk.CTkFrame(self.side, fg_color="black", height=140, border_width=1, border_color="#1a1a25")
        self.cam_f.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(self.cam_f, text="OPTIC FEED", font=("Orbitron", 8), text_color="#333333").place(relx=0.5, rely=0.5, anchor="center")

        # Links
        self.links = {}
        for link in ["NEURAL", "OPTIC", "VOICE", "DATA"]:
            f = ctk.CTkFrame(self.side, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=4)
            ctk.CTkLabel(f, text=link, font=("Consolas", 9), text_color="#666666").pack(side="left")
            val = ctk.CTkLabel(f, text="READY", font=("Consolas", 9), text_color="#00ffcc")
            val.pack(side="right")
            self.links[link] = val

        # Metrics
        self.metrics_f = ctk.CTkFrame(self.side, fg_color="transparent")
        self.metrics_f.pack(fill="x", padx=20, pady=10)
        self.cpu_bar = self._add_metric("CORE LOAD")
        self.ram_bar = self._add_metric("MEM ALLOC")

        # Protocols
        ctk.CTkLabel(self.side, text="PROTOCOLS", font=("Orbitron", 10, "bold"), text_color="#00d4ff").pack(pady=(20, 5))
        for proto in ["STEALTH", "FOCUS", "GAMING"]:
            cb = ctk.CTkCheckBox(self.side, text=proto, font=("Orbitron", 8), border_width=1, corner_radius=0,
                                 checkbox_height=14, checkbox_width=14, text_color="#cccccc")
            cb.pack(anchor="w", padx=30, pady=3)

    def _add_metric(self, label):
        ctk.CTkLabel(self.metrics_f, text=label, font=("Orbitron", 8), text_color="#666666").pack(anchor="w", pady=(10, 2))
        bar = ctk.CTkProgressBar(self.metrics_f, height=6, progress_color="#00d4ff", fg_color="#121217")
        bar.pack(fill="x")
        bar.set(0.3)
        return bar

    def _init_neural_core(self):
        self.core_f = ctk.CTkFrame(self, fg_color="transparent")
        self.core_f.grid(row=0, column=1, sticky="nsew")

        # Aura
        self.aura = tk.Canvas(self.core_f, bg="#050508", highlightthickness=0)
        self.aura.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.canvas = tk.Canvas(self.core_f, bg="#050508", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center", width=500, height=500)

        self.points = []; self.angle_y = 0
        self.globe_cx = 250; self.globe_cy = 250

        self._init_earth()

    def _init_earth(self):
        """Generates latitude/longitude points for a digital Earth mesh."""
        lats = 16; longs = 24
        for i in range(lats):
            lat = math.pi * i / (lats - 1)
            for j in range(longs):
                lon = 2 * math.pi * j / longs
                x = math.sin(lat) * math.cos(lon)
                y = math.cos(lat)
                z = math.sin(lat) * math.sin(lon)
                self.points.append([x, y, z])

    def _init_chat_interface(self):
        self.chat_f = ctk.CTkFrame(self, fg_color="#0a0a0f", corner_radius=0, border_width=1, border_color="#1a1a25")
        self.chat_f.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)

        self.chat_scroll = ctk.CTkScrollableFrame(self.chat_f, fg_color="transparent")
        self.chat_scroll.pack(expand=True, fill="both", padx=5, pady=5)

        self.bottom_bar = ctk.CTkFrame(self.chat_f, fg_color="#08080c", height=80, corner_radius=0)
        self.bottom_bar.pack(fill="x", side="bottom")

        self.input_entry = ctk.CTkEntry(self.bottom_bar, placeholder_text="Ask Veda...", font=("Consolas", 12),
                                        fg_color="#121217", border_color="#1a1a25", corner_radius=20)
        self.input_entry.place(relx=0.45, rely=0.5, relwidth=0.8, anchor="center")
        self.input_entry.bind("<Return>", self._send_command)

        # Typing indicator
        self.typing_label = ctk.CTkLabel(self.chat_f, text="", font=("Segoe UI", 9, "italic"), text_color="#666666")
        self.typing_label.pack(side="bottom", anchor="w", padx=20, pady=2)

        self.mic_btn = ctk.CTkButton(self.bottom_bar, text="🎤", width=40, height=40, corner_radius=20, fg_color="transparent", hover_color="#1a1a25",
                                     text_color="#00d4ff", font=("Segoe UI", 18), command=self._on_voice)
        self.mic_btn.place(relx=0.92, rely=0.5, anchor="center")

    def _on_voice(self):
        threading.Thread(target=self.assistant._trigger_mic, daemon=True).start()

    def add_message(self, role, text):
        align = "e" if role == "User" else "w"
        # WhatsApp Dark Teal for User, Deep Charcoal for Veda
        bg_color = "#075E54" if role == "User" else "#121212"

        frame = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        frame.pack(fill="x", pady=4, padx=10)

        bubble = ctk.CTkFrame(frame, fg_color=bg_color, corner_radius=12)
        bubble.pack(anchor=align, padx=5)

        if role != "User":
            # Gemini-inspired AI branding
            ctk.CTkLabel(bubble, text="✧ VEDA CORE", font=("Orbitron", 8, "bold"), text_color="#00ffcc").pack(anchor="w", padx=12, pady=(6, 0))

        msg = ctk.CTkLabel(bubble, text=text, font=("Segoe UI", 11), text_color="#eeeeee", wraplength=220, justify="left")
        msg.pack(padx=12, pady=(2, 8))

        meta_f = ctk.CTkFrame(bubble, fg_color="transparent")
        meta_f.pack(anchor="e", padx=10, pady=(0, 5))
        ctk.CTkLabel(meta_f, text=time.strftime("%H:%M"), font=("Segoe UI", 7), text_color="#888888").pack(side="left")
        if role == "User":
            ctk.CTkLabel(meta_f, text=" ✓✓", font=("Segoe UI", 7), text_color="#34B7F1").pack(side="left")

        self.chat_scroll._parent_canvas.yview_moveto(1.0)

    def set_state(self, status):
        valid_states = ["idle", "thinking", "speaking", "alert"]
        self.status = status if status in valid_states else "idle"

        if self.status == "thinking":
            self.typing_label.configure(text="Veda is analyzing...")
        elif self.status == "speaking":
            self.typing_label.configure(text="Veda is replying...")
        else:
            self.typing_label.configure(text="")

    def _animate_system(self):
        self._animate_aura()
        self._animate_earth()
        self.after(40, self._animate_system)

    def _animate_aura(self):
        self.aura.delete("glow")
        # Faster pulse if thinking/speaking
        inc = 0.15 if self.status in ["thinking", "speaking"] else 0.05
        self.pulse = (self.pulse + inc) % (2 * math.pi)

        color_map = {
            "idle": (0, 212, 255),    # Cyan
            "thinking": (176, 38, 255), # Vivid Purple
            "speaking": (0, 255, 204), # Bright Mint
            "alert": (255, 62, 62)     # Hazard Red
        }
        r, g, b = color_map.get(self.status, (0, 212, 255))

        for i in range(3):
            # Dynamic scaling based on system status
            osc = (math.sin(self.pulse + i) + 1) / 2
            base_size = 360 if self.status == "idle" else 420
            size = base_size + i * 70 + osc * 50
            hex_color = f'#{r:02x}{g:02x}{b:02x}'
            self.aura.create_oval(
                600/2 - size/2, 750/2 - size/2,
                600/2 + size/2, 750/2 + size/2,
                outline=hex_color, width=1, tags="glow"
            )

    def _animate_earth(self):
        self.canvas.delete("globe")
        speed = 0.04 if self.status == "thinking" else 0.015
        self.angle_y += speed

        # Heartbeat pulse while speaking
        pulse_scale = 1.0
        if self.status == "speaking":
            pulse_scale = 1.0 + 0.05 * math.sin(time.time() * 12)

        scale = 220 * pulse_scale

        color_map = {"idle": "#00d4ff", "thinking": "#b026ff", "speaking": "#00ffcc", "alert": "#ff3e3e"}
        color = color_map.get(self.status, "#00d4ff")

        proj = []
        for p in self.points:
            x, y, z = p
            # Rotate
            nx = x * math.cos(self.angle_y) - z * math.sin(self.angle_y)
            nz = x * math.sin(self.angle_y) + z * math.cos(self.angle_y)
            proj.append((nx * scale + self.globe_cx, y * scale + self.globe_cy, nz))

        # Draw mesh lines (Earth Grid style)
        for i, pt in enumerate(proj):
            if pt[2] < -0.1: continue

            # Horizontal (Latitudes)
            next_lon = (i + 1) if (i + 1) % 24 != 0 else i - 23
            self.canvas.create_line(pt[0], pt[1], proj[next_lon][0], proj[next_lon][1], fill=color, tags="globe", width=1)

            # Vertical (Longitudes)
            next_lat = i + 24
            if next_lat < len(proj):
                self.canvas.create_line(pt[0], pt[1], proj[next_lat][0], proj[next_lat][1], fill=color, tags="globe", width=1)

            # Nodes
            self.canvas.create_oval(pt[0]-1, pt[1]-1, pt[0]+1, pt[1]+1, fill=color, outline="", tags="globe")

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
