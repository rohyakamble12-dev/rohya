import os

# Robust import for Windows Toast notifications
try:
    from winrt.windows.ui.notifications import ToastNotificationManager, ToastNotification
    from winrt.windows.data.xml.dom import XmlDocument
    WINRT_AVAILABLE = True
except:
    WINRT_AVAILABLE = False

try:
    from win10toast import ToastNotifier
    WIN10TOAST_AVAILABLE = True
    toaster = ToastNotifier()
except:
    WIN10TOAST_AVAILABLE = False

class VedaNotifications:
    @staticmethod
    def send_toast(title, message):
        """Sends a native Windows Toast notification with multiple fallbacks."""
        # 1. Try WinRT (Modern Win 10/11)
        if WINRT_AVAILABLE:
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
                notifier = ToastNotificationManager.create_toast_notifier("Veda Assistant")
                notifier.show(notification)
                return
            except:
                pass

        # 2. Try win10toast (Classic)
        if WIN10TOAST_AVAILABLE:
            try:
                toaster.show_toast(title, message, duration=5, threaded=True)
                return
            except:
                pass

        # 3. Last resort: Console
        print(f"[TOAST FALLBACK] {title}: {message}")

    @staticmethod
    def alert(title, message):
        """Standard alert that uses both toast and log."""
        VedaNotifications.send_toast(title, message)
        print(f"NOTIFICATION: {title} - {message}")
