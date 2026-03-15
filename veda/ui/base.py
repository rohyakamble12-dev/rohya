import customtkinter as ctk

class VedaPanel(ctk.CTkFrame):
    def __init__(self, master, title, **kwargs):
        super().__init__(master, fg_color="#0a0a0f", border_color="#1a1a20", border_width=1, **kwargs)
        self.accent_color = "#00d4ff"

        # Header (No rounded corners)
        self.header = ctk.CTkFrame(self, fg_color="#050507", height=30, corner_radius=0)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        self.title_label = ctk.CTkLabel(
            self.header, text=title.upper(),
            font=("Orbitron", 12, "bold"), text_color=self.accent_color
        )
        self.title_label.pack(side="left", padx=10)

    def refresh_theme(self, color):
        self.accent_color = color
        self.title_label.configure(text_color=color)
        # Inherited panels will override for more specific updates
