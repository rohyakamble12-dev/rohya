import os
import psutil

class VedaModes:
    def __init__(self, assistant_ref):
        self.assistant = assistant_ref
        self.active_mode = "NORMAL"

    def focus_mode(self):
        """Optimizes system for focus."""
        self.active_mode = "FOCUS"
        # 1. Set volume to a lower, focus-friendly level
        self.assistant.system.set_volume(20)
        # 2. Lower brightness for eye comfort
        self.assistant.system.set_brightness(40)
        # 3. Protocol updates
        self.assistant.protocols.protocols["context_monitoring"] = True
        return "Focus Mode Engaged. I've optimized your environment for deep work."

    def stealth_mode(self):
        """Minimizes Veda's presence."""
        self.active_mode = "STEALTH"
        # 1. Mute voice (or very low)
        self.assistant.system.set_volume(0)
        # 2. Update HUD via assistant reference (alpha/transparency)
        self.assistant.gui.after(0, lambda: self.assistant.gui.attributes("-alpha", 0.4))
        # 3. Disable context tracking for maximum privacy
        self.assistant.protocols.protocols["context_monitoring"] = False
        self.assistant.context.stop_monitoring()
        return "Stealth Mode Active. I will remain in the shadows."

    def gaming_mode(self):
        """Optimizes system for high performance gaming."""
        self.active_mode = "GAMING"
        # 1. Boost brightness
        self.assistant.system.set_brightness(100)
        # 2. Notification management (Quiet HUD)
        self.assistant.gui.after(0, lambda: self.assistant.gui.attributes("-alpha", 0.3))
        # 3. Memory Optimization (Clear RAM simulation)
        count = 0
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                # We won't actually kill random processes for safety, but we'll show we're monitoring
                if proc.info['memory_info'].rss > 500 * 1024 * 1024: # 500MB+
                    count += 1
            except:
                pass

        return f"Gaming Mode engaged. System levels optimized. Found {count} high-memory background tasks."

    def normal_mode(self):
        """Restores standard settings."""
        self.active_mode = "NORMAL"
        self.assistant.system.set_volume(50)
        self.assistant.system.set_brightness(70)
        self.assistant.gui.after(0, lambda: self.assistant.gui.attributes("-alpha", 0.85))
        self.assistant.protocols.protocols["context_monitoring"] = True
        self.assistant.context.start_monitoring()
        return "Standard protocols restored."
