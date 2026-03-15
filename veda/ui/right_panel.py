import customtkinter as ctk
from veda.ui.base import VedaPanel
import queue

class RightPanel(VedaPanel):
    def __init__(self, master, assistant):
        super().__init__(master, "Tactical Feed")
        self.assistant = assistant
        self.token_queue = queue.Queue()
        self.active_textbox = None

        self.chat_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.chat_container.pack(expand=True, fill="both", padx=5, pady=5)

        self.typing_label = ctk.CTkLabel(self, text="· · ·", font=("Consolas", 14, "bold"))

        self.ticker = ctk.CTkLabel(self, text="READY", font=("Consolas", 10), text_color="#00d4ff")
        self.ticker.pack(fill="x", padx=10)

        self.entry = ctk.CTkEntry(self, placeholder_text="COMMAND >>", font=("Consolas", 12), border_width=1)
        self.entry.pack(fill="x", padx=10, pady=10)
        self.entry.bind("<Return>", lambda e: self.master.send_command())

        self.after(100, self._drain_tokens)

    def add_message(self, sender, text="", is_user=False):
        bubble_color = "#1a1a20" if is_user else "#050507"
        align = "e" if is_user else "w"

        frame = ctk.CTkFrame(self.chat_container, fg_color=bubble_color, corner_radius=12)
        frame.pack(fill="x", pady=5, padx=5, anchor=align)

        label = ctk.CTkLabel(frame, text=sender.upper(), font=("Orbitron", 8, "bold"), text_color=self.accent_color)
        label.pack(anchor="w", padx=10, pady=(5,0))

        txt = ctk.CTkTextbox(frame, font=("Consolas", 11), height=20, border_width=0, fg_color="transparent")
        txt.pack(fill="both", expand=True, padx=5, pady=5)

        if text:
            txt.insert("0.0", text)
            # Adjust height based on content
            line_count = int(txt.index('end-1c').split('.')[0])
            txt.configure(height=min(200, line_count * 20))
            txt.configure(state="disabled")

        self.active_textbox = txt
        return txt

    def start_streaming(self, sender):
        self.add_message(sender, text="")
        self.active_textbox.configure(state="normal")

    def queue_token(self, token):
        self.token_queue.put(token)

    def _drain_tokens(self):
        if not self.token_queue.empty() and self.active_textbox:
            token = self.token_queue.get()
            self.active_textbox.insert("end", token)
            self.active_textbox.see("end")

            # Auto-height adjustment
            line_count = int(self.active_textbox.index('end-1c').split('.')[0])
            self.active_textbox.configure(height=min(200, line_count * 20))

        self.after(20, self._drain_tokens)

    def show_typing(self, show=True):
        if show:
            self.typing_label.pack(side="bottom", pady=2)
            self._pulse_typing()
        else:
            self.typing_label.pack_forget()

    def _pulse_typing(self):
        if self.typing_label.winfo_manager():
            current = self.typing_label.cget("text")
            next_t = "· · ·" if current == " " else " "
            self.typing_label.configure(text=next_t)
            self.after(500, self._pulse_typing)

    def update_ticker(self, text):
        self.ticker.configure(text=text.upper())

    def refresh_theme(self, color):
        super().refresh_theme(color)
        self.ticker.configure(text_color=color)
        self.entry.configure(border_color=color)
        self.typing_label.configure(text_color=color)
