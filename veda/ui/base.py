import customtkinter as ctk

class VedaPanel(ctk.CTkFrame):
    def __init__(self, master, title, **kwargs):
        super().__init__(master, fg_color="#0a0a0f", border_color="#1a1a20", border_width=1, corner_radius=0, **kwargs)
        self.accent_color = "#00d4ff"
        self.accent_widgets = []

        self.header = ctk.CTkFrame(self, fg_color="#050507", height=35, corner_radius=0)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        self.title_label = ctk.CTkLabel(
            self.header, text=title.upper(),
            font=("Orbitron", 12, "bold"), text_color=self.accent_color
        )
        self.title_label.pack(side="left", padx=15)
        self.register_accent_widget(self.title_label, "text")

        # Border accent for MCU feel
        self.accent_border = ctk.CTkFrame(self.header, fg_color=self.accent_color, width=3, height=35)
        self.accent_border.pack(side="left")
        self.register_accent_widget(self.accent_border, "fg")

    def register_accent_widget(self, widget, attr="text"):
        self.accent_widgets.append((widget, attr))

    def refresh_theme(self, color):
        self.accent_color = color
        for widget, attr in self.accent_widgets:
            try:
                if attr == "text": widget.configure(text_color=color)
                elif attr == "border": widget.configure(border_color=color)
                elif attr == "progress": widget.configure(progress_color=color)
                elif attr == "fg": widget.configure(fg_color=color)
            except: pass
