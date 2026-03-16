import customtkinter as ctk
import queue
import logging
from veda.ui.base import VedaPanel
from veda.ui.theme import VedaTheme, VedaState

logger = logging.getLogger("VEDA")

class RightPanel(VedaPanel):
    def __init__(self, master, assistant, theme: VedaTheme, state_ref: VedaState):
        super().__init__(master, "Tactical Feed", theme, state_ref)
        self.assistant = assistant
        self.token_queue = queue.Queue()
        self.active_textbox = None
        self.typing_dots = "·  "

        self.chat_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.chat_container.pack(expand=True, fill="both", padx=5, pady=5)

        self.typing_label = ctk.CTkLabel(self, text="", font=theme.font_chat, text_color="#666666")

        self.ticker = ctk.CTkLabel(self, text="LINK ESTABLISHED | READY", font=theme.font_data, text_color=theme.idle)
        self.ticker.pack(fill="x", padx=10, pady=(5, 0)); self.register_accent_widget(self.ticker, "text")

        self.entry = ctk.CTkEntry(self, placeholder_text="COMMAND >>", font=theme.font_chat, border_width=1, corner_radius=0)
        self.entry.pack(fill="x", padx=10, pady=15); self.register_accent_widget(self.entry, "border")
        self.entry.bind("<Return>", lambda e: master.send_command())

        self.after(100, self._drain_stream_queue)

    def add_message(self, sender, text="", is_user=False):
        bubble_color = self.theme.user_bubble if is_user else self.theme.assistant_bubble
        align = "e" if is_user else "w"

        frame = ctk.CTkFrame(self.chat_container, fg_color=bubble_color, corner_radius=12, border_width=1, border_color="#1a1a20")
        frame.pack(fill="x", pady=8, padx=10, anchor=align)

        label = ctk.CTkLabel(frame, text=sender.upper(), font=self.theme.font_header, text_color=self.accent_color)
        label.pack(anchor="w", padx=15, pady=(8,0))

        # O(1) text insertion system using CTkTextbox
        txt = ctk.CTkTextbox(frame, font=self.theme.font_chat, height=20, border_width=0, fg_color="transparent", wrap="word")
        txt.pack(fill="both", expand=True, padx=10, pady=5)

        if text:
            txt.insert("0.0", text)
            txt.configure(state="disabled")
            self._resize_bubble(txt)

        self.active_textbox = txt
        return txt

    def _resize_bubble(self, txt):
        try:
            line_count = int(txt.index('end-1c').split('.')[0])
            height = min(300, max(45, line_count * 22))
            txt.configure(height=height)
        except: pass

    def start_streaming(self, sender):
        self.show_typing(False)
        self.add_message(sender, text="")
        if self.active_textbox: self.active_textbox.configure(state="normal")

    def queue_token(self, token):
        self.token_queue.put(token)

    def _drain_stream_queue(self):
        count = 0
        while not self.token_queue.empty() and count < 5:
            if self.active_textbox:
                token = self.token_queue.get()
                self.active_textbox.insert("end", token)
                self.active_textbox.see("end")
                self._resize_bubble(self.active_textbox)
            count += 1
        self.after(16, self._drain_stream_queue)

    def show_typing(self, show=True):
        if show:
            self.typing_label.pack(side="bottom", pady=2)
            self._animate_typing()
        else:
            self.typing_label.pack_forget()

    def _animate_typing(self):
        if self.typing_label.winfo_manager():
            self.typing_dots = {"·  ": "·· ", "·· ": "···", "···": "·  "}[self.typing_dots]
            self.typing_label.configure(text=self.typing_dots)
            self.after(400, self._animate_typing)

    def update_ticker(self, text):
        self.ticker.configure(text=text.upper())
