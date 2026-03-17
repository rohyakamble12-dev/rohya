try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
except:
    TOAST_AVAILABLE = False

class NotificationModule:
    def __init__(self, gui):
        self.gui = gui
        self.toaster = ToastNotifier() if TOAST_AVAILABLE else None

    def notify(self, message, title="VEDA"):
        self.gui.add_message("System", message)
        if self.toaster:
            try: self.toaster.show_toast(title, message, duration=5, threaded=True)
            except: pass
