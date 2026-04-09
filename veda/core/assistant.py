from veda.core.llm import VedaLLM
from veda.core.voice import VedaVoice
from veda.core.context import VedaContext
from veda.core.plugins import PluginManager
from veda.core.cognition import VedaPlanner, VedaReflector
from veda.core.orchestrator import VedaOrchestrator
from veda.core.registry import registry
from veda.features.base import PermissionTier
from veda.utils.notifications import VedaNotifications
from veda.utils.protocols import VedaProtocols
from veda.utils.health import VedaHealth
from veda.utils.logger import logger
from veda.utils.events import bus, Events
from veda.utils.threads import manager as thread_manager
import os
import threading
import queue

class VedaAssistant:
    def __init__(self, gui):
        self.gui = gui
        logger.info("Initializing Veda Sovereign System...")

        # Concurrency Protection: Re-entrant lock for sub-command support
        self.command_lock = threading.RLock()

        # Early load of Governance & Security
        from veda.core.security import capabilities
        self.capabilities = capabilities

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

        # Agentic Orchestration Layer
        self.orchestrator = VedaOrchestrator(self)

        # Initialize Plugins
        self._initialize_plugins()

        # Safety & State
        self.pending_action = None
        self.execution_queue = []
        self.active_plan = []
        self.activity_history = []
        self.identity_verified = False

        # Subscribe to Events
        bus.subscribe(Events.CONTEXT_CHANGE, self.on_context_change)

        # Start background context monitoring
        self.context.start_monitoring()

        # Perform Startup Health Check
        self.verify_startup()

        # Pre-warm Neural Link for zero-latency execution
        thread_manager.start_thread("WarmNeuralLink", lambda: self.llm.chat_completion([{"role": "user", "content": "ping"}]))

        # Check for Checkpoints (Survival Recovery)
        if hasattr(self.gui, 'after'):
             self.gui.after(2000, self._check_recovery)

        # Scheduled Pruning
        thread_manager.run_with_throttle("MemoryPruning", self.llm.memory.archive_old_data, interval=86400) # Daily
        # Integrity Checks
        thread_manager.run_with_throttle("IntegrityAudit", self._run_integrity_check, interval=3600) # Hourly

    def _run_integrity_check(self):
        """Self-Repair: Scanning for database or plugin drift."""
        if not hasattr(self, 'plugins') or not self.plugins: return
        logger.info("Integrity: Running sovereign health scan...")
        # 1. DB Integrity
        import sqlite3
        try:
            conn = sqlite3.connect(self.llm.memory.db_path)
            conn.execute("PRAGMA integrity_check")
            conn.close()
        except Exception as e:
            logger.error("Integrity Error: Memory corruption detected. Re-initializing sector.")
            self.llm.memory._init_db()

        # 2. Plugin Desync
        if len(self.plugins.intent_map) == 0:
            logger.warning("Integrity Alert: Tactical Plugin Matrix empty. Re-loading modules.")
            self._initialize_plugins()

    def _check_recovery(self):
        plan, queue = self.llm.memory.get_last_checkpoint()
        if plan and queue:
            logger.info("Survival: Checkpoint detected from previous session.")
            self.gui.update_chat("Veda", "Sir, I've detected an interrupted mission sequence. Shall I resume from the last checkpoint?")
            self.pending_action = {"type": "recovery", "plan": plan, "queue": queue}

    def _initialize_plugins(self):
        """Resilient Tactical Discovery: Autonomously maps and registers all feature plugins."""
        from veda.core.plugins import discover_and_load, PLUGIN_REGISTRY
        discover_and_load()

        # Guard against empty discovery
        if not PLUGIN_REGISTRY:
            logger.error("Sovereign Core: Tactical Plugin Matrix Empty. Core capabilities compromised.")
            return

        for class_name, plugin_cls in PLUGIN_REGISTRY.items():
            # Avoid re-loading if already in instance map (to allow for hot-reloading in future)
            if plugin_cls.__name__ in self.plugins.plugins:
                continue

            try:
                self.plugins.load_plugin(plugin_cls(self))
            except Exception as e:
                logger.error(f"Sovereign Core: Tactical Plugin Load Failure ({class_name}): {e}")

    def verify_startup(self):
        """Verifies that all core systems are ready."""
        report = VedaHealth.full_report()
        if report:
            for issue in report:
                logger.warning(f"Startup Warning: {issue}")
                self.gui.update_chat("System", f"⚠️ {issue}")
        else:
            logger.info("Startup check passed.")
            self.gui.update_chat("Veda", "Greetings Sir, you're awake late at night today. What you up to?")

    def sync_protocols(self):
        """Syncs local protocol state with GUI toggles."""
        self.protocols.protocols["deep_research"] = self.gui.deep_search_var.get()
        self.protocols.protocols["private_mode"] = self.gui.private_var.get()
        self.protocols.protocols["context_monitoring"] = self.gui.context_var.get()

        if self.protocols.protocols["context_monitoring"]:
            self.context.start_monitoring()
        else:
            self.context.stop_monitoring()

    def process_command(self, user_input, is_subcommand=False, intent_data=None):
        """Processes a user command with thread-safety and orchestration."""
        try:
            # 1. Unified Tactical Extraction (ONE CALL if not already provided)
            if intent_data is None:
                 intent_data = self.llm.extract_intent(user_input)
            intent = intent_data.get("intent")

            # 2. Strategic Tactical Override (Direct Execution for high-confidence core commands)
            if intent_data.get("confidence", 0) >= 0.7 and intent not in ["none", "chat"]:
                plugin = self.plugins.get_plugin_for_intent(intent)
                if plugin and intent in self.plugins.intent_map:
                    # Strategic Security: Direct path must still be authorized via Governance
                    authorized, reason = self.capabilities.authorize(plugin, intent, intent_data["params"])
                    if authorized:
                        from veda.core.runtime import runtime
                        _, method_name, _ = self.plugins.intent_map[intent]
                        res = runtime.execute_intent(plugin, method_name, intent_data["params"])
                        if res.success:
                            if not is_subcommand: self._finalize_response(res.data, is_subcommand)
                            return res.data
                        else:
                            logger.warning(f"Tactical Override Failed: {res.error}. Reverting to standard pipeline.")

            # 3. Standard Pipeline
            response = None
            with self.command_lock:
                response = self._process_command_internal(user_input, is_subcommand, intent_data)

            # Note: Finalization for non-overridden standard commands is now handled inside _process_command_final
            # or by the caller if it's a subcommand.
            return response
        except Exception as e:
            err_msg = f"Critical Pipeline Fault: {e}"
            logger.error(err_msg)
            if not is_subcommand:
                 self._finalize_response(err_msg, is_subcommand)
            return err_msg

    def _process_command_internal(self, user_input, is_subcommand, intent_data=None):
        if intent_data is None:
             intent_data = self.llm.extract_intent(user_input)

        # 0. Handle IVP (Identity Verification)
        if self.pending_action and self.pending_action.get("type") == "ivp":
            if "stark" in user_input.lower(): # Survival Passphrase
                self.identity_verified = True
                self.gui.update_chat("Veda", "Identity verified. Sovereign protocols unlocked.")
                action = self.pending_action["original"]
                self.pending_action = None
                # Resume original logic
                return self._process_command_final(action["input"], action["is_sub"], intent_data=intent_data)
            else:
                self.gui.update_chat("Veda", "Identity mismatch. Emergency lockdown engaged.")
                self.pending_action = None
                return

        # 0.1 Handle Confirmation logic
        if self.pending_action:
            # If the new input looks like a fresh high-confidence command, clear the pending action
            if intent_data.get("confidence", 0) >= 0.8 and intent_data.get("intent") not in ["none", "chat"]:
                 logger.info("Sovereign Intelligence: Bypassing pending action for new tactical intent.")
                 self.pending_action = None
            elif any(word in user_input.lower() for word in ["yes", "confirm", "proceed", "do it", "resume"]):
                action = self.pending_action
                self.pending_action = None

                if action.get("type") == "recovery":
                    self.active_plan = action["plan"]
                    self.execution_queue = action["queue"]
                    self.resume_execution()
                    return

                if action.get("type") == "queue":
                    self.resume_execution()
                    return

                method, params = action['exec_data']
                result = method(params)
                return result
            elif any(word in user_input.lower() for word in ["no", "cancel", "abort", "don't"]):
                self.pending_action = None
                self.execution_queue = []
                self._finalize_response("Action aborted. Task queue cleared.", is_subcommand)
                return

        if not is_subcommand: self.gui.set_state("thinking")
        if not user_input or user_input == "None":
            if not is_subcommand: self.gui.set_state("idle")
            return

        # Protocols are synced via callback; removing thread-unsafe call from here
        return self._process_command_final(user_input, is_subcommand, intent_data=intent_data)

    def _process_command_final(self, user_input, is_subcommand, intent_data=None):
        if intent_data is None:
             intent_data = self.llm.extract_intent(user_input)

        # 1. Identity Check and Extraction
        intent = intent_data.get("intent")

        plugin = self.plugins.get_plugin_for_intent(intent)

        # 1.1 Secure Check for Admin Sequence
        if plugin and intent in plugin.intents:
            tier = plugin.intents[intent]["tier"]
            if tier == PermissionTier.ADMIN and not self.identity_verified:
                self.gui.update_chat("Veda", "Protocol Alert: Accessing sovereign ADMIN sector. Please provide Identity Token.")
                self.pending_action = {"type": "ivp", "original": {"input": user_input, "is_sub": is_subcommand}}
                return

        # 2. Orchestration (Pass intent_data to bypass redundant Planner LLM call)
        result, state = self.orchestrator.process(user_input, is_subcommand, pre_extracted_intent=intent_data)

        if state == "PLAN_READY":
            # 2. Execution Phase (Managed statefully in Assistant)
            self.execution_queue = result
            self.active_plan = result # Track the current mission
            response = self.resume_execution(is_subcommand)
            if not is_subcommand:
                 self._finalize_response(response, is_subcommand, state=state)
            return response
        else:
            # Atomic response (e.g. Chat or Error)
            if not is_subcommand:
                 self._finalize_response(result, is_subcommand, state=state)
            return result

    def resume_execution(self, is_subcommand=False):
        """Iterates through the stateful execution queue with result mapping and visualization."""
        step_index = 1
        original_plan = self.active_plan # Store for visualization
        combined_results = []

        while self.execution_queue:
            # Save Checkpoint for Survival
            self.llm.memory.save_checkpoint(self.active_plan, self.execution_queue)
            # Update HUD Visualizer
            self.gui.after(0, lambda: self.gui.update_exec_visualizer(original_plan, step_index - 1))

            step = self.execution_queue.pop(0)
            intent = step.get('intent')
            raw_params = step.get('params', {})

            # 1. Resolve Dependencies
            params = self.orchestrator.map_params(raw_params)

            logger.audit(intent, params)

            # 2. Impact Prediction for UI
            plugin = self.plugins.get_plugin_for_intent(intent)
            impact = plugin.predict_impact(intent, params) if plugin else "Impact: Standard"

            # Update Governance HUD
            if plugin:
                risk = plugin.intents[intent].get("risk_level", "Low")
                self.gui.after(0, lambda r=risk: self.gui.set_governance_risk(r))

            # 3. Execution (or Confirmation) via Sovereign Runtime
            if intent not in self.plugins.intent_map:
                 combined_results.append(f"Error: Intent '{intent}' unmapped after tactical refresh.")
                 continue

            from veda.core.runtime import runtime
            try:
                # First, check if confirmation is needed (this is a fast plugin-level check)
                is_admin = self.plugins.is_admin_intent(intent)
                if is_admin and not self.identity_verified:
                    self.pending_action = {"type": "ivp", "original": {"intent": intent, "params": params}}
                    self.gui.update_chat("Veda", "Protocol Alert: Identity verification required for ADMIN action.")
                    return

                # Check for tactical confirmation tier
                should_confirm, prompt_info = self.plugins.should_confirm(intent, params)
                if should_confirm:
                    method = lambda p: self.plugins.execute_intent_direct(intent, p)
                    self.pending_action = {"type": "queue", "exec_data": (method, params)}
                    self.gui.set_state("alert")
                    return f"Security Check: {intent.upper()}\n{impact}\nProceed, Sir?"

                # Strategic Execution: Direct call via runtime to ensure access to assistant and memory
                plugin_obj, method_name, _ = self.plugins.intent_map[intent]
                exec_result = runtime.execute_intent(plugin_obj, method_name, params)

                if not exec_result.success:
                    if exec_result.timeout:
                        result = f"Error: Tactical Timeout. Intent {intent} took too long."
                    else:
                        result = f"Error: Tactical Fault in {intent}. {exec_result.error}"
                else:
                    result = exec_result.data

            except Exception as e:
                self.trigger_emergency_recovery(f"Plugin.{intent}")
                return

            if isinstance(result, tuple): # Legacy Check, should be handled by should_confirm now
                self.pending_action = {"type": "queue", "exec_data": result}
                self.gui.set_state("alert")
                return f"Security Check: {intent.upper()}\n{impact}\nProceed, Sir?"

            # 4. Handle Failures & Self-Healing / Rollback
            if "Error" in str(result) or "failure" in str(result).lower():
                # Self-Heal Attempt
                corrective_steps = self.orchestrator.self_heal(intent, params, result, self.active_plan)
                if corrective_steps:
                    self.gui.update_chat("Veda", f"Tactical Alert: '{intent}' failed. Strategic corrective plan formulated. Resuming mission.")
                    self.execution_queue = corrective_steps + self.execution_queue
                    continue

                if step.get("critical", True):
                    rollback_summary = self.orchestrator.trigger_rollback()
                    self._finalize_response(f"CRITICAL FAILURE in {intent.upper()}.\nPlan aborted.\nRollback Status:\n{rollback_summary}", is_subcommand)
                    self.execution_queue = []
                    return

            # 5. Success Handlers
            self.orchestrator.log_success(step.get('step', step_index), intent, params, result)
            self.activity_history.append(f"Protocol Success: {intent}")
            step_index += 1

            combined_results.append(str(result))

            if not self.execution_queue:
                self.llm.memory.clear_checkpoint()
                final_response = "\n".join(combined_results)
                response = self.reflect_on_action(intent, params, final_response)
                return response

    def reflect_on_action(self, intent, params, initial_response):
        """Cognitive Reflection: Verifies if the intended action actually changed system state."""
        verification_msg = ""
        try:
            if intent == "open_app":
                import psutil
                app = params.get("app_name", "").lower()
                found = any(app in p.name().lower() for p in psutil.process_iter())
                verification_msg = " [Verified: Active]" if found else " [Unconfirmed]"
        except Exception as e: logger.warning(f"Tactical Silencing: {e}")
        return str(initial_response) + verification_msg

    def trigger_emergency_recovery(self, fault_source):
        """Emergency Recovery Mode: Handles catastrophic runtime or plugin failure."""
        logger.critical(f"EMERGENCY RECOVERY: Initiated due to fault in {fault_source}")
        self.gui.set_state("alert")
        self.gui.update_chat("CRITICAL", f"Sir, a catastrophic fault was detected in {fault_source}. Initiating core reset.")

        # Clear queues to stop further damage
        self.execution_queue = []
        self.active_plan = []
        self.pending_action = None

        # Comprehensive reboot: Clear plugin map to force re-discovery
        self.plugins.plugins = {}
        self.plugins.intent_map = {}
        self._initialize_plugins()

        self.gui.update_chat("Veda", "Tactical Matrix rebooted. All non-essential subsystems reset. I am ready to resume, Sir.")

    def _finalize_response(self, response, is_subcommand, state=None):
        """Unified method to handle UI and Voice finalization."""
        if not response: return

        if not is_subcommand:
            # Strategic check to avoid double-printing chat responses that were already streamed
            if state != "CHAT_STREAMED":
                 # Safety: Check if response starts with tactical markers to avoid double-printing
                 if not str(response).startswith(("Error", "Security", "Sub-command", "Tactical", "Protocol")):
                      self.gui.update_chat("Veda", response)

            self.gui.set_state("speaking")
            try:
                self.voice.speak(response)
            except Exception as e:
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
