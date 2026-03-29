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
        self.iot = IOTModule(assistant)
        self.protocols = ProtocolModule(assistant)
        self.comms = CommsModule()
        self.auto = AutomationModule()

    def get_registry(self):
        """Returns a summarized registry of all tactical intents."""
        return (
            "--- TACTICAL COMMAND REGISTRY ---\n"
            "SYSTEM: open_app, close_app, screenshot, lock_pc, shutdown, restart, sleep, set_theme, set_volume, set_brightness, move_file, optimize_system, system_info, network_info.\n"
            "INTEL: web_search, wikipedia, weather, news, market_data, deep_research, convert_currency, convert_units, get_eta, creator_registry.\n"
            "VISION: vision_describe, vision_face, security_scan, vision_scan, screen_read.\n"
            "AUTOMATION: macro_record, macro_stop, macro_play, macro_list, type_text, execute_script.\n"
            "PROTOCOLS: morning, night, home, lockdown, barn, legion, verity, ultron, clean_slate, power_efficiency.\n"
            "MISC: switch_identity, add_todo, show_todo, pomodoro, play_music, translate, session_save, session_restore, command_registry."
        )

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
                return self.system.get_sys_info(self.assistant)
            elif intent == "network_info":
                return self.system.get_network_info()
            elif intent == "lock_pc":
                return self.system.lock_pc()
            elif intent == "shutdown":
                return self.system.shutdown()
            elif intent == "restart":
                return self.system.restart()
            elif intent == "sleep":
                return self.system.sleep_mode()
            elif intent == "active_window":
                return self.system.get_active_window()
            elif intent == "window_control":
                return self.system.manipulate_window(params.get("action"), params.get("title"))
            elif intent == "set_theme":
                return self.system.set_dark_mode(params.get("mode", "dark") == "dark")
            elif intent == "hud_mode":
                return self.assistant.gui.set_hud_mode(params.get("mode", "analytical"))
            elif intent == "set_wallpaper":
                return self.system.set_wallpaper(params.get("path"))
            elif intent == "set_dnd":
                return self.system.toggle_focus_assist(params.get("enabled", True))
            elif intent == "desktop_switch":
                return self.system.switch_virtual_desktop(params.get("direction", "next"))
            elif intent == "night_light":
                return self.system.set_night_light(params.get("enabled", True))
            elif intent == "set_workspace":
                return self.system.set_workspace(params.get("mode"), self.assistant)
            elif intent == "clipboard_get":
                return self.system.get_clipboard()
            elif intent == "clipboard_set":
                return self.system.set_clipboard(params.get("text"))
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
            elif intent == "macro_list":
                return self.auto.list_macros()
            elif intent == "type_text":
                return self.auto.type_text(params.get("text"))
            elif intent == "execute_script":
                return self.auto.execute_script(params.get("code"))
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
            elif intent == "session_save":
                return self.system.capture_session(self.assistant)
            elif intent == "session_restore":
                return self.system.restore_session(self.assistant)
            elif intent == "network_discovery":
                return self.system.discover_network_devices()
            elif intent == "optimize_system":
                return self.system.optimize_system()
            elif intent == "learn_command":
                self.assistant.memory.add_rule(params.get("trigger"), params.get("action"))
                return f"Rule integrated: '{params.get('trigger')}' now triggers tactical sequence."

            # 2. Intel & Search
            elif intent == "web_search":
                return self.intel.search(params.get("query"))
            elif intent == "site_search":
                return self.intel.site_search(params.get("platform"), params.get("query"))
            elif intent == "wikipedia":
                return self.intel.get_wiki(params.get("topic"))
            elif intent == "weather":
                return self.intel.get_weather(params.get("city"))
            elif intent == "get_eta":
                return self.intel.get_eta(params.get("origin"), params.get("destination"))
            elif intent == "news":
                return self.intel.get_news(params.get("topic", "technology"))
            elif intent == "market_data":
                return self.intel.get_market_data(params.get("symbol"))
            elif intent == "deep_research":
                return self.intel.deep_research(params.get("query"))
            elif intent == "convert_currency":
                return self.intel.convert_currency(float(params.get("amount", 1)), params.get("from_curr"), params.get("to_curr"))
            elif intent == "convert_units":
                return self.intel.convert_units(float(params.get("value")), params.get("from_unit"), params.get("to_unit"))
            elif intent == "creator_registry":
                return self.intel.get_creator_registry()

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
            elif intent == "daily_outlook":
                return self.prod.daily_strategic_outlook()
            elif intent == "affinity_report":
                return self.assistant.monitor.get_affinity_report()

            # 5. Vision
            elif intent == "vision_describe":
                return self.vision.capture_and_describe()
            elif intent == "vision_face":
                return self.vision.face_detect()
            elif intent == "security_scan":
                return self.vision.security_perimeter_scan()
            elif intent == "operator_state":
                return self.vision.analyze_operator_state()
            elif intent == "vision_scan":
                return self.vision.scan_objects()
            elif intent == "vision_camera":
                return self.assistant.toggle_camera()
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
            elif intent == "organize_files":
                return self.files.organize_directory(params.get("path"))
            elif intent == "find_duplicates":
                return self.files.find_duplicates(params.get("path"))

            # 7. Protocols
            elif intent == "switch_identity":
                return self.assistant.switch_identity(params.get("name", "FRIDAY"))
            elif intent == "protocol":
                p_name = params.get("protocol_name", "").lower()
                if "party" in p_name: return self.protocols.house_party()
                if "slate" in p_name: return self.protocols.clean_slate()
                if "mark" in p_name: return self.protocols.mark_42()
                if "edith" in p_name: return self.protocols.edith()
                if "ultron" in p_name: return self.protocols.ultron()
                if "morning" in p_name: return self.protocols.good_morning()
                if "night" in p_name: return self.protocols.good_night()
                if "home" in p_name: return self.protocols.im_home()
                if "lockdown" in p_name: return self.protocols.security_lockdown()
                if "power" in p_name: return self.protocols.power_efficiency()
                if "extremis" in p_name: return self.protocols.extremis()

            elif intent == "command_registry":
                return self.get_registry()

            # 8. IOT
            elif intent == "iot_trigger":
                return self.iot.trigger(params.get("device"))
            elif intent == "habitat_report":
                return self.iot.get_habitat_report()
            elif intent == "set_scene":
                return self.iot.set_scene(params.get("name"))

            return None
        except Exception as e:
            logging.error(f"Routing error: {e}")
            return f"Kernel routing failed: {e}"
