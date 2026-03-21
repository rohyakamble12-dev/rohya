from modules.system import SystemModule
from modules.intel import IntelModule
from modules.media import MediaModule
from modules.productivity import ProductivityModule
from modules.vision import VisionModule
from modules.files import FilesModule
from modules.protocols import ProtocolModule
from modules.iot import IOTModule
from modules.comms import CommsModule
from modules.automation import AutomationModule
import logging

class CommandRouter:
    def __init__(self, assistant):
        self.assistant = assistant
        self.system = SystemModule()
        self.intel = IntelModule()
        self.media = MediaModule()
        self.prod = ProductivityModule(assistant)
        self.vision = VisionModule()
        self.files = FilesModule()
        self.iot = IOTModule(assistant.config)
        self.protocols = ProtocolModule(assistant)
        self.comms = CommsModule()
        self.auto = AutomationModule()

    def route(self, intent_data):
        try:
            intent = intent_data.get("intent", "none")
            params = intent_data.get("params", {})

            # 1. System Controls
            if intent == "open_app":
                res = self.system.open_app(params.get("app_name"))
                if "failed" in res.lower() or "violation" in res.lower():
                    # App-to-Web Fallback
                    intel_res = self.intel.search(f"How to open {params.get('app_name')} or official site")
                    return f"Local interface for {params.get('app_name')} not found. Intelligence report: {intel_res}"
                return res
            elif intent == "close_app":
                return self.system.close_app(params.get("app_name"))
            elif intent == "screenshot":
                return self.system.screenshot()
            elif intent == "system_health":
                return self.system.get_health()
            elif intent == "system_info":
                return self.system.get_sys_info()
            elif intent == "network_info":
                return self.system.get_network_info()
            elif intent == "lock_pc":
                return self.system.lock_pc()
            elif intent == "active_window":
                return self.system.get_active_window()
            elif intent == "window_control":
                return self.system.manipulate_window(params.get("action"), params.get("title"))
            elif intent == "set_theme":
                return self.system.set_dark_mode(params.get("mode", "dark") == "dark")
            elif intent == "send_email":
                return self.comms.send_email(params.get("recipient"), params.get("subject"), params.get("body"))
            elif intent == "open_social":
                return self.comms.open_social(params.get("platform"))
            elif intent == "macro_record":
                return self.auto.start_recording(params.get("name"))
            elif intent == "macro_stop":
                return self.auto.stop_recording()
            elif intent == "macro_play":
                return self.auto.play_macro(params.get("name"))
            elif intent == "list_procs":
                return self.system.list_processes()
            elif intent == "kill_proc":
                return self.system.terminate_process(params.get("process_name"))
            elif intent == "move_file":
                return self.system.move_file(params.get("source"), params.get("destination"))
            elif intent == "set_volume":
                return self.system.set_volume(params.get("level", 50), params.get("app_name"))
            elif intent == "set_brightness":
                return self.system.set_brightness(params.get("level", 50))

            # 2. Intel & Search
            elif intent == "web_search":
                return self.intel.search(params.get("query"))
            elif intent == "wikipedia":
                return self.intel.get_wiki(params.get("topic"))
            elif intent == "weather":
                return self.intel.get_weather(params.get("city"))

            # 3. Media
            elif intent == "play_music":
                return self.media.play_youtube(params.get("song"))
            elif intent == "media_control":
                return self.media.control(params.get("action"))
            elif intent == "translate":
                return self.media.translate(params.get("text"), params.get("target_lang", "en"))

            # 4. Productivity
            elif intent == "add_todo":
                self.assistant.memory.add_todo(params.get("task"))
                return f"Task added: {params.get('task')}"
            elif intent == "show_todo":
                todos = self.assistant.memory.get_todos()
                return "\n".join([f"{t[0]}. {t[1]}" for t in todos]) if todos else "Clear schedule."
            elif intent == "pomodoro":
                return self.prod.start_pomodoro(int(params.get("minutes", 25)))
            elif intent == "reminder":
                return self.prod.remind_me(params.get("task"), params.get("time_str"))
            elif intent == "list_schedule":
                return self.prod.list_schedule()

            # 5. Vision
            elif intent == "vision_describe":
                return self.vision.capture_and_describe()
            elif intent == "vision_face":
                return self.vision.face_detect()
            elif intent == "screen_read":
                return self.vision.screen_ocr()

            # 6. Files
            elif intent == "read_pdf":
                return self.files.read_pdf(params.get("path"))
            elif intent == "open_doc":
                return self.files.open_document(params.get("name"))
            elif intent == "file_find":
                return self.files.find_file(params.get("filename"))
            elif intent == "file_analyze":
                return self.files.analyze_found_file(params.get("filename"))

            # 7. Protocols
            elif intent == "protocol":
                p_name = params.get("protocol_name", "").lower()
                if "party" in p_name: return self.protocols.house_party()
                if "slate" in p_name: return self.protocols.clean_slate()
                if "mark" in p_name: return self.protocols.mark_42()

            # 8. IOT
            elif intent == "iot_trigger":
                return self.iot.trigger(params.get("device"))

            return None
        except Exception as e:
            logging.error(f"Routing error: {e}")
            return f"Kernel routing failed: {e}"
