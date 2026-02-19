import customtkinter as ctk
import threading
import tkinter as tk

class VedaGUI(ctk.CTk):
    def __init__(self, on_send_callback, on_voice_callback):
        super().__init__()

        self.on_send_callback = on_send_callback
        self.on_voice_callback = on_voice_callback

        # HUD Configuration
        self.title("VEDA HUD")
        self.geometry("450x600+50+50") # Set to a corner by default
        self.overrideredirect(True) # Remove standard title bar
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.85) # Transparency
        self.configure(fg_color="#010a12") # Very dark blue/black

        # Colors
        self.accent_color = "#00d4ff" # Jarvis Cyan
        self.text_color = "#e0f7fa"

        # Dragging functionality for the HUD
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.do_move)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header / Title Bar Area
        self.header = ctk.CTkFrame(self, height=40, fg_color="#021627", corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")

        self.title_label = ctk.CTkLabel(self.header, text="V E D A  I N T E R F A C E",
                                        font=("Orbitron", 14, "bold"), text_color=self.accent_color)
        self.title_label.pack(side="left", padx=20)

        self.close_btn = ctk.CTkButton(self.header, text="X", width=30, height=30,
                                       fg_color="transparent", hover_color="#ff4b2b",
                                       command=self.destroy)
        self.close_btn.pack(side="right", padx=10)

        # Chat display area
        self.chat_display = ctk.CTkTextbox(self, width=430, height=450,
                                           fg_color="#01121f",
                                           text_color=self.text_color,
                                           font=("Consolas", 12),
                                           border_width=1, border_color=self.accent_color)
        self.chat_display.grid(row=1, column=0, padx=10, pady=(10, 5), sticky="nsew")
        self.chat_display.configure(state="disabled")

        # Status Bar
        self.status_bar = ctk.CTkLabel(self, text="SYSTEM READY", font=("Consolas", 10), text_color=self.accent_color)
        self.status_bar.grid(row=2, column=0, sticky="w", padx=15)

        self.metrics_label = ctk.CTkLabel(self, text="CPU: 0% | RAM: 0%", font=("Consolas", 10), text_color=self.accent_color)
        self.metrics_label.grid(row=2, column=0, sticky="e", padx=15)

        # Input area
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Enter Command...",
                                        fg_color="#01121f", border_color=self.accent_color,
                                        text_color=self.accent_color)
        self.input_entry.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
        self.input_entry.bind("<Return>", lambda e: self.send_message())

        self.voice_button = ctk.CTkButton(self.input_frame, text="MIC", width=60,
                                          fg_color="transparent", border_width=1,
                                          border_color=self.accent_color,
                                          text_color=self.accent_color,
                                          hover_color="#004d61",
                                          command=self.trigger_voice)
        self.voice_button.grid(row=0, column=1, padx=0, pady=10)

        # Protocol Toggles (New)
        self.protocol_frame = ctk.CTkFrame(self, fg_color="#01121f", border_width=1, border_color=self.accent_color)
        self.protocol_frame.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.deep_search_var = tk.BooleanVar(value=False)
        self.deep_search_cb = ctk.CTkCheckBox(self.protocol_frame, text="DEEP RESEARCH",
                                              variable=self.deep_search_var,
                                              command=lambda: self.on_protocol_toggle("deep_research"),
                                              font=("Consolas", 10), text_color=self.accent_color,
                                              fg_color=self.accent_color, hover_color="#004d61")
        self.deep_search_cb.pack(side="left", padx=10, pady=5)

        self.private_var = tk.BooleanVar(value=False)
        self.private_cb = ctk.CTkCheckBox(self.protocol_frame, text="SECURE MODE",
                                          variable=self.private_var,
                                          command=lambda: self.on_protocol_toggle("private_mode"),
                                          font=("Consolas", 10), text_color=self.accent_color,
                                          fg_color=self.accent_color, hover_color="#004d61")
        self.private_cb.pack(side="left", padx=10, pady=5)

        self.context_var = tk.BooleanVar(value=True)
        self.context_cb = ctk.CTkCheckBox(self.protocol_frame, text="REAL-TIME CONTEXT",
                                          variable=self.context_var,
                                          command=lambda: self.on_protocol_toggle("context_monitoring"),
                                          font=("Consolas", 10), text_color=self.accent_color,
                                          fg_color=self.accent_color, hover_color="#004d61")
        self.context_cb.pack(side="left", padx=10, pady=5)

        # Suggestions area
        self.suggestion_label = ctk.CTkLabel(self, text="", font=("Consolas", 11, "italic"), text_color="#ffff00")
        self.suggestion_label.grid(row=5, column=0, padx=15, pady=(0, 5), sticky="w")

        self.update_chat("Veda", "HUD Initialized. Connection established.")
        self.pulse_status()
        self.update_metrics()

    def update_metrics(self):
        """Periodically updates hardware metrics on the HUD."""
        import psutil
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        self.metrics_label.configure(text=f"CPU: {cpu}% | RAM: {ram}%")
        self.after(5000, self.update_metrics)

    def pulse_status(self):
        """Adds a subtle glowing animation to the status bar."""
        current_text = self.status_bar.cget("text")
        if "READY" in current_text:
            colors = [self.accent_color, "#006d82", self.accent_color]
            def animate(idx=0):
                if "READY" in self.status_bar.cget("text"):
                    self.status_bar.configure(text_color=colors[idx % len(colors)])
                    self.after(1000, animate, idx + 1)
            animate()

    def update_chat(self, sender, message):
        """Thread-safe way to update the chat display."""
        self.after(0, self._update_chat_ui, sender, message)

    def _update_chat_ui(self, sender, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"[{sender.upper()}]: {message}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def send_message(self):
        message = self.input_entry.get()
        if message:
            self.update_chat("User", message)
            self.input_entry.delete(0, "end")
            self.status_bar.configure(text="PROCESSING...")
            threading.Thread(target=self.on_send_callback, args=(message,), daemon=True).start()

    def show_suggestion(self, text):
        """Displays a proactive suggestion on the HUD."""
        self.after(0, lambda: self.suggestion_label.configure(text=f"VEDA TIP: {text}"))

    def on_protocol_toggle(self, name):
        # We'll pass this back to the assistant via a callback if needed,
        # but for now we'll just handle it in the assistant's reference
        self.status_bar.configure(text=f"PROTOCOL {name.upper()} UPDATED")

    def trigger_voice(self):
        self.voice_button.configure(text="...", border_color="#ff4b2b", text_color="#ff4b2b")
        self.status_bar.configure(text="LISTENING...")
        threading.Thread(target=self.on_voice_callback, daemon=True).start()

    def reset_voice_button(self):
        self.after(0, self._reset_voice_ui)

    def _reset_voice_ui(self):
        self.voice_button.configure(text="MIC", border_color=self.accent_color, text_color=self.accent_color)
        self.status_bar.configure(text="SYSTEM READY")

    # Movement Logic
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")
