import customtkinter as ctk
from veda.ui.theme import VedaTheme, VedaState

class VedaPanel(ctk.CTkFrame):
    def __init__(self, master, title: str, theme: VedaTheme, state: VedaState, **kwargs):
        super().__init__(
            master,
            fg_color=theme.bg_panel,
            border_color=theme.border_main,
            border_width=1,
            corner_radius=0,
            **kwargs
        )
        self.theme = theme
        self.state = state
        self.accent_widgets = []

        # Header (Cinematic minimalist)
        self.header = ctk.CTkFrame(self, fg_color=theme.bg_header, height=theme.header_height, corner_radius=0)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        self.title_label = ctk.CTkLabel(
            self.header, text=title.upper(),
            font=theme.font_header, text_color=theme.idle
        )
        self.title_label.pack(side="left", padx=10)
        self.register_accent_widget(self.title_label, "text")

        # Stark-style vertical accent border
        self.accent_border = ctk.CTkFrame(self.header, fg_color=theme.idle, width=2, height=theme.header_height)
        self.accent_border.pack(side="left")
        self.register_accent_widget(self.accent_border, "fg")

    def register_accent_widget(self, widget, attr="text"):
        """Registers a widget to be updated when the theme color changes."""
        self.accent_widgets.append((widget, attr))

    def refresh_theme(self, color: str):
        """Standard interface for panel re-theming."""
        for widget, attr in self.accent_widgets:
            try:
                if attr == "text": widget.configure(text_color=color)
                elif attr == "border": widget.configure(border_color=color)
                elif attr == "progress": widget.configure(progress_color=color)
                elif attr == "fg": widget.configure(fg_color=color)
            except: pass
