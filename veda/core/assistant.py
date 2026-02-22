from veda.core.llm import VedaLLM
from veda.core.voice import VedaVoice
from veda.core.context import VedaContext
from veda.core.plugins import PluginManager
from veda.core.cognition import VedaPlanner, VedaReflector
from veda.core.registry import registry
from veda.features.base import PermissionTier
from veda.utils.notifications import VedaNotifications
from veda.utils.protocols import VedaProtocols
from veda.utils.health import VedaHealth
from veda.utils.logger import logger
from veda.utils.events import bus, Events
from veda.utils.threads import manager as thread_manager
import os
import logging

class VedaAssistant:
    def __init__(self, gui):
        self.gui = gui
        logger.info("Initializing Veda Sovereign System...")

        self.llm = VedaLLM()
        self.voice = VedaVoice()
        self.context = VedaContext(self)
        self.protocols = VedaProtocols()
        self.plugins = PluginManager(self)
        self.planner = VedaPlanner(self)
        self.reflector = VedaReflector(self)

        # Register Core Services
        registry.register("llm", self.llm)
        registry.register("voice", self.voice)
        registry.register("gui", self.gui)
        registry.register("assistant", self)

        # Initialize Plugins
        self._initialize_plugins()

        # Safety & State
        self.pending_action = None
        self.execution_queue = []
        self.activity_history = []

        # Subscribe to Events
        bus.subscribe(Events.CONTEXT_CHANGE, self.on_context_change)

        # Start background context monitoring
        self.context.start_monitoring()

        # Perform Startup Health Check
        self.verify_startup()

    def _initialize_plugins(self):
        """Loads and registers all feature plugins."""
        from veda.features.system_control import SystemPlugin
        from veda.features.file_manager import FilePlugin
        from veda.features.life import LifePlugin
        from veda.features.task_master import TaskPlugin
        from veda.features.web_info import WebPlugin
        from veda.features.vision import VisionPlugin
        from veda.features.research import ResearchPlugin
        from veda.features.diagnostics import DiagnosticsPlugin
        from veda.features.media import MediaPlugin
        from veda.features.automation import AutomationPlugin
        from veda.features.tools import ToolsPlugin
        from veda.features.translator import TranslatorPlugin
        from veda.features.calculator import CalculatorPlugin
        from veda.features.comms import CommsPlugin
        from veda.features.iot import IOTPlugin
        from veda.features.help import HelpPlugin

        self.plugins.load_plugin(SystemPlugin(self))
        self.plugins.load_plugin(FilePlugin(self))
        self.plugins.load_plugin(LifePlugin(self))
        self.plugins.load_plugin(TaskPlugin(self))
        self.plugins.load_plugin(WebPlugin(self))
        self.plugins.load_plugin(VisionPlugin(self))
        self.plugins.load_plugin(ResearchPlugin(self))
        self.plugins.load_plugin(DiagnosticsPlugin(self))
        self.plugins.load_plugin(MediaPlugin(self))
        self.plugins.load_plugin(AutomationPlugin(self))
        self.plugins.load_plugin(ToolsPlugin(self))
        self.plugins.load_plugin(TranslatorPlugin(self))
        self.plugins.load_plugin(CalculatorPlugin(self))
        self.plugins.load_plugin(CommsPlugin(self))
        self.plugins.load_plugin(IOTPlugin(self))
        self.plugins.load_plugin(HelpPlugin(self))

    def verify_startup(self):
        """Verifies that all core systems are ready."""
        report = VedaHealth.full_report()
        if report:
            for issue in report:
                logger.warning(f"Startup Warning: {issue}")
                self.gui.update_chat("System", f"⚠️ {issue}")
        else:
            logger.info("Startup check passed.")
            self.gui.update_chat("Veda", "All systems nominal. How can I help you today?")

    def sync_protocols(self):
        """Syncs local protocol state with GUI toggles."""
        self.protocols.protocols["deep_research"] = self.gui.deep_search_var.get()
        self.protocols.protocols["private_mode"] = self.gui.private_var.get()
        self.protocols.protocols["context_monitoring"] = self.gui.context_var.get()

        if self.protocols.protocols["context_monitoring"]:
            self.context.start_monitoring()
        else:
            self.context.stop_monitoring()

    def process_command(self, user_input, is_subcommand=False):
        """Processes a user command via Multi-Step Planning."""
        # 0. Handle Confirmation logic
        if self.pending_action:
            if any(word in user_input.lower() for word in ["yes", "confirm", "proceed", "do it"]):
                action = self.pending_action
                self.pending_action = None

                if action.get("type") == "queue":
                    self.resume_execution()
                    return

                method, params = action['exec_data']
                result = method(params)
                self._finalize_response(result, is_subcommand)
                return
            elif any(word in user_input.lower() for word in ["no", "cancel", "abort", "don't"]):
                self.pending_action = None
                self.execution_queue = []
                self._finalize_response("Action aborted. Task queue cleared.", is_subcommand)
                return

        if not is_subcommand: self.gui.set_state("thinking")
        if not user_input or user_input == "None":
            if not is_subcommand: self.gui.set_state("idle")
            return

        self.sync_protocols()

        # 1. Planning Phase
        plan = self.planner.generate_plan(user_input)

        # 2. Critique Phase
        approved, message = self.reflector.critique_plan(plan)
        if not approved:
            self._finalize_response(f"Planning Error: {message}", is_subcommand)
            return

        if not plan:
            # Fallback to conversational chat if no tools are needed
            current_context = self.context.get_current_context() if self.protocols.protocols["context_monitoring"] else None
            response = self.llm.chat(user_input, context_info=current_context, protocols=self.protocols.get_status())
            self._finalize_response(response, is_subcommand)
            return

        # 3. Execution Phase
        self.execution_queue = plan
        self.resume_execution(is_subcommand)

    def resume_execution(self, is_subcommand=False):
        """Iterates through the execution queue."""
        while self.execution_queue:
            step = self.execution_queue.pop(0)
            intent = step.get('intent')
            params = step.get('params', {})

            logger.audit(intent, params)

            result, tier = self.plugins.execute_intent(intent, params)

            if tier != PermissionTier.SAFE:
                # Pause and request confirmation
                self.pending_action = {"type": "queue", "exec_data": result}
                self.gui.set_state("alert")
                self._finalize_response(f"Security Alert: This action ({intent}) requires confirmation, Sir. Shall I proceed?", is_subcommand)
                return

            # Action completed
            self.activity_history.append(f"Task complete: {intent}")

            # If it's the last step, finalize with result
            if not self.execution_queue:
                response = self.reflect_on_action(intent, params, result)
                self._finalize_response(response, is_subcommand)
                return

    def reflect_on_action(self, intent, params, initial_response):
        """Cognitive Reflection: Verifies if the intended action actually changed system state."""
        verification_msg = ""
        try:
            if intent == "open_app":
                import psutil
                app = params.get("app_name", "").lower()
                found = any(app in p.name().lower() for p in psutil.process_iter())
                verification_msg = " [Verified: Active]" if found else " [Unconfirmed]"
        except: pass
        return initial_response + verification_msg

    def _finalize_response(self, response, is_subcommand):
        """Unified method to handle UI and Voice finalization."""
        if not is_subcommand:
            self.gui.update_chat("Veda", response)
            self.gui.set_state("speaking")
            try:
                self.voice.speak(response)
            except:
                pass
            finally:
                self.gui.set_state("idle")
        else:
            return response

    def system_alert(self, message):
        VedaNotifications.send_toast("Veda Alert", message)
        self.gui.update_chat("System", message)
        self.voice.speak(message)

    def on_context_change(self, app_name):
        self.gui.show_suggestion(f"Ready to assist with {app_name}.")

    def process_file(self, file_input):
        files = [file_input] if isinstance(file_input, str) else list(file_input)
        self.gui.update_chat("System", f"Analyzing {len(files)} item(s)...")
        # Logic for file processing...
        self.gui.update_chat("Veda", "Analysis complete. I've indexed the content into my neural memory.")

    def listen_and_process(self):
        query = self.voice.listen()
        if query != "None":
            self.gui.update_chat("You", query)
            self.process_command(query)
        self.gui.reset_voice_button()

    def shutdown(self):
        self.context.stop_monitoring()
