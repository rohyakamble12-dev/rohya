import customtkinter as ctk
from veda.ui.base import VedaPanel
from veda.ui.theme import VedaTheme, VedaState

class TopBar(VedaPanel):
    def __init__(self, master, theme: VedaTheme, state_ref: VedaState):
        super().__init__(master, "Veda Core", theme, state_ref, fg_color=theme.bg_topbar, height=theme.topbar_height)
        self.theme = theme
        self.state_ref = state_ref
        self.pack_propagate(False)


        # Action Buttons
        self.btn_unload = ctk.CTkButton(
            self, text="UNLOAD", fg_color="#440000", hover_color="#ff4b2b",
            width=80, height=25, font=theme.font_header, corner_radius=0,
            command=master.terminate
        )
        self.btn_unload.pack(side="right", padx=10)

        # Minimize button (requested)
        self.btn_min = ctk.CTkButton(
            self, text="—", fg_color="transparent", hover_color="#1a1a20",
            width=30, height=25, font=theme.font_header, corner_radius=0,
            command=master.iconify
        )
        self.btn_min.pack(side="right", padx=5)

    def refresh_theme(self, new_color: str):
        self.title_label.configure(text_color=new_color)
