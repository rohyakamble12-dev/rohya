import customtkinter as ctk
import threading

class VedaGUI(ctk.CTk):
    def __init__(self, on_send_callback, on_voice_callback):
        super().__init__()

        self.on_send_callback = on_send_callback
        self.on_voice_callback = on_voice_callback

        self.title("VEDA - Advanced Assistant")
        self.geometry("600x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Chat display
        self.chat_display = ctk.CTkTextbox(self, width=580, height=500)
        self.chat_display.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.chat_display.configure(state="disabled")

        # Input frame
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Type a command...")
        self.input_entry.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
        self.input_entry.bind("<Return>", lambda e: self.send_message())

        self.send_button = ctk.CTkButton(self.input_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=0, column=1, padx=5, pady=10)

        self.voice_button = ctk.CTkButton(self.input_frame, text="Voice", command=self.trigger_voice, fg_color="green")
        self.voice_button.grid(row=0, column=2, padx=5, pady=10)

        self.update_chat("Veda", "System Online. Ready to assist.")

    def update_chat(self, sender, message):
        """Thread-safe way to update the chat display."""
        self.after(0, self._update_chat_ui, sender, message)

    def _update_chat_ui(self, sender, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"{sender}: {message}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def send_message(self):
        message = self.input_entry.get()
        if message:
            self.update_chat("You", message)
            self.input_entry.delete(0, "end")
            # Run the callback in a separate thread to keep UI responsive
            threading.Thread(target=self.on_send_callback, args=(message,), daemon=True).start()

    def trigger_voice(self):
        self.voice_button.configure(text="Listening...", fg_color="red")
        threading.Thread(target=self.on_voice_callback, daemon=True).start()

    def reset_voice_button(self):
        self.after(0, lambda: self.voice_button.configure(text="Voice", fg_color="green"))
