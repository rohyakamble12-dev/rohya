from veda.utils.logger import logger
from veda.core.registry import registry
from veda.features.base import PermissionTier

class VedaOrchestrator:
    def __init__(self, assistant):
        self.assistant = assistant
        self.results_cache = {}
        self.execution_history = [] # List of (plugin, intent, params)
        registry.register("orchestrator", self)

    def process(self, user_input, is_subcommand=False, pre_extracted_intent=None):
        """Strategic Loop: Plan -> Validate -> Execute."""
        # 1. PLAN (Bypass for high-confidence atomic intents)
        intent_data = pre_extracted_intent or self.assistant.llm.extract_intent(user_input)
        intent = intent_data.get("intent")

        if intent_data.get("confidence", 0) >= 0.8 and intent != "none":
            if intent == "chat":
                return intent_data["params"]["response"], "CHAT"
            plan = [{"step": 1, "intent": intent, "params": intent_data.get("params", {}), "critical": True}]
        else:
            plan = self.assistant.planner.generate_plan(user_input)

        if not plan:
            # Multi-token streaming for chat responses
            self.assistant.gui.after(0, lambda: self.assistant.gui._update_chat_ui("Veda", "", is_streaming=True))
            # The chat result will be printed by the streaming callback.
            # We return a special state to the Assistant to prevent a second static print.
            res = self.assistant.llm.chat(user_input, stream_callback=self.assistant.gui.stream_to_chat)
            return res, "CHAT_STREAMED"

        # 2. VALIDATE
        validator = registry.get("capability_manager")
        if not validator:
             logger.warning("Governance: Capability Manager missing. Bypassing validation.")
             return plan, "PLAN_READY"

        for step in plan:
            intent = step.get("intent")
            params = step.get("params", {})
            plugin = self.assistant.plugins.get_plugin_for_intent(intent)

            if not plugin:
                 logger.warning(f"Tactical Desync: {intent} unmapped. Attempting core refresh.")
                 self.assistant._initialize_plugins()
                 plugin = self.assistant.plugins.get_plugin_for_intent(intent)
                 if not plugin: return f"Tactical Error: Intent '{intent}' remains unmapped after refresh.", "ERROR"

            auth, reason = validator.authorize(plugin, intent, params)
            if not auth and "Policy" in reason: return f"Security Block: {reason}", "ERROR"

            valid, msg = validator.validate_input(plugin, intent, params)
            if not valid: return f"Schema Violation [{intent}]: {msg}", "ERROR"

        self.results_cache = {}
        self.execution_history = []
        return plan, "PLAN_READY"

    def map_params(self, params):
        mapped = {}
        for k, v in params.items():
            if isinstance(v, str) and v.startswith("$RESULT_"):
                try:
                    parts = v.split("_")
                    if len(parts) > 1:
                        step_idx = int(parts[1])
                        mapped[k] = self.results_cache.get(step_idx, v)
                    else:
                        mapped[k] = v
                except (ValueError, IndexError):
                    mapped[k] = v
            else:
                mapped[k] = v
        return mapped

    def log_success(self, step_index, intent, params, result):
        plugin = self.assistant.plugins.get_plugin_for_intent(intent)
        self.results_cache[step_index] = result
        self.execution_history.append((plugin, intent, params))

    def trigger_rollback(self):
        """Reverses state-altering actions in reverse order."""
        logger.warning(f"ROLLBACK INITIATED: Reversing {len(self.execution_history)} steps.")
        self.assistant.gui.after(0, lambda: self.assistant.gui.set_rollback_state(True))

        reversal_log = []
        for plugin, intent, params in reversed(self.execution_history):
            metadata = plugin.intents.get(intent)
            undo_method = metadata.get("undo_method")

            if undo_method:
                try:
                    logger.info(f"Rollback: Executing undo for {intent}")
                    undo_method(params)
                    reversal_log.append(f"✓ Reversed {intent}")
                except Exception as e:
                    logger.error(f"Rollback Failure for {intent}: {e}")
                    reversal_log.append(f"✗ Failed to reverse {intent}")
            else:
                reversal_log.append(f"○ {intent} (No undo logic)")

        self.assistant.gui.after(2000, lambda: self.assistant.gui.set_rollback_state(False))
        return "\n".join(reversal_log)

    def self_heal(self, failed_intent, params, error, current_plan):
        """Self-Healing: Requests an alternative strategy from the LLM upon step failure."""
        logger.warning(f"SELF-HEAL: Strategic failure in {failed_intent}. Requesting corrective plan.")
        self.assistant.gui.after(0, lambda: self.assistant.gui.set_self_heal_state(True))

        heal_prompt = (
            f"Veda Tactical Alert: Sub-task '{failed_intent}' failed with params {params}.\n"
            f"Error: {error}\n"
            f"Current Mission Plan: {current_plan}\n"
            f"Sir, this approach failed. Generate an alternative single-step command or "
            f"a revised sequence to achieve the original goal. Respond ONLY with raw JSON."
        )

        try:
            # High-attention tactical request
            res = self.assistant.llm.chat(heal_prompt, protocols="emergency_heal")
            # Parse corrective plan using the hardened JSON parser
            corrective_steps = self.assistant.llm._parse_json(res)

            self.assistant.gui.after(2000, lambda: self.assistant.gui.set_self_heal_state(False))
            return corrective_steps if isinstance(corrective_steps, list) else [corrective_steps]
        except Exception as e:
            self.assistant.gui.after(2000, lambda: self.assistant.gui.set_self_heal_state(False))
            return None
