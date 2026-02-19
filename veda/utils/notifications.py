import os

# Robust import for Windows Toast notifications
try:
    from winrt.windows.ui.notifications import ToastNotificationManager, ToastNotification
    from winrt.windows.data.xml.dom import XmlDocument
    WINRT_AVAILABLE = True
except ImportError:
    WINRT_AVAILABLE = False
    print("Warning: Windows Toast notifications (winrt) not found. Falling back to console alerts.")

class VedaNotifications:
    @staticmethod
    def send_toast(title, message):
        """Sends a native Windows 11 Toast notification."""
        if not WINRT_AVAILABLE:
            print(f"[TOAST FALLBACK] {title}: {message}")
            return

        try:
            # Create the toast XML template
            toast_xml = f"""
            <toast>
                <visual>
                    <binding template='ToastGeneric'>
                        <text>{title}</text>
                        <text>{message}</text>
                    </binding>
                </visual>
            </toast>
            """

            xml_doc = XmlDocument()
            xml_doc.load_xml(toast_xml)

            notification = ToastNotification(xml_doc)
            # App ID is required to show the toast
            notifier = ToastNotificationManager.create_toast_notifier("Veda Assistant")
            notifier.show(notification)
        except Exception as e:
            print(f"Failed to send toast: {e}")

    @staticmethod
    def alert(title, message):
        """Standard alert that uses both toast and log."""
        VedaNotifications.send_toast(title, message)
        print(f"NOTIFICATION: {title} - {message}")
