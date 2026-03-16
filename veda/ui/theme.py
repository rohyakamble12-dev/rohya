from dataclasses import dataclass, field
from typing import Dict, Tuple

@dataclass
class VedaTheme:
    # Basic Colors
    bg_main: str = "#08080a"
    bg_panel: str = "#0a0a0f"
    bg_header: str = "#121217"
    bg_topbar: str = "#050507"

    border_main: str = "#1a1a20"
    border_grid: str = "#1a1a25"

    # State Colors
    idle: str = "#00d4ff"
    thinking: str = "#ffcc00"
    speaking: str = "#00ff7f"
    alert: str = "#ff4b2b"

    # Bubble Colors
    user_bubble: str = "#1a1a25"
    assistant_bubble: str = "#0a0a15"
    system_bubble: str = "#201010"

    # Fonts
    # Orbitron for headers/labels, Consolas for data/chat
    font_header: Tuple = ("Orbitron", 9, "bold")
    font_label: Tuple = ("Orbitron", 8)
    font_metrics: Tuple = ("Consolas", 9, "bold")
    font_chat: Tuple = ("Consolas", 11)
    font_data: Tuple = ("Consolas", 10)
    font_timestamp: Tuple = ("Consolas", 7)

    # Sizes
    header_height: int = 22
    topbar_height: int = 45
    window_width: int = 1100
    window_height: int = 650
    bubble_radius: int = 12

@dataclass
class VedaState:
    status: str = "idle"
    camera_active: bool = True
    mic_active: bool = False
    pulse_active: bool = False
    neural_link: bool = True
    network_up: bool = True
    topmost: bool = False

    # Protocol States
    protocols: Dict[str, bool] = field(default_factory=lambda: {
        "deep_search": False,
        "private": True,
        "context": True
    })

    execution_plan: str = "Standby."

    def get_protocols(self) -> Dict[str, bool]:
        return self.protocols
