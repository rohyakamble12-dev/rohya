import customtkinter as ctk
from veda.ui.theme import VedaTheme, VedaState

class VedaPanel(ctk.CTkFrame):
    def __init__(self, master, title: str, theme: VedaTheme, state_ref: VedaState, **kwargs):
        # Establish default tactical parameters
        params = {
            "fg_color": theme.bg_panel,
            "border_color": theme.border_main,
            "border_width": 1,
            "corner_radius": 0
        }
        # Allow kwargs to override defaults (prevents multiple values for same key)
        params.update(kwargs)

        super().__init__(master, **params)
        self.theme = theme
        self.state_ref = state_ref
        self.accent_widgets = []

        # Panel Header
        self.header = ctk.CTkFrame(self, fg_color=theme.bg_header, height=theme.header_height, corner_radius=0)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        # Left accent vertical line
        self.accent_line = ctk.CTkFrame(self.header, fg_color=theme.idle, width=2, height=theme.header_height)
        self.accent_line.pack(side="left")
        self.register_accent_widget(self.accent_line, "fg")

        self.title_label = ctk.CTkLabel(
            self.header, text=title.upper(),
            font=theme.font_header, text_color=theme.idle
        )
        self.title_label.pack(side="left", padx=10)
        self.register_accent_widget(self.title_label, "text")

    def register_accent_widget(self, widget, attr="text"):
        """Adds a widget to the local accent update registry."""
        self.accent_widgets.append((widget, attr))

    def refresh_theme(self, new_color: str):
        """Standard interface to update every registered accent widget."""
        for widget, attr in self.accent_widgets:
            try:
                if attr == "text":
                    widget.configure(text_color=new_color)
                elif attr == "border":
                    widget.configure(border_color=new_color)
                elif attr == "progress":
                    widget.configure(progress_color=new_color)
                elif attr == "fg":
                    widget.configure(fg_color=new_color)
            except Exception:
                pass
