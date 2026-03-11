import customtkinter as ctk
import threading
import random
import time
from veda.utils.health import get_system_summary

class VedaGUI(ctk.CTk):
    def __init__(self, on_send_callback, on_voice_callback):
        super().__init__()

        self.on_send_callback = on_send_callback
        self.on_voice_callback = on_voice_callback

        self.title("VEDA | Tactical Interface")
        self.geometry("900x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main Chat Area
        self.chat_display = ctk.CTkTextbox(self, width=580, height=500, font=("Consolas", 12))
        self.chat_display.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.chat_display.configure(state="disabled")

        # Tactical HUD
        self.hud_frame = ctk.CTkFrame(self)
        self.hud_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.hud_label = ctk.CTkLabel(self.hud_frame, text="SYSTEM DIAGNOSTICS", font=("Courier", 14, "bold"))
        self.hud_label.pack(pady=10)

        self.status_text = ctk.CTkTextbox(self.hud_frame, width=200, height=250, font=("Courier", 10))
        self.status_text.pack(padx=5, pady=5)
        self.status_text.configure(state="disabled")

        self.protocol_label = ctk.CTkLabel(self.hud_frame, text="ACTIVE PROTOCOLS", font=("Courier", 12))
        self.protocol_label.pack(pady=(20, 5))
        self.protocol_display = ctk.CTkLabel(self.hud_frame, text="STANDARD", text_color="cyan", font=("Courier", 14, "bold"))
        self.protocol_display.pack()

        # Neural Link Status
        self.link_label = ctk.CTkLabel(self.hud_frame, text="NEURAL LINK", font=("Courier", 12))
        self.link_label.pack(pady=(20, 5))
        self.link_display = ctk.CTkLabel(self.hud_frame, text="ESTABLISHED", text_color="green", font=("Courier", 12, "bold"))
        self.link_display.pack()

        # Input Area
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Enter tactical command...", font=("Consolas", 12))
        self.input_entry.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
        self.input_entry.bind("<Return>", lambda e: self.send_message())

        self.send_button = ctk.CTkButton(self.input_frame, text="EXECUTE", command=self.send_message, font=("Courier", 12, "bold"))
        self.send_button.grid(row=0, column=1, padx=5, pady=10)

        self.voice_button = ctk.CTkButton(self.input_frame, text="AUDIO LINK", command=self.trigger_voice, fg_color="green", font=("Courier", 12, "bold"))
        self.voice_button.grid(row=0, column=2, padx=5, pady=10)

        self.update_chat("Veda", "Tactical interface established. Systems operational.")

        # Start animations and HUD
        self.after(1000, self.update_hud)
        self.after(2000, self.glitch_effect)

    def update_chat(self, sender, message):
        if hasattr(self, 'chat_display'):
            self.after(0, self._update_chat_ui, sender, message)

    def _update_chat_ui(self, sender, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"[{sender.upper()}]: {message}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def update_hud(self):
        summary = get_system_summary()
        text = f"OS: {summary['os']}\n"
        text += f"PYTHON: {summary['python']}\n"

        try:
            stats = self.on_send_callback("system_stats_internal")
            if stats:
                text += f"\n-- HARDWARE --\n{stats}"
        except: pass

        text += f"\n\nDEPS: {'OK' if not summary['missing_deps'] else 'MISSING'}\n"
        if summary['missing_deps']:
            text += f"- {', '.join(summary['missing_deps'][:2])}"

        self.status_text.configure(state="normal")
        self.status_text.delete("1.0", "end")
        self.status_text.insert("1.0", text)
        self.status_text.configure(state="disabled")

        # Random "Heartbeat" flicker on link display
        colors = ["green", "#00FF00", "lime"]
        self.link_display.configure(text_color=random.choice(colors))

        self.after(5000, self.update_hud)

    def glitch_effect(self):
        """MCU-inspired digital glitch animation."""
        if random.random() > 0.95:
             original_color = self.protocol_display.cget("text_color")
             self.protocol_display.configure(text_color="red")
             self.after(100, lambda: self.protocol_display.configure(text_color=original_color))
        self.after(random.randint(1000, 5000), self.glitch_effect)

    def update_protocol(self, protocol_name):
        self.after(0, lambda: self.protocol_display.configure(text=protocol_name.upper()))

    def update_link_status(self, connected):
        if connected:
            self.link_display.configure(text="ESTABLISHED", text_color="green")
        else:
            self.link_display.configure(text="COMPROMISED", text_color="red")

    def send_message(self):
        message = self.input_entry.get()
        if message:
            self.update_chat("Operator", message)
            self.input_entry.delete(0, "end")
            threading.Thread(target=self.on_send_callback, args=(message,), daemon=True).start()

    def trigger_voice(self):
        self.voice_button.configure(text="LISTENING...", fg_color="red")
        threading.Thread(target=self.on_voice_callback, daemon=True).start()

    def reset_voice_button(self):
        self.after(0, lambda: self.voice_button.configure(text="AUDIO LINK", fg_color="green"))
