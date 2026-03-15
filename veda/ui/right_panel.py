import customtkinter as ctk
import queue
import logging
from veda.ui.base import VedaPanel

logger = logging.getLogger("VEDA")

class RightPanel(VedaPanel):
    def __init__(self, master, assistant):
        super().__init__(master, "Tactical Feed")
        self.assistant = assistant
        self.token_queue = queue.Queue()
        self.active_textbox = None

        self.chat_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.chat_container.pack(expand=True, fill="both", padx=5, pady=5)

        # Typing indicator (Pulsing label)
        self.typing_label = ctk.CTkLabel(self, text="NEURAL PROCESSOR ACTIVE · · ·", font=("Consolas", 10, "bold"), text_color="#aaaaaa")

        self.ticker = ctk.CTkLabel(self, text="LINK ESTABLISHED | READY", font=("Consolas", 11), text_color="#00d4ff")
        self.ticker.pack(fill="x", padx=10, pady=(5, 0))
        self.register_accent_widget(self.ticker, "text")

        # Command entry
        self.entry = ctk.CTkEntry(self, placeholder_text="ENTER COMMAND >>", font=("Consolas", 12), border_width=1, corner_radius=0)
        self.entry.pack(fill="x", padx=10, pady=15)
        self.register_accent_widget(self.entry, "border")
        self.entry.bind("<Return>", lambda e: self.master.send_command())

        self._drain_tokens()

    def add_message(self, sender, text="", is_user=False):
        bubble_color = "#1a1a20" if is_user else "#08080c"
        align = "e" if is_user else "w"

        frame = ctk.CTkFrame(self.chat_container, fg_color=bubble_color, corner_radius=12, border_width=1, border_color="#1a1a20")
        frame.pack(fill="x", pady=8, padx=10, anchor=align)

        label = ctk.CTkLabel(frame, text=sender.upper(), font=("Orbitron", 9, "bold"), text_color=self.accent_color)
        label.pack(anchor="w", padx=15, pady=(8,0))

        # Scrollable bubble content
        txt = ctk.CTkTextbox(frame, font=("Consolas", 11), height=20, border_width=0, fg_color="transparent", wrap="word")
        txt.pack(fill="both", expand=True, padx=10, pady=5)

        if text:
            txt.insert("0.0", text)
            txt.configure(state="disabled")
            self._update_bubble_height(txt)

        self.active_textbox = txt
        return txt

    def _update_bubble_height(self, textbox):
        try:
            line_count = int(textbox.index('end-1c').split('.')[0])
            height = min(350, max(45, line_count * 22))
            textbox.configure(height=height)
        except:
            pass

    def start_streaming(self, sender):
        self.add_message(sender, text="")
        self.active_textbox.configure(state="normal")

    def queue_token(self, token):
        self.token_queue.put(token)

    def _drain_tokens(self):
        try:
            if not self.token_queue.empty() and self.active_textbox:
                token = self.token_queue.get()
                self.active_textbox.insert("end", token)
                self.active_textbox.see("end")
                self._update_bubble_height(self.active_textbox)

            # Smooth interval
            self.after(30, self._drain_tokens)
        except Exception as e:
            logger.warning(f"Token link error: {e}")
            self.after(100, self._drain_tokens)

    def show_typing(self, show=True):
        if show:
            self.typing_label.pack(side="bottom", pady=2)
            self._pulse_typing()
        else:
            self.typing_label.pack_forget()

    def _pulse_typing(self):
        if self.typing_label.winfo_manager():
            try:
                current = self.typing_label.cget("text")
                if "· · ·" in current: next_t = "NEURAL PROCESSOR ACTIVE"
                else: next_t = "NEURAL PROCESSOR ACTIVE · · ·"
                self.typing_label.configure(text=next_t)
                self.after(600, self._pulse_typing)
            except: pass

    def update_ticker(self, text):
        self.ticker.configure(text=text.upper())

    def refresh_theme(self, color):
        super().refresh_theme(color)
        self.typing_label.configure(text_color=color)
